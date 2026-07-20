"use client";

import { RefreshCw, Sparkles } from "lucide-react";

type Props = {
  onIndex: () => void;
  indexing: boolean;
};

export function TopBar({ onIndex, indexing }: Props) {
  return (
    <header className="flex h-16 items-center justify-between border-b border-sage bg-paper/90 px-5 backdrop-blur">
      <div className="flex items-center gap-3">
        <div className="grid h-9 w-9 place-items-center rounded-md bg-moss text-paper">
          <Sparkles size={18} aria-hidden />
        </div>
        <div>
          <h1 className="text-base font-semibold tracking-normal text-ink">SIOU Document AI</h1>
          <p className="text-xs text-graphite/70">Lecture, recherche et dialogue strictement ancrés dans le PDF ouvert</p>
        </div>
      </div>
      <button
        type="button"
        onClick={onIndex}
        disabled={indexing}
        className="inline-flex items-center gap-2 rounded-md bg-ink px-3 py-2 text-sm font-medium text-paper transition hover:bg-graphite disabled:cursor-not-allowed disabled:opacity-60"
        title="Indexer les PDF locaux"
      >
        <RefreshCw size={16} className={indexing ? "animate-spin" : ""} aria-hidden />
        Indexer
      </button>
    </header>
  );
}

