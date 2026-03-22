# RAG Frontend UI Design

## Goal

Add a focused React frontend for the RAG Agent project so a user can upload a document, ask a question, and inspect the sources behind the answer from a single page.

## Approval Baseline

This design treats the Linear ticket description as the approved product brief because the session is unattended. Any ambiguity is handled through documented assumptions and defensive implementation rather than expanded scope.

## Approaches Considered

### 1. Root-level Vite app with lightweight component state

- Keeps `npm run build` at the repository root, matching the ticket acceptance criteria.
- Minimizes moving pieces because the current repo has no frontend package yet.
- Recommended because it delivers the requested UI with the least structural churn.

### 2. Nested `frontend/` package inside the repo

- Creates stronger separation between backend and frontend concerns.
- Would require extra wrapper scripts or directory-specific instructions to satisfy root-level build expectations.
- Rejected because the added indirection does not buy much for a single-page app.

### 3. Server-rendered HTML from FastAPI

- Avoids introducing a Node toolchain.
- Conflicts with the explicit React + Vite requirement and weakens future frontend iteration.
- Rejected because it misses the specified stack.

## Selected Design

- Add a root-level Vite + React + TypeScript app with Tailwind CSS.
- Keep the interface on a single route, rendered by `src/App.tsx`.
- Use a small `api.ts` helper to isolate request formatting, response normalization, and human-readable error extraction.
- Model the page as two primary sections inside one centered shell:
  - Document upload with file input, upload CTA, and result banners.
  - Q&A form with question input, loading CTA, answer panel, and expandable sources list.
- Use a refined minimal aesthetic: warm-tinted neutrals, a crisp blue action color, and subtle editorial spacing rather than generic stacked cards.

## Component and Data Flow

- `App.tsx` owns the main page state and coordinates both forms.
- `uploadDocument(file)` sends `FormData` to `POST /documents` and returns a normalized `{ filename, chunkCount }`.
- `queryDocuments(question)` sends JSON to `POST /query` and returns a normalized `{ answer, sources[] }`.
- Source rows stay collapsed by default and expand inline so the answer remains scannable.
- Local validation handles missing question text and empty files before making network calls.

## Error Handling

- Upload and query actions each clear stale success state before a new submission.
- Network or backend failures render concise red error banners near the relevant section.
- Response normalization falls back across likely field names to avoid brittle UI failures during local integration.
- Buttons disable while the matching request is in flight.

## Testing Strategy

- Start with failing UI tests for the empty upload validation, successful upload feedback, loading/answer rendering, and source expansion.
- Mock `fetch` directly in Vitest so the tests stay fast and deterministic.
- Finish with `npm run test -- --run` and `npm run build` as the required verification pair.
