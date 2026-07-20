"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import api from "@/services/api";
import { 
  FolderPlus, Folder, LogOut, User, Plus, UploadCloud, 
  FileText, CheckCircle, Database, AlertCircle, 
  TrendingUp, TableProperties, Binary, Calendar, Loader2,
  Trash2, ShieldAlert, Zap, BarChart2, Layers, Shuffle,
  HelpCircle, RefreshCw, Eye, ArrowLeft, RefreshCcw,
  Cpu, Play, History, GitCompare, Download
} from "lucide-react";

interface Project {
  _id: string;
  projectName: string;
  description?: string;
  createdAt: string;
}

interface Dataset {
  _id: string;
  fileName: string;
  rows: number;
  columns: number;
  missingValues: number;
  duplicateRows: number;
  size: number;
  columnTypes: Record<string, string>;
  numericalColumns: string[];
  categoricalColumns: string[];
  dateColumns: string[];
  rawFilePath?: string;
  cleaningHistory: Array<{
    opType: string;
    params: Record<string, any>;
    timestamp: string;
  }>;
}

export default function DashboardPage() {
  const { user, loading: authLoading, logout } = useAuth();
  const router = useRouter();

  // Project states
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectDesc, setNewProjectDesc] = useState("");

  // Dataset states
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Tab systems
  const [activeTab, setActiveTab] = useState<"overview" | "clean" | "stats" | "correlations" | "visuals" | "insights" | "ml" | "forecasting" | "copilot">("overview");

  // Additional analytics states
  const [healthData, setHealthData] = useState<any>(null);
  const [insights, setInsights] = useState<any[]>([]);
  const [statsData, setStatsData] = useState<any>(null);
  const [corrData, setCorrData] = useState<any>(null);
  
  // Visualizations query states
  const [visualsColX, setVisualsColX] = useState<string>("");
  const [visualsColY, setVisualsColY] = useState<string>("");
  const [visualsChartType, setVisualsChartType] = useState<string>("histogram");
  const [visualsData, setVisualsData] = useState<any[] | null>(null);
  const [visualsBoxData, setVisualsBoxData] = useState<any | null>(null);
  const [visualsLoading, setVisualsLoading] = useState<boolean>(false);

  // Cleaning form states
  const [cleanOpType, setCleanOpType] = useState<string>("impute_missing");
  const [cleanCol, setCleanCol] = useState<string>("");
  const [cleanStrategy, setCleanStrategy] = useState<string>("mean");
  const [cleanFillVal, setCleanFillVal] = useState<string>("");
  const [cleanMethod, setCleanMethod] = useState<string>("iqr");
  const [cleanAction, setCleanAction] = useState<string>("drop");
  const [cleanThreshold, setCleanThreshold] = useState<number>(3.0);
  const [cleanEncodeMethod, setCleanEncodeMethod] = useState<string>("label");
  const [cleanEncodeOrder, setCleanEncodeOrder] = useState<string>("");
  const [cleanScaleMethod, setCleanScaleMethod] = useState<string>("standard");
  const [cleaningActionLoading, setCleaningActionLoading] = useState<boolean>(false);

  // ML States
  const [mlModels, setMlModels] = useState<any[]>([]);
  const [activeModel, setActiveModel] = useState<any | null>(null);
  const [activeModelVisuals, setActiveModelVisuals] = useState<any | null>(null);
  const [mlSubTab, setMlSubTab] = useState<"train" | "history" | "compare" | "predict">("train");
  
  // Training Wizard States
  const [mlTarget, setMlTarget] = useState<string>("");
  const [mlFeatures, setMlFeatures] = useState<string[]>([]);
  const [mlAlgo, setMlAlgo] = useState<string>("linear_regression");
  const [mlParams, setMlParams] = useState<string>("{}");
  const [mlSplit, setMlSplit] = useState<number>(0.2);
  const [mlSeed, setMlSeed] = useState<number>(42);
  const [mlStratified, setMlStratified] = useState<boolean>(false);
  const [mlTrainingLoading, setMlTrainingLoading] = useState<boolean>(false);
  const [mlTrainingError, setMlTrainingError] = useState<string | null>(null);
  
  // Comparison States
  const [comparisonData, setComparisonData] = useState<any | null>(null);
  const [comparisonLoading, setComparisonLoading] = useState<boolean>(false);
  
  // Prediction States
  const [predictManualInput, setPredictManualInput] = useState<string>("{\n  \n}");
  const [predictResults, setPredictResults] = useState<any[] | null>(null);
  const [predictLoading, setPredictLoading] = useState<boolean>(false);
  const predictFileInputRef = useRef<HTMLInputElement>(null);

  // Forecasting States
  const [forecastModels, setForecastModels] = useState<any[]>([]);
  const [activeForecastModel, setActiveForecastModel] = useState<any | null>(null);
  const [activeForecastVisuals, setActiveForecastVisuals] = useState<any | null>(null);
  const [forecastSubTab, setForecastSubTab] = useState<"train" | "history" | "explain" | "recommendations">("train");
  
  const [forecastDetectResult, setForecastDetectResult] = useState<any | null>(null);
  const [forecastDetectLoading, setForecastDetectLoading] = useState<boolean>(false);
  const [forecastTrainLoading, setForecastTrainLoading] = useState<boolean>(false);
  const [forecastLoadingVisuals, setForecastLoadingVisuals] = useState<boolean>(false);
  
  const [forecastDateCol, setForecastDateCol] = useState<string>("");
  const [forecastTargetCol, setForecastTargetCol] = useState<string>("");
  const [forecastAlgo, setForecastAlgo] = useState<string>("arima");
  const [forecastHorizon, setForecastHorizon] = useState<number>(30);
  const [forecastConfLevel, setForecastConfLevel] = useState<number>(0.95);
  const [forecastSeasonalPeriod, setForecastSeasonalPeriod] = useState<number>(7);
  const [forecastTrainRatio, setForecastTrainRatio] = useState<number>(0.8);
  const [forecastError, setForecastError] = useState<string | null>(null);

  // Explainability States
  const [explainMlModelId, setExplainMlModelId] = useState<string>("");
  const [explainRowIndex, setExplainRowIndex] = useState<number>(0);
  const [explainData, setExplainData] = useState<any | null>(null);
  const [explainLoading, setExplainLoading] = useState<boolean>(false);
  const [explainError, setExplainError] = useState<string | null>(null);
  const [recommendationData, setRecommendationData] = useState<any | null>(null);

  // AI Copilot States
  const [aiConversations, setAiConversations] = useState<any[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [aiMessages, setAiMessages] = useState<any[]>([]);
  const [aiMessageInput, setAiMessageInput] = useState<string>("");
  const [aiLoading, setAiLoading] = useState<boolean>(false);
  const [aiSubTab, setAiSubTab] = useState<"chat" | "report" | "recommendations" | "settings">("chat");
  const [aiReportFormat, setAiReportFormat] = useState<"markdown" | "html" | "pdf">("markdown");
  const [aiReportResult, setAiReportResult] = useState<string | null>(null);
  const [aiReportLoading, setAiReportLoading] = useState<boolean>(false);
  const [aiRecommendationCards, setAiRecommendationCards] = useState<any[]>([]);
  const [aiRecommendationsLoading, setAiRecommendationsLoading] = useState<boolean>(false);
  const [aiProvider, setAiProvider] = useState<string>("mock");
  const [aiModel, setAiModel] = useState<string>("gemini-2.5-flash");
  const [aiTemperature, setAiTemperature] = useState<number>(0.2);
  const [aiMaxTokens, setAiMaxTokens] = useState<number>(2048);
  const [aiSearchQuery, setAiSearchQuery] = useState<string>("");
  const [aiError, setAiError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Forecasting Functions
  const runForecastDetect = useCallback(async () => {
    if (!activeProject || !dataset) return;
    setForecastDetectLoading(true);
    setForecastError(null);
    try {
      const res = await api.get(`/projects/${activeProject._id}/forecast/detect`, {
        params: { datasetId: dataset._id }
      });
      setForecastDetectResult(res.data);
      if (res.data.isFeasible) {
        setForecastDateCol(res.data.datetimeColumn || "");
        setForecastTargetCol(res.data.suggestedTarget || "");
      }
    } catch (err: any) {
      console.error("TS feasibility detection failed:", err);
      setForecastError(err.response?.data?.detail || "TS detection failed.");
    } finally {
      setForecastDetectLoading(false);
    }
  }, [activeProject, dataset]);

  const loadForecastModels = useCallback(async () => {
    if (!activeProject) return;
    try {
      const res = await api.get(`/projects/${activeProject._id}/forecast/models`);
      setForecastModels(res.data);
    } catch (err) {
      console.error("Failed to load forecast models:", err);
    }
  }, [activeProject]);

  const loadForecastVisuals = useCallback(async (modelId: string) => {
    if (!activeProject) return;
    setForecastLoadingVisuals(true);
    try {
      const res = await api.get(`/projects/${activeProject._id}/forecast/models/${modelId}/visuals`);
      setActiveForecastVisuals(res.data);
    } catch (err) {
      console.error("Failed to load forecast visuals:", err);
    } finally {
      setForecastLoadingVisuals(false);
    }
  }, [activeProject]);

  const runForecastTrain = async () => {
    if (!activeProject || !dataset || !forecastDateCol || !forecastTargetCol) return;
    setForecastTrainLoading(true);
    setForecastError(null);
    try {
      const res = await api.post(`/projects/${activeProject._id}/forecast/train`, {
        datasetId: dataset._id,
        dateColumn: forecastDateCol,
        targetColumn: forecastTargetCol,
        algorithm: forecastAlgo,
        horizon: forecastHorizon,
        confidenceLevel: forecastConfLevel,
        seasonalPeriod: forecastSeasonalPeriod,
        trainRatio: forecastTrainRatio
      });
      setForecastModels(prev => [res.data, ...prev]);
      setActiveForecastModel(res.data);
      setForecastSubTab("history");
    } catch (err: any) {
      console.error("Forecasting training failed:", err);
      setForecastError(err.response?.data?.detail || "Forecasting training failed.");
    } finally {
      setForecastTrainLoading(false);
    }
  };

  const loadExplanations = useCallback(async (mlModelId: string, idx: number) => {
    if (!activeProject) return;
    setExplainLoading(true);
    setExplainError(null);
    try {
      const res = await api.get(`/projects/${activeProject._id}/models/${mlModelId}/explanations`, {
        params: { rowIndex: idx }
      });
      setExplainData(res.data);
      
      // Also get recommendations
      const recRes = await api.get(`/projects/${activeProject._id}/models/${mlModelId}/recommendations`);
      setRecommendationData(recRes.data);
    } catch (err: any) {
      console.error("Failed to load XAI explanations:", err);
      setExplainError(err.response?.data?.detail || "Explainability computation failed.");
    } finally {
      setExplainLoading(false);
    }
  }, [activeProject]);

  // Forecasting Effects
  useEffect(() => {
    if (activeProject && dataset && activeTab === "forecasting") {
      runForecastDetect();
      loadForecastModels();
    }
  }, [activeProject, dataset, activeTab, runForecastDetect, loadForecastModels]);

  useEffect(() => {
    if (activeForecastModel) {
      loadForecastVisuals(activeForecastModel._id || activeForecastModel.id);
    }
  }, [activeForecastModel, loadForecastVisuals]);

  useEffect(() => {
    if (explainMlModelId && activeTab === "forecasting" && forecastSubTab === "explain") {
      loadExplanations(explainMlModelId, explainRowIndex);
    }
  }, [explainMlModelId, explainRowIndex, activeTab, forecastSubTab, loadExplanations]);

  // AI Copilot Functions
  const loadAiHistory = useCallback(async () => {
    if (!activeProject) return;
    try {
      const res = await api.get(`/projects/${activeProject._id}/ai/history`, {
        params: aiSearchQuery ? { q: aiSearchQuery } : {}
      });
      setAiConversations(res.data);
    } catch (err) {
      console.error("Failed to load AI conversations history:", err);
    }
  }, [activeProject, aiSearchQuery]);

  const loadAiMessages = useCallback(async (convId: string) => {
    if (!activeProject) return;
    setAiLoading(true);
    try {
      const res = await api.get(`/projects/${activeProject._id}/ai/history/${convId}`);
      setAiMessages(res.data.messages || []);
      setActiveConversationId(convId);
    } catch (err) {
      console.error("Failed to load conversation details:", err);
    } finally {
      setAiLoading(false);
    }
  }, [activeProject]);

  const sendAiChatMessage = async (overrideMessage?: string) => {
    if (!activeProject || !dataset) return;
    const msgText = overrideMessage || aiMessageInput;
    if (!msgText.trim()) return;
    
    setAiLoading(true);
    setAiError(null);
    if (!overrideMessage) {
      setAiMessageInput("");
    }
    
    // Optimistic User message add
    const userMsg = { role: "user", content: msgText, timestamp: new Date().toISOString() };
    setAiMessages(prev => [...prev, userMsg]);
    
    try {
      const res = await api.post(`/projects/${activeProject._id}/ai/chat`, {
        message: msgText,
        conversationId: activeConversationId || undefined,
        datasetId: dataset._id
      });
      
      const assistantMsg = { role: "assistant", content: res.data.response, timestamp: new Date().toISOString() };
      setAiMessages(prev => [...prev, assistantMsg]);
      setActiveConversationId(res.data.conversationId);
      await loadAiHistory();
    } catch (err: any) {
      console.error("AI Chat message send failed:", err);
      setAiError(err.response?.data?.detail || "AI Copilot failed to generate a response.");
    } finally {
      setAiLoading(false);
    }
  };

  const deleteAiConversation = async (convId: string) => {
    if (!activeProject) return;
    try {
      await api.delete(`/projects/${activeProject._id}/ai/history/${convId}`);
      if (activeConversationId === convId) {
        setActiveConversationId(null);
        setAiMessages([]);
      }
      await loadAiHistory();
    } catch (err) {
      console.error("Failed to delete conversation session:", err);
    }
  };

  const generateAiReport = async () => {
    if (!activeProject || !dataset) return;
    setAiReportLoading(true);
    setAiReportResult(null);
    setAiError(null);
    try {
      const res = await api.post(`/projects/${activeProject._id}/ai/report`, {
        datasetId: dataset._id,
        format: aiReportFormat
      });
      setAiReportResult(res.data.report);
    } catch (err: any) {
      console.error("Failed to generate AI executive report:", err);
      setAiError(err.response?.data?.detail || "Report generation failed.");
    } finally {
      setAiReportLoading(false);
    }
  };

  const loadAiRecommendations = useCallback(async () => {
    if (!activeProject || !dataset) return;
    setAiRecommendationsLoading(true);
    setAiError(null);
    try {
      const res = await api.post(`/projects/${activeProject._id}/ai/recommendations`, {
        datasetId: dataset._id
      });
      setAiRecommendationCards(res.data);
    } catch (err: any) {
      console.error("Failed to load AI recommendations:", err);
    } finally {
      setAiRecommendationsLoading(false);
    }
  }, [activeProject, dataset]);

  // AI Copilot Effects
  useEffect(() => {
    if (activeProject && dataset && activeTab === "copilot") {
      loadAiHistory();
      loadAiRecommendations();
    }
  }, [activeProject, dataset, activeTab, loadAiHistory, loadAiRecommendations]);

  useEffect(() => {
    if (activeProject && activeTab === "copilot" && aiSubTab === "recommendations") {
      loadAiRecommendations();
    }
  }, [activeProject, activeTab, aiSubTab, loadAiRecommendations]);

  const fetchProjects = useCallback(async () => {
    try {
      const res = await api.get("/projects");
      setProjects(res.data);
      if (res.data.length > 0 && !activeProject) {
        setActiveProject(res.data[0]);
      }
    } catch (err) {
      console.error("Failed to load projects:", err);
    }
  }, [activeProject]);

  const fetchAllAnalytics = useCallback(async (projectId: string) => {
    try {
      const [healthRes, insightsRes, statsRes, corrRes] = await Promise.all([
        api.get(`/projects/${projectId}/datasets/health-score`),
        api.get(`/projects/${projectId}/datasets/insights`),
        api.get(`/projects/${projectId}/datasets/statistics`),
        api.get(`/projects/${projectId}/datasets/correlations`)
      ]);
      setHealthData(healthRes.data);
      setInsights(insightsRes.data);
      setStatsData(statsRes.data);
      setCorrData(corrRes.data);
    } catch (err) {
      console.error("Failed to load analytics details:", err);
    }
  }, []);

  const fetchDataset = useCallback(async (projectId: string) => {
    try {
      setError(null);
      const res = await api.get(`/projects/${projectId}/datasets`);
      setDataset(res.data);
    } catch (err: unknown) {
      let is404 = false;
      const response = (err as { response?: { status?: number } }).response;
      if (response && response.status === 404) {
        is404 = true;
      }
      if (!is404) {
        console.error("Failed to fetch dataset:", err);
        setError("Failed to load dataset details.");
      } else {
        setDataset(null);
      }
    }
  }, []);

  const fetchVisualsData = useCallback(async () => {
    if (!activeProject || !visualsColX) return;
    if ((visualsChartType === "scatter" || visualsChartType === "line") && !visualsColY) return;
    setVisualsLoading(true);
    try {
      let url = `/projects/${activeProject._id}/datasets/visualizations?col=${encodeURIComponent(visualsColX)}&chart_type=${visualsChartType}`;
      if (visualsColY && (visualsChartType === "scatter" || visualsChartType === "line")) {
        url += `&col_y=${encodeURIComponent(visualsColY)}`;
      }
      const res = await api.get(url);
      if (visualsChartType === "boxplot") {
        setVisualsBoxData(res.data);
        setVisualsData(null);
      } else {
        setVisualsData(res.data);
        setVisualsBoxData(null);
      }
    } catch (err) {
      console.error("Failed to load visualization data:", err);
    } finally {
      setVisualsLoading(false);
    }
  }, [activeProject, visualsColX, visualsColY, visualsChartType]);

  const handleFileUpload = useCallback(async (file: File) => {
    if (!activeProject) return;
    setUploadLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await api.post(`/projects/${activeProject._id}/datasets/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });
      setDataset(res.data);
    } catch (err: unknown) {
      let message = "Failed to process dataset. Please check file format.";
      const response = (err as { response?: { data?: { detail?: string } } }).response;
      if (response && response.data && response.data.detail) {
        message = response.data.detail;
      }
      setError(message);
    } finally {
      setUploadLoading(false);
    }
  }, [activeProject]);

  const handleCreateProject = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;

    try {
      const res = await api.post("/projects", {
        projectName: newProjectName,
        description: newProjectDesc
      });
      setProjects((prev) => [...prev, res.data]);
      setActiveProject(res.data);
      setShowCreateModal(false);
      setNewProjectName("");
      setNewProjectDesc("");
    } catch (err) {
      console.error("Failed to create project:", err);
    }
  }, [newProjectName, newProjectDesc]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleFileUpload(e.dataTransfer.files[0]);
    }
  }, [handleFileUpload]);

  const handleFileChange = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await handleFileUpload(e.target.files[0]);
    }
  }, [handleFileUpload]);

  const handleCleanOperation = async () => {
    if (!activeProject || !dataset) return;
    setCleaningActionLoading(true);
    setError(null);
    
    let params: Record<string, any> = {};
    if (cleanOpType === "impute_missing") {
      params = {
        column: cleanCol || dataset.numericalColumns[0] || Object.keys(dataset.columnTypes)[0],
        strategy: cleanStrategy,
        fill_value: cleanFillVal ? parseFloat(cleanFillVal) || cleanFillVal : undefined
      };
    } else if (cleanOpType === "drop_missing_rows") {
      params = {
        column: cleanCol || undefined
      };
    } else if (cleanOpType === "drop_column") {
      params = {
        column: cleanCol || Object.keys(dataset.columnTypes)[0]
      };
    } else if (cleanOpType === "remove_duplicates") {
      params = {};
    } else if (cleanOpType === "handle_outliers") {
      params = {
        column: cleanCol || dataset.numericalColumns[0],
        method: cleanMethod,
        action: cleanAction,
        threshold: cleanThreshold
      };
    } else if (cleanOpType === "encode_column") {
      params = {
        column: cleanCol || dataset.categoricalColumns[0] || Object.keys(dataset.columnTypes)[0],
        method: cleanEncodeMethod,
        order: cleanEncodeOrder ? cleanEncodeOrder.split(",").map(s => s.trim()) : undefined
      };
    } else if (cleanOpType === "scale_column") {
      params = {
        column: cleanCol || dataset.numericalColumns[0],
        method: cleanScaleMethod
      };
    }
    
    try {
      const res = await api.post(`/projects/${activeProject._id}/datasets/clean`, {
        opType: cleanOpType,
        params
      });
      setDataset(res.data);
    } catch (err: any) {
      console.error("Cleaning failed:", err);
      setError(err.response?.data?.detail || "Cleaning operation failed.");
    } finally {
      setCleaningActionLoading(false);
    }
  };

  const handleRevertOperation = async () => {
    if (!activeProject || !dataset) return;
    setCleaningActionLoading(true);
    setError(null);
    try {
      const res = await api.post(`/projects/${activeProject._id}/datasets/revert`);
      setDataset(res.data);
    } catch (err: any) {
      console.error("Revert failed:", err);
      setError(err.response?.data?.detail || "Revert operation failed.");
    } finally {
      setCleaningActionLoading(false);
    }
  };

  const handleSelectModel = async (model: any) => {
    setActiveModel(model);
    setActiveModelVisuals(null);
    const mId = model?._id || model?.id;
    if (!mId || !activeProject?._id) return;
    try {
      const res = await api.get(`/projects/${activeProject._id}/models/${mId}/visuals`);
      setActiveModelVisuals(res.data);
    } catch (err) {
      console.error("Failed to load model visuals:", err);
    }
  };

  const handleTrainModel = async () => {
    if (!activeProject || !dataset) return;
    setMlTrainingLoading(true);
    setMlTrainingError(null);
    try {
      let parsedParams = {};
      try {
        if (mlParams.trim()) {
          parsedParams = JSON.parse(mlParams);
        }
      } catch (err) {
        throw new Error("Invalid hyperparameters JSON format.");
      }
      
      const isClustering = ["kmeans", "dbscan", "hierarchical"].includes(mlAlgo);
      
      const trainPayload = {
        datasetId: dataset._id,
        targetColumn: isClustering ? undefined : mlTarget,
        features: mlFeatures,
        algorithm: mlAlgo,
        hyperparameters: parsedParams,
        splitRatio: mlSplit,
        randomState: mlSeed,
        stratified: mlStratified
      };
      
      const res = await api.post(`/projects/${activeProject._id}/models/train`, trainPayload);
      setMlModels((prev) => [...prev, res.data]);
      setMlSubTab("history");
      await handleSelectModel(res.data);
    } catch (err: any) {
      console.error("Model training failed:", err);
      setMlTrainingError(err.response?.data?.detail || err.message || "Failed to train model.");
    } finally {
      setMlTrainingLoading(false);
    }
  };

  const handleLoadComparison = async () => {
    if (!activeProject) return;
    setComparisonLoading(true);
    try {
      const res = await api.get(`/projects/${activeProject._id}/models/compare`);
      setComparisonData(res.data);
    } catch (err) {
      console.error("Failed to load comparisons:", err);
    } finally {
      setComparisonLoading(false);
    }
  };

  const handleDeleteModel = async (modelId: string) => {
    if (!activeProject) return;
    try {
      await api.delete(`/projects/${activeProject._id}/models/${modelId}`);
      setMlModels((prev) => prev.filter(m => (m._id || m.id) !== modelId));
      if ((activeModel?._id || activeModel?.id) === modelId) {
        setActiveModel(null);
        setActiveModelVisuals(null);
      }
    } catch (err) {
      console.error("Failed to delete model:", err);
    }
  };

  const handlePredictManual = async () => {
    const mId = activeModel?._id || activeModel?.id;
    if (!activeProject || !activeModel || !mId) return;
    setPredictLoading(true);
    try {
      const parsedInput = JSON.parse(predictManualInput);
      const payload = {
        data: Array.isArray(parsedInput) ? parsedInput : [parsedInput]
      };
      const res = await api.post(`/projects/${activeProject._id}/models/${mId}/predict`, payload);
      setPredictResults(res.data.predictions);
    } catch (err: any) {
      alert(err.message || "Prediction failed. Check input format.");
    } finally {
      setPredictLoading(false);
    }
  };

  const handlePredictFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const mId = activeModel?._id || activeModel?.id;
    if (!activeProject || !activeModel || !mId || !e.target.files || !e.target.files[0]) return;
    const file = e.target.files[0];
    setPredictLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await api.post(
        `/projects/${activeProject._id}/models/${mId}/predict/file`,
        formData,
        { responseType: "blob" }
      );
      
      const blob = new Blob([res.data], { type: "text/csv" });
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = `predicted_${file.name}`;
      link.click();
    } catch (err) {
      console.error("Batch prediction failed:", err);
      alert("Batch prediction failed.");
    } finally {
      setPredictLoading(false);
    }
  };

  const handleDeleteDataset = async () => {
    if (!activeProject) return;
    setError(null);
    try {
      await api.delete(`/projects/${activeProject._id}/datasets`);
      setDataset(null);
      setHealthData(null);
      setInsights([]);
      setStatsData(null);
      setCorrData(null);
    } catch (err) {
      console.error("Failed to delete dataset:", err);
      setError("Failed to delete dataset.");
    }
  };

  // Redirect if not logged in
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  // Fetch projects on mount
  useEffect(() => {
    if (user) {
      Promise.resolve().then(() => fetchProjects());
    }
  }, [user, fetchProjects]);

  // Fetch dataset when active project changes
  useEffect(() => {
    if (activeProject) {
      Promise.resolve().then(() => fetchDataset(activeProject._id));
    } else {
      Promise.resolve().then(() => setDataset(null));
    }
  }, [activeProject, fetchDataset]);

  // Fetch additional analytics when dataset changes
  useEffect(() => {
    if (activeProject && dataset) {
      Promise.resolve().then(() => fetchAllAnalytics(activeProject._id));
      
      // Auto populate clean operations default column selection
      const allCols = Object.keys(dataset.columnTypes);
      if (allCols.length > 0) {
        setCleanCol(allCols[0]);
      }
      
      // Set defaults for visualizations
      if (dataset.numericalColumns.length > 0) {
        setVisualsColX(dataset.numericalColumns[0]);
        if (dataset.numericalColumns.length > 1) {
          setVisualsColY(dataset.numericalColumns[1]);
        } else if (dataset.categoricalColumns.length > 0) {
          setVisualsColY(dataset.categoricalColumns[0]);
        }
      } else if (dataset.categoricalColumns.length > 0) {
        setVisualsColX(dataset.categoricalColumns[0]);
      }
    }
  }, [activeProject, dataset, fetchAllAnalytics]);

  // ML Initialization Effect
  useEffect(() => {
    if (activeProject && dataset) {
      Promise.resolve().then(async () => {
        try {
          const res = await api.get(`/projects/${activeProject._id}/models`);
          setMlModels(res.data);
        } catch (err) {
          console.error("Failed to load models list:", err);
        }
      });
      
      const allCols = Object.keys(dataset.columnTypes);
      if (allCols.length > 0) {
        const targetCandidate = allCols.find(c => ["target", "label", "class", "price", "salary"].includes(c.toLowerCase())) || allCols[allCols.length - 1];
        setMlTarget(targetCandidate);
        setMlFeatures(allCols.filter(c => c !== targetCandidate));
      }
    }
  }, [activeProject, dataset]);

  // Auto-fetch comparisons when subtab changes
  useEffect(() => {
    if (activeProject && mlSubTab === "compare") {
      Promise.resolve().then(() => handleLoadComparison());
    }
  }, [activeProject, mlSubTab]);

  // Fetch visual graph coordinates
  useEffect(() => {
    if (activeProject && dataset && visualsColX) {
      Promise.resolve().then(() => fetchVisualsData());
    }
  }, [activeProject, dataset, visualsColX, visualsColY, visualsChartType, fetchVisualsData]);

  if (authLoading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  const formatSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Sidebar Workspace */}
      <aside className="w-80 bg-slate-900 border-r border-slate-800 flex flex-col justify-between z-10 shrink-0">
        <div>
          {/* Header */}
          <div className="p-6 border-b border-slate-800 flex items-center justify-between">
            <h1 className="text-xl font-bold flex items-center gap-2">
              <Database className="w-5 h-5 text-indigo-400" />
              Insight<span className="text-indigo-400">AI</span>
            </h1>
            <button 
              onClick={() => setShowCreateModal(true)}
              className="p-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white cursor-pointer transition-colors"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          {/* Project List */}
          <div className="p-4">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 px-3">
              Workspaces ({projects.length})
            </p>
            <div className="space-y-1 overflow-y-auto max-h-[calc(100vh-250px)] pr-2">
              {projects.map((proj) => (
                <button
                  key={proj._id}
                  onClick={() => {
                    setActiveProject(proj);
                    setDataset(null);
                  }}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-left cursor-pointer ${
                    activeProject?._id === proj._id
                      ? "bg-indigo-600/10 border border-indigo-500/30 text-indigo-400"
                      : "border border-transparent text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                  }`}
                >
                  <Folder className="w-4 h-4 shrink-0" />
                  <span className="truncate">{proj.projectName}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Profile Card */}
        <div className="p-4 border-t border-slate-800 flex items-center justify-between bg-slate-900/40">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0">
              <User className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-slate-200 truncate">{user.name}</p>
              <p className="text-xs text-slate-500 truncate">{user.email}</p>
            </div>
          </div>
          <button 
            onClick={logout}
            className="p-2 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 cursor-pointer transition-all"
            title="Sign Out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Main Workspace Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto relative">
        {/* Workspace Background Gradients */}
        <div className="absolute top-10 right-10 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />

        {activeProject ? (
          <div className="p-10 max-w-6xl w-full mx-auto space-y-8 z-10">
            {/* Project Details */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
              <div>
                <h2 className="text-3xl font-extrabold text-white tracking-tight">
                  {activeProject.projectName}
                </h2>
                <p className="text-slate-400 text-sm mt-1 max-w-xl">
                  {activeProject.description || "No description provided."}
                </p>
              </div>
              {dataset && (
                <button
                  onClick={handleDeleteDataset}
                  className="flex items-center gap-2 border border-rose-500/20 bg-rose-500/5 hover:bg-rose-500/10 text-rose-400 px-4 py-2 rounded-xl text-xs font-semibold cursor-pointer transition-colors"
                >
                  <Trash2 className="w-4 h-4" /> Delete Dataset
                </button>
              )}
            </div>

            {error && (
              <div className="rounded-xl bg-rose-500/10 border border-rose-500/20 p-4 text-sm text-rose-400 flex gap-3 items-center">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Content Switcher: Upload OR Tabbed Dashboard */}
            {!dataset ? (
              <div className="space-y-6">
                <div className="text-center max-w-md mx-auto py-10">
                  <h3 className="text-lg font-semibold text-slate-300">Upload Dataset</h3>
                  <p className="text-slate-500 text-sm mt-1">
                    To start analysis, drop a CSV or Excel dataset below.
                  </p>
                </div>

                {/* Drag & Drop zone */}
                <div
                  onDragEnter={handleDrag}
                  onDragOver={handleDrag}
                  onDragLeave={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`border-2 border-dashed rounded-2xl p-12 flex flex-col items-center justify-center transition-all cursor-pointer ${
                    dragActive
                      ? "border-indigo-500 bg-indigo-500/5"
                      : "border-slate-800 bg-slate-900/30 hover:border-slate-700 hover:bg-slate-900/50"
                  }`}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    onChange={handleFileChange}
                    accept=".csv, .xlsx, .xls"
                    className="hidden"
                  />
                  {uploadLoading ? (
                    <div className="flex flex-col items-center gap-3">
                      <Loader2 className="h-10 w-10 animate-spin text-indigo-400" />
                      <p className="text-sm font-medium text-slate-300">Parsing dataset health & metadata...</p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center text-center">
                      <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
                        <UploadCloud className="w-6 h-6" />
                      </div>
                      <p className="text-sm font-semibold text-slate-300">
                        Drag and drop your file here, or <span className="text-indigo-400">browse</span>
                      </p>
                      <p className="text-xs text-slate-500 mt-2">
                        Supports CSV and Excel files (up to 50MB)
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-8 animate-in fade-in duration-300">
                {/* Meta Statistics Summary Grid */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  {/* Rows */}
                  <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5">
                    <p className="text-xs text-slate-500 font-medium">Total Rows</p>
                    <p className="text-2xl font-bold text-white mt-1">{dataset.rows.toLocaleString()}</p>
                  </div>
                  {/* Columns */}
                  <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5">
                    <p className="text-xs text-slate-500 font-medium">Columns</p>
                    <p className="text-2xl font-bold text-white mt-1">{dataset.columns}</p>
                  </div>
                  {/* Size */}
                  <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5">
                    <p className="text-xs text-slate-500 font-medium">File Size</p>
                    <p className="text-2xl font-bold text-white mt-1">{formatSize(dataset.size)}</p>
                  </div>
                  {/* Missing cells */}
                  <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5">
                    <p className="text-xs text-slate-500 font-medium">Missing Cells</p>
                    <p className={`text-2xl font-bold mt-1 ${dataset.missingValues > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                      {dataset.missingValues.toLocaleString()}
                    </p>
                  </div>
                  {/* Health Score */}
                  <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 relative overflow-hidden">
                    <p className="text-xs text-slate-500 font-medium">Health Score</p>
                    <p className={`text-2xl font-bold mt-1 ${
                      (healthData?.score || 0) >= 85 ? 'text-emerald-400' : (healthData?.score || 0) >= 60 ? 'text-amber-400' : 'text-rose-400'
                    }`}>
                      {healthData ? `${healthData.score}/100` : "--"}
                    </p>
                  </div>
                </div>

                {/* Tab Navigation System */}
                <div className="flex border-b border-slate-850 gap-2 overflow-x-auto pb-px">
                  <button
                    onClick={() => setActiveTab("overview")}
                    className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
                      activeTab === "overview"
                        ? "border-indigo-500 text-indigo-400 font-bold"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    Overview & Schema
                  </button>
                  <button
                    onClick={() => setActiveTab("clean")}
                    className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
                      activeTab === "clean"
                        ? "border-indigo-500 text-indigo-400 font-bold"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    Data Cleaning
                  </button>
                  <button
                    onClick={() => setActiveTab("stats")}
                    className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
                      activeTab === "stats"
                        ? "border-indigo-500 text-indigo-400 font-bold"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    Statistics
                  </button>
                  <button
                    onClick={() => setActiveTab("correlations")}
                    className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
                      activeTab === "correlations"
                        ? "border-indigo-500 text-indigo-400 font-bold"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    Correlations
                  </button>
                  <button
                    onClick={() => setActiveTab("visuals")}
                    className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
                      activeTab === "visuals"
                        ? "border-indigo-500 text-indigo-400 font-bold"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    Visualizations
                  </button>
                  <button
                    onClick={() => setActiveTab("insights")}
                    className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
                      activeTab === "insights"
                        ? "border-indigo-500 text-indigo-400 font-bold"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    Insights Panel
                  </button>
                  <button
                    onClick={() => setActiveTab("ml")}
                    className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
                      activeTab === "ml"
                        ? "border-indigo-500 text-indigo-400 font-bold"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    Machine Learning
                  </button>
                  <button
                    onClick={() => setActiveTab("forecasting")}
                    className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
                      activeTab === "forecasting"
                        ? "border-indigo-500 text-indigo-400 font-bold"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    Forecasting & XAI
                  </button>
                  <button
                    onClick={() => setActiveTab("copilot")}
                    className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
                      activeTab === "copilot"
                        ? "border-indigo-500 text-indigo-400 font-bold"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    AI Copilot
                  </button>
                </div>

                {/* Tab Content rendering */}
                <div className="space-y-6 min-h-[350px]">
                  
                  {/* OVERVIEW TAB */}
                  {activeTab === "overview" && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-200">
                      {/* Left: Columns Schema list */}
                      <div className="lg:col-span-2 space-y-4">
                        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5">
                          <h4 className="text-sm font-bold text-white mb-3">Columns Catalog</h4>
                          <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm text-slate-300">
                              <thead className="text-xs font-semibold text-slate-400 uppercase border-b border-slate-800">
                                <tr>
                                  <th className="py-2.5">Name</th>
                                  <th className="py-2.5">Data Type</th>
                                  <th className="py-2.5">Profiling Group</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-slate-855">
                                {Object.entries(dataset.columnTypes).map(([colName, type]) => (
                                  <tr key={colName} className="hover:bg-slate-800/10">
                                    <td className="py-3 font-mono text-slate-200">{colName}</td>
                                    <td className="py-3 text-slate-500 font-mono text-xs">
                                      {healthData?.dataTypes?.[colName] || "unknown"}
                                    </td>
                                    <td className="py-3">
                                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${
                                        type === "numerical" 
                                          ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-400"
                                          : type === "datetime"
                                          ? "bg-amber-500/10 border-amber-500/20 text-amber-400"
                                          : "bg-purple-500/10 border-purple-500/20 text-purple-400"
                                      }`}>
                                        {type}
                                      </span>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>

                      {/* Right: Health recommendations summary */}
                      <div className="space-y-6">
                        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6">
                          <h4 className="text-sm font-bold text-white mb-3">Health Status</h4>
                          {healthData ? (
                            <div className="space-y-4">
                              <div className="flex items-center gap-4">
                                <div className="text-4xl font-extrabold text-indigo-400">{healthData.score}%</div>
                                <div className="text-xs text-slate-400">calculated using missing percentages, skewness, outliers, and row ratios.</div>
                              </div>
                              
                              {/* Strengths */}
                              {healthData.strengths.length > 0 && (
                                <div>
                                  <p className="text-xs font-bold text-slate-400 uppercase mb-1">Strengths</p>
                                  <ul className="space-y-1">
                                    {healthData.strengths.map((str: string, idx: number) => (
                                      <li key={idx} className="text-xs text-emerald-400 flex items-center gap-1.5">
                                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
                                        {str}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                              
                              {/* Warnings */}
                              {healthData.warnings.length > 0 && (
                                <div>
                                  <p className="text-xs font-bold text-slate-400 uppercase mb-1">Warnings</p>
                                  <ul className="space-y-1">
                                    {healthData.warnings.map((warn: string, idx: number) => (
                                      <li key={idx} className="text-xs text-amber-400 flex items-center gap-1.5">
                                        <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0" />
                                        {warn}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          ) : (
                            <div className="text-slate-500 text-xs py-4 flex items-center gap-2">
                              <Loader2 className="w-4 h-4 animate-spin" /> Loading health metrics...
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* DATA CLEANING TAB */}
                  {activeTab === "clean" && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-200">
                      {/* Left side: Cleaning parameters and trigger */}
                      <div className="lg:col-span-2 space-y-6">
                        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 space-y-6">
                          <div>
                            <h4 className="text-sm font-bold text-white">Preprocessing Action Console</h4>
                            <p className="text-xs text-slate-500 mt-0.5">Select a cleaning operation to apply on the dataset.</p>
                          </div>

                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-xs font-semibold text-slate-400 mb-1.5">Operation Type</label>
                              <select
                                value={cleanOpType}
                                onChange={(e) => setCleanOpType(e.target.value)}
                                className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2.5 px-3 text-slate-200 text-sm focus:border-indigo-500 focus:outline-none"
                              >
                                <option value="impute_missing">Impute Missing Values</option>
                                <option value="drop_missing_rows">Drop Null Rows</option>
                                <option value="drop_column">Drop Column</option>
                                <option value="remove_duplicates">Remove Duplicate Rows</option>
                                <option value="handle_outliers">Handle Outliers</option>
                                <option value="encode_column">Encode Categorical Column</option>
                                <option value="scale_column">Scale Feature</option>
                              </select>
                            </div>

                            {/* Column Selection (unless it is remove_duplicates) */}
                            {cleanOpType !== "remove_duplicates" && (
                              <div>
                                <label className="block text-xs font-semibold text-slate-400 mb-1.5">Column</label>
                                <select
                                  value={cleanCol}
                                  onChange={(e) => setCleanCol(e.target.value)}
                                  className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2.5 px-3 text-slate-200 text-sm focus:border-indigo-500 focus:outline-none"
                                >
                                  {/* Filter columns based on operation type */}
                                  {Object.keys(dataset.columnTypes).map((col) => (
                                    <option key={col} value={col}>{col}</option>
                                  ))}
                                </select>
                              </div>
                            )}
                          </div>

                          {/* Dynamic Inputs based on CleanOpType */}
                          {cleanOpType === "impute_missing" && (
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-850">
                              <div>
                                <label className="block text-xs font-semibold text-slate-400 mb-1.5">Imputation Strategy</label>
                                <select
                                  value={cleanStrategy}
                                  onChange={(e) => setCleanStrategy(e.target.value)}
                                  className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-200 text-xs focus:outline-none"
                                >
                                  <option value="mean">Mean (Numerical Only)</option>
                                  <option value="median">Median (Numerical Only)</option>
                                  <option value="mode">Mode (Most Frequent)</option>
                                  <option value="ffill">Forward Fill</option>
                                  <option value="bfill">Backward Fill</option>
                                  <option value="val">Custom Fill Value</option>
                                </select>
                              </div>
                              {cleanStrategy === "val" && (
                                <div>
                                  <label className="block text-xs font-semibold text-slate-400 mb-1.5">Custom Value</label>
                                  <input
                                    type="text"
                                    value={cleanFillVal}
                                    onChange={(e) => setCleanFillVal(e.target.value)}
                                    placeholder="Enter custom value"
                                    className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-200 text-xs focus:outline-none"
                                  />
                                </div>
                              )}
                            </div>
                          )}

                          {cleanOpType === "handle_outliers" && (
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 border-t border-slate-850">
                              <div>
                                <label className="block text-xs font-semibold text-slate-400 mb-1.5">Method</label>
                                <select
                                  value={cleanMethod}
                                  onChange={(e) => setCleanMethod(e.target.value)}
                                  className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-200 text-xs focus:outline-none"
                                >
                                  <option value="iqr">IQR Bounds</option>
                                  <option value="zscore">Z-Score Cutoff</option>
                                </select>
                              </div>
                              <div>
                                <label className="block text-xs font-semibold text-slate-400 mb-1.5">Action</label>
                                <select
                                  value={cleanAction}
                                  onChange={(e) => setCleanAction(e.target.value)}
                                  className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-200 text-xs focus:outline-none"
                                >
                                  <option value="drop">Drop Rows</option>
                                  <option value="cap">Cap Outliers (Clip)</option>
                                </select>
                              </div>
                              <div>
                                <label className="block text-xs font-semibold text-slate-400 mb-1.5">Threshold</label>
                                <input
                                  type="number"
                                  step="0.1"
                                  value={cleanThreshold}
                                  onChange={(e) => setCleanThreshold(parseFloat(e.target.value) || 3.0)}
                                  className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-200 text-xs focus:outline-none"
                                />
                              </div>
                            </div>
                          )}

                          {cleanOpType === "encode_column" && (
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-850">
                              <div>
                                <label className="block text-xs font-semibold text-slate-400 mb-1.5">Encoding Method</label>
                                <select
                                  value={cleanEncodeMethod}
                                  onChange={(e) => setCleanEncodeMethod(e.target.value)}
                                  className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-200 text-xs focus:outline-none"
                                >
                                  <option value="label">Label Encoding (0, 1, 2...)</option>
                                  <option value="onehot">One-Hot Encoding (Dummies)</option>
                                  <option value="ordinal">Ordinal Encoding (Custom order)</option>
                                </select>
                              </div>
                              {cleanEncodeMethod === "ordinal" && (
                                <div>
                                  <label className="block text-xs font-semibold text-slate-400 mb-1.5">Order (comma-separated)</label>
                                  <input
                                    type="text"
                                    value={cleanEncodeOrder}
                                    onChange={(e) => setCleanEncodeOrder(e.target.value)}
                                    placeholder="e.g. Low, Medium, High"
                                    className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-200 text-xs focus:outline-none"
                                  />
                                </div>
                              )}
                            </div>
                          )}

                          {cleanOpType === "scale_column" && (
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-850">
                              <div>
                                <label className="block text-xs font-semibold text-slate-400 mb-1.5">Scaler Type</label>
                                <select
                                  value={cleanScaleMethod}
                                  onChange={(e) => setCleanScaleMethod(e.target.value)}
                                  className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-200 text-xs focus:outline-none"
                                >
                                  <option value="standard">Standard Scaler (Z-Score)</option>
                                  <option value="minmax">MinMax Scaler (0-1)</option>
                                  <option value="robust">Robust Scaler (Median/IQR)</option>
                                </select>
                              </div>
                            </div>
                          )}

                          {/* Trigger button */}
                          <div className="pt-4 border-t border-slate-855 flex justify-end">
                            <button
                              onClick={handleCleanOperation}
                              disabled={cleaningActionLoading}
                              className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2 cursor-pointer disabled:opacity-50 transition-colors"
                            >
                              {cleaningActionLoading ? (
                                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              ) : (
                                <Zap className="w-3.5 h-3.5" />
                              )}
                              Run Cleaning Operation
                            </button>
                          </div>
                        </div>
                      </div>

                      {/* Right side: Cleaning history & revert controls */}
                      <div className="space-y-6">
                        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 space-y-4">
                          <div className="flex items-center justify-between">
                            <h4 className="text-xs font-bold text-white uppercase tracking-wider">Cleaning History</h4>
                            {dataset.cleaningHistory.length > 0 && (
                              <button
                                onClick={handleRevertOperation}
                                disabled={cleaningActionLoading}
                                className="flex items-center gap-1.5 text-xs text-amber-400 border border-amber-500/20 bg-amber-500/5 hover:bg-amber-500/10 px-3 py-1.5 rounded-lg cursor-pointer transition-all disabled:opacity-50"
                              >
                                <RefreshCcw className="w-3 h-3" /> Revert Last
                              </button>
                            )}
                          </div>
                          
                          {dataset.cleaningHistory.length === 0 ? (
                            <p className="text-xs text-slate-500 italic py-4">No cleaning operations applied yet. Use the console to clean this dataset.</p>
                          ) : (
                            <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2">
                              {dataset.cleaningHistory.map((step, idx) => (
                                <div key={idx} className="p-3 bg-slate-950 border border-slate-850 rounded-xl text-xs space-y-1">
                                  <div className="flex items-center justify-between font-bold text-slate-300">
                                    <span className="capitalize text-indigo-400">{step.opType.replace('_', ' ')}</span>
                                    <span className="text-[10px] text-slate-500">
                                      {new Date(step.timestamp).toLocaleTimeString()}
                                    </span>
                                  </div>
                                  <div className="text-slate-500 text-[10px] font-mono whitespace-pre-wrap">
                                    {JSON.stringify(step.params)}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* STATISTICS TAB */}
                  {activeTab === "stats" && (
                    <div className="space-y-6 animate-in fade-in duration-200">
                      {/* Numerical Stats Table */}
                      {statsData?.numerical && Object.keys(statsData.numerical).length > 0 ? (
                        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6">
                          <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-indigo-400" />
                            Numerical Features Descriptive Statistics
                          </h4>
                          <div className="overflow-x-auto">
                            <table className="w-full text-left text-xs text-slate-300">
                              <thead className="bg-slate-900/80 font-bold text-slate-400 border-b border-slate-850 uppercase">
                                <tr>
                                  <th className="px-3 py-3">Feature</th>
                                  <th className="px-3 py-3 text-right">Mean</th>
                                  <th className="px-3 py-3 text-right">Median</th>
                                  <th className="px-3 py-3 text-right">Min</th>
                                  <th className="px-3 py-3 text-right">Max</th>
                                  <th className="px-3 py-3 text-right">Std Dev</th>
                                  <th className="px-3 py-3 text-right">Q1 (25%)</th>
                                  <th className="px-3 py-3 text-right">Q3 (75%)</th>
                                  <th className="px-3 py-3 text-right">Skewness</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-slate-855 font-mono">
                                {Object.entries(statsData.numerical).map(([col, data]: [string, any]) => (
                                  <tr key={col} className="hover:bg-slate-800/10">
                                    <td className="px-3 py-3.5 font-sans font-bold text-slate-200">{col}</td>
                                    <td className="px-3 py-3.5 text-right">{data.mean?.toFixed(2) ?? "--"}</td>
                                    <td className="px-3 py-3.5 text-right">{data.median?.toFixed(2) ?? "--"}</td>
                                    <td className="px-3 py-3.5 text-right">{data.min?.toFixed(2) ?? "--"}</td>
                                    <td className="px-3 py-3.5 text-right">{data.max?.toFixed(2) ?? "--"}</td>
                                    <td className="px-3 py-3.5 text-right">{data.std?.toFixed(2) ?? "--"}</td>
                                    <td className="px-3 py-3.5 text-right">{data.q25?.toFixed(2) ?? "--"}</td>
                                    <td className="px-3 py-3.5 text-right">{data.q75?.toFixed(2) ?? "--"}</td>
                                    <td className={`px-3 py-3.5 text-right font-bold ${
                                      Math.abs(data.skewness || 0) > 1.5 ? 'text-rose-400' : 'text-slate-400'
                                    }`}>
                                      {data.skewness?.toFixed(2) ?? "--"}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      ) : (
                        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-8 text-center text-slate-500 text-xs">
                          No numerical columns found to analyze.
                        </div>
                      )}

                      {/* Categorical Stats List */}
                      {statsData?.categorical && Object.keys(statsData.categorical).length > 0 && (
                        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6">
                          <h4 className="text-sm font-bold text-white mb-4">Categorical Features Distributions</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {Object.entries(statsData.categorical).map(([col, data]: [string, any]) => (
                              <div key={col} className="p-4 bg-slate-950 border border-slate-850 rounded-xl space-y-3">
                                <div className="flex items-center justify-between border-b border-slate-850 pb-2">
                                  <span className="font-bold text-slate-200">{col}</span>
                                  <span className="text-xs text-indigo-400">{data.uniqueValues} Unique Values</span>
                                </div>
                                <div className="text-xs text-slate-400 flex items-center justify-between">
                                  <span>Most Frequent: <strong className="text-slate-200">{data.topCategory || "--"}</strong></span>
                                  <span>Count: <strong className="text-slate-200">{data.topCategoryCount}</strong></span>
                                </div>
                                <div className="space-y-1.5 pt-2">
                                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Top Frequencies</p>
                                  {Object.entries(data.frequencies || {}).slice(0, 3).map(([val, freq]: [string, any]) => {
                                    const percent = ((freq / dataset.rows) * 100).toFixed(1);
                                    return (
                                      <div key={val} className="space-y-1 text-xs">
                                        <div className="flex justify-between text-slate-400 text-[10px]">
                                          <span className="truncate max-w-[150px]">{val}</span>
                                          <span>{freq} ({percent}%)</span>
                                        </div>
                                        <div className="w-full bg-slate-900 rounded-full h-1.5">
                                          <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: `${percent}%` }} />
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* CORRELATIONS TAB */}
                  {activeTab === "correlations" && (
                    <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 animate-in fade-in duration-200 space-y-6">
                      <div>
                        <h4 className="text-sm font-bold text-white">Pearson Correlation Heatmap Matrix</h4>
                        <p className="text-xs text-slate-500 mt-0.5">Displays linear correlation pairings between numeric variables (-1 to +1).</p>
                      </div>

                      {corrData?.columns && corrData.columns.length >= 2 ? (
                        <div className="space-y-6">
                          <div className="overflow-x-auto flex justify-center">
                            <div className="bg-slate-950 p-6 rounded-xl border border-slate-850">
                              <div className="grid" style={{ gridTemplateColumns: `120px repeat(${corrData.columns.length}, 80px)` }}>
                                {/* Header row */}
                                <div className="h-10" />
                                {corrData.columns.map((c: string) => (
                                  <div key={c} className="h-10 text-center font-bold text-[10px] text-slate-400 truncate px-1 flex items-center justify-center uppercase tracking-wide">
                                    {c}
                                  </div>
                                ))}

                                {/* Matrix grid */}
                                {corrData.columns.map((rowCol: string, rIdx: number) => (
                                  <React.Fragment key={rowCol}>
                                    {/* Left label */}
                                    <div className="h-14 font-bold text-[10px] text-slate-400 truncate flex items-center justify-end pr-3 uppercase tracking-wide">
                                      {rowCol}
                                    </div>
                                    {/* Heatmap cells */}
                                    {corrData.columns.map((colCol: string, cIdx: number) => {
                                      const val = corrData.pearson[rIdx][cIdx];
                                      // Generate scale color based on val
                                      // Purple/indigo for high correlation, slate for near zero, blue for negative
                                      let cellBg = "bg-slate-900";
                                      let textColor = "text-slate-400";
                                      if (val !== null) {
                                        if (val > 0.8) { cellBg = "bg-indigo-600/35 border-indigo-500/20"; textColor = "text-indigo-300 font-bold"; }
                                        else if (val > 0.5) { cellBg = "bg-indigo-600/20"; textColor = "text-indigo-400"; }
                                        else if (val > 0.1) { cellBg = "bg-indigo-600/5"; textColor = "text-slate-400"; }
                                        else if (val < -0.8) { cellBg = "bg-blue-600/35 border-blue-500/20"; textColor = "text-blue-300 font-bold"; }
                                        else if (val < -0.5) { cellBg = "bg-blue-600/20"; textColor = "text-blue-400"; }
                                        else if (val < -0.1) { cellBg = "bg-blue-600/5"; textColor = "text-slate-400"; }
                                      }
                                      return (
                                        <div
                                          key={colCol}
                                          className={`h-14 w-20 flex flex-col items-center justify-center border border-slate-900/60 text-xs transition-all hover:scale-105 hover:z-10 ${cellBg} ${textColor}`}
                                          title={`${rowCol} & ${colCol}: ${val?.toFixed(4) || "0"}`}
                                        >
                                          {val !== null ? val.toFixed(2) : "0"}
                                        </div>
                                      );
                                    })}
                                  </React.Fragment>
                                ))}
                              </div>
                            </div>
                          </div>

                          {/* Legend */}
                          <div className="flex justify-center gap-6 text-[10px] text-slate-500">
                            <span className="flex items-center gap-1.5">
                              <span className="w-3 h-3 bg-indigo-600/35 border border-indigo-500/20 rounded shrink-0" />
                              Strong Positive (&gt; 0.8)
                            </span>
                            <span className="flex items-center gap-1.5">
                              <span className="w-3 h-3 bg-slate-900 border border-slate-800 rounded shrink-0" />
                              Weak / None (0.0)
                            </span>
                            <span className="flex items-center gap-1.5">
                              <span className="w-3 h-3 bg-blue-600/35 border border-blue-500/20 rounded shrink-0" />
                              Strong Negative (&lt; -0.8)
                            </span>
                          </div>
                        </div>
                      ) : (
                        <div className="bg-slate-955 border border-slate-850 rounded-xl p-8 text-center text-slate-500 text-xs">
                          Correlation calculation requires at least two numerical columns.
                        </div>
                      )}
                    </div>
                  )}

                  {/* VISUALIZATIONS TAB */}
                  {activeTab === "visuals" && (
                    <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 animate-in fade-in duration-200 space-y-6">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-855 pb-4">
                        <div>
                          <h4 className="text-sm font-bold text-white">Visual Distribution & Relationship Charts</h4>
                          <p className="text-xs text-slate-500 mt-0.5">Explore column traits dynamically using responsive custom SVG rendering.</p>
                        </div>

                        {/* Controls */}
                        <div className="flex flex-wrap items-center gap-3">
                          {/* X Column */}
                          <div>
                            <select
                              value={visualsColX}
                              onChange={(e) => setVisualsColX(e.target.value)}
                              className="rounded-xl border border-slate-800 bg-slate-950 py-1.5 px-3 text-slate-200 text-xs focus:outline-none"
                            >
                              {Object.keys(dataset.columnTypes).map((c) => (
                                <option key={c} value={c}>X: {c}</option>
                              ))}
                            </select>
                          </div>

                          {/* Chart Type */}
                          <div>
                            <select
                              value={visualsChartType}
                              onChange={(e) => setVisualsChartType(e.target.value)}
                              className="rounded-xl border border-slate-800 bg-slate-950 py-1.5 px-3 text-slate-200 text-xs focus:outline-none"
                            >
                              <option value="histogram">Histogram (Dist)</option>
                              <option value="boxplot">Box & Whisker Plot</option>
                              <option value="pie">Pie Chart (Slices)</option>
                              <option value="bar">Bar Chart (Counts)</option>
                              <option value="scatter">Scatter Plot (X vs Y)</option>
                              <option value="line">Line Chart (Date vs Y)</option>
                            </select>
                          </div>

                          {/* Y Column (visible for scatter/line) */}
                          {(visualsChartType === "scatter" || visualsChartType === "line") && (
                            <div>
                              <select
                                value={visualsColY}
                                onChange={(e) => setVisualsColY(e.target.value)}
                                className="rounded-xl border border-slate-800 bg-slate-950 py-1.5 px-3 text-slate-200 text-xs focus:outline-none"
                              >
                                {Object.keys(dataset.columnTypes).map((c) => (
                                  <option key={c} value={c}>Y: {c}</option>
                                ))}
                              </select>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Rendering the Chart */}
                      <div className="bg-slate-950 rounded-xl p-6 flex flex-col items-center justify-center min-h-[350px]">
                        {visualsLoading ? (
                          <div className="flex flex-col items-center gap-2 text-slate-500 text-xs">
                            <Loader2 className="w-6 h-6 animate-spin text-indigo-500" />
                            Loading chart coordinate points...
                          </div>
                        ) : visualsChartType === "boxplot" && visualsBoxData ? (
                          // Render Boxplot
                          <div className="w-full max-w-lg space-y-4">
                            <div className="flex justify-between border-b border-slate-850 pb-2 text-xs font-semibold text-slate-400">
                              <span>Box Plot Metrics: {visualsColX}</span>
                              <span className="font-mono">IQR Range</span>
                            </div>
                            <div className="flex h-56 justify-center items-center">
                              <svg className="w-80 h-48 overflow-visible" viewBox="0 0 300 200">
                                {/* Whisker line */}
                                <line x1="150" y1="20" x2="150" y2="180" stroke="#6366f1" strokeWidth="2" strokeDasharray="3 3" />
                                
                                {/* Min / Max lines */}
                                <line x1="120" y1="20" x2="180" y2="20" stroke="#6366f1" strokeWidth="2" />
                                <line x1="120" y1="180" x2="180" y2="180" stroke="#6366f1" strokeWidth="2" />
                                
                                {/* Q1/Q3 Box */}
                                <rect x="100" y="60" width="100" height="80" fill="#6366f1" fillOpacity="0.15" stroke="#6366f1" strokeWidth="2" />
                                
                                {/* Median Line */}
                                <line x1="100" y1="100" x2="200" y2="100" stroke="#ec4899" strokeWidth="3" />
                                
                                {/* Value Labels */}
                                <text x="215" y="25" fill="#94a3b8" fontSize="10" fontFamily="monospace">Max: {visualsBoxData.max?.toFixed(2) || "0"}</text>
                                <text x="215" y="65" fill="#94a3b8" fontSize="10" fontFamily="monospace">Q3: {visualsBoxData.q3?.toFixed(2) || "0"}</text>
                                <text x="215" y="105" fill="#ec4899" fontSize="10" fontWeight="bold" fontFamily="monospace">Med: {visualsBoxData.median?.toFixed(2) || "0"}</text>
                                <text x="215" y="145" fill="#94a3b8" fontSize="10" fontFamily="monospace">Q1: {visualsBoxData.q1?.toFixed(2) || "0"}</text>
                                <text x="215" y="185" fill="#94a3b8" fontSize="10" fontFamily="monospace">Min: {visualsBoxData.min?.toFixed(2) || "0"}</text>
                              </svg>
                            </div>
                            {visualsBoxData.outliers?.length > 0 && (
                              <p className="text-[10px] text-slate-500 font-mono text-center">
                                Outlier count trimmed/plotted: {visualsBoxData.outliers.length} values.
                              </p>
                            )}
                          </div>
                        ) : visualsData && visualsData.length > 0 ? (
                          // Render generic visual SVG based on type
                          <div className="w-full space-y-4">
                            <div className="flex h-64 w-full items-end justify-between px-10 gap-2 border-b border-slate-800 pb-2">
                              {visualsChartType === "histogram" && (
                                visualsData.map((d: any, idx: number) => {
                                  // Max count to scale heights
                                  const maxCount = Math.max(...visualsData.map((v: any) => v.count)) || 1;
                                  const heightPercent = ((d.count / maxCount) * 100).toFixed(1);
                                  return (
                                    <div key={idx} className="flex-1 flex flex-col items-center gap-2 group relative">
                                      {/* Bar */}
                                      <div 
                                        className="w-full bg-indigo-500/20 hover:bg-indigo-500/40 border-t border-indigo-400 rounded-t-sm transition-all relative cursor-pointer"
                                        style={{ height: `${parseFloat(heightPercent) * 1.8}px` }}
                                      >
                                        {/* Tooltip */}
                                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block bg-slate-900 border border-slate-800 p-2 rounded-lg text-[10px] text-slate-300 pointer-events-none whitespace-nowrap z-20 shadow-xl">
                                          Bin: {d.binName}<br />
                                          Count: {d.count}
                                        </div>
                                      </div>
                                      {/* Label */}
                                      <span className="text-[8px] text-slate-500 font-mono rotate-12 origin-top-left whitespace-nowrap max-w-[50px] truncate">{d.min?.toFixed(1)}</span>
                                    </div>
                                  );
                                })
                              )}

                              {visualsChartType === "bar" && (
                                visualsData.map((d: any, idx: number) => {
                                  const maxCount = Math.max(...visualsData.map((v: any) => v.count)) || 1;
                                  const heightPercent = ((d.count / maxCount) * 100).toFixed(1);
                                  return (
                                    <div key={idx} className="flex-1 flex flex-col items-center gap-2 group relative">
                                      <div 
                                        className="w-full bg-purple-500/20 hover:bg-purple-500/40 border-t border-purple-400 rounded-t-sm transition-all cursor-pointer relative"
                                        style={{ height: `${parseFloat(heightPercent) * 1.8}px` }}
                                      >
                                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block bg-slate-900 border border-slate-800 p-2 rounded-lg text-[10px] text-slate-300 pointer-events-none whitespace-nowrap z-20 shadow-xl">
                                          Category: {d.category}<br />
                                          Count: {d.count}
                                        </div>
                                      </div>
                                      <span className="text-[8px] text-slate-500 rotate-12 origin-top-left whitespace-nowrap max-w-[60px] truncate">{d.category}</span>
                                    </div>
                                  );
                                })
                              )}

                              {(visualsChartType === "scatter" || visualsChartType === "line") && (
                                <div className="w-full h-full relative border-l border-b border-slate-800">
                                  {/* Render standard coordinate chart */}
                                  <svg className="w-full h-56 overflow-visible">
                                    {/* Render circles */}
                                    {visualsChartType === "scatter" && visualsData.map((d: any, idx: number) => {
                                      const validXs = visualsData.map((v: any) => v.x).filter((v: any) => typeof v === "number" && !isNaN(v));
                                      const validYs = visualsData.map((v: any) => v.y).filter((v: any) => typeof v === "number" && !isNaN(v));
                                      
                                      const minX = validXs.length ? Math.min(...validXs) : 0;
                                      const maxX = validXs.length ? Math.max(...validXs) : 1;
                                      const minY = validYs.length ? Math.min(...validYs) : 0;
                                      const maxY = validYs.length ? Math.max(...validYs) : 1;
                                      
                                      const width = 500;
                                      const height = 200;
                                      
                                      const scaleX = maxX - minX > 0 ? ((d.x ?? 0) - minX) / (maxX - minX) : 0.5;
                                      const scaleY = maxY - minY > 0 ? ((d.y ?? 0) - minY) / (maxY - minY) : 0.5;
                                      
                                      const rawCx = 30 + scaleX * (width - 60);
                                      const rawCy = height - 20 - scaleY * (height - 40);
                                      
                                      const cx = isNaN(rawCx) || !isFinite(rawCx) ? 30 : rawCx;
                                      const cy = isNaN(rawCy) || !isFinite(rawCy) ? height - 20 : rawCy;
                                      
                                      return (
                                        <circle 
                                          key={idx} 
                                          cx={cx} 
                                          cy={cy} 
                                          r="4" 
                                          fill="#6366f1" 
                                          fillOpacity="0.6"
                                          stroke="#818cf8"
                                          strokeWidth="1"
                                          className="transition-all hover:r-6 hover:fill-pink-500 hover:stroke-pink-400 cursor-pointer"
                                        >
                                          <title>X: {d.x?.toFixed(2)}, Y: {d.y?.toFixed(2)}</title>
                                        </circle>
                                      );
                                    })}

                                    {/* Render Line Paths */}
                                    {visualsChartType === "line" && (
                                      <polyline
                                        fill="none"
                                        stroke="#818cf8"
                                        strokeWidth="2"
                                        points={visualsData.map((d: any, idx: number) => {
                                          const validValues = visualsData.map((v: any) => v.value).filter((v: any) => typeof v === "number" && !isNaN(v));
                                          const minY = validValues.length ? Math.min(...validValues) : 0;
                                          const maxY = validValues.length ? Math.max(...validValues) : 1;
                                          
                                          const width = 500;
                                          const height = 200;
                                          
                                          const scaleX = visualsData.length > 1 ? idx / (visualsData.length - 1) : 0.5;
                                          const scaleY = maxY - minY > 0 ? ((d.value ?? 0) - minY) / (maxY - minY) : 0.5;
                                          
                                          const rawCx = 30 + scaleX * (width - 60);
                                          const rawCy = height - 20 - scaleY * (height - 40);
                                          const cx = isNaN(rawCx) || !isFinite(rawCx) ? 30 : rawCx;
                                          const cy = isNaN(rawCy) || !isFinite(rawCy) ? height - 20 : rawCy;
                                          return `${cx},${cy}`;
                                        }).join(" ")}
                                      />
                                    )}
                                  </svg>
                                  <div className="absolute top-1 right-2 text-[8px] text-slate-500 font-mono">
                                    X: {visualsColX} vs Y: {visualsColY}
                                  </div>
                                </div>
                              )}

                              {visualsChartType === "pie" && (
                                <div className="w-full flex justify-center py-6">
                                  <div className="space-y-4 w-72">
                                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center">Top Slice Percentages</p>
                                    <div className="space-y-2">
                                      {visualsData.map((d: any, idx: number) => (
                                        <div key={idx} className="flex flex-col gap-1 text-xs">
                                          <div className="flex justify-between font-mono">
                                            <span>{d.name}</span>
                                            <span>{d.percentage?.toFixed(1)}%</span>
                                          </div>
                                          <div className="w-full bg-slate-900 rounded-full h-2">
                                            <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${d.percentage}%` }} />
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>
                            <p className="text-center text-[10px] text-slate-500 font-semibold uppercase tracking-wider mt-4">
                              {visualsChartType} Representation of {visualsColX}
                            </p>
                          </div>
                        ) : (
                          <div className="text-slate-500 text-xs py-4 flex items-center gap-1.5">
                            <Eye className="w-4 h-4 text-slate-600" /> Choose values or adjust query attributes.
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* INSIGHTS PANEL TAB */}
                  {activeTab === "insights" && (
                    <div className="space-y-6 animate-in fade-in duration-200">
                      <div>
                        <h4 className="text-sm font-bold text-white">Statistical Observations & Warnings</h4>
                        <p className="text-xs text-slate-500 mt-0.5">Deterministic insights computed from feature spreads and correlations.</p>
                      </div>

                      {insights.length === 0 ? (
                        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-8 text-center text-slate-500 text-xs">
                          No alerts or significant patterns detected in this dataset.
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {insights.map((ins, idx) => {
                            let typeClass = "bg-indigo-500/10 border-indigo-500/20 text-indigo-400";
                            if (ins.type === "warning") {
                              typeClass = "bg-rose-500/10 border-rose-500/20 text-rose-400";
                            } else if (ins.type === "success") {
                              typeClass = "bg-emerald-500/10 border-emerald-500/20 text-emerald-400";
                            } else if (ins.type === "info") {
                              typeClass = "bg-amber-500/10 border-amber-500/20 text-amber-400";
                            }
                            return (
                              <div key={idx} className={`p-5 rounded-xl border flex gap-4 items-start ${typeClass}`}>
                                <ShieldAlert className="w-5 h-5 shrink-0 mt-0.5" />
                                <div className="space-y-1">
                                  <h5 className="font-bold text-xs uppercase tracking-wider">{ins.title}</h5>
                                  <p className="text-xs text-slate-300">{ins.description}</p>
                                  <div className="text-[10px] text-slate-400 font-semibold pt-1 border-t border-slate-800/40 mt-2">
                                    Recommended: {ins.action}
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  )}
                  {/* MACHINE LEARNING TAB */}
                  {activeTab === "ml" && (
                    <div className="space-y-6 animate-in fade-in duration-200">
                      {/* ML Sub navigation */}
                      <div className="flex border-b border-slate-800 gap-4 pb-px text-xs font-semibold">
                        <button
                          onClick={() => setMlSubTab("train")}
                          className={`pb-2.5 border-b-2 transition-all cursor-pointer ${
                            mlSubTab === "train"
                              ? "border-indigo-500 text-indigo-400 font-bold"
                              : "border-transparent text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          <span className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5" /> 1. Train Wizard</span>
                        </button>
                        <button
                          onClick={() => setMlSubTab("history")}
                          className={`pb-2.5 border-b-2 transition-all cursor-pointer ${
                            mlSubTab === "history"
                              ? "border-indigo-500 text-indigo-400 font-bold"
                              : "border-transparent text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          <span className="flex items-center gap-1.5"><History className="w-3.5 h-3.5" /> 2. Model Registry</span>
                        </button>
                        <button
                          onClick={() => setMlSubTab("compare")}
                          className={`pb-2.5 border-b-2 transition-all cursor-pointer ${
                            mlSubTab === "compare"
                              ? "border-indigo-500 text-indigo-400 font-bold"
                              : "border-transparent text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          <span className="flex items-center gap-1.5"><GitCompare className="w-3.5 h-3.5" /> 3. Comparisons</span>
                        </button>
                        <button
                          onClick={() => setMlSubTab("predict")}
                          className={`pb-2.5 border-b-2 transition-all cursor-pointer ${
                            mlSubTab === "predict"
                              ? "border-indigo-500 text-indigo-400 font-bold"
                              : "border-transparent text-slate-400 hover:text-slate-200"
                          }`}
                        >
                          <span className="flex items-center gap-1.5"><Play className="w-3.5 h-3.5" /> 4. Prediction Panel</span>
                        </button>
                      </div>

                      {/* SUB TAB 1: TRAINING WIZARD */}
                      {mlSubTab === "train" && (
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                          <div className="lg:col-span-2 bg-slate-900/40 border border-slate-800 rounded-xl p-6 space-y-6">
                            <div>
                              <h4 className="text-sm font-bold text-white">Model Configuration</h4>
                              <p className="text-xs text-slate-500 mt-0.5">Select your parameters and columns to train a pipeline.</p>
                            </div>

                            <div className="space-y-4">
                              {/* Algorithm */}
                              <div>
                                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Predictive Algorithm</label>
                                <select
                                  value={mlAlgo}
                                  onChange={(e) => setMlAlgo(e.target.value)}
                                  className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2 px-3 text-slate-300 text-xs focus:outline-none focus:border-indigo-500"
                                >
                                  <optgroup label="Regression">
                                    <option value="linear_regression">Linear Regression</option>
                                    <option value="ridge">Ridge Regression</option>
                                    <option value="lasso">Lasso Regression</option>
                                    <option value="decision_tree">Decision Tree Regressor</option>
                                    <option value="random_forest">Random Forest Regressor</option>
                                    <option value="xgboost">XGBoost Regressor</option>
                                  </optgroup>
                                  <optgroup label="Classification">
                                    <option value="logistic_regression">Logistic Regression</option>
                                    <option value="decision_tree_clf">Decision Tree Classifier</option>
                                    <option value="random_forest_clf">Random Forest Classifier</option>
                                    <option value="svm">Support Vector Machine (SVM)</option>
                                    <option value="naive_bayes">Naive Bayes</option>
                                    <option value="xgboost_clf">XGBoost Classifier</option>
                                  </optgroup>
                                  <optgroup label="Clustering (Unsupervised)">
                                    <option value="kmeans">K-Means Clustering</option>
                                    <option value="dbscan">DBSCAN</option>
                                    <option value="hierarchical">Hierarchical Clustering</option>
                                  </optgroup>
                                </select>
                              </div>

                              {/* Target Column (if not clustering) */}
                              {!["kmeans", "dbscan", "hierarchical"].includes(mlAlgo) && (
                                <div>
                                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Target Variable (Column to Predict)</label>
                                  <select
                                    value={mlTarget}
                                    onChange={(e) => setMlTarget(e.target.value)}
                                    className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2 px-3 text-slate-300 text-xs focus:outline-none focus:border-indigo-500 font-mono"
                                  >
                                    {Object.keys(dataset.columnTypes).map(c => (
                                      <option key={c} value={c}>{c}</option>
                                    ))}
                                  </select>
                                </div>
                              )}

                              {/* Features Selection */}
                              <div>
                                <div className="flex items-center justify-between mb-2">
                                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">Features (Input Columns)</label>
                                  <div className="flex gap-2">
                                    <button
                                      type="button"
                                      onClick={() => setMlFeatures(Object.keys(dataset.columnTypes).filter(c => c !== mlTarget))}
                                      className="text-[10px] text-indigo-400 hover:text-indigo-300 font-bold"
                                    >
                                      Select All
                                    </button>
                                    <button
                                      type="button"
                                      onClick={() => setMlFeatures([])}
                                      className="text-[10px] text-slate-500 hover:text-slate-400 font-bold"
                                    >
                                      Clear All
                                    </button>
                                  </div>
                                </div>
                                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 border border-slate-800 bg-slate-950/40 p-4 rounded-xl max-h-40 overflow-y-auto">
                                  {Object.keys(dataset.columnTypes).map((col) => {
                                    const disabled = col === mlTarget && !["kmeans", "dbscan", "hierarchical"].includes(mlAlgo);
                                    return (
                                      <label key={col} className={`flex items-center gap-2 text-xs font-mono truncate ${disabled ? 'opacity-30' : 'cursor-pointer hover:text-slate-200 text-slate-400'}`}>
                                        <input
                                          type="checkbox"
                                          disabled={disabled}
                                          checked={mlFeatures.includes(col) && !disabled}
                                          onChange={(e) => {
                                            if (e.target.checked) {
                                              setMlFeatures((prev) => [...prev, col]);
                                            } else {
                                              setMlFeatures((prev) => prev.filter(c => c !== col));
                                            }
                                          }}
                                          className="rounded border-slate-800 text-indigo-600 bg-slate-950 focus:ring-indigo-500 focus:ring-offset-0"
                                        />
                                        {col}
                                      </label>
                                    );
                                  })}
                                </div>
                              </div>

                              {/* Parameters JSON */}
                              <div>
                                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Custom Hyperparameters (JSON format)</label>
                                <textarea
                                  value={mlParams}
                                  onChange={(e) => setMlParams(e.target.value)}
                                  placeholder='e.g. {"n_estimators": 100, "max_depth": 5}'
                                  className="w-full h-20 bg-slate-950 border border-slate-800 rounded-xl py-2 px-3 text-slate-300 font-mono text-xs focus:outline-none focus:border-indigo-500"
                                />
                              </div>

                              {/* Split & Seed */}
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div>
                                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Test Split Ratio ({Math.round(mlSplit * 100)}%)</label>
                                  <input
                                    type="range"
                                    min="0.1"
                                    max="0.5"
                                    step="0.05"
                                    value={mlSplit}
                                    onChange={(e) => setMlSplit(parseFloat(e.target.value))}
                                    className="w-full accent-indigo-500 bg-slate-800 h-1 rounded-lg appearance-none cursor-pointer"
                                  />
                                </div>
                                <div>
                                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Random Seed</label>
                                  <input
                                    type="number"
                                    value={mlSeed}
                                    onChange={(e) => setMlSeed(parseInt(e.target.value) || 42)}
                                    className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2 px-3 text-slate-300 text-xs focus:outline-none focus:border-indigo-500"
                                  />
                                </div>
                              </div>

                              {/* Stratified split (classification only) */}
                              {!["kmeans", "dbscan", "hierarchical"].includes(mlAlgo) && 
                               dataset.categoricalColumns.includes(mlTarget) && (
                                <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer hover:text-slate-200">
                                  <input
                                    type="checkbox"
                                    checked={mlStratified}
                                    onChange={(e) => setMlStratified(e.target.checked)}
                                    className="rounded border-slate-800 text-indigo-600 bg-slate-950 focus:ring-indigo-500 focus:ring-offset-0"
                                  />
                                  Stratified Train/Test Split (preserves class frequencies)
                                </label>
                              )}
                            </div>

                            {mlTrainingError && (
                              <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex gap-2">
                                <AlertCircle className="w-4 h-4 shrink-0" />
                                <span>{mlTrainingError}</span>
                              </div>
                            )}

                            <button
                              onClick={handleTrainModel}
                              disabled={mlTrainingLoading || mlFeatures.length === 0}
                              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 py-3 rounded-xl font-bold text-xs text-white cursor-pointer transition-colors flex items-center justify-center gap-2"
                            >
                              {mlTrainingLoading ? (
                                <>
                                  <Loader2 className="w-4 h-4 animate-spin" /> Fitting Pipeline & Estimators...
                                </>
                              ) : (
                                <>
                                  <Zap className="w-4 h-4" /> Train Model Pipeline
                                </>
                              )}
                            </button>
                          </div>

                          {/* Info panel */}
                          <div className="space-y-6">
                            <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 space-y-4">
                              <h4 className="text-sm font-bold text-white">Pipeline Summary</h4>
                              <p className="text-xs text-slate-400">
                                InsightAI uses a standard preprocessing + estimator scikit-learn pipeline.
                              </p>
                              <div className="space-y-2 border-t border-slate-800/40 pt-3">
                                <div className="flex justify-between text-xs">
                                  <span className="text-slate-500">Numeric Scaler:</span>
                                  <span className="font-mono text-indigo-400 text-[10px]">StandardScaler</span>
                                </div>
                                <div className="flex justify-between text-xs">
                                  <span className="text-slate-500">Categorical Encoder:</span>
                                  <span className="font-mono text-indigo-400 text-[10px]">OneHotEncoder</span>
                                </div>
                                <div className="flex justify-between text-xs">
                                  <span className="text-slate-500">Imputer:</span>
                                  <span className="font-mono text-indigo-400 text-[10px]">Median/Mode</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* SUB TAB 2: MODEL REGISTRY */}
                      {mlSubTab === "history" && (
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                          {/* Models list */}
                          <div className="lg:col-span-1 bg-slate-900/40 border border-slate-800 rounded-xl p-5 space-y-4 h-[600px] overflow-y-auto">
                            <h4 className="text-sm font-bold text-white">Models ({mlModels.length})</h4>
                            
                            {mlModels.length === 0 ? (
                              <p className="text-slate-500 text-xs">No trained models yet. Train one using the Train Wizard.</p>
                            ) : (
                              <div className="space-y-2">
                                {mlModels.map((m) => {
                                  const mId = m._id || m.id;
                                  const isActive = (activeModel?._id || activeModel?.id) === mId;
                                  return (
                                    <div
                                      key={mId}
                                      onClick={() => handleSelectModel(m)}
                                      className={`p-4 rounded-xl border transition-all cursor-pointer text-left ${
                                        isActive
                                          ? "bg-indigo-600/10 border-indigo-500/40"
                                          : "bg-slate-950 border-slate-850 hover:border-slate-700"
                                      }`}
                                    >
                                      <div className="flex justify-between items-start gap-2">
                                        <p className="text-xs font-bold text-white truncate font-mono">{m.modelName}</p>
                                        <button
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            handleDeleteModel(mId);
                                          }}
                                          className="text-slate-500 hover:text-rose-400 transition-colors"
                                        >
                                        <Trash2 className="w-3.5 h-3.5" />
                                      </button>
                                    </div>
                                    <div className="flex justify-between text-[10px] text-slate-500 font-semibold uppercase tracking-wider mt-2">
                                      <span>{m.algorithm.replace('_', ' ')}</span>
                                      <span>{m.taskType}</span>
                                    </div>
                                  </div>
                                  );
                                })}
                              </div>
                            )}
                          </div>

                          {/* Active model details / metrics / graphs */}
                          <div className="lg:col-span-2 space-y-6">
                            {activeModel ? (
                              <div className="space-y-6 animate-in fade-in duration-200">
                                {/* Model Meta Cards */}
                                <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6">
                                  <h3 className="text-base font-bold text-white font-mono">{activeModel.modelName}</h3>
                                  <p className="text-xs text-slate-500 mt-1 uppercase font-semibold tracking-wider">
                                    Algorithm: {activeModel.algorithm.replace('_', ' ')} • Task: {activeModel.taskType}
                                  </p>
                                  
                                  {/* Metrics parameters */}
                                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 border-t border-slate-800/40 pt-6">
                                    {Object.entries(activeModel.metrics).map(([name, score]) => (
                                      <div key={name} className="bg-slate-950/60 p-3 rounded-lg border border-slate-850">
                                        <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">{name}</span>
                                        <p className="text-lg font-mono font-bold text-white mt-1">
                                          {typeof score === "number" ? score.toFixed(4) : String(score ?? "--")}
                                        </p>
                                      </div>
                                    ))}
                                    <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-850">
                                      <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Train Time</span>
                                      <p className="text-lg font-mono font-bold text-white mt-1">
                                        {activeModel.trainingTime?.toFixed(3)}s
                                      </p>
                                    </div>
                                  </div>
                                </div>

                                {/* Feature Importance */}
                                {activeModel.featureImportance && activeModel.featureImportance.length > 0 && (
                                  <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6">
                                    <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">Gini Feature Importances / Coefficients</h4>
                                    <div className="space-y-3">
                                      {activeModel.featureImportance.slice(0, 10).map((f: any, idx: number) => (
                                        <div key={idx} className="space-y-1">
                                          <div className="flex justify-between text-xs font-mono text-slate-300">
                                            <span>{f.feature}</span>
                                            <span>{f.importance?.toFixed(4)}</span>
                                          </div>
                                          <div className="w-full bg-slate-950 rounded-full h-1.5 border border-slate-900">
                                            <div
                                              className="bg-indigo-500 h-1.5 rounded-full"
                                              style={{ width: `${Math.min(100, (f.importance * 100))}%` }}
                                            />
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Graphs coordinate renderer */}
                                {activeModelVisuals ? (
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {/* Actual vs Predicted scatter for Regression */}
                                    {activeModel.taskType === "regression" && activeModelVisuals.actualVsPredicted && (
                                      <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 space-y-4">
                                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Actual vs Predicted Scatter</h4>
                                        <div className="relative border border-slate-800 bg-slate-950 h-56 rounded-xl flex items-center justify-center">
                                          <svg className="w-full h-full p-6">
                                            {/* Draw diagonal reference line */}
                                            <line x1="0%" y1="100%" x2="100%" y2="0%" stroke="#334155" strokeDasharray="4 4" strokeWidth="1.5" />
                                            {/* Draw scatter dots */}
                                            {activeModelVisuals.actualVsPredicted.map((pt: any, i: number) => {
                                              const actuals = activeModelVisuals.actualVsPredicted.map((v: any) => v.actual).filter((v: any) => typeof v === "number" && !isNaN(v));
                                              const preds = activeModelVisuals.actualVsPredicted.map((v: any) => v.predicted).filter((v: any) => typeof v === "number" && !isNaN(v));
                                              const minVal = actuals.length && preds.length ? Math.min(...actuals, ...preds) : 0;
                                              const maxVal = actuals.length && preds.length ? Math.max(...actuals, ...preds) : 1;
                                              const diff = maxVal - minVal || 1.0;
                                              
                                              const rawCx = (((pt.actual ?? 0) - minVal) / diff) * 100;
                                              const rawCy = 100 - ((((pt.predicted ?? 0) - minVal) / diff) * 100);
                                              const cx = isNaN(rawCx) || !isFinite(rawCx) ? 50 : Math.max(0, Math.min(100, rawCx));
                                              const cy = isNaN(rawCy) || !isFinite(rawCy) ? 50 : Math.max(0, Math.min(100, rawCy));
                                              return (
                                                <circle key={i} cx={`${cx}%`} cy={`${cy}%`} r="3" fill="#6366f1" opacity="0.6" />
                                              );
                                            })}
                                          </svg>
                                        </div>
                                      </div>
                                    )}

                                    {/* Residuals plot for Regression */}
                                    {activeModel.taskType === "regression" && activeModelVisuals.residualPlot && (
                                      <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 space-y-4">
                                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Residual Plot (Error vs Predict)</h4>
                                        <div className="relative border border-slate-800 bg-slate-950 h-56 rounded-xl flex items-center justify-center">
                                          <svg className="w-full h-full p-6">
                                            {/* Draw center 0 reference line */}
                                            <line x1="0%" y1="50%" x2="100%" y2="50%" stroke="#475569" strokeDasharray="3 3" strokeWidth="1.5" />
                                            {/* Draw residuals dots */}
                                            {activeModelVisuals.residualPlot.map((pt: any, i: number) => {
                                              const preds = activeModelVisuals.residualPlot.map((v: any) => v.predicted).filter((v: any) => typeof v === "number" && !isNaN(v));
                                              const resids = activeModelVisuals.residualPlot.map((v: any) => v.residual).filter((v: any) => typeof v === "number" && !isNaN(v));
                                              const minPred = preds.length ? Math.min(...preds) : 0;
                                              const maxPred = preds.length ? Math.max(...preds) : 1;
                                              const diffPred = maxPred - minPred || 1.0;
                                              
                                              const absResids = resids.map(Math.abs);
                                              const maxAbsResid = absResids.length ? Math.max(...absResids) : 1.0;
                                              
                                              const rawCx = (((pt.predicted ?? 0) - minPred) / diffPred) * 100;
                                              const rawCy = 50 - (((pt.residual ?? 0) / (maxAbsResid || 1.0)) * 50);
                                              const cx = isNaN(rawCx) || !isFinite(rawCx) ? 50 : Math.max(0, Math.min(100, rawCx));
                                              const cy = isNaN(rawCy) || !isFinite(rawCy) ? 50 : Math.max(0, Math.min(100, rawCy));
                                              return (
                                                <circle key={i} cx={`${cx}%`} cy={`${cy}%`} r="3" fill="#ec4899" opacity="0.6" />
                                              );
                                            })}
                                          </svg>
                                        </div>
                                      </div>
                                    )}

                                    {/* ROC Curve for Classification */}
                                    {activeModel.taskType === "classification" && activeModelVisuals.rocCurve && (
                                      <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 space-y-4">
                                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">ROC Curve</h4>
                                        <div className="relative border border-slate-800 bg-slate-950 h-56 rounded-xl flex items-center justify-center">
                                          <svg className="w-full h-full p-6">
                                            {/* Baseline random path */}
                                            <line x1="0%" y1="100%" x2="100%" y2="0%" stroke="#334155" strokeDasharray="3 3" />
                                            
                                            {/* ROC Line path */}
                                            {activeModelVisuals.rocCurve.length > 1 && (
                                              <polyline
                                                fill="none"
                                                stroke="#6366f1"
                                                strokeWidth="2.5"
                                                points={activeModelVisuals.rocCurve.map((pt: any) => {
                                                  const rawCx = (pt.fpr ?? 0) * 100;
                                                  const rawCy = 100 - ((pt.tpr ?? 0) * 100);
                                                  const cx = isNaN(rawCx) || !isFinite(rawCx) ? 0 : Math.max(0, Math.min(100, rawCx));
                                                  const cy = isNaN(rawCy) || !isFinite(rawCy) ? 100 : Math.max(0, Math.min(100, rawCy));
                                                  return `${cx}%,${cy}%`;
                                                }).join(" ")}
                                              />
                                            )}
                                          </svg>
                                          <div className="absolute bottom-2 right-4 text-[10px] text-indigo-400 font-bold font-mono">
                                            AUC: {activeModel.metrics?.rocAuc?.toFixed(4) || "N/A"}
                                          </div>
                                        </div>
                                      </div>
                                    )}

                                    {/* PCA Cluster scatter plot for Clustering */}
                                    {activeModel.taskType === "clustering" && activeModelVisuals.clusterScatter && (
                                      <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 space-y-4">
                                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">2D PCA Cluster View</h4>
                                        <div className="relative border border-slate-800 bg-slate-950 h-56 rounded-xl flex items-center justify-center">
                                          <svg className="w-full h-full p-6">
                                            {activeModelVisuals.clusterScatter.map((pt: any, i: number) => {
                                              const xs = activeModelVisuals.clusterScatter.map((v: any) => v.x).filter((v: any) => typeof v === "number" && !isNaN(v));
                                              const ys = activeModelVisuals.clusterScatter.map((v: any) => v.y).filter((v: any) => typeof v === "number" && !isNaN(v));
                                              const minX = xs.length ? Math.min(...xs) : 0;
                                              const maxX = xs.length ? Math.max(...xs) : 1;
                                              const minY = ys.length ? Math.min(...ys) : 0;
                                              const maxY = ys.length ? Math.max(...ys) : 1;
                                              
                                              const rawCx = (((pt.x ?? 0) - minX) / (maxX - minX || 1)) * 100;
                                              const rawCy = 100 - ((((pt.y ?? 0) - minY) / (maxY - minY || 1)) * 100);
                                              const cx = isNaN(rawCx) || !isFinite(rawCx) ? 50 : Math.max(0, Math.min(100, rawCx));
                                              const cy = isNaN(rawCy) || !isFinite(rawCy) ? 50 : Math.max(0, Math.min(100, rawCy));
                                              
                                              const colors = ["#6366f1", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6", "#3b82f6", "#14b8a6"];
                                              const dotColor = colors[Math.max(0, pt.cluster ?? 0) % colors.length];
                                              
                                              return (
                                                <circle key={i} cx={`${cx}%`} cy={`${cy}%`} r="3.5" fill={dotColor} opacity="0.8" />
                                              );
                                            })}
                                          </svg>
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                ) : (
                                  <div className="text-slate-500 text-xs py-4 flex items-center gap-1.5">
                                    <Loader2 className="w-4 h-4 animate-spin text-slate-650" /> Loading visuals coordinates...
                                  </div>
                                )}
                              </div>
                            ) : (
                              <div className="bg-slate-900/20 border border-slate-850 rounded-xl p-12 text-center text-slate-500 text-xs">
                                Load a model pipeline from the Model Registry sidebar to see details.
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* SUB TAB 3: COMPARISONS */}
                      {mlSubTab === "compare" && (
                        <div className="space-y-6">
                          {comparisonLoading ? (
                            <div className="text-slate-500 text-xs py-12 text-center flex items-center justify-center gap-2">
                              <Loader2 className="w-4 h-4 animate-spin text-indigo-400" /> Computing comparative rankings...
                            </div>
                          ) : comparisonData ? (
                            <div className="space-y-6">
                              {/* Best model recommendation */}
                              <div className="p-6 rounded-xl border border-indigo-500/20 bg-indigo-500/5">
                                <h4 className="text-sm font-bold text-indigo-400">InsightAI Recommended Pipeline</h4>
                                <p className="text-xs text-slate-300 mt-2 leading-relaxed">{comparisonData.recommendationReason}</p>
                              </div>

                              {/* Comparison Table */}
                              <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 space-y-4">
                                <h4 className="text-xs font-bold text-white uppercase tracking-wider">Models Comparison Matrix</h4>
                                <div className="overflow-x-auto">
                                  <table className="w-full text-left text-xs font-mono text-slate-300">
                                    <thead className="text-[10px] text-slate-500 uppercase tracking-wider border-b border-slate-850 font-sans">
                                      <tr>
                                        <th className="py-3">Model Name</th>
                                        <th className="py-3">Algorithm</th>
                                        <th className="py-3">Train Time</th>
                                        <th className="py-3 text-right">Metrics Scores</th>
                                      </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-855">
                                      {comparisonData.comparisonTable.map((row: any) => (
                                        <tr key={row.modelId} className={row.modelId === comparisonData.bestModelId ? "bg-indigo-500/5 text-indigo-300 font-bold" : ""}>
                                          <td className="py-4">{row.modelName}</td>
                                          <td className="py-4 uppercase text-[10px]">{row.algorithm.replace('_', ' ')}</td>
                                          <td className="py-4">{row.trainingTime?.toFixed(3)}s</td>
                                          <td className="py-4 text-right">
                                            {Object.entries(row.metrics).map(([n, val]: [any, any]) => (
                                              <span key={n} className="inline-block bg-slate-950/80 px-2 py-0.5 rounded ml-2 text-[10px] border border-slate-850">
                                                {n}: {typeof val === "number" ? val.toFixed(4) : String(val ?? "")}
                                              </span>
                                            ))}
                                          </td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              </div>
                            </div>
                          ) : (
                            <div className="bg-slate-900/20 border border-slate-850 rounded-xl p-12 text-center text-slate-500 text-xs">
                              No models available to compare. Train multiple pipelines first.
                            </div>
                          )}
                        </div>
                      )}

                      {/* SUB TAB 4: PREDICTION PANEL */}
                      {mlSubTab === "predict" && (
                        <div className="space-y-6">
                          {activeModel ? (
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-200">
                              <div className="lg:col-span-2 space-y-6">
                                {/* Manual Entry Panel */}
                                <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 space-y-4">
                                  <div>
                                    <h4 className="text-sm font-bold text-white">Manual Predictions</h4>
                                    <p className="text-xs text-slate-500 mt-0.5">Input a JSON dictionary matching features list columns.</p>
                                  </div>
                                  
                                  <textarea
                                    value={predictManualInput}
                                    onChange={(e) => setPredictManualInput(e.target.value)}
                                    className="w-full h-32 bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-300 focus:outline-none focus:border-indigo-500"
                                  />
                                  
                                  <div className="flex gap-2">
                                    <button
                                      onClick={() => {
                                        // Auto generate template based on model features
                                        const template: Record<string, any> = {};
                                        activeModel.features.forEach((f: string) => {
                                          template[f] = dataset.numericalColumns.includes(f) ? 0.0 : "";
                                        });
                                        setPredictManualInput(JSON.stringify(template, null, 2));
                                      }}
                                      className="px-4 py-2 border border-slate-700 hover:bg-slate-800 rounded-xl text-xs font-semibold text-slate-300 cursor-pointer transition-colors"
                                    >
                                      Load JSON Template
                                    </button>
                                    <button
                                      onClick={handlePredictManual}
                                      disabled={predictLoading}
                                      className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-650 rounded-xl text-xs font-bold text-white cursor-pointer transition-colors flex items-center gap-1.5"
                                    >
                                      {predictLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                                      Generate Predictions
                                    </button>
                                  </div>
                                </div>

                                {/* Results table */}
                                {predictResults && (
                                  <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 space-y-3">
                                    <h4 className="text-xs font-bold text-white uppercase tracking-wider">Prediction Results</h4>
                                    <div className="overflow-x-auto max-h-56">
                                      <table className="w-full text-left text-xs font-mono text-slate-300">
                                        <thead className="text-[10px] text-slate-500 uppercase tracking-wider border-b border-slate-850 font-sans">
                                          <tr>
                                            <th className="py-2.5">Row Index</th>
                                            <th className="py-2.5 text-right text-indigo-400">Prediction Output</th>
                                          </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-855">
                                          {predictResults.map((val: any, idx: number) => (
                                            <tr key={idx}>
                                              <td className="py-2.5">Input Row {idx + 1}</td>
                                              <td className="py-2.5 text-right font-bold text-indigo-400">{typeof val === "number" ? val.toFixed(4) : String(val)}</td>
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    </div>
                                  </div>
                                )}
                              </div>

                              {/* Batch Prediction Panel */}
                              <div className="space-y-6">
                                <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 space-y-4">
                                  <h4 className="text-sm font-bold text-white">Batch Upload Prediction</h4>
                                  <p className="text-xs text-slate-400 leading-relaxed">
                                    Upload a new CSV containing the same columns. InsightAI will return the file appended with a <span className="font-mono font-bold text-indigo-400">Prediction</span> column.
                                  </p>
                                  
                                  <div
                                    onClick={() => predictFileInputRef.current?.click()}
                                    className="border border-dashed border-slate-850 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer hover:bg-slate-950/20"
                                  >
                                    <input
                                      ref={predictFileInputRef}
                                      type="file"
                                      accept=".csv"
                                      onChange={handlePredictFileUpload}
                                      className="hidden"
                                    />
                                    <Download className="w-5 h-5 text-indigo-400 mb-2" />
                                    <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">Select new CSV</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          ) : (
                            <div className="bg-slate-900/20 border border-slate-850 rounded-xl p-12 text-center text-slate-500 text-xs">
                              Please active/load a model pipeline in the Model Registry registry first before making predictions.
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {/* FORECASTING & EXPLAINABLE AI TAB */}
                  {activeTab === "forecasting" && (
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 animate-in fade-in duration-200">
                      {/* Left Sidebar navigation */}
                      <div className="space-y-4">
                        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4 flex flex-col gap-2">
                          <button
                            onClick={() => setForecastSubTab("train")}
                            className={`flex items-center gap-2 px-3 py-2 text-xs font-semibold rounded-lg transition-colors cursor-pointer text-left ${
                              forecastSubTab === "train"
                                ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/20"
                                : "text-slate-400 hover:bg-slate-800/40"
                            }`}
                          >
                            <TrendingUp className="w-4 h-4" /> Time Series Forecast
                          </button>
                          <button
                            onClick={() => setForecastSubTab("history")}
                            className={`flex items-center gap-2 px-3 py-2 text-xs font-semibold rounded-lg transition-colors cursor-pointer text-left ${
                              forecastSubTab === "history"
                                ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/20"
                                : "text-slate-400 hover:bg-slate-800/40"
                            }`}
                          >
                            <History className="w-4 h-4" /> Forecast History
                          </button>
                          <button
                            onClick={() => {
                              setForecastSubTab("explain");
                              if (mlModels.length > 0 && !explainMlModelId) {
                                setExplainMlModelId(mlModels[0]._id || mlModels[0].id);
                              }
                            }}
                            className={`flex items-center gap-2 px-3 py-2 text-xs font-semibold rounded-lg transition-colors cursor-pointer text-left ${
                              forecastSubTab === "explain"
                                ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/20"
                                : "text-slate-400 hover:bg-slate-800/40"
                            }`}
                          >
                            <Cpu className="w-4 h-4" /> Explainable AI (XAI)
                          </button>
                          <button
                            onClick={() => {
                              setForecastSubTab("recommendations");
                              if (mlModels.length > 0 && !explainMlModelId) {
                                setExplainMlModelId(mlModels[0]._id || mlModels[0].id);
                              }
                            }}
                            className={`flex items-center gap-2 px-3 py-2 text-xs font-semibold rounded-lg transition-colors cursor-pointer text-left ${
                              forecastSubTab === "recommendations"
                                ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/20"
                                : "text-slate-400 hover:bg-slate-800/40"
                            }`}
                          >
                            <Zap className="w-4 h-4" /> Business Recommendations
                          </button>
                        </div>
                      </div>

                      {/* Right main area */}
                      <div className="lg:col-span-3 space-y-6">
                        {forecastError && (
                          <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-xl flex items-start gap-2">
                            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                            <div>
                              <p className="font-bold">Execution Error</p>
                              <p className="mt-0.5">{forecastError}</p>
                            </div>
                          </div>
                        )}

                        {/* SUB TAB 1: TRAIN WIZARD */}
                        {forecastSubTab === "train" && (
                          <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 space-y-6">
                            <div>
                              <h4 className="text-sm font-bold text-white">Time Series Detection & Feasibility</h4>
                              <p className="text-xs text-slate-500 mt-0.5">We analyze sequential dates and targets for regression forecasting suitability.</p>
                            </div>

                            {forecastDetectLoading ? (
                              <div className="text-slate-500 text-xs py-6 flex items-center gap-2">
                                <Loader2 className="w-4 h-4 animate-spin text-indigo-400" /> Scanning dates alignment...
                              </div>
                            ) : forecastDetectResult ? (
                              <div className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                  <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-850">
                                    <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Datetime Column</span>
                                    <p className="text-sm font-mono font-bold text-white mt-1">
                                      {forecastDetectResult.datetimeColumn || "None Detected"}
                                    </p>
                                  </div>
                                  <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-850">
                                    <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Inferred Frequency</span>
                                    <p className="text-sm font-mono font-bold text-white mt-1">
                                      {forecastDetectResult.frequency || "Irregular"}
                                    </p>
                                  </div>
                                  <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-850">
                                    <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Missing Timestamps</span>
                                    <p className="text-sm font-mono font-bold text-white mt-1">
                                      {forecastDetectResult.missingTimestampsCount} gaps
                                    </p>
                                  </div>
                                </div>

                                {forecastDetectResult.warnings.length > 0 && (
                                  <div className="p-4 bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs rounded-xl space-y-1">
                                    <p className="font-bold flex items-center gap-1"><ShieldAlert className="w-4 h-4" /> Warnings & Recommendations:</p>
                                    <ul className="list-disc pl-5 mt-1 space-y-1">
                                      {forecastDetectResult.warnings.map((w: string, i: number) => (
                                        <li key={i}>{w}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {forecastDetectResult.isFeasible ? (
                                  <div className="border-t border-slate-800/60 pt-6 space-y-4">
                                    <h5 className="text-xs font-bold text-white uppercase tracking-wider">Model Training Configuration</h5>
                                    
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                      <div>
                                        <label className="block text-xs font-semibold text-slate-400 mb-1.5">Date Column</label>
                                        <select
                                          value={forecastDateCol}
                                          onChange={(e) => setForecastDateCol(e.target.value)}
                                          className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-350 text-xs focus:outline-none focus:border-indigo-500"
                                        >
                                          <option value="">Select column</option>
                                          {Object.keys(dataset.columnTypes).map(col => (
                                            <option key={col} value={col}>{col}</option>
                                          ))}
                                        </select>
                                      </div>

                                      <div>
                                        <label className="block text-xs font-semibold text-slate-400 mb-1.5">Target Variable</label>
                                        <select
                                          value={forecastTargetCol}
                                          onChange={(e) => setForecastTargetCol(e.target.value)}
                                          className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-350 text-xs focus:outline-none focus:border-indigo-500"
                                        >
                                          <option value="">Select target</option>
                                          {forecastDetectResult.targetCandidates.map((col: string) => (
                                            <option key={col} value={col}>{col}</option>
                                          ))}
                                        </select>
                                      </div>

                                      <div>
                                        <label className="block text-xs font-semibold text-slate-400 mb-1.5">Algorithm</label>
                                        <select
                                          value={forecastAlgo}
                                          onChange={(e) => setForecastAlgo(e.target.value)}
                                          className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-350 text-xs focus:outline-none focus:border-indigo-500"
                                        >
                                          <option value="arima">ARIMA (Autoregressive Integrated Moving Average)</option>
                                          <option value="sarima">SARIMA (Seasonal ARIMA)</option>
                                          <option value="prophet">Prophet (Holt-Winters Fallback)</option>
                                        </select>
                                      </div>

                                      <div>
                                        <label className="block text-xs font-semibold text-slate-400 mb-1.5">Forecast Horizon (steps)</label>
                                        <input
                                          type="number"
                                          value={forecastHorizon}
                                          onChange={(e) => setForecastHorizon(parseInt(e.target.value) || 10)}
                                          className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-350 text-xs focus:outline-none focus:border-indigo-500"
                                        />
                                      </div>

                                      <div>
                                        <label className="block text-xs font-semibold text-slate-400 mb-1.5">Seasonal Period</label>
                                        <input
                                          type="number"
                                          value={forecastSeasonalPeriod}
                                          onChange={(e) => setForecastSeasonalPeriod(parseInt(e.target.value) || 7)}
                                          className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-350 text-xs focus:outline-none focus:border-indigo-500"
                                        />
                                      </div>

                                      <div>
                                        <label className="block text-xs font-semibold text-slate-400 mb-1.5">Confidence Level</label>
                                        <select
                                          value={forecastConfLevel}
                                          onChange={(e) => setForecastConfLevel(parseFloat(e.target.value))}
                                          className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2 px-3 text-slate-350 text-xs focus:outline-none focus:border-indigo-500"
                                        >
                                          <option value="0.95">95% Confidence Interval</option>
                                          <option value="0.90">90% Confidence Interval</option>
                                          <option value="0.80">80% Confidence Interval</option>
                                        </select>
                                      </div>
                                    </div>

                                    <div>
                                      <div className="flex justify-between items-center text-xs text-slate-400 mb-1">
                                        <span>Train / Test Split Ratio: {(forecastTrainRatio * 100).toFixed(0)}% Train</span>
                                        <span>{((1 - forecastTrainRatio) * 100).toFixed(0)}% Test</span>
                                      </div>
                                      <input
                                        type="range"
                                        min="0.5"
                                        max="0.95"
                                        step="0.05"
                                        value={forecastTrainRatio}
                                        onChange={(e) => setForecastTrainRatio(parseFloat(e.target.value))}
                                        className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                                      />
                                    </div>

                                    <button
                                      onClick={runForecastTrain}
                                      disabled={forecastTrainLoading}
                                      className="w-full flex items-center justify-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 px-4 py-2.5 text-xs font-bold text-white transition-colors cursor-pointer border-none"
                                    >
                                      {forecastTrainLoading ? (
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                      ) : (
                                        <TrendingUp className="w-4 h-4" />
                                      )}
                                      Train Forecasting Pipeline
                                    </button>
                                  </div>
                                ) : (
                                  <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-xl font-medium">
                                    Forecasting is not feasible on this dataset due to fatal warnings above.
                                  </div>
                                )}
                              </div>
                            ) : (
                              <div className="bg-slate-950/40 p-12 text-center rounded-xl border border-slate-850 text-slate-500 text-xs">
                                No detection results available. Select active project.
                              </div>
                            )}
                          </div>
                        )}

                        {/* SUB TAB 2: HISTORY */}
                        {forecastSubTab === "history" && (
                          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            {/* Models Registry Sidebar */}
                            <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4 space-y-3 h-[450px] overflow-y-auto">
                              <h4 className="text-xs font-bold text-white uppercase tracking-wider">Models Registry</h4>
                              {forecastModels.length === 0 ? (
                                <div className="text-slate-550 text-xs py-8 text-center">No forecasting models trained yet.</div>
                              ) : (
                                <div className="flex flex-col gap-2">
                                  {forecastModels.map((m: any) => (
                                    <button
                                      key={m._id || m.id}
                                      onClick={() => setActiveForecastModel(m)}
                                      className={`p-3 text-left rounded-lg text-xs transition-all cursor-pointer border ${
                                        (activeForecastModel?._id || activeForecastModel?.id) === (m._id || m.id)
                                          ? "bg-indigo-500/10 border-indigo-500/40 text-indigo-300 font-semibold"
                                          : "bg-slate-950/20 border-slate-850 hover:bg-slate-900 text-slate-400"
                                      }`}
                                    >
                                      <p className="font-bold truncate">{m.targetColumn} Forecast</p>
                                      <p className="text-[10px] text-slate-500 mt-1 uppercase font-mono">
                                        Algo: {m.algorithm} • Horizon: {m.horizon}
                                      </p>
                                    </button>
                                  ))}
                                </div>
                              )}
                            </div>

                            {/* Chart & details view */}
                            <div className="lg:col-span-2 space-y-6">
                              {activeForecastModel ? (
                                <div className="space-y-6 animate-in fade-in duration-200">
                                  {/* Detail & Metrics header */}
                                  <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 space-y-4">
                                    <div>
                                      <h4 className="text-sm font-bold text-white">{activeForecastModel.targetColumn} Forecasting Pipeline</h4>
                                      <p className="text-[10px] text-slate-500 mt-0.5">
                                        Horizon: {activeForecastModel.horizon} steps • Seasonal period: {activeForecastModel.seasonalPeriod}
                                      </p>
                                    </div>

                                    {/* Metrics Grid */}
                                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-2">
                                      <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-850">
                                        <span className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">MAE</span>
                                        <p className="text-sm font-mono font-bold text-white mt-0.5">{activeForecastModel.metrics?.mae?.toFixed(4)}</p>
                                      </div>
                                      <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-850">
                                        <span className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">RMSE</span>
                                        <p className="text-sm font-mono font-bold text-white mt-0.5">{activeForecastModel.metrics?.rmse?.toFixed(4)}</p>
                                      </div>
                                      <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-850">
                                        <span className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">MAPE</span>
                                        <p className="text-sm font-mono font-bold text-white mt-0.5">{activeForecastModel.metrics?.mape?.toFixed(2)}%</p>
                                      </div>
                                      <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-850">
                                        <span className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">SMAPE</span>
                                        <p className="text-sm font-mono font-bold text-white mt-0.5">{activeForecastModel.metrics?.smape?.toFixed(2)}%</p>
                                      </div>
                                    </div>
                                  </div>

                                  {/* Forecast Graph */}
                                  <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 space-y-3">
                                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-sans">Forecast vs Historical Actuals</h4>
                                    {forecastLoadingVisuals ? (
                                      <div className="h-56 flex items-center justify-center text-slate-500 text-xs">
                                        <Loader2 className="w-4 h-4 animate-spin text-indigo-400 mr-2" /> Loading timeline data...
                                      </div>
                                    ) : activeForecastVisuals && activeForecastVisuals.historical ? (
                                      <div className="relative border border-slate-800 bg-slate-950/80 h-72 rounded-xl p-6 flex flex-col justify-between">
                                        <div className="flex-1 relative">
                                          <svg className="w-full h-full overflow-visible">
                                            {/* Confidence region */}
                                            {activeForecastVisuals.forecast && activeForecastVisuals.forecast.length > 0 && (() => {
                                              const hist = activeForecastVisuals.historical;
                                              const fore = activeForecastVisuals.forecast;
                                              const allVals = [
                                                ...hist.map((h: any) => h.value),
                                                ...fore.map((f: any) => f.prediction),
                                                ...fore.map((f: any) => f.lower),
                                                ...fore.map((f: any) => f.upper)
                                              ].filter(v => typeof v === "number" && !isNaN(v));
                                              const minVal = Math.min(...allVals, 0);
                                              const maxVal = Math.max(...allVals, 100);
                                              const diff = maxVal - minVal || 1.0;
                                              const totalPoints = hist.length + fore.length;

                                              const upperPoints = fore.map((f: any, i: number) => {
                                                const idx = hist.length + i;
                                                const x = (idx / (totalPoints - 1)) * 100;
                                                const y = 100 - (((f.upper - minVal) / diff) * 100);
                                                return `${x},${y}`;
                                              });

                                              const lowerPoints = fore.map((f: any, i: number) => {
                                                const idx = hist.length + i;
                                                const x = (idx / (totalPoints - 1)) * 100;
                                                const y = 100 - (((f.lower - minVal) / diff) * 100);
                                                return `${x},${y}`;
                                              });

                                              return (
                                                <path
                                                  d={`M ${upperPoints.map((p: string) => p.replace(',', ' ')).join(' L ')} L ${[...lowerPoints].reverse().map((p: string) => p.replace(',', ' ')).join(' L ')} Z`}
                                                  fill="rgba(99, 102, 241, 0.08)"
                                                  className="transition-all duration-300"
                                                />
                                              );
                                            })()}

                                            {/* Historical path */}
                                            {(() => {
                                              const hist = activeForecastVisuals.historical;
                                              const fore = activeForecastVisuals.forecast || [];
                                              const allVals = [
                                                ...hist.map((h: any) => h.value),
                                                ...fore.map((f: any) => f.prediction)
                                              ].filter(v => typeof v === "number" && !isNaN(v));
                                              const minVal = Math.min(...allVals, 0);
                                              const maxVal = Math.max(...allVals, 100);
                                              const diff = maxVal - minVal || 1.0;
                                              const totalPoints = hist.length + fore.length;

                                              const points = hist.map((h: any, i: number) => {
                                                const x = (i / (totalPoints - 1)) * 100;
                                                const y = 100 - (((h.value - minVal) / diff) * 100);
                                                return `${x},${y}`;
                                              });

                                              return (
                                                <path
                                                  d={`M ${points.map((p: string) => p.replace(',', ' ')).join(' L ')}`}
                                                  fill="none"
                                                  stroke="#94a3b8"
                                                  strokeWidth="2"
                                                  strokeLinecap="round"
                                                />
                                              );
                                            })()}

                                            {/* Forecast path */}
                                            {activeForecastVisuals.forecast && activeForecastVisuals.forecast.length > 0 && (() => {
                                              const hist = activeForecastVisuals.historical;
                                              const fore = activeForecastVisuals.forecast;
                                              const allVals = [
                                                ...hist.map((h: any) => h.value),
                                                ...fore.map((f: any) => f.prediction)
                                              ].filter(v => typeof v === "number" && !isNaN(v));
                                              const minVal = Math.min(...allVals, 0);
                                              const maxVal = Math.max(...allVals, 100);
                                              const diff = maxVal - minVal || 1.0;
                                              const totalPoints = hist.length + fore.length;

                                              const lastHistPt = hist[hist.length - 1];
                                              const startX = ((hist.length - 1) / (totalPoints - 1)) * 100;
                                              const startY = 100 - (((lastHistPt.value - minVal) / diff) * 100);

                                              const forecastPoints = fore.map((f: any, i: number) => {
                                                const idx = hist.length + i;
                                                const x = (idx / (totalPoints - 1)) * 100;
                                                const y = 100 - (((f.prediction - minVal) / diff) * 100);
                                                return `${x},${y}`;
                                              });

                                              return (
                                                <path
                                                  d={`M ${startX} ${startY} L ${forecastPoints.map((p: string) => p.replace(',', ' ')).join(' L ')}`}
                                                  fill="none"
                                                  stroke="#6366f1"
                                                  strokeWidth="2.5"
                                                  strokeDasharray="4 2"
                                                  strokeLinecap="round"
                                                />
                                              );
                                            })()}
                                          </svg>
                                        </div>

                                        <div className="flex justify-between items-center text-[10px] text-slate-500 font-mono mt-4 pt-2 border-t border-slate-900">
                                          <span>Start: {activeForecastVisuals.historical[0]?.date}</span>
                                          <div className="flex gap-4">
                                            <span className="flex items-center gap-1"><span className="w-2.5 h-0.5 bg-slate-400 inline-block"></span> Historical</span>
                                            <span className="flex items-center gap-1"><span className="w-2.5 h-0.5 bg-indigo-500 inline-block"></span> Forecast</span>
                                            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 bg-indigo-500/10 inline-block"></span> Confidence Bands</span>
                                          </div>
                                          <span>End: {activeForecastVisuals.forecast?.[activeForecastVisuals.forecast.length - 1]?.date || activeForecastVisuals.historical[activeForecastVisuals.historical.length - 1]?.date}</span>
                                        </div>
                                      </div>
                                    ) : (
                                      <div className="text-slate-500 text-xs py-8 text-center">No visual coordinates returned.</div>
                                    )}
                                  </div>
                                </div>
                              ) : (
                                <div className="bg-slate-900/20 border border-slate-850 rounded-xl p-12 text-center text-slate-500 text-xs">
                                  Select a trained forecasting pipeline from the registry list to see parameters.
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* SUB TAB 3: EXPLAINABILITY (XAI) */}
                        {forecastSubTab === "explain" && (
                          <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 space-y-6">
                            <div className="flex justify-between items-center border-b border-slate-800/60 pb-4">
                              <div>
                                <h4 className="text-sm font-bold text-white">Explainable AI Workspace</h4>
                                <p className="text-xs text-slate-500 mt-0.5">Inspect global feature importances and local predictions weights using SHAP and LIME.</p>
                              </div>

                              {/* Model selector */}
                              <div className="flex gap-2">
                                <select
                                  value={explainMlModelId}
                                  onChange={(e) => setExplainMlModelId(e.target.value)}
                                  className="rounded-xl border border-slate-800 bg-slate-950 py-1.5 px-3 text-slate-350 text-xs focus:outline-none focus:border-indigo-500"
                                >
                                  <option value="">Select ML Model</option>
                                  {mlModels.map((m: any) => (
                                    <option key={m._id || m.id} value={m._id || m.id}>{m.modelName} ({m.algorithm})</option>
                                  ))}
                                </select>
                              </div>
                            </div>

                            {explainLoading ? (
                              <div className="text-slate-500 text-xs py-12 text-center flex items-center justify-center gap-2">
                                <Loader2 className="w-4 h-4 animate-spin text-indigo-400" /> Computing explanation vectors (SHAP & LIME)...
                              </div>
                            ) : explainData ? (
                              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-in fade-in duration-200">
                                {/* SHAP Summary Plot */}
                                <div className="bg-slate-950/50 p-5 rounded-xl border border-slate-850 space-y-4">
                                  <div>
                                    <h4 className="text-xs font-bold text-white uppercase tracking-wider">SHAP Feature Importance & Summary</h4>
                                    <p className="text-[10px] text-slate-500 mt-0.5">Dotted distribution mapping feature value to positive/negative SHAP output direction.</p>
                                  </div>
                                  <div className="space-y-4">
                                    {explainData.shap.globalImportance.map((item: any) => {
                                      const featurePoints = explainData.shap.summaryScatter.filter((s: any) => s.feature === item.feature);
                                      const shapVals = explainData.shap.summaryScatter.map((s: any) => s.shapValue);
                                      const minShap = Math.min(...shapVals, -0.01);
                                      const maxShap = Math.max(...shapVals, 0.01);
                                      const shapDiff = maxShap - minShap || 1.0;

                                      return (
                                        <div key={item.feature} className="grid grid-cols-4 gap-4 items-center border-b border-slate-900/60 py-3">
                                          <span className="text-xs font-mono text-slate-300 truncate">{item.feature}</span>
                                          <div className="col-span-3 relative h-8 bg-slate-950/60 rounded-lg border border-slate-900 overflow-hidden flex items-center">
                                            {/* Zero center vertical guideline */}
                                            <div 
                                              className="absolute top-0 bottom-0 w-0.5 bg-slate-800"
                                              style={{ left: `${((-minShap) / shapDiff) * 100}%` }}
                                            />
                                            
                                            {/* Plot dots */}
                                            {featurePoints.map((pt: any, i: number) => {
                                              const leftPct = ((pt.shapValue - minShap) / shapDiff) * 100;
                                              const featVals = featurePoints.map((p: any) => p.featureValue);
                                              const minFeat = Math.min(...featVals);
                                              const maxFeat = Math.max(...featVals);
                                              const featDiff = maxFeat - minFeat || 1.0;
                                              const normVal = (pt.featureValue - minFeat) / featDiff;
                                              
                                              // Color interpolation: blue (low) to red (high)
                                              const r = Math.round(59 + normVal * (239 - 59));
                                              const g = Math.round(130 + normVal * (68 - 130));
                                              const b = Math.round(246 - normVal * (246 - 68));
                                              const dotColor = `rgb(${r}, ${g}, ${b})`;
                                              
                                              return (
                                                <div
                                                  key={i}
                                                  className="absolute w-2 h-2 rounded-full cursor-pointer hover:scale-125 transition-transform"
                                                  style={{
                                                    left: `${leftPct}%`,
                                                    backgroundColor: dotColor,
                                                    transform: 'translate(-50%, -50%)',
                                                    top: '50%'
                                                  }}
                                                  title={`SHAP: ${pt.shapValue.toFixed(4)}, Val: ${pt.featureValue.toFixed(2)}`}
                                                />
                                              );
                                            })}
                                          </div>
                                        </div>
                                      );
                                    })}
                                    <div className="flex justify-between items-center text-[9px] text-slate-500 font-mono pt-2">
                                      <span>Negative Impact</span>
                                      <div className="flex gap-2 items-center">
                                        <span className="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block"></span>
                                        <span>Low Value</span>
                                        <span className="w-10 h-1 bg-gradient-to-r from-blue-500 to-red-500 inline-block rounded"></span>
                                        <span>High Value</span>
                                        <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block"></span>
                                      </div>
                                      <span>Positive Impact</span>
                                    </div>
                                  </div>
                                </div>

                                {/* LIME local explainer */}
                                <div className="bg-slate-950/50 p-5 rounded-xl border border-slate-850 space-y-4">
                                  <div className="flex justify-between items-start">
                                    <div>
                                      <h4 className="text-xs font-bold text-white uppercase tracking-wider">LIME Local Feature Contribution</h4>
                                      <p className="text-[10px] text-slate-500 mt-0.5">Explains how individual features contribute to prediction output on row index.</p>
                                    </div>
                                    {/* Row selector */}
                                    <div className="flex items-center gap-1.5">
                                      <span className="text-[10px] text-slate-500 font-semibold">Row Index:</span>
                                      <input
                                        type="number"
                                        min="0"
                                        max="50"
                                        value={explainRowIndex}
                                        onChange={(e) => setExplainRowIndex(parseInt(e.target.value) || 0)}
                                        className="w-12 bg-slate-950 border border-slate-800 rounded px-1.5 py-0.5 text-center text-xs text-white focus:outline-none"
                                      />
                                    </div>
                                  </div>
                                  <div className="space-y-3">
                                    {explainData.lime.map((item: any, idx: number) => {
                                      const isPositive = item.weight >= 0;
                                      const weights = explainData.lime.map((l: any) => Math.abs(l.weight));
                                      const maxW = Math.max(...weights, 0.001);
                                      const absPct = (Math.abs(item.weight) / maxW) * 45; // Max 45% left or right
                                      
                                      return (
                                        <div key={idx} className="grid grid-cols-4 gap-4 items-center py-1">
                                          <span className="text-xs font-mono text-slate-300 truncate">{item.feature}</span>
                                          <div className="col-span-3 relative h-6 flex items-center">
                                            {/* Centered zero line */}
                                            <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-slate-800" />
                                            
                                            {/* Bar */}
                                            <div 
                                              className={`absolute h-4 rounded transition-all duration-300 ${
                                                isPositive ? "bg-emerald-500/80 border border-emerald-500/20" : "bg-rose-500/80 border border-rose-500/20"
                                              }`}
                                              style={{
                                                left: isPositive ? '50%' : 'auto',
                                                right: isPositive ? 'auto' : '50%',
                                                width: `${absPct}%`
                                              }}
                                            />
                                            
                                            {/* Text indicator */}
                                            <span 
                                              className={`absolute text-[10px] font-mono font-semibold ${
                                                isPositive ? "text-emerald-400" : "text-rose-400"
                                              }`}
                                              style={{
                                                left: isPositive ? `calc(50% + ${absPct}% + 6px)` : 'auto',
                                                right: isPositive ? 'auto' : `calc(50% + ${absPct}% + 6px)`
                                              }}
                                            >
                                              {item.weight.toFixed(4)}
                                            </span>
                                          </div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              </div>
                            ) : (
                              <div className="bg-slate-900/20 border border-slate-850 rounded-xl p-12 text-center text-slate-500 text-xs">
                                Select a trained ML model above to generate model explainability analysis.
                              </div>
                            )}
                          </div>
                        )}

                        {/* SUB TAB 4: RECOMMENDATIONS */}
                        {forecastSubTab === "recommendations" && (
                          <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 space-y-6">
                            <div className="flex justify-between items-center border-b border-slate-800/60 pb-4">
                              <div>
                                <h4 className="text-sm font-bold text-white">Business Decisions & Optimization recommendations</h4>
                                <p className="text-xs text-slate-500 mt-0.5">Deterministic recommendations for feature selections and skewness corrections.</p>
                              </div>
                              <select
                                value={explainMlModelId}
                                onChange={(e) => setExplainMlModelId(e.target.value)}
                                className="rounded-xl border border-slate-800 bg-slate-950 py-1.5 px-3 text-slate-350 text-xs focus:outline-none focus:border-indigo-500"
                              >
                                <option value="">Select ML Model</option>
                                {mlModels.map((m: any) => (
                                  <option key={m._id || m.id} value={m._id || m.id}>{m.modelName} ({m.algorithm})</option>
                                ))}
                              </select>
                            </div>

                            {explainLoading ? (
                              <div className="text-slate-500 text-xs py-12 text-center flex items-center justify-center gap-2">
                                <Loader2 className="w-4 h-4 animate-spin text-indigo-400" /> Computing business cards...
                              </div>
                            ) : recommendationData ? (
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-in fade-in duration-200">
                                {recommendationData.recommendations.map((rec: any, idx: number) => {
                                  let cardColor = "border-slate-850 bg-slate-950/20";
                                  let iconColor = "text-indigo-400";
                                  if (rec.category === "multicollinearity") {
                                    cardColor = "border-amber-500/20 bg-amber-500/5";
                                    iconColor = "text-amber-400";
                                  } else if (rec.category === "removal") {
                                    cardColor = "border-rose-500/20 bg-rose-500/5";
                                    iconColor = "text-rose-400";
                                  } else if (rec.category === "strength") {
                                    cardColor = "border-emerald-500/20 bg-emerald-500/5";
                                    iconColor = "text-emerald-400";
                                  }
                                  
                                  return (
                                    <div key={idx} className={`p-5 rounded-xl border flex gap-4 ${cardColor}`}>
                                      <div className={`w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center flex-shrink-0 ${iconColor}`}>
                                        {rec.category === "multicollinearity" ? <ShieldAlert className="w-4 h-4" /> : rec.category === "removal" ? <Trash2 className="w-4 h-4" /> : <Zap className="w-4 h-4" />}
                                      </div>
                                      <div>
                                        <h5 className="text-xs font-bold text-white uppercase tracking-wider">{rec.title}</h5>
                                        <p className="text-xs text-slate-350 mt-1 leading-relaxed">{rec.description}</p>
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            ) : (
                              <div className="bg-slate-900/20 border border-slate-850 rounded-xl p-12 text-center text-slate-500 text-xs">
                                Select a trained ML model above to generate optimization recommendation cards.
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* AI COPILOT WORKSPACE TAB */}
                  {activeTab === "copilot" && (
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 animate-in fade-in duration-200">
                      {/* Left Column: History & settings */}
                      <div className="space-y-4">
                        {/* Conversation sessions */}
                        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4 space-y-3 flex flex-col h-[300px]">
                          <div className="flex justify-between items-center">
                            <h4 className="text-xs font-bold text-white uppercase tracking-wider">Conversations</h4>
                            <button
                              onClick={() => {
                                setActiveConversationId(null);
                                setAiMessages([]);
                              }}
                              className="text-[10px] text-indigo-400 font-bold hover:underline cursor-pointer bg-transparent border-none"
                            >
                              New Chat
                            </button>
                          </div>
                          
                          {/* Search bar */}
                          <input
                            type="text"
                            value={aiSearchQuery}
                            onChange={(e) => setAiSearchQuery(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") loadAiHistory();
                            }}
                            placeholder="Search chats..."
                            className="w-full bg-slate-950 border border-slate-850 rounded-lg py-1.5 px-2.5 text-xs text-slate-350 focus:outline-none focus:border-indigo-500"
                          />

                          <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
                            {aiConversations.length === 0 ? (
                              <div className="text-slate-600 text-[10px] text-center py-6">No conversations found.</div>
                            ) : (
                              aiConversations.map((session) => (
                                <div
                                  key={session._id}
                                  className={`flex justify-between items-center p-2 rounded-lg text-xs transition-all border ${
                                    activeConversationId === session._id
                                      ? "bg-indigo-500/10 border-indigo-500/30 text-indigo-300 font-semibold"
                                      : "bg-slate-950/20 border-slate-850 hover:bg-slate-900 text-slate-400"
                                  }`}
                                >
                                  <button
                                    onClick={() => loadAiMessages(session._id)}
                                    className="flex-1 text-left truncate cursor-pointer bg-transparent border-none text-xs text-slate-300 hover:text-indigo-400 mr-2"
                                  >
                                    {session.previewText}
                                  </button>
                                  <button
                                    onClick={() => deleteAiConversation(session._id)}
                                    className="text-slate-600 hover:text-rose-400 cursor-pointer bg-transparent border-none p-0.5"
                                  >
                                    <Trash2 className="w-3.5 h-3.5" />
                                  </button>
                                </div>
                              ))
                            )}
                          </div>
                        </div>

                        {/* Settings & Configs */}
                        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4 space-y-4 text-xs">
                          <h4 className="text-xs font-bold text-white uppercase tracking-wider">Copilot Config</h4>
                          
                          <div>
                            <label className="block text-[10px] font-semibold text-slate-500 mb-1">AI Provider</label>
                            <select
                              value={aiProvider}
                              onChange={(e) => setAiProvider(e.target.value)}
                              className="w-full bg-slate-950 border border-slate-800 rounded-lg py-1 px-2 text-slate-300 text-xs focus:outline-none"
                            >
                              <option value="mock">Mock Offline Engine</option>
                              <option value="gemini">Google Gemini API</option>
                            </select>
                          </div>

                          <div>
                            <label className="block text-[10px] font-semibold text-slate-500 mb-1">Model Name</label>
                            <select
                              value={aiModel}
                              onChange={(e) => setAiModel(e.target.value)}
                              className="w-full bg-slate-950 border border-slate-800 rounded-lg py-1 px-2 text-slate-300 text-xs focus:outline-none"
                            >
                              <option value="gemini-2.5-flash">gemini-2.5-flash</option>
                              <option value="gemini-2.5-pro">gemini-2.5-pro</option>
                            </select>
                          </div>

                          <div>
                            <div className="flex justify-between items-center text-[10px] text-slate-550 mb-0.5">
                              <span>Temperature</span>
                              <span>{aiTemperature.toFixed(2)}</span>
                            </div>
                            <input
                              type="range"
                              min="0"
                              max="1"
                              step="0.1"
                              value={aiTemperature}
                              onChange={(e) => setAiTemperature(parseFloat(e.target.value))}
                              className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                            />
                          </div>

                          <div>
                            <label className="block text-[10px] font-semibold text-slate-500 mb-1">Max Response Tokens</label>
                            <input
                              type="number"
                              value={aiMaxTokens}
                              onChange={(e) => setAiMaxTokens(parseInt(e.target.value) || 1024)}
                              className="w-full bg-slate-950 border border-slate-800 rounded-lg py-1 px-2 text-slate-300 text-xs focus:outline-none"
                            />
                          </div>
                        </div>
                      </div>

                      {/* Right Column: AI tabs */}
                      <div className="lg:col-span-3 space-y-6">
                        {/* Sub tab navigation */}
                        <div className="border-b border-slate-800 flex gap-2">
                          <button
                            onClick={() => setAiSubTab("chat")}
                            className={`px-4 py-2 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                              aiSubTab === "chat"
                                ? "border-indigo-500 text-indigo-400 font-bold"
                                : "border-transparent text-slate-400 hover:text-slate-200"
                            }`}
                          >
                            Chat Copilot
                          </button>
                          <button
                            onClick={() => setAiSubTab("report")}
                            className={`px-4 py-2 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                              aiSubTab === "report"
                                ? "border-indigo-500 text-indigo-400 font-bold"
                                : "border-transparent text-slate-400 hover:text-slate-200"
                            }`}
                          >
                            Executive Reports
                          </button>
                          <button
                            onClick={() => setAiSubTab("recommendations")}
                            className={`px-4 py-2 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                              aiSubTab === "recommendations"
                                ? "border-indigo-500 text-indigo-400 font-bold"
                                : "border-transparent text-slate-400 hover:text-slate-200"
                            }`}
                          >
                            Intelligent recommendations
                          </button>
                        </div>

                        {aiError && (
                          <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-xl flex items-start gap-2">
                            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                            <div>
                              <p className="font-bold">AI Execution Error</p>
                              <p className="mt-0.5">{aiError}</p>
                            </div>
                          </div>
                        )}

                        {/* CHAT INTERFACE */}
                        {aiSubTab === "chat" && (
                          <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 space-y-4 flex flex-col h-[520px]">
                            {/* Message Thread */}
                            <div className="flex-1 overflow-y-auto space-y-4 pr-1">
                              {aiMessages.length === 0 ? (
                                <div className="h-full flex flex-col items-center justify-center text-center p-8 space-y-6">
                                  <div>
                                    <h4 className="text-sm font-bold text-white">Ask anything about your workspace data</h4>
                                    <p className="text-xs text-slate-500 mt-1 max-w-sm">I have access to dataset health, variables catalog, statistical correlations, and trained model metrics.</p>
                                  </div>
                                  
                                  {/* Prompt Shortcuts Library */}
                                  <div className="grid grid-cols-2 gap-3 max-w-lg w-full">
                                    <button
                                      onClick={() => sendAiChatMessage("Summarize my dataset details")}
                                      className="p-3 border border-slate-850 bg-slate-950/40 rounded-xl text-left text-xs text-slate-300 hover:border-indigo-500/40 hover:text-indigo-400 cursor-pointer transition-all"
                                    >
                                      📊 Summarize dataset
                                    </button>
                                    <button
                                      onClick={() => sendAiChatMessage("Which machine learning model performs best in this workspace?")}
                                      className="p-3 border border-slate-855 bg-slate-950/40 rounded-xl text-left text-xs text-slate-300 hover:border-indigo-500/40 hover:text-indigo-400 cursor-pointer transition-all"
                                    >
                                      🏆 Compare model performance
                                    </button>
                                    <button
                                      onClick={() => sendAiChatMessage("Explain the feature engineering opportunities or outliers recommendations")}
                                      className="p-3 border border-slate-855 bg-slate-950/40 rounded-xl text-left text-xs text-slate-300 hover:border-indigo-500/40 hover:text-indigo-400 cursor-pointer transition-all"
                                    >
                                      💡 Suggest feature engineering
                                    </button>
                                    <button
                                      onClick={() => sendAiChatMessage("Explain the model SHAP feature importance variables")}
                                      className="p-3 border border-slate-855 bg-slate-950/40 rounded-xl text-left text-xs text-slate-300 hover:border-indigo-500/40 hover:text-indigo-400 cursor-pointer transition-all"
                                    >
                                      🔍 Explain SHAP interpretations
                                    </button>
                                  </div>
                                </div>
                              ) : (
                                aiMessages.map((msg, idx) => {
                                  const isUser = msg.role === "user";
                                  return (
                                    <div key={idx} className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
                                      <div className={`p-4 rounded-2xl max-w-xl text-xs leading-relaxed ${
                                        isUser 
                                          ? "bg-slate-950 text-white border border-slate-850" 
                                          : "bg-indigo-950/30 text-slate-300 border border-indigo-500/10"
                                      }`}>
                                        <div className="flex justify-between items-center mb-1 text-[9px] text-slate-500">
                                          <span className="font-bold uppercase tracking-wider">{isUser ? "You" : "Antigravity AI Copilot"}</span>
                                        </div>
                                        <p className="whitespace-pre-line">{msg.content}</p>
                                      </div>
                                    </div>
                                  );
                                })
                              )}
                              
                              {aiLoading && (
                                <div className="flex justify-start">
                                  <div className="p-4 rounded-2xl bg-indigo-950/10 text-slate-550 text-xs border border-slate-850 flex items-center gap-2">
                                    <Loader2 className="w-4 h-4 animate-spin text-indigo-400" /> Copilot is reasoning...
                                  </div>
                                </div>
                              )}
                            </div>

                            {/* Chat Input form */}
                            <form 
                              onSubmit={(e) => {
                                e.preventDefault();
                                sendAiChatMessage();
                              }}
                              className="border-t border-slate-850/60 pt-3 flex gap-3"
                            >
                              <input
                                type="text"
                                value={aiMessageInput}
                                onChange={(e) => setAiMessageInput(e.target.value)}
                                placeholder="Ask Copilot e.g., Which features are highly correlated?"
                                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl py-2.5 px-4 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                              />
                              <button
                                type="submit"
                                disabled={aiLoading || !aiMessageInput.trim()}
                                className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-850 text-xs font-bold text-white transition-colors cursor-pointer border-none"
                              >
                                Send
                              </button>
                            </form>
                          </div>
                        )}

                        {/* REPORTS GENERATOR */}
                        {aiSubTab === "report" && (
                          <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 space-y-6">
                            <div className="flex justify-between items-center">
                              <div>
                                <h4 className="text-sm font-bold text-white">Executive Report Generator</h4>
                                <p className="text-xs text-slate-500 mt-0.5">Generate a professional, publication-quality executive summary.</p>
                              </div>
                              
                              <div className="flex items-center gap-3">
                                <select
                                  value={aiReportFormat}
                                  onChange={(e: any) => setAiReportFormat(e.target.value)}
                                  className="bg-slate-950 border border-slate-800 rounded-xl py-1.5 px-3 text-slate-350 text-xs focus:outline-none"
                                >
                                  <option value="markdown">Markdown Layout</option>
                                  <option value="html">Styled HTML</option>
                                  <option value="pdf">Print Ready PDF Format</option>
                                </select>
                                
                                <button
                                  onClick={generateAiReport}
                                  disabled={aiReportLoading}
                                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-850 rounded-xl text-xs font-bold text-white cursor-pointer transition-colors border-none"
                                >
                                  {aiReportLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5 inline-block" /> : null}
                                  Generate Report
                                </button>
                              </div>
                            </div>

                            {aiReportLoading ? (
                              <div className="py-24 text-center text-slate-500 text-xs">
                                <Loader2 className="w-6 h-6 animate-spin text-indigo-400 mx-auto mb-3" />
                                Compiling statistical parameters and ML results into document...
                              </div>
                            ) : aiReportResult ? (
                              <div className="space-y-4 animate-in fade-in duration-200">
                                <div className="flex justify-end gap-2">
                                  <button
                                    onClick={() => {
                                      navigator.clipboard.writeText(aiReportResult);
                                      alert("Copied report contents to clipboard!");
                                    }}
                                    className="px-3 py-1.5 border border-slate-700 hover:bg-slate-800 rounded-lg text-[10px] font-semibold text-slate-300 cursor-pointer"
                                  >
                                    Copy Contents
                                  </button>
                                  <a
                                    href={`data:text/plain;charset=utf-8,${encodeURIComponent(aiReportResult)}`}
                                    download={aiReportFormat === "markdown" ? "executive_report.md" : "executive_report.html"}
                                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-[10px] font-semibold text-slate-300 cursor-pointer"
                                  >
                                    Download File
                                  </a>
                                </div>

                                <div className="border border-slate-800 bg-slate-950/80 rounded-xl p-6 max-h-[400px] overflow-y-auto">
                                  {aiReportFormat === "markdown" ? (
                                    <pre className="text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed">
                                      {aiReportResult}
                                    </pre>
                                  ) : (
                                    <iframe 
                                      srcDoc={aiReportResult} 
                                      className="w-full h-[350px] border-none bg-slate-950" 
                                    />
                                  )}
                                </div>
                              </div>
                            ) : (
                              <div className="bg-slate-950/40 p-12 text-center rounded-xl border border-slate-850 text-slate-500 text-xs">
                                Click "Generate Report" above to build the executive workspace summary document.
                              </div>
                            )}
                          </div>
                        )}

                        {/* RECOMMENDATIONS CARDS */}
                        {aiSubTab === "recommendations" && (
                          <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 space-y-6">
                            <div>
                              <h4 className="text-sm font-bold text-white">Evidence-Based Optimization suggestions</h4>
                              <p className="text-xs text-slate-500 mt-0.5">Recommendations constructed directly by querying data quality scores, correlations and SHAP results.</p>
                            </div>

                            {aiRecommendationsLoading ? (
                              <div className="text-slate-500 text-xs py-12 text-center flex items-center justify-center gap-2">
                                <Loader2 className="w-4 h-4 animate-spin text-indigo-400" /> Fetching pipeline recommendations...
                              </div>
                            ) : aiRecommendationCards.length > 0 ? (
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-in fade-in duration-200">
                                {aiRecommendationCards.map((card, idx) => (
                                  <div key={idx} className="p-5 rounded-xl border border-slate-850 bg-slate-950/40 flex flex-col justify-between space-y-3">
                                    <div className="space-y-2">
                                      <div className="flex justify-between items-start">
                                        <span className="text-[9px] font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded uppercase tracking-wider">
                                          {card.category}
                                        </span>
                                        <span className="text-[10px] font-mono text-slate-500">
                                          {(card.confidence * 100).toFixed(0)}% Confidence
                                        </span>
                                      </div>
                                      <h5 className="text-xs font-bold text-white uppercase tracking-wider">{card.title}</h5>
                                      <p className="text-xs text-slate-350 leading-relaxed">{card.description}</p>
                                    </div>
                                    
                                    <div className="pt-3 border-t border-slate-900 text-[10px] font-mono text-slate-500 flex justify-between">
                                      <span>Evidence:</span>
                                      <span className="text-indigo-300 font-bold">{card.evidence}</span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div className="bg-slate-950/40 p-12 text-center rounded-xl border border-slate-850 text-slate-500 text-xs">
                                No recommendations found.
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Bottom status alert bar */}
                <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/5 p-5 flex items-center justify-between">
                  <div className="flex gap-3 items-center">
                    <CheckCircle className="text-indigo-400 w-5 h-5" />
                    <div>
                      <p className="text-sm font-semibold text-indigo-400">Dataset Loaded Successfully</p>
                      <p className="text-xs text-slate-400 mt-0.5">Parsed column schemas and health checks are ready for modeling.</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => setDataset(null)}
                    className="px-3.5 py-1.5 rounded-lg border border-slate-700 text-xs font-semibold text-slate-300 hover:bg-slate-800 cursor-pointer transition-colors"
                  >
                    Replace File
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
            <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 mb-4">
              <FolderPlus className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white">No active workspace</h3>
            <p className="text-slate-500 text-sm mt-1 max-w-sm">
              Create a workspace or select an existing one from the sidebar to ingest datasets.
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="mt-6 flex items-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 px-4 py-2.5 text-sm font-semibold text-white transition-all cursor-pointer"
            >
              <Plus className="w-4 h-4" /> Create Workspace
            </button>
          </div>
        )}
      </main>

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 relative">
            <h3 className="text-lg font-bold text-white mb-2">Create Workspace</h3>
            <p className="text-slate-400 text-sm mb-6">Setup a workspace to isolate your data models and analytics.</p>
            
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">Workspace Name</label>
                <input
                  type="text"
                  required
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="e.g. Sales Forecast 2026"
                  className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2.5 px-3 text-slate-200 placeholder-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">Description (Optional)</label>
                <textarea
                  value={newProjectDesc}
                  onChange={(e) => setNewProjectDesc(e.target.value)}
                  placeholder="Describe the goals of this workspace..."
                  className="block w-full rounded-xl border border-slate-800 bg-slate-950 py-2.5 px-3 text-slate-200 placeholder-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:text-sm h-24 resize-none"
                />
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-slate-200 border border-slate-800 bg-transparent hover:bg-slate-800/30 text-sm font-medium cursor-pointer transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold cursor-pointer transition-colors"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
