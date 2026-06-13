import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { searchMemory, type SearchResponse, type DecisionCase } from "@/lib/api";
import { SiteHeader } from "@/components/SiteHeader";
import { AmbientScene } from "@/components/AmbientScene";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Lightbulb, BookOpen, Loader2, ChevronDown } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "EchoMind — Search expert decisions" },
      {
        name: "description",
        content:
          "Ask EchoMind a problem and surface what senior experts decided in similar past situations.",
      },
      { property: "og:title", content: "EchoMind — Search expert decisions" },
      {
        property: "og:description",
        content:
          "Ask EchoMind a problem and surface what senior experts decided in similar past situations.",
      },
    ],
  }),
  component: SearchPage,
});

function SearchPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<SearchResponse | null>(null);

  const mutation = useMutation({
    mutationFn: searchMemory,
    onSuccess: (data) => setResult(data),
    onError: (err: Error) => toast.error(err.message),
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    mutation.mutate(query.trim());
  }

  return (
    <div className="relative min-h-screen bg-background overflow-hidden">
      <AmbientScene />
      <SiteHeader />
      <main className="relative z-10 mx-auto max-w-3xl px-6 py-16">
        <div className="relative text-center mb-10 rounded-[2rem] border border-border/60 bg-background/72 px-6 py-10 shadow-2xl shadow-primary/10 backdrop-blur-lg">
          <h1 className="font-serif text-5xl md:text-6xl tracking-tight text-foreground">
            Ask the memory.
          </h1>
          <p className="mt-4 text-muted-foreground text-lg">
            Describe a problem. EchoMind surfaces what senior experts decided when it
            mattered.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="relative space-y-3">
          <Textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Abnormal vibration on Conveyor Belt B after maintenance…"
            rows={4}
            className="resize-none text-base bg-card/70 backdrop-blur-md border-border/70 shadow-sm"
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                e.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">⌘/Ctrl + Enter to search</span>
            <Button type="submit" disabled={mutation.isPending || !query.trim()} size="lg">
              {mutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" /> Searching…
                </>
              ) : (
                "Search Memory"
              )}
            </Button>
          </div>
        </form>

        {mutation.isPending && <ResultsSkeleton />}
        {result && !mutation.isPending && <Results result={result} />}
      </main>
    </div>
  );
}

function ResultsSkeleton() {
  return (
    <div className="mt-12 space-y-6 animate-pulse">
      <div className="h-32 rounded-xl bg-muted" />
      <div className="h-20 rounded-xl bg-muted" />
      <div className="h-20 rounded-xl bg-muted" />
    </div>
  );
}

function Results({ result }: { result: SearchResponse }) {
  return (
    <div className="mt-12 space-y-8">
      <section className="rounded-2xl border border-border bg-card p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-3 text-sm font-medium text-muted-foreground uppercase tracking-wider">
          <Lightbulb className="h-4 w-4" />
          AI Recommendation
        </div>
        <p className="text-lg leading-relaxed whitespace-pre-wrap text-foreground">
          {result.recommendation}
        </p>
      </section>

      <section>
        <div className="flex items-center gap-2 mb-4 text-sm font-medium text-muted-foreground uppercase tracking-wider">
          <BookOpen className="h-4 w-4" />
          Historical Evidence ({result.cases.length})
        </div>
        <div className="space-y-3">
          {result.cases.map((c) => (
            <CaseCard key={c.id} c={c} />
          ))}
          {result.cases.length === 0 && (
            <p className="text-muted-foreground text-sm">No past cases matched.</p>
          )}
        </div>
      </section>
    </div>
  );
}

function CaseCard({ c }: { c: DecisionCase }) {
  return (
    <Collapsible className="rounded-xl border border-border bg-card overflow-hidden group">
      <CollapsibleTrigger className="w-full text-left p-4 flex items-start justify-between gap-3 hover:bg-accent/40 transition-colors">
        <div className="min-w-0">
          <p className="font-medium text-foreground line-clamp-1">{c.problem_description}</p>
          <p className="text-xs text-muted-foreground mt-1">
            {new Date(c.created_at).toLocaleDateString()}
          </p>
        </div>
        <ChevronDown className="h-4 w-4 text-muted-foreground transition-transform group-data-[state=open]:rotate-180 shrink-0 mt-1" />
      </CollapsibleTrigger>
      <CollapsibleContent className="px-4 pb-4 pt-0 space-y-3 text-sm">
        <Field label="Context" value={c.context} />
        <Field label="Options considered" value={c.options_considered} />
        <Field label="Decision taken" value={c.decision_taken} highlight />
        <Field label="Reasoning" value={c.reasoning} />
        <Field label="Outcome" value={c.outcome} />
      </CollapsibleContent>
    </Collapsible>
  );
}

function Field({
  label,
  value,
  highlight,
}: {
  label: string;
  value?: string;
  highlight?: boolean;
}) {
  if (!value) return null;
  return (
    <div>
      <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">
        {label}
      </div>
      <p
        className={`whitespace-pre-wrap ${
          highlight ? "text-foreground font-medium" : "text-foreground/80"
        }`}
      >
        {value}
      </p>
    </div>
  );
}
