"use client";

import clsx from "clsx";
import { Bot, FileText, Landmark, MessagesSquare, Users } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const links = [
  { href: "/", label: "Chat", icon: Bot },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/services", label: "Services", icon: Landmark },
  { href: "/users", label: "Utilisateurs", icon: Users },
  { href: "/conversations", label: "Conversations", icon: MessagesSquare }
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <main className="min-h-screen bg-[#eef3ef] text-ink">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-5 sm:px-6 lg:px-8">
        <header className="mb-5 overflow-hidden rounded-lg border border-[#cfdccd] bg-paper shadow-panel">
          <div className="h-1.5 bg-gradient-to-r from-moss via-ocean to-copper" />
          <div className="flex flex-col gap-4 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="min-w-0">
              <div className="flex items-center gap-3">
                <div className="grid h-11 w-11 shrink-0 place-items-center rounded-md bg-ink text-paper">
                  <Bot size={21} aria-hidden />
                </div>
                <div className="min-w-0">
                  <h1 className="truncate text-xl font-semibold leading-tight text-ink sm:text-2xl">SIOU</h1>
                  <p className="truncate text-sm text-graphite/70">Assistant intelligent d'orientation des usagers</p>
                </div>
              </div>
            </div>
            <nav className="thin-scrollbar flex gap-2 overflow-x-auto pb-1 lg:pb-0">
              {links.map((link) => {
                const active = pathname === link.href;
                const Icon = link.icon;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={clsx(
                      "inline-flex shrink-0 items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition",
                      active ? "bg-ink text-paper" : "border border-sage bg-[#f7faf5] text-graphite hover:border-moss hover:bg-sage"
                    )}
                  >
                    <Icon size={16} aria-hidden />
                    {link.label}
                  </Link>
                );
              })}
            </nav>
          </div>
        </header>
        {children}
      </div>
    </main>
  );
}
