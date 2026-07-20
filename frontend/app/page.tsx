"use client";

import { motion } from "framer-motion";
import { ArrowUp, Bot, FileText, Loader2, MessageSquarePlus, RefreshCw, User } from "lucide-react";
import { FormEvent, useEffect, useRef, useState } from "react";
import { formatConfidence } from "@/lib/format";
import { api } from "@/services/api";
import type { ChatMessage, ChatSource } from "@/types/document";

const suggestedQuestions = [
  "Je veux créer une startup numérique, par où dois-je commencer ?",
  "Quel service contacter pour un incident de cybersécurité sur une plateforme publique ?",
  "Où dois-je orienter quelqu'un qui cherche une information sur l'open data ?",
  "Y a-t-il un événement sur l'intelligence artificielle prévu en septembre 2026 ?"
];

const welcomeMessage: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Bonjour. Pose ta question, je vais fouiller les PDF indexés, extraire les passages utiles, les analyser et répondre uniquement avec les informations trouvées dans les documents."
};

export default function HomePage() {
  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function submit(event?: FormEvent<HTMLFormElement>, forcedQuestion?: string) {
    event?.preventDefault();
    const current = (forcedQuestion ?? question).trim();
    if (!current || loading) return;

    setQuestion("");
    setMessages((items) => [...items, { id: crypto.randomUUID(), role: "user", content: current }]);
    setLoading(true);

    try {
      const response = await api.chat(current);
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
    } catch (error) {
      setMessages((items) => [
        ...items,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: error instanceof Error ? error.message : "Je n'ai pas pu préparer la réponse."
        }
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function indexDocuments() {
    setIndexing(true);
    try {
      await api.index();
      setMessages((items) => [
        ...items,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "Indexation terminée. Tu peux maintenant poser tes questions sur les documents."
        }
      ]);
    } catch (error) {
      setMessages((items) => [
        ...items,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: error instanceof Error ? error.message : "L'indexation a échoué."
        }
      ]);
    } finally {
      setIndexing(false);
    }
  }

  function startNewChat() {
    setQuestion("");
    setLoading(false);
    setMessages([{ ...welcomeMessage, id: crypto.randomUUID() }]);
  }

  return (
    <main className="flex min-h-screen bg-mist text-ink">
      <section className="mx-auto flex min-h-screen w-full max-w-5xl flex-col px-4 py-5 sm:px-6 lg:px-8">
        <header className="mb-5 flex items-center justify-between gap-4 rounded-md border border-sage bg-paper px-4 py-3 shadow-panel">
          <div className="flex min-w-0 items-center gap-3">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-md bg-moss text-paper">
              <Bot size={20} aria-hidden />
            </div>
            <div className="min-w-0">
              <h1 className="truncate text-base font-semibold text-ink">SIOU</h1>
              <p className="truncate text-xs text-graphite/70">Assistant intelligent d'orientation des usagers vers les services compétents</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={startNewChat}
              className="inline-flex items-center gap-2 rounded-md border border-sage bg-paper px-3 py-2 text-sm font-medium text-graphite transition hover:border-moss hover:bg-sage"
              title="Vider le chat"
            >
              <MessageSquarePlus size={16} aria-hidden />
              Vider le chat
            </button>
            <button
              type="button"
              onClick={indexDocuments}
              disabled={indexing}
              className="inline-flex items-center gap-2 rounded-md bg-ink px-3 py-2 text-sm font-medium text-paper transition hover:bg-graphite disabled:cursor-not-allowed disabled:opacity-60"
              title="Indexer les PDF"
            >
              <RefreshCw size={16} className={indexing ? "animate-spin" : ""} aria-hidden />
              Indexer
            </button>
          </div>
        </header>

        <div className="thin-scrollbar min-h-0 flex-1 overflow-y-auto rounded-md border border-sage bg-paper shadow-panel">
          <div className="space-y-5 p-4 sm:p-6">
            {messages.map((message) => (
              <ChatBubble key={message.id} message={message} />
            ))}

            {loading && (
              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex items-start gap-3">
                <div className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-sage text-moss">
                  <Loader2 size={18} className="animate-spin" aria-hidden />
                </div>
                <div className="rounded-md bg-mist px-4 py-3 text-sm text-graphite">Préparation de la réponse...</div>
              </motion.div>
            )}

            {messages.length <= 1 && (
              <div className="grid gap-2 sm:grid-cols-2">
                {suggestedQuestions.map((item) => (
                  <button
                    key={item}
                    type="button"
                    onClick={() => submit(undefined, item)}
                    className="rounded-md border border-sage bg-mist p-3 text-left text-sm text-graphite transition hover:border-moss hover:bg-sage/70"
                  >
                    {item}
                  </button>
                ))}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        <form onSubmit={submit} className="mt-4 rounded-md border border-sage bg-paper p-3 shadow-panel">
          <div className="flex gap-3">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  submit();
                }
              }}
              placeholder="Pose une question sur les documents..."
              rows={2}
              className="min-h-14 flex-1 resize-none rounded-md border-sage bg-mist text-sm leading-6 focus:border-moss focus:ring-moss"
            />
            <button
              type="submit"
              disabled={!question.trim() || loading}
              className="grid h-14 w-14 shrink-0 place-items-center rounded-md bg-moss text-paper transition hover:bg-ocean disabled:cursor-not-allowed disabled:opacity-45"
              title="Envoyer"
            >
              <ArrowUp size={20} aria-hidden />
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}

function ChatBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}
    >
      <div className={`grid h-9 w-9 shrink-0 place-items-center rounded-md ${isUser ? "bg-ink text-paper" : "bg-sage text-moss"}`}>
        {isUser ? <User size={17} aria-hidden /> : <Bot size={17} aria-hidden />}
      </div>
      <div className={`max-w-[82%] ${isUser ? "text-right" : "text-left"}`}>
        <div className={`rounded-md px-4 py-3 text-sm leading-6 ${isUser ? "bg-ink text-paper" : "bg-mist text-ink"}`}>
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
        {!isUser && typeof message.confidence === "number" && (
          <p className="mt-2 text-xs font-medium text-moss">Confiance : {formatConfidence(message.confidence)}</p>
        )}
        {!isUser && message.sources && message.sources.length > 0 && <SourceList sources={message.sources} />}
      </div>
    </motion.div>
  );
}

function SourceList({ sources }: { sources: ChatSource[] }) {
  const uniqueSources = Array.from(new Map(sources.map((source) => [source.document, source])).values());

  return (
    <div className="mt-3 space-y-1.5">
      {uniqueSources.map((source) => (
        <div
          key={source.document}
          className="flex min-h-8 items-center gap-2 rounded-md border border-sage bg-paper px-3 py-1.5 text-left text-xs text-moss"
          title={`Issu du document : ${source.document} - page ${source.page}`}
        >
          <FileText size={14} className="shrink-0" aria-hidden />
          <span className="min-w-0 truncate font-semibold">Issu du document : {source.document}</span>
          <span className="shrink-0 text-graphite/65">Page {source.page}</span>
        </div>
      ))}
    </div>
  );
}
