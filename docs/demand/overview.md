# RAG Agent Demand Overview

## Scope v1

- Keep the existing FastAPI + PostgreSQL backend bootstrap intact as the API host for local development.
- Add a React + Vite frontend at the repository root so `npm run build` works from the same workspace.
- Support document upload for `.pdf` and `.txt` files through `POST /documents`.
- Support question answering through `POST /query` with answer text and expandable source details.
- Deliver a clean Tailwind-based single-page UI that remains readable on both mobile and desktop widths.

## Not Doing

- No authentication, user accounts, or persisted chat history.
- No drag-and-drop upload, progress bars, or multi-file queue management.
- No document library browser, delete flow, or upload history.
- No markdown rendering, citation highlighting, or answer streaming.
- No deployment pipeline changes beyond a local Vite build.

## Key Flows

1. A user opens `/`, reads the short product description, and uploads a supported document.
2. The UI posts the file to `POST /documents`, then shows a green success banner with the filename and chunk count.
3. The UI rejects an empty file locally and surfaces backend upload failures in a red error banner.
4. A user enters a question, submits it, sees a loading state, and then reads the answer below the form.
5. A user expands a source row to inspect the filename, chunk preview, and relevance score that informed the answer.

## Data and Boundaries

- The frontend owns transient UI state only: selected file, form inputs, loading flags, result payloads, and error messages.
- The backend remains the source of truth for document processing and answer generation.
- The frontend should normalize a small set of likely API field aliases so it can tolerate minor response-shape drift during local development.
- API calls target `http://localhost:8000` by default, with an env override for `VITE_API_BASE_URL`.

## Integrations

- FastAPI backend running locally at `http://localhost:8000`.
- Vite + React for the frontend runtime and build.
- Tailwind CSS for layout, spacing, and component styling.
- Vitest + Testing Library for targeted UI behavior verification.

## Assumptions

- The upload endpoint accepts `multipart/form-data` with the file under a `file` field.
- The query endpoint accepts JSON with a `question` field.
- Upload responses include a filename and chunk count, but the exact chunk-count field name may vary.
- Query responses include answer text plus a `sources` array containing filename/content/score-style fields.
- The unattended ticket description is sufficiently specific to treat the outlined UX as approved scope.

## Risks

- The backend contract is not fully documented in this repository, so the frontend needs defensive response parsing and clear error handling.
- Because the repository already contains backend-only files at the root, Node and Python tooling must coexist cleanly.
- The UI should stay polished without overshooting the intentionally minimal product brief.

## Validation Notes

- Baseline proof before implementation: `npm run build` fails because `package.json` does not exist yet.
- Frontend proof after implementation: `npm run test -- --run`
- Build proof after implementation: `npm run build`
- Runtime proof after implementation: `npm run dev` with the local API available at `http://localhost:8000`
