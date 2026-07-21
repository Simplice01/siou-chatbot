export type DocumentSummary = {
  id: string;
  name: string;
  size_bytes: number;
  modified_at: number;
  indexed: boolean;
  page_count: number | null;
  chunk_count: number | null;
};

export type ChatSource = {
  document: string;
  page: number;
  chunk_id: string;
  score: number;
  citation: string;
};

export type ChatResponse = {
  answer: string;
  confidence: number;
  sources: ChatSource[];
  pages: number[];
  citation: string | null;
  conversation_id: string | null;
  message_id: string | null;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  confidence?: number;
  sources?: ChatSource[];
};

export type DatabaseDocument = {
  id: string;
  source_file_id: string | null;
  organization_id: string | null;
  title: string;
  type: string;
  status: string;
  summary: string | null;
  created_at: string;
  updated_at: string;
};

export type SourceFile = {
  id: string;
  original_filename: string;
  kind: string;
  mime_type: string | null;
  file_size_bytes: number | null;
  page_count: number | null;
  collected_at: string;
};

export type Organization = {
  id: string;
  name: string;
  acronym: string | null;
  type: string;
  description: string | null;
  email: string | null;
  phone: string | null;
  website: string | null;
  is_active: boolean;
};

export type ServiceCard = {
  id: string;
  organization_id: string;
  source_document_id: string | null;
  title: string;
  public_name: string | null;
  target_users: string | null;
  orientation_summary: string;
  procedure_summary: string | null;
  status: string;
};

export type UserRecord = {
  id: string;
  organization_id: string | null;
  email: string | null;
  full_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
};

export type Conversation = {
  id: string;
  user_id: string | null;
  channel: string;
  title: string | null;
  created_at: string;
  updated_at: string;
};

export type AdminStats = {
  users: number;
  documents: number;
  document_chunks: number;
  organizations: number;
  service_cards: number;
  conversations: number;
  messages: number;
};
