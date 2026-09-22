import { useEffect, useState } from "react";

type State<T> =
  | { status: "loading" }
  | { status: "ok"; data: T }
  | { status: "error"; error: Error };

/**
 * Minimal async loader. No TanStack Query: there is no server, no cache invalidation and no
 * refetching, so a cache library would be weight without a job (plan §6).
 */
export function useAsync<T>(fn: () => Promise<T>, deps: unknown[] = []): State<T> {
  const [state, setState] = useState<State<T>>({ status: "loading" });
  useEffect(() => {
    let alive = true;
    setState({ status: "loading" });
    fn()
      .then((data) => alive && setState({ status: "ok", data }))
      .catch((error: Error) => alive && setState({ status: "error", error }));
    return () => {
      alive = false;
    };
    // eslint-disable-next-line
  }, deps);
  return state;
}
