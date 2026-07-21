export function LoadingState() {
  return <div className="rounded-lg border border-sage bg-paper p-5 text-sm text-graphite shadow-panel">Chargement des donnees...</div>;
}

export function ErrorState({ message }: { message: string }) {
  return <div className="rounded-lg border border-[#e3b6a4] bg-[#fff8f5] p-5 text-sm text-[#8d3f24] shadow-panel">{message}</div>;
}

export function EmptyState({ label }: { label: string }) {
  return <div className="rounded-lg border border-sage bg-paper p-5 text-sm text-graphite shadow-panel">{label}</div>;
}
