'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { TaskResponse, QueryRequest, FileUploadResponse } from '@/types';
import MessageList from './MessageList';
import InputBox from './InputBox';
import AgentStatus from './AgentStatus';
import FileUpload from './FileUpload';
import { Loader2, FileText, Download } from 'lucide-react';

export default function ChatInterface() {
  const [task, setTask] = useState<TaskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<FileUploadResponse[]>([]);
  
  // Settings
  const [useWebSearch, setUseWebSearch] = useState(true);
  const [useUploadedDocs, setUseUploadedDocs] = useState(false);
  const [generateReport, setGenerateReport] = useState(false);

  const handleQuery = async (query: string) => {
    setLoading(true);
    setError(null);

    try {
      const request: QueryRequest = {
        query,
        include_web_search: useWebSearch,
        use_uploaded_docs: useUploadedDocs && uploadedFiles.length > 0,
        generate_report: generateReport,
      };

      const response = await api.processQuery(request);
      setTask(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred');
      console.error('Error processing query:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    try {
      const response = await api.uploadFile(file);
      setUploadedFiles(prev => [...prev, response]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'File upload failed');
      console.error('Error uploading file:', err);
    }
  };

  const handleDownloadReport = async () => {
    if (!task?.task_id) return;
    
    try {
      const response = await api.generateReport(task.task_id, 'pdf');
      window.open(response.report_url, '_blank');
    } catch (err: any) {
      setError('Failed to generate report');
      console.error('Error generating report:', err);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">
            Multi-Agent AI Assistant
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Startup Knowledge & Research Platform
          </p>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden flex">
        <div className="flex-1 flex flex-col max-w-6xl mx-auto w-full">
          {/* Settings Bar */}
          <div className="bg-white border-b border-gray-200 px-6 py-3">
            <div className="flex items-center gap-4 text-sm">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useWebSearch}
                  onChange={(e) => setUseWebSearch(e.target.checked)}
                  className="rounded border-gray-300"
                />
                <span>Web Search</span>
              </label>
              
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useUploadedDocs}
                  onChange={(e) => setUseUploadedDocs(e.target.checked)}
                  className="rounded border-gray-300"
                  disabled={uploadedFiles.length === 0}
                />
                <span>Use Uploaded Docs ({uploadedFiles.length})</span>
              </label>
              
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={generateReport}
                  onChange={(e) => setGenerateReport(e.target.checked)}
                  className="rounded border-gray-300"
                />
                <span>Generate Report</span>
              </label>

              <div className="ml-auto">
                <FileUpload onFileUpload={handleFileUpload} />
              </div>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            {task ? (
              <div className="space-y-6">
                <AgentStatus agentResponses={task.agent_responses} />
                <MessageList messages={task.messages} />
                
                {task.report_url && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <FileText className="w-5 h-5 text-blue-600" />
                        <span className="font-medium text-blue-900">
                          Report Generated
                        </span>
                      </div>
                      <button
                        onClick={handleDownloadReport}
                        className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        <Download className="w-4 h-4" />
                        Download PDF
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <h2 className="text-xl font-semibold mb-2">
                    Welcome to Multi-Agent AI Assistant
                  </h2>
                  <p className="text-sm">
                    Ask anything about market research, competitors, or funding guidance
                  </p>
                </div>
              </div>
            )}

            {loading && (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                {error}
              </div>
            )}
          </div>

          {/* Input Box */}
          <div className="border-t border-gray-200 bg-white px-6 py-4">
            <InputBox onSubmit={handleQuery} disabled={loading} />
          </div>
        </div>
      </div>
    </div>
  );
}