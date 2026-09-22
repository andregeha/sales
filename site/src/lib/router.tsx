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

/** The route WITHOUT its query string — what the router matches on. */
export function useRoutePath(): string {
  const r = useRoute();
  const i = r.indexOf("?");
  return i === -1 ? r : r.slice(0, i);
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
  title,
}: {
  to: string;
  children: React.ReactNode;
  className?: string;
  /** Needed where a link collapses to an icon and the label is no longer visible. */
  title?: string;
}) {
  return (
    <a href={`#${to}`} className={className} title={title}>
      {children}
    </a>
  );
}
