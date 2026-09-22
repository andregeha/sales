import { useEffect } from "react";
import { navigate } from "./router";

/**
 * The keyboard layer the plan promised (§5.7) and the first build did not have (finding F3).
 *
 * `/` focus search · `j`/`k` move · `Enter` open · `Esc` clear · `g` then `t`/`c`/`s`/`m` jump.
 * Deliberately no library: this is ~40 lines and a dependency would be weight for a keymap.
 */
export function useKeyboard() {
  useEffect(() => {
    let awaitingGoto = false;
    let gotoTimer: number | undefined;

    function isTyping(el: EventTarget | null) {
      const t = el as HTMLElement | null;
      return !!t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable);
    }

    function onKey(e: KeyboardEvent) {
      // Never steal a key from someone typing, except Escape.
      if (isTyping(e.target) && e.key !== "Escape") return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      if (awaitingGoto) {
        awaitingGoto = false;
        window.clearTimeout(gotoTimer);
        const dest: Record<string, string> = {
          t: "/",
          c: "/companies",
          s: "/sources",
          m: "/markets",
          r: "/runs",
          q: "/questions",
        };
        const to = dest[e.key];
        if (to) {
          e.preventDefault();
          navigate(to);
        }
        return;
      }

      switch (e.key) {
        case "/": {
          const input = document.querySelector<HTMLInputElement>(
            'input[type="text"], input:not([type])',
          );
          if (input) {
            e.preventDefault();
            input.focus();
            input.select();
          }
          break;
        }
        case "Escape": {
          const el = document.activeElement as HTMLElement | null;
          if (isTyping(el)) el?.blur();
          break;
        }
        case "g":
          awaitingGoto = true;
          gotoTimer = window.setTimeout(() => {
            awaitingGoto = false;
          }, 1200);
          break;
        case "j":
        case "k": {
          e.preventDefault();
          moveSelection(e.key === "j" ? 1 : -1);
          break;
        }
        case "Enter": {
          const row = document.querySelector<HTMLElement>("tbody tr[data-selected='true']");
          row?.click();
          break;
        }
        default:
          break;
      }
    }

    function moveSelection(delta: number) {
      const rows = [...document.querySelectorAll<HTMLElement>("tbody tr")].filter((r) =>
        r.querySelector("td")?.textContent?.trim(),
      );
      if (rows.length === 0) return;
      const current = rows.findIndex((r) => r.dataset.selected === "true");
      const next = Math.max(0, Math.min(rows.length - 1, current === -1 ? 0 : current + delta));
      for (const r of rows) r.dataset.selected = "false";
      const target = rows[next];
      if (target) {
        target.dataset.selected = "true";
        target.scrollIntoView({ block: "nearest" });
      }
    }

    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
}
