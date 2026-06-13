import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { getHealth, API_BASE_URL } from "@/lib/api";
import { Brain } from "lucide-react";

export function SiteHeader() {
  const { data, isError } = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 30_000,
    retry: false,
  });

  const ok = !!data && data.status === "ok" && !isError;

  return (
    <header className="border-b border-border/60 bg-background/80 backdrop-blur sticky top-0 z-40">
      <div className="mx-auto max-w-6xl px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <Brain className="h-5 w-5 text-accent-foreground" />
          <span className="font-serif text-xl tracking-tight">EchoMind</span>
        </Link>
        <nav className="flex items-center gap-1 text-sm">
          <NavLink to="/">Search</NavLink>
          <NavLink to="/capture">Capture</NavLink>
          <NavLink to="/upload">AI Upload</NavLink>
          <div
            className="ml-3 flex items-center gap-2 text-xs text-muted-foreground"
            title={
              ok
                ? `Connected to ${API_BASE_URL}`
                : `Cannot reach ${API_BASE_URL}. Is your backend running?`
            }
          >
            <span
              className={`inline-block h-2 w-2 rounded-full ${
                ok ? "bg-emerald-500" : "bg-rose-500"
              }`}
            />
            {ok ? "online" : "offline"}
          </div>
        </nav>
      </div>
    </header>
  );
}

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  return (
    <Link
      to={to}
      className="px-3 py-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
      activeProps={{ className: "px-3 py-2 rounded-md text-foreground bg-accent" }}
      activeOptions={{ exact: true }}
    >
      {children}
    </Link>
  );
}
