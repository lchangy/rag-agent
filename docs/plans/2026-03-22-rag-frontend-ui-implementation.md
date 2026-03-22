# RAG Frontend UI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the repository's first React + Vite frontend for document upload and question answering.

**Architecture:** Add a root-level Vite + React + TypeScript application that coexists with the existing Python backend. Keep API access isolated in a small client module, render a single-page UI in `src/App.tsx`, and use focused component tests to drive the behavior.

**Tech Stack:** React 19, Vite 7, TypeScript 5, Tailwind CSS 3, Vitest, Testing Library

---

### Task 1: Establish the frontend toolchain and the first failing UI tests

**Files:**
- Create: `package.json`
- Create: `tsconfig.json`
- Create: `tsconfig.node.json`
- Create: `vite.config.ts`
- Create: `vitest.setup.ts`
- Create: `tests-ui/app.test.tsx`

**Step 1: Write the failing test**

Create tests that describe:
- empty file upload shows a validation error,
- successful upload shows filename and chunk count,
- successful query shows answer text and expandable source details.

**Step 2: Run test to verify it fails**

Run: `npm run test -- --run`
Expected: FAIL because the Vite/React app and test tooling do not exist yet.

**Step 3: Write minimal implementation**

Add package scripts and the test runner configuration needed to execute the new tests.

**Step 4: Run test to verify it still exercises the missing UI**

Run: `npm run test -- --run`
Expected: FAIL with missing application modules until the app files are created.

**Step 5: Commit**

```bash
git add package.json tsconfig.json tsconfig.node.json vite.config.ts vitest.setup.ts tests-ui/app.test.tsx
git commit -m "test: scaffold frontend toolchain and UI specs"
```

### Task 2: Implement the upload and query experience

**Files:**
- Create: `index.html`
- Create: `postcss.config.js`
- Create: `tailwind.config.js`
- Create: `src/main.tsx`
- Create: `src/App.tsx`
- Create: `src/api.ts`
- Create: `src/index.css`

**Step 1: Write or extend failing tests**

Add assertions for:
- upload button behavior during submit,
- query button disabled/loading while awaiting the answer,
- source previews capped to the first 100 characters.

**Step 2: Run test to verify it fails**

Run: `npm run test -- --run`
Expected: FAIL because the new behaviors are not implemented yet.

**Step 3: Write minimal implementation**

Create the page shell, forms, API helpers, status banners, spinner, answer panel, and expandable sources list with Tailwind styling.

**Step 4: Run test to verify it passes**

Run: `npm run test -- --run`
Expected: PASS

**Step 5: Commit**

```bash
git add index.html postcss.config.js tailwind.config.js src tests-ui/app.test.tsx
git commit -m "feat: add rag frontend upload and qa experience"
```

### Task 3: Harden responsiveness and repository integration

**Files:**
- Modify: `.gitignore`
- Modify: `README.md`

**Step 1: Write the failing validation**

Run: `npm run build`
Expected: FAIL until the full app and CSS pipeline are wired correctly.

**Step 2: Write minimal implementation**

Document the frontend workflow, add Node build artifacts to `.gitignore`, and make any final responsive/style refinements required by the tests and manual review.

**Step 3: Run validation to verify it passes**

Run:
- `npm run test -- --run`
- `npm run build`

**Step 4: Commit**

```bash
git add .gitignore README.md
git commit -m "docs: describe frontend workflow and ignore node artifacts"
```
