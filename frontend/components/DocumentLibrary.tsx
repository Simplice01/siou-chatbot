"use client";

import clsx from "clsx";
import { FileText, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { formatBytes } from "@/lib/format";
import type { DocumentSummary } from "@/types/document";

type Props = {
  documents: DocumentSummary[];
  selectedId: string | null;
  onSelect: (doc: DocumentSummary) => void;
};

export function DocumentLibrary({ documents, selectedId, onSelect }: Props) {
  const [query, setQuery] = useState("");
  const filtered = useMemo(
    () => documents.filter((doc) => doc.name.toLowerCase().includes(query.toLowerCase())),
    [documents, query]
  );

  return (
    <aside className="flex min-h-0 flex-col border-r border-sage bg-paper">
      <div className="border-b border-sage p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-ink">Bibliothèque</h2>
          <span className="rounded-md bg-sage px-2 py-1 text-xs text-graphite">{documents.length}</span>
        </div>
        <label className="relative block">
          <Search className="pointer-events-none absolute left-3 top-2.5 text-graphite/55" size={16} aria-hidden />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Rechercher un PDF"
            className="w-full rounded-md border-sage bg-mist py-2 pl-9 pr-3 text-sm outline-none transition focus:border-moss focus:ring-moss"
          />
        </label>
      </div>
      <div className="thin-scrollbar min-h-0 flex-1 overflow-y-auto p-3">
        {filtered.map((doc) => (
          <button
            key={doc.id}
            type="button"
            onClick={() => onSelect(doc)}
            className={clsx(
              "mb-2 w-full rounded-md border p-3 text-left transition",
              selectedId === doc.id ? "border-moss bg-sage/75" : "border-transparent bg-transparent hover:bg-mist"
            )}
          >
            <div className="flex items-start gap-3">
              <FileText className="mt-0.5 shrink-0 text-ocean" size={18} aria-hidden />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-ink">{doc.name}</p>
                <p className="mt-1 text-xs text-graphite/70">
                  {formatBytes(doc.size_bytes)} · {doc.page_count ?? "?"} pages
                </p>
                <p className={clsx("mt-2 text-xs font-medium", doc.indexed ? "text-moss" : "text-copper")}>
                  {doc.indexed ? `${doc.chunk_count ?? 0} fragments indexés` : "À indexer"}
                </p>
              </div>
            </div>
          </button>
        ))}
        {filtered.length === 0 && <p className="px-2 py-8 text-center text-sm text-graphite/60">Aucun PDF trouvé</p>}
      </div>
    </aside>
  );
}

