import { useSyncExternalStore } from "react";

/** Narrow-screen detection, so the grid and filters can drop to a phone layout (finding F5/F7). */
export function useMediaQuery(query: string): boolean {
  return useSyncExternalStore(
    (cb) => {
      const mql = window.matchMedia(query);
      mql.addEventListener("change", cb);
      return () => mql.removeEventListener("change", cb);
    },
    () => window.matchMedia(query).matches,
    () => false,
  );
}

/**
 * Three tiers, not two.
 *
 * Two was not enough: at ~870px the full seven-column grid technically fits but leaves the company
 * name 136px, which is unreadable for names like "Patrimium Asset Management (DIFC)". The middle
 * tier drops the two columns a reader can infer or filter for — segment and status — and gives the
 * space to the name and the reason to write.
 */
export const useIsNarrow = () => useMediaQuery("(max-width: 767px)");
export const useIsMedium = () => useMediaQuery("(min-width: 768px) and (max-width: 1179px)");
