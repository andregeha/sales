/**
 * Routing. Deliberately a tiny hash router rather than a dependency.
 *
 * The site is opened from disk (file://) as often as from a dev server, and history-based routing
 * does not survive that. Hash routing works in both, needs no server rewrites, and keeps filter
 * state shareable in the URL — which is the only thing we actually needed a router for.
 */
import { useSyncExternalStore } from "react";

function subscribe(cb: () => void) {
  window.addEventListener("hashchange", cb);
  return () => window.removeEventListener("hashchange", cb);
}

export function useRoute(): string {
  const hash = useSyncExternalStore(
    subscribe,
    () => window.location.hash,
    () => "",
  );
  return (hash || "#/").replace(/^#/, "") || "/";
}

export function navigate(to: string) {
  window.location.hash = to;
}

export function Link({
  to,
  children,
  className,
}: {
  to: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <a href={`#${to}`} className={className}>
      {children}
    </a>
  );
}
