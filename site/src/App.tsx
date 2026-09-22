/**
 * App shell and route table.
 *
 * Navigation is deliberately flat and short. Ten destinations, ordered by how often Andre will
 * need them, with the two honesty surfaces — Sources and Runs — visible rather than buried in a
 * settings menu.
 */
import {
  Activity,
  Building2,
  CircleHelp,
  FileText,
  Globe2,
  History,
  LayoutGrid,
  Moon,
  Radio,
  ServerCog,
  Sun,
} from "lucide-react";
import { Suspense, useEffect, useState } from "react";
import { cn } from "./design/primitives";
import { Link, useRoute } from "./lib/router";
import { Companies } from "./routes/Companies";
import { CompanyDetail } from "./routes/CompanyDetail";
import { Events } from "./routes/Events";
import { Markets } from "./routes/Markets";
import { Pipeline } from "./routes/Pipeline";
import { Questions } from "./routes/Questions";
import { Rfps } from "./routes/Rfps";
import { Runs } from "./routes/Runs";
import { Sources } from "./routes/Sources";
import { Today } from "./routes/Today";

const NAV = [
  { to: "/", label: "Today", icon: LayoutGrid },
  { to: "/companies", label: "Companies", icon: Building2 },
  { to: "/triggers", label: "Triggers", icon: Activity },
  { to: "/pipeline", label: "Pipeline", icon: Radio },
  { to: "/rfps", label: "RFPs", icon: FileText },
  { to: "/markets", label: "Markets", icon: Globe2 },
  { to: "/sources", label: "Sources", icon: ServerCog },
  { to: "/runs", label: "Runs", icon: History },
  { to: "/questions", label: "Questions", icon: CircleHelp },
] as const;

function ThemeToggle() {
  const [theme, setTheme] = useState<"system" | "light" | "dark">("system");
  useEffect(() => {
    const root = document.documentElement;
    if (theme === "system") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", theme);
  }, [theme]);
  return (
    <button
      type="button"
      title={`Theme: ${theme}. Click to change.`}
      onClick={() => setTheme(theme === "system" ? "light" : theme === "light" ? "dark" : "system")}
      className="rounded-[var(--radius-sm)] p-1.5 text-muted hover:bg-surface-raised hover:text-text"
    >
      {theme === "dark" ? <Moon className="size-4" /> : <Sun className="size-4" />}
    </button>
  );
}

function Nav({ route }: { route: string }) {
  return (
    <nav className="sticky top-0 z-20 border-b bg-surface/85 backdrop-blur-sm">
      <div className="mx-auto flex max-w-[1400px] items-center gap-1 overflow-x-auto px-3 sm:px-6">
        <Link
          to="/"
          className="mr-3 shrink-0 py-3 font-semibold tracking-[-0.01em] whitespace-nowrap"
        >
          OFS <span className="text-muted">Sales</span>
        </Link>
        {NAV.map(({ to, label, icon: Icon }) => {
          const active = to === "/" ? route === "/" : route.startsWith(to);
          return (
            <Link
              key={to}
              to={to}
              className={cn(
                "flex shrink-0 items-center gap-1.5 border-b-2 px-2.5 py-3 text-small whitespace-nowrap transition-colors",
                active
                  ? "border-[var(--accent)] text-text"
                  : "border-transparent text-muted hover:text-text",
              )}
            >
              <Icon className="size-4" aria-hidden />
              {label}
            </Link>
          );
        })}
        <div className="ml-auto shrink-0 pl-3">
          <ThemeToggle />
        </div>
      </div>
    </nav>
  );
}

function Loading() {
  return <div className="px-6 py-16 text-small text-subtle">Loading…</div>;
}

function render(route: string) {
  if (route === "/") return <Today />;
  if (route.startsWith("/companies/"))
    return <CompanyDetail slug={decodeURIComponent(route.slice("/companies/".length))} />;
  if (route.startsWith("/companies")) return <Companies />;
  if (route.startsWith("/triggers")) return <Events />;
  if (route.startsWith("/pipeline")) return <Pipeline />;
  if (route.startsWith("/rfps")) return <Rfps />;
  if (route.startsWith("/markets")) return <Markets />;
  if (route.startsWith("/sources")) return <Sources />;
  if (route.startsWith("/runs")) return <Runs />;
  if (route.startsWith("/questions")) return <Questions />;
  return <Today />;
}

export function App() {
  const route = useRoute();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  return (
    <>
      <Nav route={route} />
      <Suspense fallback={<Loading />}>{render(route)}</Suspense>
    </>
  );
}
