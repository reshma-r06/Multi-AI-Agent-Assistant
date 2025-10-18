export enum AgentType {
  RESEARCH = 'research',
  ANALYSIS = 'analysis',
  SUMMARY = 'summary',
  REPORT = 'report'
}

export enum TaskStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system',
  AGENT = 'agent'
}

export interface ChatMessage {
  role: MessageRole;
  content: string;
  agent_type?: AgentType;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface AgentResponse {
  agent_type: AgentType;
  content: string;
  status: TaskStatus;
  execution_time: number;
  sources?: string[];
  metadata?: Record<string, any>;
}

export interface TaskResponse {
  task_id: string;
  status: TaskStatus;
  messages: ChatMessage[];
  agent_responses: AgentResponse[];
  final_answer?: string;
  report_url?: string;
  created_at: string;
  completed_at?: string;
}

export interface QueryRequest {
  query: string;
  session_id?: string;
  include_web_search: boolean;
  use_uploaded_docs: boolean;
  generate_report: boolean;
}

export interface FileUploadResponse {
  filename: string;
  file_id: string;
  size: number;
  content_type: string;
  processed: boolean;
  chunks_created?: number;
}