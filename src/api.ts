const DEFAULT_API_BASE_URL = "http://localhost:8000";

type JsonRecord = Record<string, unknown>;

export interface UploadResult {
  filename: string;
  chunkCount: number;
}

export interface Source {
  filename: string;
  preview: string;
  score: number | null;
}

export interface QueryResult {
  answer: string;
  sources: Source[];
}

function getApiBaseUrl(): string {
  const envBaseUrl = import.meta.env.VITE_API_BASE_URL;
  return typeof envBaseUrl === "string" && envBaseUrl.trim() ? envBaseUrl : DEFAULT_API_BASE_URL;
}

async function parseJson(response: Response): Promise<JsonRecord> {
  const contentType = response.headers.get("Content-Type") ?? "";

  if (!contentType.includes("application/json")) {
    return {};
  }

  try {
    const body = (await response.json()) as unknown;
    return isRecord(body) ? body : {};
  } catch {
    return {};
  }
}

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null;
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function asNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }

  return null;
}

function extractErrorMessage(payload: JsonRecord, fallback: string): string {
  const detail = payload.detail;
  const message = payload.message;
  const error = payload.error;

  if (isNonEmptyString(detail)) {
    return detail;
  }

  if (isNonEmptyString(message)) {
    return message;
  }

  if (isNonEmptyString(error)) {
    return error;
  }

  return fallback;
}

function normalizeUpload(payload: JsonRecord, fallbackFilename: string): UploadResult {
  const filename =
    (isNonEmptyString(payload.filename) && payload.filename) ||
    (isRecord(payload.document) && isNonEmptyString(payload.document.filename) && payload.document.filename) ||
    fallbackFilename;

  const chunkCount =
    asNumber(payload.chunk_count) ??
    asNumber(payload.chunks_created) ??
    asNumber(payload.chunkCount) ??
    asNumber(payload.chunks) ??
    asNumber(payload.n_chunks);

  if (chunkCount === null) {
    throw new Error("The upload response did not include a chunk count.");
  }

  return { filename, chunkCount };
}

function normalizeSource(source: unknown, index: number): Source {
  const record = isRecord(source) ? source : {};
  const filename =
    (isNonEmptyString(record.filename) && record.filename) ||
    (isNonEmptyString(record.document_name) && record.document_name) ||
    `Source ${index + 1}`;
  const rawPreview =
    (isNonEmptyString(record.preview) && record.preview) ||
    (isNonEmptyString(record.content) && record.content) ||
    (isNonEmptyString(record.chunk) && record.chunk) ||
    (isNonEmptyString(record.text) && record.text) ||
    "";

  return {
    filename,
    preview: rawPreview.slice(0, 100),
    score:
      asNumber(record.score) ??
      asNumber(record.relevance_score) ??
      asNumber(record.relevance) ??
      null,
  };
}

function normalizeQuery(payload: JsonRecord): QueryResult {
  const answer =
    (isNonEmptyString(payload.answer) && payload.answer) ||
    (isNonEmptyString(payload.response) && payload.response) ||
    (isNonEmptyString(payload.text) && payload.text) ||
    "";

  if (!answer) {
    throw new Error("The query response did not include answer text.");
  }

  const rawSources = Array.isArray(payload.sources) ? payload.sources : [];

  return {
    answer,
    sources: rawSources.map(normalizeSource),
  };
}

export async function uploadDocument(file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${getApiBaseUrl()}/documents`, {
    method: "POST",
    body: formData,
  });
  const payload = await parseJson(response);

  if (!response.ok) {
    throw new Error(extractErrorMessage(payload, "Unable to upload the document."));
  }

  return normalizeUpload(payload, file.name);
}

export async function queryDocuments(question: string): Promise<QueryResult> {
  const response = await fetch(`${getApiBaseUrl()}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });
  const payload = await parseJson(response);

  if (!response.ok) {
    throw new Error(extractErrorMessage(payload, "Unable to answer the question."));
  }

  return normalizeQuery(payload);
}
