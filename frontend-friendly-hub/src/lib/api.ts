export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000";

export interface DecisionCase {
  id: string;
  problem_description: string;
  context?: string;
  decision_taken: string;
  reasoning: string;
  outcome?: string;
  options_considered?: string;
  created_at: string;
}

export interface SearchResponse {
  recommendation: string;
  cases: DecisionCase[];
}

export interface CaptureInput {
  problem_description: string;
  decision_taken: string;
  reasoning: string;
  context?: string;
  options_considered?: string;
  outcome?: string;
}

export interface CaptureResponse {
  success: boolean;
  decision_id: string;
}

export interface ExtractedData {
  problem_description: string;
  context?: string;
  options_considered?: string;
  decision_taken: string;
  reasoning: string;
  outcome?: string;
}

export interface UploadResponse {
  success: boolean;
  data: ExtractedData;
}

export interface HealthResponse {
  status: string;
  openai: boolean;
  supabase: boolean;
  pinecone: boolean;
}

async function handle<T>(res: Response): Promise<T> {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error((data as { detail?: string }).detail ?? `Request failed (${res.status})`);
  }
  return data as T;
}

export async function searchMemory(query: string): Promise<SearchResponse> {
  const res = await fetch(`${API_BASE_URL}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  return handle<SearchResponse>(res);
}

export async function captureDecision(input: CaptureInput): Promise<CaptureResponse> {
  const res = await fetch(`${API_BASE_URL}/api/capture`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  return handle<CaptureResponse>(res);
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });
  return handle<UploadResponse>(res);
}

export async function confirmExtracted(input: CaptureInput): Promise<CaptureResponse> {
  const res = await fetch(`${API_BASE_URL}/api/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  return handle<CaptureResponse>(res);
}

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/health`);
  return handle<HealthResponse>(res);
}
