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
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  confidence?: number;
  sources?: ChatSource[];
};

