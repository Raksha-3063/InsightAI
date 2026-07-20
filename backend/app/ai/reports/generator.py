from typing import Dict, Any
from app.ai.providers.gemini import call_gemini_api
from app.ai.prompts.templates import COPILOT_SYSTEM_INSTRUCTION, format_report_generation_prompt

def generate_report_markdown(context: Dict[str, Any]) -> str:
    """
    Generate an AI Executive Report in Markdown format using the LLM context.
    """
    prompt = format_report_generation_prompt(context)
    report_text = call_gemini_api(prompt, system_instruction=COPILOT_SYSTEM_INSTRUCTION)
    return report_text

def convert_md_to_html(markdown_text: str, project_name: str) -> str:
    """
    A basic, lightweight Markdown-to-HTML formatter with beautiful Tailwind styles for report viewing.
    """
    html_lines = []
    lines = markdown_text.split("\n")
    
    # Styles header
    html_lines.append(
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        "<meta charset='utf-8'>\n"
        f"<title>Executive Report - {project_name}</title>\n"
        "<script src='https://cdn.tailwindcss.com'></script>\n"
        "</head>\n"
        "<body class='bg-slate-950 text-slate-100 p-8 max-w-4xl mx-auto space-y-6 font-sans'>\n"
        f"<div class='border-b border-slate-800 pb-6 mb-8'>"
        f"<span class='text-[10px] text-indigo-400 font-bold uppercase tracking-wider'>InsightAI Executive Report</span>"
        f"<h1 class='text-3xl font-extrabold text-white mt-2'>{project_name}</h1>"
        f"<p class='text-xs text-slate-500 mt-1'>Generated automatically on demand by Enterprise Analytics Copilot</p>"
        f"</div>"
    )
    
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue
            
        # Headers
        if stripped.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h4 class='text-md font-bold text-indigo-300 mt-6 mb-2'>{stripped[4:]}</h4>")
        elif stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3 class='text-lg font-bold text-white mt-8 mb-3 border-b border-slate-900 pb-1'>{stripped[3:]}</h3>")
        elif stripped.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2 class='text-2xl font-black text-white mt-10 mb-4'>{stripped[2:]}</h2>")
            
        # Lists
        elif stripped.startswith("* ") or stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul class='list-disc pl-6 space-y-1.5 text-slate-300 text-sm'>")
                in_list = True
            content = stripped[2:]
            # Bold highlights
            if "**" in content:
                parts = content.split("**")
                for i in range(1, len(parts), 2):
                    parts[i] = f"<strong class='text-white font-bold'>{parts[i]}</strong>"
                content = "".join(parts)
            html_lines.append(f"<li>{content}</li>")
            
        # Standard paragraphs
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            content = stripped
            if "**" in content:
                parts = content.split("**")
                for i in range(1, len(parts), 2):
                    parts[i] = f"<strong class='text-white font-bold'>{parts[i]}</strong>"
                content = "".join(parts)
            html_lines.append(f"<p class='text-slate-300 text-sm leading-relaxed mb-4'>{content}</p>")
            
    if in_list:
        html_lines.append("</ul>")
        
    html_lines.append("</body>\n</html>")
    return "\n".join(html_lines)
