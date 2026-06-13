import { createFileRoute } from "@tanstack/react-router";
import { useMutation } from "@tanstack/react-query";
import { useState, useRef } from "react";
import { uploadDocument, confirmExtracted, type ExtractedData } from "@/lib/api";
import { SiteHeader } from "@/components/SiteHeader";
import { AmbientScene } from "@/components/AmbientScene";
import { DecisionForm } from "@/components/DecisionForm";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Upload, FileText, Loader2, RotateCcw } from "lucide-react";

export const Route = createFileRoute("/upload")({
  head: () => ({
    meta: [
      { title: "AI Upload — EchoMind" },
      {
        name: "description",
        content:
          "Upload a .txt or .pdf and let AI extract the structured decision before you confirm.",
      },
      { property: "og:title", content: "AI Upload — EchoMind" },
      {
        property: "og:description",
        content:
          "Upload a .txt or .pdf and let AI extract the structured decision before you confirm.",
      },
    ],
  }),
  component: UploadPage,
});

function UploadPage() {
  const [extracted, setExtracted] = useState<ExtractedData | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const uploadMut = useMutation({
    mutationFn: uploadDocument,
    onSuccess: (res) => {
      setExtracted(res.data);
      toast.success("Knowledge extracted — review below");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const confirmMut = useMutation({
    mutationFn: confirmExtracted,
    onSuccess: (res) => {
      toast.success("Saved to EchoMind", { description: `Decision ${res.decision_id}` });
      reset();
    },
    onError: (err: Error) => toast.error(err.message),
  });

  function handleFiles(files: FileList | null) {
    const file = files?.[0];
    if (!file) return;
    setFileName(file.name);
    uploadMut.mutate(file);
  }

  function reset() {
    setExtracted(null);
    setFileName(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div className="relative min-h-screen bg-background overflow-hidden">
      <AmbientScene variant="subtle" />
      <SiteHeader />
      <main className="relative z-10 mx-auto max-w-2xl px-6 py-14">
        <div className="mb-8 rounded-3xl border border-border/60 bg-background/60 px-6 py-8 shadow-xl shadow-primary/5 backdrop-blur-lg">
          <h1 className="font-serif text-4xl tracking-tight">
            {extracted ? "Review extracted data" : "Upload a document"}
          </h1>
          <p className="mt-2 text-muted-foreground">
            {extracted
              ? "Edit anything that looks off, then save it to EchoMind."
              : "Drop a .txt or .pdf and we'll extract the structured decision for you."}
          </p>
        </div>

        {!extracted && (
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              handleFiles(e.dataTransfer.files);
            }}
            className={`rounded-3xl border-2 border-dashed p-12 text-center transition-colors backdrop-blur-lg shadow-xl shadow-primary/5 ${
              dragOver ? "border-foreground bg-accent/60" : "border-border/70 bg-card/65"
            }`}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".txt,.pdf"
              className="hidden"
              onChange={(e) => handleFiles(e.target.files)}
            />

            {uploadMut.isPending ? (
              <div className="flex flex-col items-center gap-3 text-muted-foreground">
                <Loader2 className="h-8 w-8 animate-spin" />
                <p>Extracting knowledge from {fileName}…</p>
              </div>
            ) : (
              <>
                <Upload className="h-10 w-10 mx-auto text-muted-foreground" />
                <p className="mt-4 text-foreground font-medium">
                  Drop a .txt or .pdf here
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  or click below to choose a file
                </p>
                <Button
                  type="button"
                  className="mt-6"
                  onClick={() => inputRef.current?.click()}
                >
                  Choose file
                </Button>
              </>
            )}
          </div>
        )}

        {extracted && (
          <div className="rounded-3xl border border-border/60 bg-card/65 p-6 md:p-8 shadow-xl shadow-primary/5 backdrop-blur-lg">
            {fileName && (
              <div className="mb-6 flex items-center gap-2 text-sm text-muted-foreground">
                <FileText className="h-4 w-4" />
                {fileName}
              </div>
            )}
            <DecisionForm
              initial={extracted}
              submitLabel="Confirm & save"
              pending={confirmMut.isPending}
              onSubmit={(data) => confirmMut.mutate(data)}
              secondaryAction={
                <Button type="button" variant="ghost" onClick={reset}>
                  <RotateCcw className="h-4 w-4" /> Start over
                </Button>
              }
            />
          </div>
        )}
      </main>
    </div>
  );
}
