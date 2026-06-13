import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import type { CaptureInput } from "@/lib/api";
import { Loader2 } from "lucide-react";

interface Props {
  initial?: Partial<CaptureInput>;
  submitLabel: string;
  pending: boolean;
  onSubmit: (data: CaptureInput) => void;
  secondaryAction?: React.ReactNode;
}

const empty: CaptureInput = {
  problem_description: "",
  decision_taken: "",
  reasoning: "",
  context: "",
  options_considered: "",
  outcome: "",
};

export function DecisionForm({
  initial,
  submitLabel,
  pending,
  onSubmit,
  secondaryAction,
}: Props) {
  const [form, setForm] = useState<CaptureInput>({ ...empty, ...initial });

  useEffect(() => {
    setForm({ ...empty, ...initial });
  }, [initial]);

  function update<K extends keyof CaptureInput>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({
      problem_description: form.problem_description.trim(),
      decision_taken: form.decision_taken.trim(),
      reasoning: form.reasoning.trim(),
      context: form.context?.trim() || undefined,
      options_considered: form.options_considered?.trim() || undefined,
      outcome: form.outcome?.trim() || undefined,
    });
  }

  const valid =
    form.problem_description.trim() &&
    form.decision_taken.trim() &&
    form.reasoning.trim();

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Field label="Problem description" required>
        <Textarea
          required
          rows={3}
          value={form.problem_description}
          onChange={(e) => update("problem_description", e.target.value)}
          placeholder="What problem came up?"
        />
      </Field>

      <Field label="Context" hint="optional">
        <Textarea
          rows={2}
          value={form.context}
          onChange={(e) => update("context", e.target.value)}
          placeholder="Surrounding circumstances, constraints…"
        />
      </Field>

      <Field label="Options considered" hint="optional">
        <Textarea
          rows={2}
          value={form.options_considered}
          onChange={(e) => update("options_considered", e.target.value)}
          placeholder="Alternatives that were on the table"
        />
      </Field>

      <Field label="Decision taken" required>
        <Textarea
          required
          rows={2}
          value={form.decision_taken}
          onChange={(e) => update("decision_taken", e.target.value)}
          placeholder="What did the expert decide to do?"
        />
      </Field>

      <Field label="Reasoning / intuition" required>
        <Textarea
          required
          rows={3}
          value={form.reasoning}
          onChange={(e) => update("reasoning", e.target.value)}
          placeholder="Why this decision? What signals or experience drove it?"
        />
      </Field>

      <Field label="Outcome" hint="optional">
        <Input
          value={form.outcome}
          onChange={(e) => update("outcome", e.target.value)}
          placeholder="What actually happened?"
        />
      </Field>

      <div className="flex items-center justify-end gap-3 pt-2">
        {secondaryAction}
        <Button type="submit" disabled={!valid || pending} size="lg">
          {pending ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Saving…
            </>
          ) : (
            submitLabel
          )}
        </Button>
      </div>
    </form>
  );
}

function Field({
  label,
  required,
  hint,
  children,
}: {
  label: string;
  required?: boolean;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-2">
      <Label className="flex items-baseline gap-2">
        <span>{label}</span>
        {required && <span className="text-rose-500 text-xs">required</span>}
        {hint && <span className="text-muted-foreground text-xs">{hint}</span>}
      </Label>
      {children}
    </div>
  );
}
