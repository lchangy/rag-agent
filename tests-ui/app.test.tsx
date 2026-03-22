import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";

const originalFetch = global.fetch;

describe("RAG Agent frontend", () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    global.fetch = originalFetch;
  });

  it("shows an error when uploading an empty document", async () => {
    const user = userEvent.setup();

    render(<App />);

    const fileInput = screen.getByLabelText(/choose a document/i);
    const uploadButton = screen.getByRole("button", { name: /upload/i });
    const emptyFile = new File([""], "empty.txt", { type: "text/plain" });

    await user.upload(fileInput, emptyFile);
    await user.click(uploadButton);

    expect(screen.getByText(/empty files cannot be uploaded/i)).toBeInTheDocument();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it("rejects unsupported file types before upload", async () => {
    const user = userEvent.setup({ applyAccept: false });

    render(<App />);

    const fileInput = screen.getByLabelText(/choose a document/i);
    const uploadButton = screen.getByRole("button", { name: /upload/i });

    await user.upload(fileInput, new File(["binary"], "photo.png", { type: "image/png" }));
    await user.click(uploadButton);

    expect(screen.getByText(/only pdf and txt files are supported/i)).toBeInTheDocument();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it.each([
    ["notes.txt", "text/plain"],
    ["manual.pdf", "application/pdf"],
  ])("uploads %s and shows the created chunk count", async (filename, type) => {
    const user = userEvent.setup();

    vi.mocked(global.fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ filename, chunks_created: 4 }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    render(<App />);

    const fileInput = screen.getByLabelText(/choose a document/i);
    await user.upload(fileInput, new File(["sample body"], filename, { type }));
    await user.click(screen.getByRole("button", { name: /upload/i }));

    await waitFor(() => {
      expect(screen.getByText(`Uploaded ${filename}, 4 chunks created`)).toBeInTheDocument();
    });
  });

  it("shows a loading state, answer text, and expandable sources during a query", async () => {
    const user = userEvent.setup();
    let resolveQuery: ((response: Response) => void) | undefined;

    vi.mocked(global.fetch).mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolveQuery = resolve;
        }),
    );

    render(<App />);

    const questionInput = screen.getByLabelText(/ask a question about your documents/i);
    await user.type(questionInput, "What does the document say?");
    await user.click(screen.getByRole("button", { name: /^ask$/i }));

    expect(screen.getByRole("button", { name: /thinking/i })).toBeDisabled();
    expect(screen.getByText(/searching your documents/i)).toBeInTheDocument();

    resolveQuery?.(
      new Response(
        JSON.stringify({
          answer: "The document explains how retrieval works.",
          sources: [
            {
              filename: "notes.txt",
              content:
                "Retrieval augmented generation combines semantic search with model reasoning to answer grounded questions for a user.",
              score: 0.91234,
            },
          ],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    await waitFor(() => {
      expect(screen.getByText(/the document explains how retrieval works/i)).toBeInTheDocument();
    });

    expect(
      screen.queryByText(/retrieval augmented generation combines semantic search/i),
    ).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /notes.txt/i }));

    expect(
      screen.getByText(/retrieval augmented generation combines semantic search/i),
    ).toBeInTheDocument();
    expect(screen.getByText(/relevance score 0.912/i)).toBeInTheDocument();
  });

  it("ignores duplicate query submits while a request is already in flight", async () => {
    const user = userEvent.setup();
    let resolveQuery: ((response: Response) => void) | undefined;

    vi.mocked(global.fetch).mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveQuery = resolve;
        }),
    );

    render(<App />);

    const questionInput = screen.getByLabelText(/ask a question about your documents/i);
    await user.type(questionInput, "Summarize the notes");
    await user.click(screen.getByRole("button", { name: /^ask$/i }));

    fireEvent.submit(questionInput.closest("form")!);

    expect(global.fetch).toHaveBeenCalledTimes(1);

    resolveQuery?.(
      new Response(JSON.stringify({ answer: "Summary", sources: [] }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await waitFor(() => {
      expect(screen.getByText("Summary")).toBeInTheDocument();
    });
  });

  it("shows a friendly upload error for non-json server failures", async () => {
    const user = userEvent.setup();

    vi.mocked(global.fetch).mockResolvedValueOnce(
      new Response("server exploded", {
        status: 500,
        headers: { "Content-Type": "text/plain" },
      }),
    );

    render(<App />);

    const fileInput = screen.getByLabelText(/choose a document/i);
    await user.upload(fileInput, new File(["sample body"], "notes.txt", { type: "text/plain" }));
    await user.click(screen.getByRole("button", { name: /upload/i }));

    await waitFor(() => {
      expect(screen.getByText(/unable to upload the document/i)).toBeInTheDocument();
    });
  });

  it("falls back to a friendly query error when the server returns malformed json", async () => {
    const user = userEvent.setup();

    vi.mocked(global.fetch).mockResolvedValueOnce(
      new Response("{not valid json", {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }),
    );

    render(<App />);

    const questionInput = screen.getByLabelText(/ask a question about your documents/i);
    await user.type(questionInput, "What failed?");
    await user.click(screen.getByRole("button", { name: /^ask$/i }));

    await waitFor(() => {
      expect(screen.getByText(/unable to answer the question/i)).toBeInTheDocument();
    });
  });
});
