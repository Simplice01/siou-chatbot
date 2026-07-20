"use client";

import { motion } from "framer-motion";
import { ArrowUp, Bot, User } from "lucide-react";
import { FormEvent, useState } from "react";
import { formatConfidence } from "@/lib/format";
import { api } from "@/services/api";
import type { ChatMessage, ChatSource, DocumentSummary } from "@/types/document";

type Props = {
  document: DocumentSummary | null;
  onSourceClick: (page: number) => void;
};

export function AiPanel({ document, onSourceClick }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const canAsk = Boolean(document?.indexed && question.trim());

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!document || !canAsk) return;
    const current = question.trim();
    setQuestion("");
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", content: current };
    setMessages((items) => [...items, userMessage]);
    setLoading(true);
    try {
      const response = await api.chat(document.id, current);
      setMessages((items) => [
        ...items,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.answer,
          confidence: response.confidence,
          sources: response.sources
        }
      ]);
    } catch (err) {
      setMessages((items) => [
        ...items,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: err instanceof Error ? err.message : "Erreur pendant la génération."
        }
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <aside className="flex min-h-0 flex-col border-l border-sage bg-paper">
      <div className="border-b border-sage p-4">
        <div className="flex items-center gap-2">
          <Bot className="text-moss" size={18} aria-hidden />
          <h2 className="text-sm font-semibold text-ink">Panneau IA</h2>
        </div>
        <p className="mt-1 text-xs text-graphite/65">{document ? "Réponses limitées au document ouvert" : "Ouvre un PDF pour commencer"}</p>
      </div>
      <div className="thin-scrollbar min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="rounded-md border border-sage bg-mist p-4 text-sm text-graphite/75">
            Pose une question précise. Si la réponse n’est pas dans le PDF, l’IA doit le dire clairement.
          </div>
        )}
        {messages.map((message) => (
          <motion.div key={message.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-2">
            <div className="flex items-start gap-2">
              <div className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-md bg-mist text-graphite">
                {message.role === "user" ? <User size={15} aria-hidden /> : <Bot size={15} aria-hidden />}
              </div>
              <div className="min-w-0 flex-1">
                <p className="whitespace-pre-wrap text-sm leading-6 text-ink">{message.content}</p>
                {typeof message.confidence === "number" && (
                  <p className="mt-2 text-xs font-medium text-moss">Confiance {formatConfidence(message.confidence)}</p>
                )}
              </div>
            </div>
            {message.sources && message.sources.length > 0 && <Sources sources={message.sources} onSourceClick={onSourceClick} />}
          </motion.div>
        ))}
        {loading && <p className="text-sm text-graphite/65">Analyse du document...</p>}
      </div>
      <form onSubmit={submit} className="border-t border-sage p-4">
        <div className="flex gap-2">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder={document?.indexed ? "Interroger ce PDF" : "Document non indexé"}
            rows={2}
            className="min-h-12 flex-1 resize-none rounded-md border-sage bg-mist text-sm focus:border-moss focus:ring-moss"
          />
          <button
            type="submit"
            disabled={!canAsk || loading}
            className="grid h-12 w-12 shrink-0 place-items-center rounded-md bg-moss text-paper transition hover:bg-ocean disabled:cursor-not-allowed disabled:opacity-45"
            title="Envoyer"
          >
            <ArrowUp size={18} aria-hidden />
          </button>
        </div>
      </form>
    </aside>
  );
}

function Sources({ sources, onSourceClick }: { sources: ChatSource[]; onSourceClick: (page: number) => void }) {
  return (
    <div className="ml-9 space-y-2">
      {sources.slice(0, 4).map((source) => (
        <button
          key={source.chunk_id}
          type="button"
          onClick={() => onSourceClick(source.page)}
          className="w-full rounded-md border border-sage bg-mist p-3 text-left transition hover:border-moss"
        >
          <div className="mb-1 flex items-center justify-between gap-2">
            <span className="text-xs font-semibold text-moss">Page {source.page}</span>
            <span className="text-xs text-graphite/60">{formatConfidence(source.score)}</span>
          </div>
          <p className="line-clamp-3 text-xs leading-5 text-graphite/80">{source.citation}</p>
        </button>
      ))}
    </div>
  );
}

