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
import { lazy, Suspense, useEffect, useState } from "react";

/**
 * Only Today is eager. Everything else is fetched when it is opened, which keeps Recharts and the
 * grid off the first load for a reader who just wants today's brief (finding F6).
 */
const Companies = lazy(() => import("./routes/Companies").then((m) => ({ default: m.Companies })));
const CompanyDetail = lazy(() =>
  import("./routes/CompanyDetail").then((m) => ({ default: m.CompanyDetail })),
);
const Events = lazy(() => import("./routes/Events").then((m) => ({ default: m.Events })));
const Markets = lazy(() => import("./routes/Markets").then((m) => ({ default: m.Markets })));
const Pipeline = lazy(() => import("./routes/Pipeline").then((m) => ({ default: m.Pipeline })));
const Questions = lazy(() => import("./routes/Questions").then((m) => ({ default: m.Questions })));
const Rfps = lazy(() => import("./routes/Rfps").then((m) => ({ default: m.Rfps })));
const Runs = lazy(() => import("./routes/Runs").then((m) => ({ default: m.Runs })));
const Sources = lazy(() => import("./routes/Sources").then((m) => ({ default: m.Sources })));

import { cn, Kbd } from "./design/primitives";
import { Link, useRoutePath } from "./lib/router";
import { useKeyboard } from "./lib/useKeyboard";
import { Today } from "./routes/Today";

/**
 * Two groups, separated visually rather than by a menu (finding F11).
 *
 * "The work" is what Andre opens daily. "The machine" is how the engine reports on itself — it
 * belongs in the nav rather than hidden in settings, because a dead connector must stay one click
 * away, but it should not compete with the work for attention.
 */
const NAV_WORK = [
  { to: "/", label: "Today", icon: LayoutGrid },
  { to: "/companies", label: "Companies", icon: Building2 },
  { to: "/triggers", label: "Triggers", icon: Activity },
  { to: "/pipeline", label: "Pipeline", icon: Radio },
  { to: "/rfps", label: "RFPs", icon: FileText },
] as const;

const NAV_MACHINE = [
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

function NavItem({
  item,
  route,
  alwaysLabel = true,
}: {
  item: { to: string; label: string; icon: typeof LayoutGrid };
  route: string;
  alwaysLabel?: boolean;
}) {
  const { to, label, icon: Icon } = item;
  const active = to === "/" ? route === "/" : route.startsWith(to);
  return (
    <Link
      to={to}
      title={label}
      className={cn(
        "flex shrink-0 items-center gap-1.5 border-b-2 px-2.5 py-3 text-small whitespace-nowrap transition-colors",
        active
          ? "border-[var(--accent)] text-text"
          : "border-transparent text-muted hover:text-text",
      )}
    >
      <Icon className="size-4" aria-hidden />
      {/* Below lg the machine group collapses to icons so the daily items keep their labels
          rather than the whole bar scrolling sideways. */}
      <span className={cn(alwaysLabel ? "inline" : "hidden lg:inline")}>{label}</span>
    </Link>
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
        {NAV_WORK.map((item) => (
          <NavItem key={item.to} item={item} route={route} />
        ))}
        <span className="mx-2 h-4 w-px shrink-0 bg-[var(--border-strong)]" aria-hidden />
        {NAV_MACHINE.map((item) => (
          <NavItem key={item.to} item={item} route={route} alwaysLabel={false} />
        ))}
        <div className="ml-auto shrink-0 pl-3">
          <ThemeToggle />
        </div>
      </div>
    </nav>
  );
}

/** Discoverability for the keyboard layer. Hidden on touch, where it would be noise. */
function KeyboardHint() {
  return (
    <footer className="mx-auto hidden max-w-[1400px] items-center gap-3 px-5 pb-8 text-micro text-subtle sm:flex sm:px-8">
      <span className="flex items-center gap-1">
        <Kbd>/</Kbd> search
      </span>
      <span className="flex items-center gap-1">
        <Kbd>j</Kbd>
        <Kbd>k</Kbd> move
      </span>
      <span className="flex items-center gap-1">
        <Kbd>↵</Kbd> open
      </span>
      <span className="flex items-center gap-1">
        <Kbd>g</Kbd> then <Kbd>t</Kbd>
        <Kbd>c</Kbd>
        <Kbd>s</Kbd>
        <Kbd>m</Kbd>
        <Kbd>r</Kbd>
        <Kbd>q</Kbd> jump
      </span>
    </footer>
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
  const route = useRoutePath();
  useKeyboard();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  return (
    <>
      <Nav route={route} />
      <Suspense fallback={<Loading />}>{render(route)}</Suspense>
      <KeyboardHint />
    </>
  );
}
