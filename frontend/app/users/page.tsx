"use client";

import { Users } from "lucide-react";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { EmptyState, ErrorState, LoadingState } from "@/components/DataState";
import { api } from "@/services/api";
import type { UserRecord } from "@/types/document";

export default function UsersPage() {
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .users()
      .then(setUsers)
      .catch((err) => setError(err instanceof Error ? err.message : "Impossible de charger les utilisateurs."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <section className="space-y-5">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-moss">Acces futurs</p>
          <h2 className="mt-2 text-2xl font-semibold text-ink">Utilisateurs</h2>
          <p className="mt-1 text-sm text-graphite/70">La table est prete pour les roles et l'authentification de la prochaine phase.</p>
        </div>

        {loading && <LoadingState />}
        {error && <ErrorState message={error} />}
        {!loading && !error && users.length === 0 && <EmptyState label="Aucun utilisateur cree pour le moment." />}

        <div className="overflow-hidden rounded-lg border border-sage bg-paper shadow-panel">
          {users.map((user) => (
            <div key={user.id} className="flex flex-col gap-2 border-b border-sage px-4 py-3 last:border-b-0 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                <div className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-sage text-moss">
                  <Users size={16} aria-hidden />
                </div>
                <div>
                  <p className="font-medium text-ink">{user.full_name ?? user.email ?? "Utilisateur sans nom"}</p>
                  <p className="text-xs text-graphite/65">{user.email ?? user.id}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="rounded-md bg-mist px-2 py-1 text-xs font-medium text-graphite">{user.role}</span>
                <span className="rounded-md bg-sage px-2 py-1 text-xs font-medium text-moss">{user.is_active ? "actif" : "inactif"}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
