"use client";

import { FileText } from "lucide-react";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { EmptyState, ErrorState, LoadingState } from "@/components/DataState";
import { api } from "@/services/api";
import type { AdminStats, DatabaseDocument, SourceFile } from "@/types/document";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DatabaseDocument[]>([]);
  const [files, setFiles] = useState<SourceFile[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.databaseDocuments(), api.sourceFiles(), api.stats()])
      .then(([docItems, fileItems, statItems]) => {
        setDocuments(docItems);
        setFiles(fileItems);
        setStats(statItems);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Impossible de charger les documents."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <section className="space-y-5">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-moss">Base documentaire</p>
          <h2 className="mt-2 text-2xl font-semibold text-ink">Documents indexes</h2>
          <p className="mt-1 text-sm text-graphite/70">Les PDF locaux sont synchronises dans PostgreSQL et utilises par le chatbot.</p>
        </div>

        {stats && (
          <div className="grid gap-3 sm:grid-cols-3">
            <Metric label="Documents" value={stats.documents} />
            <Metric label="Chunks" value={stats.document_chunks} />
            <Metric label="Fichiers sources" value={files.length} />
          </div>
        )}

        {loading && <LoadingState />}
        {error && <ErrorState message={error} />}
        {!loading && !error && documents.length === 0 && <EmptyState label="Aucun document trouve dans la base." />}

        <div className="grid gap-3">
          {documents.map((document) => (
            <article key={document.id} className="rounded-lg border border-sage bg-paper p-4 shadow-panel">
              <div className="flex items-start gap-3">
                <div className="grid h-10 w-10 shrink-0 place-items-center rounded-md bg-sage text-moss">
                  <FileText size={18} aria-hidden />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="truncate text-base font-semibold text-ink">{document.title}</h3>
                    <span className="rounded-md bg-mist px-2 py-1 text-xs font-medium text-graphite">{document.status}</span>
                    <span className="rounded-md bg-sage px-2 py-1 text-xs font-medium text-moss">{document.type}</span>
                  </div>
                  {document.summary && <p className="mt-2 line-clamp-2 text-sm leading-6 text-graphite">{document.summary}</p>}
                  <p className="mt-3 text-xs text-graphite/60">ID document : {document.id}</p>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>
    </AppShell>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-sage bg-paper p-4 shadow-panel">
      <p className="text-xs font-medium uppercase tracking-[0.16em] text-graphite/60">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
    </div>
  );
}
