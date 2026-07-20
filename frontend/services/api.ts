import { API_BASE_URL } from "@/lib/config";
import type { ChatResponse, DocumentSummary } from "@/types/document";

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
  index: () => request<Array<Record<string, unknown>>>("/index", { method: "POST" }),
  chat: (question: string, document?: string) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify({ question, ...(document ? { document } : {}) })
    }),
  pdfUrl: (documentId: string) => `${API_BASE_URL}/documents/${encodeURIComponent(documentId)}/file`
};
