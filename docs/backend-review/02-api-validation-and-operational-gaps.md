# [Backend review]: API, validation, and operational gaps

## Scope and baseline

Track findings **F011-F020** from the Python backend review at [`c4808c01d8b08b800fbddcc02547afb2701554eb`](https://github.com/lucasandre22/smart-minutes/commit/c4808c01d8b08b800fbddcc02547afb2701554eb).

Evidence is static inspection of request handling, service calls, and background-job behavior. Load, timeout, restart, and browser/CORS experiments were not run. All 49 Python files parsed; full tests were unavailable because the review interpreter had no pytest installed. These are confirmed implementation gaps; resource-exhaustion severity depends on deployment and workload.

## Findings

- [ ] **F011 - Request bodies bypass schema validation.** Routes directly index JSON dictionaries, so missing fields and invalid types/settings fail at runtime rather than yielding structured validation responses. Add Pydantic request/response contracts, bounds, supported values, and clear errors. [Source](https://github.com/lucasandre22/smart-minutes/blob/c4808c01d8b08b800fbddcc02547afb2701554eb/backend/api/controllers/controller.py#L153).
- [ ] **F012 - Uploads are fully buffered without size limits.** `await source_file.read()` loads each complete file into memory. Large or concurrent uploads can exhaust memory. Stream to a staged file and enforce bounded sizes and cleanup on failure. [Source](https://github.com/lucasandre22/smart-minutes/blob/c4808c01d8b08b800fbddcc02547afb2701554eb/backend/api/services/service.py#L117).
- [ ] **F013 - File validation trusts MIME type or is disabled.** PDF validation checks a client-supplied content type, while transcript validation is commented out. Validate supported formats, actual parseability, encoding, and empty content before making files available. [Source](https://github.com/lucasandre22/smart-minutes/blob/c4808c01d8b08b800fbddcc02547afb2701554eb/backend/api/controllers/controller.py#L36).
- [ ] **F014 - Async handlers execute blocking work.** Synchronous HTTP, PDF parsing, embeddings, filesystem writes, and FAISS persistence run through async routes. Offload blocking operations or use asynchronous clients, then demonstrate that unrelated requests remain responsive. [HTTP source](https://github.com/lucasandre22/smart-minutes/blob/c4808c01d8b08b800fbddcc02547afb2701554eb/backend/api/services/service.py#L88); [indexing source](https://github.com/lucasandre22/smart-minutes/blob/c4808c01d8b08b800fbddcc02547afb2701554eb/backend/api/services/service.py#L338).
- [ ] **F015 - Model discovery has no timeout or connection handling.** An unresponsive Ollama request can hang; connection failures escape, and non-success status becomes an empty list. Bound request time and distinguish unavailable service, invalid response, and a valid empty model list. [Source](https://github.com/lucasandre22/smart-minutes/blob/c4808c01d8b08b800fbddcc02547afb2701554eb/backend/api/services/service.py#L87).
- [ ] **F016 - Generation has no bounded scheduling or durable execution.** Every request schedules an in-process background job without a queue limit, explicit concurrency policy, timeout, or restart recovery. Define workload limits and recovery semantics appropriate to local/shared GPU execution. [Source](https://github.com/lucasandre22/smart-minutes/blob/c4808c01d8b08b800fbddcc02547afb2701554eb/backend/api/controllers/controller.py#L162).
- [ ] **F017 - Clear, cancel, dismiss, and download behavior are conflated.** Clearing tracking does not stop inference, which can later recreate a completed task. Download also clears shared state and can hide another job. Define separate job-scoped operations and cancellation semantics. [Source](https://github.com/lucasandre22/smart-minutes/blob/c4808c01d8b08b800fbddcc02547afb2701554eb/backend/api/controllers/controller.py#L136).
- [ ] **F018 - GET requests mutate task state.** Clear endpoints and output downloads change global state, making retries or prefetching potentially destructive to tracking. Make GET read-only and expose explicit mutation operations. [Source](https://github.com/lucasandre22/smart-minutes/blob/c4808c01d8b08b800fbddcc02547afb2701554eb/backend/api/controllers/sse_controller.py#L20).
- [ ] **F019 - CORS permits broad access with credentials enabled.** Wildcard origins, methods, and headers are combined with credential support. Configure explicit allowed origins and credential behavior for the supported deployment. [Source](https://github.com/lucasandre22/smart-minutes/blob/c4808c01d8b08b800fbddcc02547afb2701554eb/backend/api/main.py#L13).
- [ ] **F020 - Model download is a no-op endpoint.** The service only reads the requested model name and neither downloads nor reports an unsupported operation. Implement observable download status/errors or remove/disable the endpoint with an explicit response. [Source](https://github.com/lucasandre22/smart-minutes/blob/c4808c01d8b08b800fbddcc02547afb2701554eb/backend/api/services/service.py#L166).

## Dependencies and implementation links

Coordinate scheduling, cancellation, and state transitions with F007-F009 in the critical-defects topic. Coordinate staged uploads with F037 in the storage topic. Link implementation issues and PRs here.

## Completion criteria

- [ ] Every finding has a linked fix and validation, or a documented evidence-based disposition.
- [ ] Verify invalid requests, supported file types, upload limits, service timeouts, and scheduling limits using isolated dependencies.
- [ ] Confirm read operations do not mutate jobs and unrelated requests remain responsive during slow operations.
- [ ] Document the resulting API contracts and deployment settings.
