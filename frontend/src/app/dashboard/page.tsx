"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import api from "@/services/api";
import { 
  FolderPlus, Folder, LogOut, User, Plus, UploadCloud, 
  FileSpreadsheet, FileText, CheckCircle, Database, AlertCircle, 
  TrendingUp, TableProperties, Binary, Calendar, Eye, Loader2
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

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Redirect if not logged in
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  // Fetch projects on mount
  useEffect(() => {
    if (user) {
      fetchProjects();
    }
  }, [user]);

  // Fetch dataset when active project changes
  useEffect(() => {
    if (activeProject) {
      fetchDataset(activeProject._id);
    } else {
      setDataset(null);
    }
  }, [activeProject]);

  const fetchProjects = async () => {
    try {
      const res = await api.get("/projects");
      setProjects(res.data);
      if (res.data.length > 0 && !activeProject) {
        setActiveProject(res.data[0]);
      }
    } catch (err) {
      console.error("Failed to load projects:", err);
    }
  };

  const fetchDataset = async (projectId: string) => {
    try {
      setError(null);
      const res = await api.get(`/projects/${projectId}/datasets`);
      setDataset(res.data);
    } catch (err: any) {
      if (err.response?.status !== 404) {
        console.error("Failed to fetch dataset:", err);
        setError("Failed to load dataset details.");
      } else {
        setDataset(null);
      }
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;

    try {
      const res = await api.post("/projects", {
        projectName: newProjectName,
        description: newProjectDesc
      });
      setProjects([...projects, res.data]);
      setActiveProject(res.data);
      setShowCreateModal(false);
      setNewProjectName("");
      setNewProjectDesc("");
    } catch (err) {
      console.error("Failed to create project:", err);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await handleFileUpload(e.target.files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
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
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Failed to process dataset. Please check file format."
      );
    } finally {
      setUploadLoading(false);
    }
  };

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
      <aside className="w-80 bg-slate-900 border-r border-slate-800 flex flex-col justify-between z-10">
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
                  onClick={() => setActiveProject(proj)}
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
            </div>

            {error && (
              <div className="rounded-xl bg-rose-500/10 border border-rose-500/20 p-4 text-sm text-rose-400 flex gap-3 items-center">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Content Switcher: Upload OR Overview */}
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
                {/* Meta Statistics Grid */}
                <div>
                  <h3 className="text-lg font-semibold text-slate-300 mb-4 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-indigo-400" />
                    Dataset Health Summary
                  </h3>
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
                    {/* Missing values */}
                    <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5">
                      <p className="text-xs text-slate-500 font-medium">Missing Cells</p>
                      <p className={`text-2xl font-bold mt-1 ${dataset.missingValues > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                        {dataset.missingValues.toLocaleString()}
                      </p>
                    </div>
                    {/* Duplicates */}
                    <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5">
                      <p className="text-xs text-slate-500 font-medium">Duplicates</p>
                      <p className={`text-2xl font-bold mt-1 ${dataset.duplicateRows > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                        {dataset.duplicateRows.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Columns Catalog */}
                <div>
                  <h3 className="text-lg font-semibold text-slate-300 mb-4 flex items-center gap-2">
                    <TableProperties className="w-4 h-4 text-indigo-400" />
                    Schema Columns
                  </h3>
                  <div className="bg-slate-900/40 border border-slate-800 rounded-xl overflow-hidden">
                    <table className="w-full text-left text-sm text-slate-300">
                      <thead className="bg-slate-900/80 text-xs font-semibold text-slate-400 uppercase border-b border-slate-800">
                        <tr>
                          <th className="px-6 py-3.5">Column Name</th>
                          <th className="px-6 py-3.5">Type</th>
                          <th className="px-6 py-3.5">Categorization</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {Object.entries(dataset.columnTypes).map(([colName, type]) => (
                          <tr key={colName} className="hover:bg-slate-800/10">
                            <td className="px-6 py-4 font-mono text-slate-200">{colName}</td>
                            <td className="px-6 py-4 text-slate-400 capitalize">{type}</td>
                            <td className="px-6 py-4">
                              <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                                type === "numerical" 
                                  ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-400"
                                  : type === "datetime"
                                  ? "bg-amber-500/10 border-amber-500/20 text-amber-400"
                                  : "bg-purple-500/10 border-purple-500/20 text-purple-400"
                              }`}>
                                {type === "numerical" && <Binary className="w-3 h-3" />}
                                {type === "datetime" && <Calendar className="w-3 h-3" />}
                                {type === "categorical" && <FileText className="w-3 h-3" />}
                                {type}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Upload Success Alert */}
                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-5 flex items-center justify-between">
                  <div className="flex gap-3 items-center">
                    <CheckCircle className="text-emerald-400 w-5 h-5" />
                    <div>
                      <p className="text-sm font-semibold text-emerald-400">Dataset Loaded Successfully</p>
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
