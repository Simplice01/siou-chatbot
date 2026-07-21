"use client";

import { Landmark } from "lucide-react";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { EmptyState, ErrorState, LoadingState } from "@/components/DataState";
import { api } from "@/services/api";
import type { Organization, ServiceCard } from "@/types/document";

export default function ServicesPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [cards, setCards] = useState<ServiceCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.organizations(), api.serviceCards()])
      .then(([orgItems, cardItems]) => {
        setOrganizations(orgItems);
        setCards(cardItems);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Impossible de charger les services."))
      .finally(() => setLoading(false));
  }, []);

  const orgById = new Map(organizations.map((item) => [item.id, item]));

  return (
    <AppShell>
      <section className="space-y-5">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-moss">Orientation</p>
          <h2 className="mt-2 text-2xl font-semibold text-ink">Services et structures</h2>
          <p className="mt-1 text-sm text-graphite/70">Vue metier des organisations et fiches d'orientation disponibles.</p>
        </div>

        {loading && <LoadingState />}
        {error && <ErrorState message={error} />}
        {!loading && !error && cards.length === 0 && <EmptyState label="Aucune fiche service disponible." />}

        <div className="grid gap-3 lg:grid-cols-2">
          {cards.map((card) => {
            const org = orgById.get(card.organization_id);
            return (
              <article key={card.id} className="rounded-lg border border-sage bg-paper p-4 shadow-panel">
                <div className="flex items-start gap-3">
                  <div className="grid h-10 w-10 shrink-0 place-items-center rounded-md bg-sage text-moss">
                    <Landmark size={18} aria-hidden />
                  </div>
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-base font-semibold text-ink">{card.public_name ?? card.title}</h3>
                      <span className="rounded-md bg-mist px-2 py-1 text-xs font-medium text-graphite">{card.status}</span>
                    </div>
                    <p className="mt-1 text-sm font-medium text-moss">{org?.acronym ?? org?.name ?? "Structure non renseignee"}</p>
                    <p className="mt-3 text-sm leading-6 text-graphite">{card.orientation_summary}</p>
                    {card.target_users && <p className="mt-3 text-xs text-graphite/65">Public cible : {card.target_users}</p>}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </section>
    </AppShell>
  );
}
