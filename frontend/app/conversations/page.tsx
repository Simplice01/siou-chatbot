"use client";

import { MessagesSquare } from "lucide-react";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { EmptyState, ErrorState, LoadingState } from "@/components/DataState";
import { api } from "@/services/api";
import type { Conversation } from "@/types/document";

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .conversations()
      .then(setConversations)
      .catch((err) => setError(err instanceof Error ? err.message : "Impossible de charger les conversations."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <section className="space-y-5">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-moss">Trace chatbot</p>
          <h2 className="mt-2 text-2xl font-semibold text-ink">Conversations</h2>
          <p className="mt-1 text-sm text-graphite/70">Chaque question posee au chatbot peut etre rattachee a une conversation PostgreSQL.</p>
        </div>

        {loading && <LoadingState />}
        {error && <ErrorState message={error} />}
        {!loading && !error && conversations.length === 0 && <EmptyState label="Aucune conversation enregistree pour le moment." />}

        <div className="grid gap-3">
          {conversations.map((conversation) => (
            <article key={conversation.id} className="rounded-lg border border-sage bg-paper p-4 shadow-panel">
              <div className="flex items-start gap-3">
                <div className="grid h-10 w-10 shrink-0 place-items-center rounded-md bg-sage text-moss">
                  <MessagesSquare size={18} aria-hidden />
                </div>
                <div className="min-w-0">
                  <h3 className="text-base font-semibold text-ink">{conversation.title ?? "Conversation sans titre"}</h3>
                  <p className="mt-1 text-sm text-graphite/70">Canal : {conversation.channel}</p>
                  <p className="mt-2 break-all text-xs text-graphite/60">ID : {conversation.id}</p>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
