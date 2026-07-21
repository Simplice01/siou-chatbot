"use client";

import { motion } from "framer-motion";
import { ArrowUp, Bot, FileText, Loader2, RefreshCw, RotateCcw, ShieldCheck, Sparkles, User } from "lucide-react";
import { FormEvent, useEffect, useRef, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { formatConfidence } from "@/lib/format";
import { api } from "@/services/api";
import type { ChatMessage, ChatSource } from "@/types/document";

const suggestedQuestions = [
  {
    title: "Creer une startup",
    question: "Je veux creer une startup numerique, par ou dois-je commencer ?"
  },
  {
    title: "Incident cybersecurite",
    question: "Quel service contacter pour un incident de cybersecurite sur une plateforme publique ?"
  },
  {
    title: "Open data",
    question: "Ou dois-je orienter quelqu'un qui cherche une information sur l'open data ?"
  },
  {
    title: "Evenement IA",
    question: "Y a-t-il un evenement sur l'intelligence artificielle prevu en septembre 2026 ?"
  }
];

const welcomeMessage: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Bonjour, je suis SIOU. Decrivez la demande de l'usager et je vous indique le service competent, le contact utile et la source documentaire utilisee."
};

export default function HomePage() {
  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
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
      const response = await api.chat(current, undefined, conversationId);
      setConversationId(response.conversation_id ?? conversationId);
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
          content: error instanceof Error ? error.message : "Je n'ai pas pu preparer la reponse."
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
          content: "Indexation terminee. Les PDF locaux sont synchronises avec la base et l'index de recherche."
        }
      ]);
    } catch (error) {
      setMessages((items) => [
        ...items,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: error instanceof Error ? error.message : "L'indexation a echoue."
        }
      ]);
    } finally {
      setIndexing(false);
    }
  }

  function startNewChat() {
    setQuestion("");
    setLoading(false);
    setConversationId(null);
    setMessages([{ ...welcomeMessage, id: crypto.randomUUID() }]);
  }

  return (
    <AppShell>
      <section className="flex min-h-0 flex-1 flex-col">
        <div className="mb-4 flex flex-col gap-3 rounded-lg border border-[#cfdccd] bg-paper p-3 shadow-panel sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold text-ink">Chatbot documentaire SIOU</p>
            <p className="text-sm text-graphite/70">Il repond uniquement a partir des documents indexes localement.</p>
          </div>
          <div className="flex w-full items-center gap-2 sm:w-auto">
            <button
              type="button"
              onClick={startNewChat}
              className="inline-flex flex-1 items-center justify-center gap-2 rounded-md border border-sage bg-[#f7faf5] px-3 py-2 text-sm font-medium text-graphite transition hover:border-moss hover:bg-sage sm:flex-none"
              title="Vider le chat"
            >
              <RotateCcw size={15} aria-hidden />
              <span className="sm:hidden">Vider</span>
              <span className="hidden sm:inline">Vider le chat</span>
            </button>
            <button
              type="button"
              onClick={indexDocuments}
              disabled={indexing}
              className="inline-flex flex-1 items-center justify-center gap-2 rounded-md bg-ink px-3 py-2 text-sm font-medium text-paper transition hover:bg-graphite disabled:cursor-not-allowed disabled:opacity-60 sm:flex-none"
              title="Indexer les PDF"
            >
              <RefreshCw size={16} className={indexing ? "animate-spin" : ""} aria-hidden />
              Indexer
            </button>
          </div>
        </div>

        <div className="thin-scrollbar min-h-0 flex-1 overflow-y-auto rounded-lg border border-[#cfdccd] bg-[#fbfcf8] shadow-panel">
          <div className="space-y-5 p-4 sm:p-6">
            {messages.map((message) => (
              <ChatBubble key={message.id} message={message} />
            ))}

            {loading && (
              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex items-start gap-3">
                <div className="grid h-10 w-10 shrink-0 place-items-center rounded-md bg-sage text-moss">
                  <Loader2 size={18} className="animate-spin" aria-hidden />
                </div>
                <div className="rounded-md border border-sage bg-paper px-4 py-3 text-sm text-graphite">
                  <p className="font-medium text-ink">Preparation de la reponse...</p>
                  <p className="mt-1 text-xs text-graphite/70">Analyse des documents et identification du service competent.</p>
                </div>
              </motion.div>
            )}

            {messages.length <= 1 && (
              <div className="grid gap-3 sm:grid-cols-2">
                {suggestedQuestions.map((item) => (
                  <button
                    key={item.question}
                    type="button"
                    onClick={() => submit(undefined, item.question)}
                    className="group rounded-md border border-sage bg-paper p-4 text-left transition hover:border-moss hover:bg-sage/60"
                  >
                    <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-moss">
                      <Sparkles size={15} className="transition group-hover:text-ocean" aria-hidden />
                      {item.title}
                    </div>
                    <p className="text-sm leading-5 text-graphite">{item.question}</p>
                  </button>
                ))}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        <form onSubmit={submit} className="mt-4 rounded-lg border border-[#cfdccd] bg-paper p-3 shadow-panel">
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
              placeholder="Decrivez la demande de l'usager..."
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
    </AppShell>
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
        <div className={`rounded-md px-4 py-3 text-sm leading-6 shadow-sm ${isUser ? "bg-ink text-paper" : "border border-sage bg-paper text-ink"}`}>
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
        {!isUser && typeof message.confidence === "number" && (
          <p className="mt-2 inline-flex items-center gap-1 rounded-md bg-sage px-2 py-1 text-xs font-medium text-moss">
            <ShieldCheck size={13} aria-hidden />
            Fiabilite estimee : {formatConfidence(message.confidence)}
          </p>
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
