import { createFileRoute } from "@tanstack/react-router";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { captureDecision } from "@/lib/api";
import { SiteHeader } from "@/components/SiteHeader";
import { AmbientScene } from "@/components/AmbientScene";
import { DecisionForm } from "@/components/DecisionForm";
import { toast } from "sonner";

export const Route = createFileRoute("/capture")({
  head: () => ({
    meta: [
      { title: "Capture a decision — EchoMind" },
      {
        name: "description",
        content: "Manually log an expert decision and the reasoning behind it.",
      },
      { property: "og:title", content: "Capture a decision — EchoMind" },
      {
        property: "og:description",
        content: "Manually log an expert decision and the reasoning behind it.",
      },
    ],
  }),
  component: CapturePage,
});

function CapturePage() {
  const [resetKey, setResetKey] = useState(0);
  const mutation = useMutation({
    mutationFn: captureDecision,
    onSuccess: (data) => {
      toast.success("Saved to EchoMind", { description: `Decision ${data.decision_id}` });
      setResetKey((k) => k + 1);
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <div className="relative min-h-screen bg-background overflow-hidden">
      <AmbientScene variant="subtle" />
      <SiteHeader />
      <main className="relative z-10 mx-auto max-w-2xl px-6 py-14">
        <div className="mb-8 rounded-3xl border border-border/60 bg-background/60 px-6 py-8 shadow-xl shadow-primary/5 backdrop-blur-lg">
          <h1 className="font-serif text-4xl tracking-tight">Log a decision</h1>
          <p className="mt-2 text-muted-foreground">
            Capture an expert's call and the reasoning behind it, so the next person can find
            it.
          </p>
        </div>
        <div className="rounded-3xl border border-border/60 bg-card/65 p-6 md:p-8 shadow-xl shadow-primary/5 backdrop-blur-lg">
          <DecisionForm
            key={resetKey}
            submitLabel="Save to EchoMind"
            pending={mutation.isPending}
            onSubmit={(data) => mutation.mutate(data)}
          />
        </div>
      </main>
    </div>
  );
}
