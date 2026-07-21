import { API_BASE_URL } from "@/lib/config";
import type {
  AdminStats,
  ChatResponse,
  Conversation,
  DatabaseDocument,
  DocumentSummary,
  Organization,
  ServiceCard,
  SourceFile,
  UserRecord
} from "@/types/document";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Erreur API ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  documents: () => request<DocumentSummary[]>("/documents", { cache: "no-store" }),
  databaseDocuments: () => request<DatabaseDocument[]>("/db/documents", { cache: "no-store" }),
  sourceFiles: () => request<SourceFile[]>("/source-files", { cache: "no-store" }),
  organizations: () => request<Organization[]>("/organizations", { cache: "no-store" }),
  serviceCards: () => request<ServiceCard[]>("/service-cards", { cache: "no-store" }),
  users: () => request<UserRecord[]>("/users", { cache: "no-store" }),
  conversations: () => request<Conversation[]>("/conversations", { cache: "no-store" }),
  stats: () => request<AdminStats>("/admin/stats", { cache: "no-store" }),
  index: () => request<Array<Record<string, unknown>>>("/index", { method: "POST" }),
  chat: (question: string, document?: string, conversationId?: string | null) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify({ question, ...(document ? { document } : {}), ...(conversationId ? { conversation_id: conversationId } : {}) })
    }),
  pdfUrl: (documentId: string) => `${API_BASE_URL}/documents/${encodeURIComponent(documentId)}/file`
};
