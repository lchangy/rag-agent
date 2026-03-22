import { FormEvent, useState } from "react";

import { queryDocuments, uploadDocument, type QueryResult, type UploadResult } from "./api";

const SUPPORTED_DOCUMENT_EXTENSIONS = [".pdf", ".txt"] as const;

function formatScore(score: number | null): string {
  if (score === null) {
    return "Relevance score unavailable";
  }

  return `Relevance score ${score.toFixed(3)}`;
}

function isSupportedDocument(file: File): boolean {
  const normalizedName = file.name.toLowerCase();

  return SUPPORTED_DOCUMENT_EXTENSIONS.some((extension) => normalizedName.endsWith(extension));
}

export default function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [uploadError, setUploadError] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  const [question, setQuestion] = useState("");
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [queryError, setQueryError] = useState("");
  const [isQuerying, setIsQuerying] = useState(false);
  const [openSourceIndex, setOpenSourceIndex] = useState<number | null>(null);

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (isUploading) {
      return;
    }

    setUploadError("");
    setUploadResult(null);

    if (!selectedFile) {
      setUploadError("Choose a PDF or TXT file to upload.");
      return;
    }

    if (selectedFile.size === 0) {
      setUploadError("Empty files cannot be uploaded.");
      return;
    }

    if (!isSupportedDocument(selectedFile)) {
      setUploadError("Only PDF and TXT files are supported.");
      return;
    }

    setIsUploading(true);

    try {
      const result = await uploadDocument(selectedFile);
      setUploadResult(result);
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : "Unable to upload the document.");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleQuery(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (isQuerying) {
      return;
    }

    setQueryError("");
    setQueryResult(null);
    setOpenSourceIndex(null);

    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) {
      setQueryError("Enter a question before asking.");
      return;
    }

    setIsQuerying(true);

    try {
      const result = await queryDocuments(trimmedQuestion);
      setQueryResult(result);
    } catch (error) {
      setQueryError(error instanceof Error ? error.message : "Unable to answer the question.");
    } finally {
      setIsQuerying(false);
    }
  }

  return (
    <main className="min-h-screen bg-canvas px-6 py-10 font-body text-ink">
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-80 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.14),_transparent_55%)]"
        aria-hidden="true"
      />

      <div className="relative mx-auto max-w-[40rem]">
        <section className="overflow-hidden rounded-[28px] border border-white/80 bg-white shadow-shell">
          <header className="border-b border-line/70 px-8 pb-6 pt-8">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-primary">RAG workspace</p>
            <h1 className="mt-4 font-display text-4xl leading-tight text-ink sm:text-[2.8rem]">RAG Agent</h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-muted sm:text-base">
              Upload a document, ask a grounded question, and inspect the source chunks behind the answer.
            </p>
          </header>

          <div className="space-y-10 px-8 py-8">
            <section aria-labelledby="upload-heading" className="space-y-4">
              <div className="flex items-baseline justify-between gap-4">
                <div>
                  <h2 id="upload-heading" className="text-lg font-semibold text-ink">
                    Document Upload
                  </h2>
                  <p className="mt-1 text-sm leading-6 text-muted">
                    Send a PDF or TXT file to the local RAG API for chunking.
                  </p>
                </div>
              </div>

              <form className="space-y-4" onSubmit={handleUpload}>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-ink" htmlFor="document-upload">
                    Choose a document
                  </label>
                  <input
                    id="document-upload"
                    type="file"
                    accept=".pdf,.txt"
                    className="block w-full rounded-2xl border border-line bg-canvas px-4 py-3 text-sm text-ink file:mr-4 file:rounded-xl file:border-0 file:bg-white file:px-3 file:py-2 file:font-medium file:text-ink hover:file:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-primary/30"
                    onChange={(event) => {
                      setUploadError("");
                      setUploadResult(null);
                      setSelectedFile(event.target.files?.[0] ?? null);
                    }}
                  />
                </div>

                <button
                  type="submit"
                  className="inline-flex min-w-32 items-center justify-center rounded-full bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 focus:outline-none focus:ring-4 focus:ring-primary/20 disabled:cursor-not-allowed disabled:bg-blue-300"
                  disabled={isUploading}
                >
                  {isUploading ? "Uploading..." : "Upload"}
                </button>
              </form>

              {uploadError ? (
                <p className="rounded-2xl border border-danger/15 bg-dangerBg px-4 py-3 text-sm font-medium text-danger">
                  {uploadError}
                </p>
              ) : null}

              {uploadResult ? (
                <p className="rounded-2xl border border-success/15 bg-successBg px-4 py-3 text-sm font-medium text-success">
                  Uploaded {uploadResult.filename}, {uploadResult.chunkCount} chunks created
                </p>
              ) : null}
            </section>

            <section aria-labelledby="qa-heading" className="space-y-4 border-t border-line/70 pt-8">
              <div>
                <h2 id="qa-heading" className="text-lg font-semibold text-ink">
                  Q&amp;A
                </h2>
                <p className="mt-1 text-sm leading-6 text-muted">
                  Ask a question and review the passages the backend considered most relevant.
                </p>
              </div>

              <form className="space-y-4" onSubmit={handleQuery}>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-ink" htmlFor="question">
                    Ask a question about your documents
                  </label>
                  <input
                    id="question"
                    type="text"
                    value={question}
                    onChange={(event) => {
                      setQuestion(event.target.value);
                      setQueryError("");
                    }}
                    placeholder="Ask a question about your documents"
                    className="w-full rounded-2xl border border-line bg-canvas px-4 py-3 text-sm text-ink placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-primary/30"
                  />
                </div>

                <button
                  type="submit"
                  className="inline-flex min-w-32 items-center justify-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 focus:outline-none focus:ring-4 focus:ring-primary/20 disabled:cursor-not-allowed disabled:bg-blue-300"
                  disabled={isQuerying}
                >
                  {isQuerying ? (
                    <>
                      <span
                        className="h-4 w-4 animate-spin rounded-full border-2 border-white/45 border-t-white"
                        aria-hidden="true"
                      />
                      Thinking...
                    </>
                  ) : (
                    "Ask"
                  )}
                </button>
              </form>

              {isQuerying ? <p className="text-sm font-medium text-muted">Searching your documents...</p> : null}

              {queryError ? (
                <p className="rounded-2xl border border-danger/15 bg-dangerBg px-4 py-3 text-sm font-medium text-danger">
                  {queryError}
                </p>
              ) : null}

              {queryResult ? (
                <article className="space-y-5 rounded-[24px] bg-slate-950 px-5 py-5 text-slate-50">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-200/80">Answer</p>
                    <p className="mt-3 text-sm leading-7 text-slate-100 sm:text-[0.96rem]">{queryResult.answer}</p>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between gap-3">
                      <h3 className="text-sm font-semibold text-white">Sources</h3>
                      <span className="text-xs uppercase tracking-[0.24em] text-sky-200/70">
                        {queryResult.sources.length} linked
                      </span>
                    </div>

                    {queryResult.sources.length ? (
                      <ul className="space-y-3">
                        {queryResult.sources.map((source, index) => {
                          const isOpen = openSourceIndex === index;

                          return (
                            <li key={`${source.filename}-${index}`} className="rounded-2xl bg-white/8 p-3">
                              <button
                                type="button"
                                className="flex w-full items-start justify-between gap-3 text-left"
                                onClick={() => setOpenSourceIndex(isOpen ? null : index)}
                              >
                                <div>
                                  <p className="text-sm font-semibold text-white">{source.filename}</p>
                                  <p className="mt-1 text-xs text-sky-100/70">{formatScore(source.score)}</p>
                                </div>
                                <span className="pt-0.5 text-xs font-semibold uppercase tracking-[0.22em] text-sky-100/70">
                                  {isOpen ? "Hide" : "Open"}
                                </span>
                              </button>

                              {isOpen ? (
                                <p className="mt-3 border-t border-white/10 pt-3 text-sm leading-6 text-slate-200">
                                  {source.preview}
                                  {source.preview.length === 100 ? "..." : ""}
                                </p>
                              ) : null}
                            </li>
                          );
                        })}
                      </ul>
                    ) : (
                      <p className="rounded-2xl bg-white/8 px-4 py-3 text-sm text-slate-200">
                        No sources were returned for this answer.
                      </p>
                    )}
                  </div>
                </article>
              ) : null}
            </section>
          </div>
        </section>
      </div>
    </main>
  );
}
