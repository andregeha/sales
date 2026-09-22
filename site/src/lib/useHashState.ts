import { useCallback } from "react";
import { useRoute } from "./router";

/**
 * Filter state that lives in the URL.
 *
 * An earlier version kept filters in `useState` while the code comment claimed they lived in the
 * hash and made a view shareable. They did not, and navigating away lost them (finding F2). This
 * makes the claim true: `#/companies?country=France&trigger=1` reproduces a view exactly, survives
 * navigation and back/forward, and can be pasted to someone else.
 */
export type HashParams = Record<string, string | undefined>;

export function parseHash(route: string): { path: string; params: HashParams } {
  const i = route.indexOf("?");
  if (i === -1) return { path: route, params: {} };
  const params: HashParams = {};
  for (const [k, v] of new URLSearchParams(route.slice(i + 1))) params[k] = v;
  return { path: route.slice(0, i), params };
}

export function useHashParams(): [HashParams, (next: HashParams) => void] {
  const route = useRoute();
  const { path, params } = parseHash(route);

  const set = useCallback(
    (next: HashParams) => {
      const sp = new URLSearchParams();
      // Sorted so the same filters always produce the same URL — a shared link is stable.
      for (const k of Object.keys(next).sort()) {
        const v = next[k];
        if (v !== undefined && v !== "") sp.set(k, v);
      }
      const q = sp.toString();
      window.location.hash = q ? `${path}?${q}` : path;
    },
    [path],
  );

  return [params, set];
}
