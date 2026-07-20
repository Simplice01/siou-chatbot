"use client";

import { ChevronLeft, ChevronRight, Minus, Plus, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import { api } from "@/services/api";
import type { DocumentSummary } from "@/types/document";

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

type Props = {
  document: DocumentSummary | null;
  page: number;
  onPageChange: (page: number) => void;
};

export function PdfReader({ document, page, onPageChange }: Props) {
  const [pages, setPages] = useState(0);
  const [zoom, setZoom] = useState(1);
  const [search, setSearch] = useState("");
  const file = useMemo(() => (document ? api.pdfUrl(document.id) : null), [document]);

  const goToPage = (next: number) => {
    if (!pages) return;
    onPageChange(Math.max(1, Math.min(pages, next)));
  };

  return (
    <main className="flex min-h-0 flex-col bg-mist">
      <div className="flex min-h-14 flex-wrap items-center justify-between gap-3 border-b border-sage bg-paper px-4 py-2">
        <div className="min-w-0">
          <h2 className="truncate text-sm font-semibold text-ink">{document?.name ?? "Sélectionne un document"}</h2>
          <p className="text-xs text-graphite/65">{document ? `${pages || document.page_count || "?"} pages` : "Dépose tes PDF dans backend/documents"}</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="relative hidden sm:block">
            <Search className="pointer-events-none absolute left-3 top-2 text-graphite/55" size={15} aria-hidden />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Recherche PDF"
              className="w-40 rounded-md border-sage bg-mist py-1.5 pl-8 pr-2 text-sm focus:border-moss focus:ring-moss"
            />
          </label>
          <button className="rounded-md border border-sage bg-paper p-2 hover:bg-sage" onClick={() => setZoom((value) => Math.max(0.7, value - 0.1))} title="Zoom arrière">
            <Minus size={16} aria-hidden />
          </button>
          <span className="w-12 text-center text-xs font-medium text-graphite">{Math.round(zoom * 100)}%</span>
          <button className="rounded-md border border-sage bg-paper p-2 hover:bg-sage" onClick={() => setZoom((value) => Math.min(1.8, value + 0.1))} title="Zoom avant">
            <Plus size={16} aria-hidden />
          </button>
        </div>
      </div>
      <div className="thin-scrollbar flex min-h-0 flex-1 justify-center overflow-auto p-6">
        {!file && <div className="mt-16 text-center text-sm text-graphite/65">Aucun document ouvert</div>}
        {file && (
          <Document file={file} onLoadSuccess={({ numPages }) => setPages(numPages)} loading={<p className="text-sm text-graphite/70">Chargement du PDF...</p>}>
            <Page pageNumber={page} scale={zoom} renderTextLayer={Boolean(search)} renderAnnotationLayer />
          </Document>
        )}
      </div>
      <footer className="flex h-14 items-center justify-center gap-3 border-t border-sage bg-paper">
        <button className="rounded-md border border-sage p-2 hover:bg-sage disabled:opacity-40" disabled={!document || page <= 1} onClick={() => goToPage(page - 1)} title="Page précédente">
          <ChevronLeft size={17} aria-hidden />
        </button>
        <input
          value={page}
          onChange={(event) => goToPage(Number(event.target.value) || 1)}
          className="h-9 w-16 rounded-md border-sage text-center text-sm focus:border-moss focus:ring-moss"
        />
        <span className="text-sm text-graphite/65">/ {pages || document?.page_count || 0}</span>
        <button className="rounded-md border border-sage p-2 hover:bg-sage disabled:opacity-40" disabled={!document || page >= pages} onClick={() => goToPage(page + 1)} title="Page suivante">
          <ChevronRight size={17} aria-hidden />
        </button>
      </footer>
    </main>
  );
}

