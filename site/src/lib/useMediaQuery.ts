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

/** Tailwind's `md` breakpoint. Below this, screen real estate is the scarce resource. */
export const useIsNarrow = () => useMediaQuery("(max-width: 767px)");
