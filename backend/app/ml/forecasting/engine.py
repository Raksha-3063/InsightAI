import time
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from backend.app.ml.statistics.service import clean_float

try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False

def compute_forecasting_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """
    Compute time series forecasting metrics: MAE, RMSE, MAPE, SMAPE.
    """
    # Filter out zeros to prevent zero division in MAPE/SMAPE
    valid_mask = y_true != 0
    y_t = y_true[valid_mask]
    y_p = y_pred[valid_mask]
    
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    
    if len(y_t) > 0:
        mape = np.mean(np.abs((y_t - y_p) / y_t)) * 100
        smape = np.mean(2 * np.abs(y_t - y_p) / (np.abs(y_t) + np.abs(y_p))) * 100
    else:
        mape = 0.0
        smape = 0.0
        
    return {
        "mae": clean_float(mae),
        "rmse": clean_float(rmse),
        "mape": clean_float(mape),
        "smape": clean_float(smape)
    }

def train_forecasting_model(
    df: pd.DataFrame,
    date_col: str,
    target_col: str,
    algorithm: str,
    horizon: int = 30,
    confidence_level: float = 0.95,
    seasonal_period: int = 7,
    train_ratio: float = 0.8,
    freq: str = "D"
) -> Tuple[Any, Dict[str, Any], Dict[str, Any]]:
    """
    Train a forecasting model and calculate predictions, confidence bands, residuals, and metrics.
    """
    # 1. Parse and sort dataframe chronologically
    df_clean = df.dropna(subset=[date_col, target_col]).copy()
    df_clean[date_col] = pd.to_datetime(df_clean[date_col])
    df_clean = df_clean.sort_values(by=date_col).reset_index(drop=True)
    
    dates = df_clean[date_col]
    values = df_clean[target_col].astype(float).values
    
    # Train / Test split ratio
    split_idx = int(len(values) * train_ratio)
    if split_idx < 5:
        split_idx = max(1, len(values) - 2)
        
    train_values = values[:split_idx]
    test_values = values[split_idx:]
    
    test_dates = dates.iloc[split_idx:]
    
    fitted_model = None
    test_preds = np.zeros(len(test_values))
    
    # 2. Fit models and predict on test split
    if algorithm == "arima":
        try:
            model = ARIMA(train_values, order=(1, 1, 1))
            fitted_model = model.fit()
            test_preds = fitted_model.forecast(steps=len(test_values))
        except Exception:
            # Fallback to simple Exponential Smoothing
            model = ExponentialSmoothing(train_values, trend="add")
            fitted_model = model.fit()
            test_preds = fitted_model.forecast(steps=len(test_values))
            algorithm = "arima_fallback_es"
            
    elif algorithm == "sarima":
        try:
            model = SARIMAX(train_values, order=(1, 1, 1), seasonal_order=(1, 1, 1, seasonal_period))
            fitted_model = model.fit(disp=False)
            test_preds = fitted_model.forecast(steps=len(test_values))
        except Exception:
            # Fallback to ARIMA
            model = ARIMA(train_values, order=(1, 1, 1))
            fitted_model = model.fit()
            test_preds = fitted_model.forecast(steps=len(test_values))
            algorithm = "sarima_fallback_arima"
            
    elif algorithm == "prophet" and HAS_PROPHET:
        try:
            df_prophet_train = pd.DataFrame({
                "ds": dates.iloc[:split_idx],
                "y": train_values
            })
            m = Prophet(interval_width=confidence_level)
            m.fit(df_prophet_train)
            fitted_model = m
            
            # Predict on test split
            future_test = pd.DataFrame({"ds": test_dates})
            forecast_test = m.predict(future_test)
            test_preds = forecast_test["yhat"].values
        except Exception:
            # Fallback to ExponentialSmoothing
            model = ExponentialSmoothing(train_values, seasonal_periods=seasonal_period, trend="add", seasonal="add")
            fitted_model = model.fit()
            test_preds = fitted_model.forecast(steps=len(test_values))
            algorithm = "prophet_fallback_es"
            
    else:  # Fallback Exponential Smoothing / Holt-Winters if Prophet not available
        try:
            model = ExponentialSmoothing(train_values, seasonal_periods=seasonal_period, trend="add", seasonal="add")
            fitted_model = model.fit()
            test_preds = fitted_model.forecast(steps=len(test_values))
        except Exception:
            # Simple Holt-Winters Exponential Smoothing without seasonal component
            model = ExponentialSmoothing(train_values, trend="add")
            fitted_model = model.fit()
            test_preds = fitted_model.forecast(steps=len(test_values))
            algorithm = "holt_winters_simple"

    # Ensure test_preds length aligns
    if len(test_preds) != len(test_values):
        # Pad or slice to match
        if len(test_preds) > len(test_values):
            test_preds = test_preds[:len(test_values)]
        else:
            test_preds = np.pad(test_preds, (0, len(test_values) - len(test_preds)), "edge")
            
    # Calculate metrics on test split
    metrics = compute_forecasting_metrics(test_values, test_preds)
    metrics["algorithmUsed"] = algorithm
    
    # 3. Generate FUTURE Forecasts (beyond dataset end date)
    future_dates = pd.date_range(start=dates.max(), periods=horizon + 1, freq=freq)[1:]
    future_preds = np.zeros(horizon)
    lower_band = np.zeros(horizon)
    upper_band = np.zeros(horizon)
    
    # Fit model on the ENTIRE dataset for future projections
    if "prophet" in algorithm and HAS_PROPHET:
        try:
            df_full = pd.DataFrame({"ds": dates, "y": values})
            m_full = Prophet(interval_width=confidence_level)
            m_full.fit(df_full)
            
            future_df = pd.DataFrame({"ds": future_dates})
            forecast_full = m_full.predict(future_df)
            
            future_preds = forecast_full["yhat"].values
            lower_band = forecast_full["yhat_lower"].values
            upper_band = forecast_full["yhat_upper"].values
        except Exception:
            # Fallback HW
            hw = ExponentialSmoothing(values, seasonal_periods=seasonal_period, trend="add", seasonal="add").fit()
            future_preds = hw.forecast(steps=horizon)
            
            residuals = values - hw.fittedvalues
            rmse = np.sqrt(np.mean(residuals**2))
            z = 1.96 if confidence_level == 0.95 else 1.64
            se = rmse * np.sqrt(np.arange(1, horizon + 1))
            lower_band = future_preds - z * se
            upper_band = future_preds + z * se
            
    elif "arima" in algorithm or "sarima" in algorithm:
        try:
            if "sarima" in algorithm:
                full_model = SARIMAX(values, order=(1, 1, 1), seasonal_order=(1, 1, 1, seasonal_period)).fit(disp=False)
            else:
                full_model = ARIMA(values, order=(1, 1, 1)).fit()
                
            forecast_res = full_model.get_forecast(steps=horizon)
            future_preds = forecast_res.predicted_mean
            
            conf_int = forecast_res.conf_int(alpha=1 - confidence_level)
            lower_band = conf_int[:, 0]
            upper_band = conf_int[:, 1]
        except Exception:
            # Fallback HW
            hw = ExponentialSmoothing(values, trend="add").fit()
            future_preds = hw.forecast(steps=horizon)
            
            residuals = values - hw.fittedvalues
            rmse = np.sqrt(np.mean(residuals**2))
            z = 1.96
            se = rmse * np.sqrt(np.arange(1, horizon + 1))
            lower_band = future_preds - z * se
            upper_band = future_preds + z * se
            
    else:  # Holt-Winters full fit
        try:
            hw = ExponentialSmoothing(values, seasonal_periods=seasonal_period, trend="add", seasonal="add").fit()
            future_preds = hw.forecast(steps=horizon)
        except Exception:
            hw = ExponentialSmoothing(values, trend="add").fit()
            future_preds = hw.forecast(steps=horizon)
            
        residuals = values - hw.fittedvalues
        rmse = np.sqrt(np.mean(residuals**2))
        z = 1.96
        se = rmse * np.sqrt(np.arange(1, horizon + 1))
        lower_band = future_preds - z * se
        upper_band = future_preds + z * se
        
    # 4. Compile visual coordinates
    # Actuals timeline
    historical_plot = [
        {"date": d.strftime("%Y-%m-%d"), "value": clean_float(v)}
        for d, v in zip(dates, values)
    ]
    
    # Future predictions timeline (with bands)
    future_plot = [
        {
            "date": d.strftime("%Y-%m-%d"),
            "prediction": clean_float(p),
            "lower": clean_float(low),
            "upper": clean_float(up)
        }
        for d, p, low, up in zip(future_dates, future_preds, lower_band, upper_band)
    ]
    
    # Residuals error plot (on test split)
    residuals_plot = [
        {
            "date": d.strftime("%Y-%m-%d"),
            "actual": clean_float(act),
            "predicted": clean_float(pred),
            "residual": clean_float(act - pred)
        }
        for d, act, pred in zip(test_dates, test_values, test_preds)
    ]
    
    # Trend Analysis (using rolling mean)
    df_clean["y_trend"] = df_clean[target_col].rolling(window=min(12, len(df_clean)), min_periods=1).mean()
    trend_plot = [
        {"date": d.strftime("%Y-%m-%d"), "trend": clean_float(t)}
        for d, t in zip(df_clean[date_col], df_clean["y_trend"])
    ]
    
    visuals = {
        "historical": historical_plot,
        "forecast": future_plot,
        "residuals": residuals_plot,
        "trend": trend_plot
    }
    
    return fitted_model, metrics, visuals
