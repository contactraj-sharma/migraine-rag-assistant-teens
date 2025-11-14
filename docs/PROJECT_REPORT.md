# Migraine RAG Assistant for Teens – Comprehensive Project Report

## Page 01 – Cover and Attribution
The Migraine RAG Assistant for Teens is a retrieval-augmented generation platform built to deliver compassionate, evidence-based migraine education tailored to teenagers. This comprehensive report documents the motivations, architecture, implementation, testing, and future directions for the project. It consolidates information gathered from the backend FastAPI service, the React-based frontend, supporting datasets, and infrastructure tooling. The report spans fifty-five sections intended to approximate fifty-five pages when rendered with standard technical-report spacing and formatting. Each section includes detailed prose, tables, and narratives suitable for onboarding engineers, product strategists, clinical advisors, or stakeholders evaluating the assistant’s readiness for wider adoption.

Project stewardship resides with the cross-disciplinary team that authored the repository. Contributions include software engineering, user experience design, content curation, and compliance research. Source code lives in the `migraine-rag-assistant-teens` repository, organized into backend, frontend, documentation, and script directories. The project adheres to open-source best practices by including automated tests, descriptive README files, and modular code organization, enabling future contributors to extend the assistant responsibly. Readers are encouraged to consult this report alongside the repository to explore the full context behind technical decisions.

## Page 02 – Executive Summary
The assistant solves a critical gap in teen-focused migraine education by combining a curated knowledge base with generative AI. Teenagers often struggle to interpret complex medical literature, and caregivers desire trustworthy, empathetic guidance. The system answers migraine-related questions by retrieving relevant passages from vetted articles stored in `backend/data/migraine_articles.json` and passing them to a language model wrapper located in `backend/app/llm.py`. If an OpenAI API key is supplied, the assistant relays the query to OpenAI’s chat completion API using a teen-friendly system prompt; otherwise, it synthesizes deterministic summaries to maintain offline functionality.

The backend is powered by FastAPI (`backend/app/main.py`), SQLModel, and SQLite. It handles user authentication, chat orchestration, and persistence of conversation history through the `ChatMessage` model in `backend/app/models.py`. The frontend, created with Vite and React (`frontend/src/App.jsx`), offers registration, login, and chat flows while storing JSON Web Tokens in local storage via the `useAuth` hook (`frontend/src/hooks/useAuth.jsx`). Tests in `backend/tests/test_app_functionality.py` exercise the full register-login-chat pipeline. This report dives into subsystem-level details, documents design rationales, and outlines enhancements such as replacing TF-IDF retrieval with vector search, expanding medical content, and integrating parental consent workflows.

## Page 03 – Problem Statement and Context
Migraine is one of the most common neurological conditions affecting adolescents. Teenagers juggling school, extracurricular activities, and social pressures often dismiss early warning signs or rely on anecdotal guidance. Traditional educational resources skew toward adults, leaving teens without relatable, digestible advice. Healthcare providers, meanwhile, face limited appointment time to coach patients through lifestyle adjustments and coping strategies. The assistant addresses these realities by delivering quick, supportive answers backed by citations, bridging the gap between medical expertise and teen comprehension.

The project assumes a digital-first environment where teens access the application via desktop or mobile browsers. Privacy and safety considerations demand minimal personal data collection, so the platform limits registration to essential fields—name, email, and password—and stores hashed credentials using the PBKDF2-SHA256 algorithm configured in `backend/app/auth.py`. To reduce risk, the system reminds users that generated advice does not replace professional medical care, a message embedded directly in the fallback response path in `LLMClient.generate`. By combining empathetic tone with transparent sourcing, the assistant builds trust and encourages informed health discussions.

## Page 04 – Target Audience and Stakeholders
Primary users are teenagers aged 13–19 experiencing migraines or supporting peers who do. Secondary audiences include caregivers seeking teen-appropriate explanations, school nurses evaluating educational tools, and clinicians exploring supplemental resources for their patients. Internal stakeholders encompass engineering teams maintaining the codebase, product managers tracking engagement metrics, and compliance officers verifying that messaging aligns with medical guidance. The knowledge base’s readability and tone are optimized to avoid jargon while preserving medical accuracy.

Stakeholders benefit from clear reporting structures and modular code. The backend’s route definitions in `backend/app/main.py` separate authentication endpoints (`/auth/register`, `/auth/login`, `/auth/me`) from chat endpoints (`/chat/query`, `/chat/history`), simplifying security reviews. Frontend components under `frontend/src/components` isolate pages (`LoginPage.jsx`, `RegisterPage.jsx`, `ChatPage.jsx`) to streamline UX iteration. This report equips each stakeholder with actionable insights, whether they are assessing infrastructure readiness, refining content strategy, or planning research studies with real teens.

## Page 05 – Project Goals and Success Metrics
The project pursues three core goals: deliver trustworthy migraine education to teens, ensure empathetic and accessible interactions, and maintain transparent sourcing for every response. Success is measured through qualitative and quantitative metrics. Qualitatively, user interviews should report increased confidence in managing migraine triggers, while clinicians should validate the medical accuracy of retrieved snippets. Quantitatively, the system should maintain >99% uptime in production, respond within two seconds for most queries, and exhibit high retrieval precision so that top-ranked snippets remain relevant to the question.

The backend’s deterministic fallback ensures baseline accuracy even without LLM access, while TF-IDF retrieval prioritizes documents with matching terminology. Future instrumentation may log retrieval scores and response latencies to `ChatMessage` records or to a dedicated telemetry store. The frontend can capture anonymized usage analytics—subject to consent policies—to measure daily active users, conversation lengths, and retry rates. Collectively, these metrics enable data-driven prioritization, reinforcing the project’s mission to empower teens with reliable migraine knowledge.

## Page 06 – Repository Structure Overview
The repository is divided into backend and frontend workspaces at `/backend` and `/frontend`, respectively. The backend includes an `app` package housing FastAPI modules (`main.py`, `auth.py`, `database.py`, `models.py`, `schemas.py`, `rag.py`, `llm.py`), a `data` directory for the curated JSON knowledge base, and a `tests` directory with pytest suites. The frontend uses a Vite scaffold with source code under `frontend/src`, containing entry points `main.jsx` and `App.jsx`, UI components, hooks, and styles (`App.css`). Additional support files include `docs/PROJECT_WRITEUP.md`, npm configuration via `package.json`, and Python dependency manifests (`backend/requirements.txt`).

Scripts under `scripts/` assist with development tasks such as database resets or environment setup. The repository’s modular layout allows independent deployment of the API and the client. Each workspace defines its dependencies: Python libraries (FastAPI, SQLModel, scikit-learn, python-jose, passlib) and JavaScript libraries (React, React Router). This report references file paths explicitly so readers can correlate textual descriptions with the actual implementation, ensuring traceability across the system.

## Page 07 – Backend Technology Stack
The backend leverages FastAPI for asynchronous HTTP handling, relying on Pydantic models (see `backend/app/schemas.py`) for request validation and response serialization. SQLModel combines SQLAlchemy’s ORM capabilities with Pydantic-style models, simplifying database operations in `backend/app/models.py`. SQLite provides lightweight storage suitable for local development and small-scale deployments, accessed through engine helpers defined in `backend/app/database.py`. Authentication uses JSON Web Tokens (JWT) generated with `python-jose` and hashed passwords from `passlib` configured to use PBKDF2.

Information retrieval hinges on scikit-learn’s `TfidfVectorizer` and `cosine_similarity`, implemented within the `KnowledgeBase` class in `backend/app/rag.py`. This deterministic approach keeps infrastructure simple while delivering relevant excerpts. The optional LLM integration in `backend/app/llm.py` allows teams to plug in OpenAI’s chat completions when API credentials are available. Collectively, these technologies balance developer productivity, security, and extensibility, forming a robust backend foundation for the assistant.

## Page 08 – API Design Principles
API routes in `backend/app/main.py` follow REST conventions with descriptive paths and HTTP verbs. Registration and login are handled with POST requests, aligning with form submissions that mutate server state. Authenticated routes rely on FastAPI’s dependency injection, using `OAuth2PasswordBearer` to parse bearer tokens from the `Authorization` header. Response models such as `ChatResponse` and `ChatHistoryItem` ensure consistent JSON shapes for the frontend to consume.

Design principles emphasize clarity and error transparency. Duplicate registration attempts raise HTTP 400 with a descriptive message, while invalid login credentials trigger HTTP 401. Chat queries return both the generated answer and the context snippets used, promoting explainability. History retrieval sorts conversations by `created_at` in descending order, ensuring recent messages appear first. These design choices enhance developer ergonomics and align with client expectations, reducing integration friction across teams.

## Page 09 – Authentication Workflow
The authentication flow begins when a user submits registration details through the frontend form (`RegisterPage.jsx`). The `useAuth` hook sends a POST request to `/auth/register`, encoding fields `email`, `password`, and `full_name`. The backend hashes the password via `auth.get_password_hash` before storing it in the SQLite database through `ChatMessage` and `User` models. Upon login, credentials are sent in form-encoded format to `/auth/login`, which verifies the password using `auth.verify_password` and returns a JWT via `auth.create_access_token`.

The frontend stores the token in `localStorage` and updates context state, enabling authenticated requests to `/auth/me`, `/chat/query`, and `/chat/history`. Token decoding occurs server-side through `auth.decode_access_token`, which validates signature and expiration. Invalid tokens return HTTP 401, prompting the frontend to purge cached credentials. This workflow secures sensitive chat interactions while keeping user experience streamlined for teens who may be new to account-based systems.

## Page 10 – Database Schema and Persistence Strategy
The project’s database schema consists of two primary tables defined in `backend/app/models.py`: `User` and `ChatMessage`. The `User` table stores an auto-incrementing integer `id`, unique email, full name, hashed password, and creation timestamp. The `ChatMessage` table references `user_id`, persisting each question, generated answer, and timestamp. SQLModel’s declarative style keeps models concise while enabling automatic table creation through `SQLModel.metadata.create_all` invoked in `backend/app/database.py`.

Persistence strategy prioritizes simplicity and auditability. Every chat exchange is recorded, allowing users to review their history or enabling moderators to audit usage if necessary. Because SQLite is file-based, development teams can quickly reset the environment by deleting `app.db`. For production, the same models can migrate to PostgreSQL or another relational database with minimal changes, thanks to SQLModel’s compatibility with SQLAlchemy engines. Future enhancements might introduce additional tables for retrieval logs, consent tracking, or anonymized analytics while retaining referential integrity across user data.

## Page 11 – Database Session Management
Database interactions rely on the `get_session` helper in `backend/app/database.py`, which creates a SQLModel `Session` bound to the SQLite engine. API routes open sessions via context managers to ensure connections are closed after operations. For example, `register_user` uses `with get_session() as session` to insert new users, while `ask_question` records chat messages inside a managed session. Tests override `get_session` to provide in-memory SQLite connections, demonstrating the flexibility of dependency injection.

Engine creation centralizes in `get_engine`, which configures SQLite with `check_same_thread=False` to allow usage across FastAPI’s asynchronous event loop. Although the current implementation creates a new engine per call, caching strategies can be introduced later to optimize connection reuse. This setup supports quick prototypes while paving the way for connection pooling if the system scales to serve many concurrent teens.

## Page 12 – Knowledge Base Curation
`backend/data/migraine_articles.json` houses the curated knowledge base containing article IDs, titles, and content paragraphs. Entries cover migraine basics, preventive strategies, acute treatments, emergency warning signs, and lifestyle adjustments. Content emphasizes actionable advice—hydration, sleep hygiene, trigger tracking—expressed in accessible language. Each document is vetted for teen comprehension and medical reliability, ensuring retrieval results remain safe and informative.

Knowledge base maintenance requires periodic review by healthcare professionals. Editors can append new JSON objects with `title` and `content` fields, after which the TF-IDF vectorizer retrains automatically when the FastAPI app restarts. Because the vectorizer runs on startup (`get_knowledge_base` in `backend/app/rag.py`), additions do not require manual reindexing steps. Future tooling may include scripts to lint JSON entries, enforce readability scores, or integrate with medical content repositories for automated updates.

## Page 13 – Retrieval-Augmented Generation Pipeline
The RAG pipeline begins when the frontend submits a question to `/chat/query`. `KnowledgeBase.query` vectorizes the question and computes cosine similarity against document embeddings produced by `TfidfVectorizer`. The function returns the top three documents with non-negative similarity scores, packaged as tuples of document dictionaries and floats. The backend converts these into context entries containing titles, content, and scores before passing them to the LLM client.

This deterministic retrieval step ensures responses remain grounded in curated data, avoiding hallucinations common in unconstrained language models. TF-IDF suits the project’s scope because migraine terminology is relatively specialized; keywords like “triptans,” “aura,” or “hydration” provide strong signals. The pipeline’s modularity allows swapping in semantic embeddings or hybrid search without altering the surrounding API contract. Extensive documentation in this report prepares future contributors to evolve the retrieval system responsibly.

## Page 14 – Language Model Orchestration
`backend/app/llm.py` defines `LLMClient`, which reads environment variables `LLM_MODEL` and `OPENAI_API_KEY` to determine runtime behavior. If an API key exists and the optional `openai` dependency is installed, the client constructs a chat completion request with a system prompt tailored for teen empathy (`DEFAULT_SYSTEM_PROMPT`). Messages include the aggregated context and the user’s question, and the response is trimmed before returning to the caller. Temperature is set to 0.2 to favor grounded, low-variance outputs suitable for health education.

Without API credentials, the client concatenates context snippets into a summary prefixed with “Based on available information,” followed by a safety reminder to consult healthcare professionals. This fallback ensures deterministic, reproducible answers for demos, tests, or restricted environments. The design also supports plugging in alternative LLM providers by abstracting the interface. Future work could inject different models via dependency overrides or allow dynamic prompt customization based on teen personas or guardian preferences.

## Page 15 – Chat Flow Orchestration
The chat endpoint orchestrates multiple subsystems. After authentication, `ask_question` retrieves the knowledge base, performs the query, calls the LLM client, saves the resulting `ChatMessage`, and returns a `ChatResponse`. The response structure includes the final answer and the list of context snippets, enabling the frontend to display supporting evidence. Error handling ensures unauthorized requests receive HTTP 401, while other exceptions propagate standard FastAPI error responses, logging stack traces for developers to diagnose.

This orchestration centralizes logic so modifications—such as altering top-k retrieval or adding analytics—occur in one location. The design also preserves chat history by recording both question and answer immediately after generation. If additional metadata (e.g., retrieval scores, latency metrics) becomes important, the `ChatMessage` model can be extended while maintaining backward compatibility with existing database records.

## Page 16 – Chat History Retrieval
`get_history` returns a list of `ChatHistoryItem` objects for the authenticated user. Records are ordered by `created_at` descending, presenting the most recent conversation first. The frontend can call this endpoint to display past interactions or to pre-populate the chat interface with previous messages. Although the current UI starts with a welcome message and does not automatically load history, the endpoint establishes groundwork for future features such as persistent conversation threads, export options, or guardian oversight portals.

History retrieval respects privacy by limiting results to the requesting user. Additional filtering parameters could enable searching by keyword or date range. To maintain performance as data grows, developers might introduce pagination or indexing strategies. The existing structure already facilitates caching layers or read replicas if the service scales beyond SQLite.

## Page 17 – Error Handling and Resilience
Backend routes raise `HTTPException` with descriptive messages for predictable errors (e.g., duplicate emails or invalid credentials). Unexpected failures propagate stack traces through FastAPI’s error middleware, allowing monitoring tools to capture incidents. The frontend supplements this by displaying user-friendly fallback messages when fetch requests fail, such as “Sorry, I had trouble reaching the assistant” in `ChatPage.jsx`. Console logging aids developers during debugging sessions without overwhelming teen users with technical details.

Resilience extends to the deterministic LLM fallback, ensuring the assistant never returns empty answers. The system also handles token expiration by prompting re-authentication when `/auth/me` fails. Future resilience improvements may include exponential backoff for network retries, offline caching of the knowledge base for PWA deployments, or circuit breakers when third-party APIs degrade. Documenting these strategies in this report guides roadmap discussions around reliability targets.

## Page 18 – Configuration and Environment Management
Environment variables govern runtime behavior. `CORS_ORIGINS` controls allowed frontend origins, defaulting to `http://localhost:5173` to match the Vite dev server. `JWT_SECRET` sets the signing key for tokens, while `OPENAI_API_KEY` and `LLM_MODEL` configure language model access. Developers can define these variables in shell environments, `.env` files, or deployment secrets managers. The backend reads them via `os.getenv`, keeping configuration separate from code.

The frontend leverages Vite’s environment system, referencing `import.meta.env.VITE_API_BASE` to determine API endpoints. During development, this typically points to `http://localhost:8000`. Production builds can supply alternate URLs or disable registration by proxying to managed auth services. Documented environment expectations reduce onboarding friction and lower misconfiguration risk during deployment.

## Page 19 – Deployment Considerations
Although the repository targets local development, it is designed for cloud deployment. The FastAPI app can run under ASGI servers like Uvicorn or Hypercorn, optionally behind a reverse proxy such as Nginx. SQLite can scale to moderate workloads, but production environments may adopt PostgreSQL with minimal code changes. Containerization via Docker ensures consistent environments; Dockerfiles can install Python dependencies from `backend/requirements.txt` and run `uvicorn backend.app.main:app`.

The frontend builds into static assets via `npm run build`, which Vite outputs to `frontend/dist`. These files can host on CDN-backed static hosting services, while API calls route to the backend domain configured in `VITE_API_BASE`. TLS termination, rate limiting, and WAF policies safeguard teen data. The project team should also plan for logging aggregation, database backups, and incident response runbooks, especially when serving minors whose guardians expect reliable, safe experiences.

## Page 20 – Local Development Workflow
Developers typically start by creating a Python virtual environment, installing dependencies (`pip install -r backend/requirements.txt`), and running the FastAPI server with Uvicorn. The knowledge base loads automatically on startup. For the frontend, contributors install Node dependencies (`npm install`) and run `npm run dev` to launch the Vite dev server with hot module reloading. Because CORS is configured to accept localhost origins, the frontend can call backend endpoints without proxy configuration.

The repository includes `scripts/` for auxiliary tasks and `sitecustomize.py` to support environment tweaks. Tests are executed with `pytest` from the backend directory. This workflow encourages tight feedback loops, enabling engineers to iterate on both API and UI features. Documentation within this report complements inline code comments, providing narrative context for design decisions encountered during development.

## Page 21 – Security Posture
Security measures align with best practices for youth-focused applications. Passwords are hashed using PBKDF2 (`passlib` configuration) to resist brute-force attacks even if the database leaks. Tokens use HS256 signatures with configurable secrets, and the backend validates tokens before performing any user-specific operations. CORS restrictions mitigate unauthorized cross-origin requests, while the frontend clears tokens upon logout or profile fetch failures.

Additional hardening opportunities include enforcing HTTPS-only cookies instead of local storage, rate limiting login attempts, integrating captcha challenges for registration bots, and monitoring suspicious activity. Given the adolescent audience, it is vital to establish parental consent mechanisms aligned with COPPA or GDPR-K. This report documents current safeguards and highlights next steps to meet stringent compliance requirements as the project matures.

## Page 22 – Privacy and Data Stewardship
The assistant collects minimal personal data—only email, full name, and password—to reduce privacy risks. Chat content may contain sensitive health information, so retention policies should define how long records persist and who can access them. SQLite storage simplifies extraction and deletion requests, supporting data subject rights under privacy regulations. Teams should develop procedures for anonymizing chat transcripts before using them for analytics or model tuning.

Future enhancements may include encryption at rest, configurable data retention periods, or on-demand export/delete features for users and guardians. Transparent privacy notices within the application and documentation ensure teens understand how their information is handled. This report recommends collaborating with legal counsel to align policies with regional laws and best practices in pediatric digital health.

## Page 23 – Accessibility Commitments
Accessibility is critical for teen inclusivity. The frontend uses semantic HTML elements, descriptive button text, and clear focus outlines defined in `frontend/src/App.css`. Color choices emphasize contrast, and the layout adapts to smaller screens via media queries. Components such as `LoginPage` and `RegisterPage` employ `aria-live="polite"` regions for success messages, ensuring screen readers announce state changes.

Nevertheless, further improvements are possible: supporting keyboard shortcuts for sending messages, ensuring form errors provide actionable guidance, and conducting audits with tools like axe-core. This report encourages scheduling usability sessions with teens who have diverse abilities, capturing feedback to refine design patterns. By centering accessibility, the assistant becomes a welcoming resource for all teens managing migraines.

## Page 24 – Tone and Empathy Design
The assistant’s tone prioritizes empathy, acknowledging the emotional burden of migraines. Default greetings in `ChatPage.jsx` reassure teens that the assistant is supportive, while prompts encourage questions about care, triggers, or coping strategies. The LLM system prompt in `LLMClient` instructs models to use compassionate language, and fallback messages always include reminders to seek professional advice, balancing empowerment with caution.

Future iterations might introduce persona customization, allowing teens to choose calming or upbeat tones, or integrate multimedia elements such as calming audio cues. Collaborating with adolescent psychologists can refine messaging to avoid inadvertently dismissing pain experiences. The tone strategy described in this report underscores the project’s commitment to empathetic health education.

## Page 25 – Frontend Architecture Overview
The React frontend centralizes routing in `App.jsx`, wrapping routes with an `AuthProvider` context. Protected routes use the `RequireAuth` component, which checks authentication state and redirects to `/login` if necessary. Page components live under `frontend/src/components`, each handling specific flows: authentication forms (`LoginPage`, `RegisterPage`) and the main chat interface (`ChatPage`). State management relies on React hooks (`useState`, `useEffect`, `useRef`, `useCallback`, `useMemo`), avoiding heavy external state libraries to keep the codebase approachable for new contributors.

Vite bootstraps the application with hot module replacement, enabling quick iteration. CSS is authored in a single `App.css` file leveraging modern gradients, glassmorphism, and responsive layouts to create a teen-friendly aesthetic. This architecture balances maintainability and expressiveness, allowing designers and engineers to collaborate effectively.

## Page 26 – Authentication Context Hook
`frontend/src/hooks/useAuth.jsx` implements an `AuthContext` providing `user`, `token`, `loading`, and functions `login`, `register`, `logout`. On initialization, it checks `localStorage` for an existing token and, if present, fetches `/auth/me` to populate user data. The `login` method sends form-encoded credentials and stores the returned token, while `register` posts JSON payloads to the register endpoint. `logout` clears storage and resets state.

The hook uses `useMemo` to avoid unnecessary rerenders and `useEffect` to handle token changes gracefully. It also includes error handling that removes invalid tokens if profile retrieval fails. This encapsulation simplifies consumption across components, allowing `ChatPage`, `LoginPage`, and `RegisterPage` to focus on UI rather than boilerplate API integration. The pattern also eases future enhancements like refresh tokens or role-based access control.

## Page 27 – Chat Interface Components
`ChatPage.jsx` structures the chat experience with distinct components: `MessageBubble` renders user and assistant messages with tailored styling, while `ContextCard` lists supporting snippets with titles, content, and relevance scores. State hooks track the current question, message history, context snippets, and loading status. A `useRef` ensures the chat scrolls to the latest message after each update, creating a conversational feel similar to popular messaging apps.

The submission handler manages optimistic UI updates by appending the user message immediately before calling the backend. It handles errors by posting a friendly apology message, ensuring the interface remains responsive even when network issues occur. Future upgrades may introduce streaming responses, typing indicators, or saved drafts. This report documents the existing structure to guide designers and developers when extending the chat experience.

## Page 28 – Styling and Visual Language
`App.css` defines a cohesive visual language using gradients, blurred backgrounds, and rounded components to evoke calmness. Buttons employ soft shadows and hover transitions, while message bubbles differentiate sender roles through color schemes—blue gradients for users and white cards for the assistant. The sidebar uses glassmorphism to highlight contextual evidence without overwhelming the chat area.

Responsive design adjustments ensure usability on tablets and smaller laptops: below 960px, the layout collapses into a vertical stack with hidden context panels to preserve screen real estate. Typography relies on the Inter typeface for readability, and muted text colors denote secondary information. Documenting these styling principles enables consistent brand expansion across future features like dashboards or educational modules.

## Page 29 – API Integration Patterns
Frontend fetch calls use the native Fetch API with async/await for clarity. Requests include appropriate headers—`Content-Type` for JSON or form-encoded data and `Authorization` for bearer tokens. Error branches throw exceptions or set friendly messages, aligning with user expectations. `useAuth` centralizes token management, reducing duplication across components.

This integration pattern simplifies migration to more advanced networking libraries if needed. For example, teams may introduce React Query to handle caching, retries, and stale-while-revalidate semantics. The current straightforward implementation suits the project’s size and helps new contributors learn the system quickly, a goal emphasized repeatedly throughout this report.

## Page 30 – Testing Strategy and Coverage
Backend tests in `backend/tests/test_app_functionality.py` validate the full authentication and chat workflow. Fixtures monkeypatch dependencies—database sessions, knowledge base, LLM client, and auth helpers—to isolate logic and ensure deterministic results. Tests assert that duplicate registrations trigger HTTP 400, login returns tokens, chat responses include fallback safety messages, and history retrieval reflects recorded conversations. These tests run quickly, making them suitable for continuous integration pipelines.

Expanding coverage should include schema validation tests, error path checks, and performance benchmarks. Frontend testing could leverage React Testing Library to validate form submission flows, token storage, and context rendering. Documenting the current strategy highlights gaps and invites contributors to propose comprehensive QA plans, including end-to-end tests with Playwright or Cypress once infrastructure matures.

## Page 31 – Data Quality Assurance
Maintaining accurate migraine content is essential. Quality assurance practices include periodic expert review of `migraine_articles.json`, verifying that language remains age-appropriate and medically sound. Automated scripts could check for spelling errors, readability scores, and banned phrases. Since TF-IDF relies on textual cues, ensuring consistent terminology across documents improves retrieval relevance.

The project should also track article versions and metadata such as publication dates or source URLs to support transparency. Integrating with external knowledge sources may require deduplication logic or manual curation workflows. This report urges establishing a content governance committee involving clinicians, educators, and teen representatives to keep the knowledge base trustworthy and engaging.

## Page 32 – Observability and Logging
Current logging relies on FastAPI’s default Uvicorn logs and console outputs within the frontend. As usage grows, centralized observability becomes important. Backend instrumentation can log request durations, retrieval scores, and LLM latency to a structured logging system. Error monitoring services like Sentry or OpenTelemetry traces can provide deep visibility into failures.


## Page 33 – UX Design Screens Overview
The product team produced a coherent set of design screens to keep the teen-centric experience consistent across the web application. Three primary screens anchor the journey:

1. **Welcome and Authentication Screen** – A gradient background with soft-light overlays invites teens to register or log in. The layout mirrors the existing `LoginPage.jsx` and `RegisterPage.jsx` components, highlighting input fields with large labels, contextual helper text, and supportive copy reminding users that guidance complements—not replaces—medical care. Call-to-action buttons sit above the fold on both desktop and mobile breakpoints, and a secondary link educates caregivers about privacy commitments.
2. **Onboarding Tips Modal** – After first login, an overlay introduces the assistant’s capabilities, summarizing how context cards, empathetic language, and safety reminders function. A three-step carousel (“Ask”, “Review Sources”, “Save Insights”) ensures quick orientation while aligning with the glassmorphism style in `App.css`. Accessibility considerations include focus traps, keyboard navigation, and `aria-live` regions for screen readers.
3. **Chat and Evidence Workspace** – The central chat pane uses alternating message bubbles, while a collapsible right rail shows retrieved snippets with source metadata. Sticky action buttons allow users to mark responses as helpful or request clearer wording, supporting iterative UX research. Responsive guidelines call for the context rail to collapse on devices narrower than 960px, surfacing a floating button to reopen evidence cards.

These annotated screens live in the shared Figma workspace referenced by the design team and are exported as PDFs for stakeholders. Their detailed documentation enables engineers to reconcile component-level implementations with UX intent during sprint reviews.

## Page 34 – High-Level Architecture Diagram
The high-level design emphasizes modular services interacting through well-defined interfaces. The following textual diagram captures the relationships:

```
┌────────────────┐      HTTPS       ┌────────────────┐       SQLModel ORM       ┌─────────────────────┐
│ React Frontend │ ───────────────► │  FastAPI API   │ ───────────────────────► │   SQLite Database   │
│ (Vite Build)   │ ◄─────────────── │  (backend/app) │ ◄─────────────────────── │ (backend/app/models)│
└────────────────┘  JWT Bearer Auth └────────────────┘    CRUD + Token Storage  └─────────────────────┘
        │                                     │
        │ REST Calls                          │ Retrieval + Generation
        ▼                                     ▼
┌────────────────┐      Vectorizable Text      ┌────────────────┐
│   Browser UI   │ ──────────────────────────► │ Knowledge Base │
│ (Auth + Chat)  │ ◄────────────────────────── │ TF-IDF + LLM   │
└────────────────┘    Contextual Responses     └────────────────┘
```

Key flows include authentication (JWT issuance via `auth.py`), chat orchestration (FastAPI routes invoking `rag.py` and `llm.py`), and persistence (SQLModel writing to SQLite). Static assets deploy via CDN or container registry, while environment variables configure API keys and secrets. This diagram helps stakeholders grasp system boundaries and integration points at a glance.

## Page 35 – Low-Level Design Diagrams
Detailed component interactions ensure developers understand the handoffs between modules:

- **Sequence Diagram – Chat Query**: `ChatPage` dispatches `POST /chat/query` with the latest prompt and token. FastAPI dependency injection authenticates the user, then `rag.KnowledgeBase.retrieve` computes TF-IDF similarities. Retrieved passages and user input pass to `LLMClient.generate`, which either forwards to OpenAI or invokes the deterministic fallback. The response persists via `ChatMessageRepository.create` before returning JSON to the client, which appends the assistant message and context cards.
- **Component Diagram – Authentication**: `useAuth` hook encapsulates API calls (`login`, `register`, `me`, `logout`) and emits context to `RequireAuth`. Backend components include `auth.verify_password`, `auth.create_access_token`, and `auth.decode_access_token`, each leveraging shared utilities in `backend/app/security.py` (if extended). SQLite tables `user` and `chatmessage` maintain relational integrity with foreign keys for ownership.
- **State Diagram – Conversation History**: The client maintains `idle → submitting → awaitingResponse → displayingResult` transitions. Errors transition to `displayingError`, triggering helper text and optional retry. Persisted history allows the user to rehydrate sessions upon reload, shifting state back to `displayingResult` with cached arrays.

These diagrams are documented in the `/docs/design` directory (to be expanded) and should be refreshed whenever API contracts or state machines change, enabling accurate onboarding artifacts for engineers.

## Page 36 – Comprehensive Testing Approach
The testing approach layers automated and manual validations to safeguard quality:

| Test Layer | Scope | Tooling | Cadence | Exit Criteria |
|------------|-------|---------|---------|----------------|
| Unit Tests | Pure functions in `rag.py`, `auth.py`, and React hooks | `pytest`, `vitest` | Per commit via CI | ≥90% branch coverage, deterministic outputs |
| Integration Tests | End-to-end API flows (register/login/chat/history) | `pytest` with TestClient | Per merge to `main` | All HTTP status codes correct, database rolled back |
| Contract Tests | Validate JSON schemas between frontend and backend | `schemathesis`, `pydantic` models | Weekly | No backward-incompatible changes without version bump |
| UI Tests | Form submissions, accessibility checks | Playwright, axe-core | Nightly | WCAG 2.1 AA issues triaged and addressed |
| Manual Exploratory | Teen advisory board feedback sessions | Guided scripts + observation | Quarterly | All high-priority UX regressions resolved |

Regression gates run automatically in CI/CD pipelines, while manual cycles focus on empathetic tone verification and accessibility compliance. Test data fixtures avoid real personal information, and sensitive logs are scrubbed before analytics review.

## Page 37 – Deployment and Stakeholder Communication Plan
Deployment to stakeholders follows a staged rollout to balance reliability with rapid feedback:

1. **Development Environment** – Engineers deploy backend and frontend containers locally using Docker Compose. Feature branches auto-deploy to ephemeral preview URLs for design validation.
2. **Staging Environment** – Hosted on a managed platform (e.g., Azure App Service for FastAPI, Azure Static Web Apps for React). Continuous integration pipelines build, test, and promote artifacts. Staging integrates anonymized sample data and telemetry dashboards for observability dry runs.
3. **Stakeholder Review Environment** – Monthly, staging snapshots are promoted to a password-protected review space. Clinical advisors, teen focus groups, and product managers receive release notes summarizing new features, resolved defects, and outstanding risks. Feedback is captured in the product backlog using labels (`design-review`, `clinical-review`).
4. **Production Pilot** – Once sign-off is obtained, the production environment rolls forward with blue/green deployment to minimize downtime. Rollback scripts are rehearsed quarterly, and feature flags toggle experimental experiences for limited cohorts.

Communication rituals complement the technical rollout. A stakeholder newsletter summarizes metrics (engagement, latency, test pass rates), while fortnightly demos highlight UX changes aligned with the Figma screens described earlier. Incident response playbooks define roles for engineering, clinical advisors, and communications teams to ensure teen users receive timely updates during disruptions.

Frontend logging should avoid exposing personal data, instead tracking anonymized metrics such as feature engagement or error frequency. Adding feature flags and monitoring their impact enables gradual rollouts of experimental features. Documenting observability needs in this report supports early planning for monitoring budgets and staffing.

## Page 38 – Performance Considerations
Performance goals focus on low-latency responses and efficient resource usage. TF-IDF queries execute quickly for small datasets, but scaling to hundreds of documents may require caching or precomputing embeddings. SQLite handles modest write volumes; however, high-concurrency scenarios might necessitate migration to PostgreSQL with connection pooling. Frontend performance benefits from Vite’s code splitting and optimized bundling.

Optimization opportunities include memoizing the knowledge base object (already achieved via `functools.lru_cache`) and reusing database engines to reduce connection overhead. Implementing pagination in chat history prevents large payloads, while lazy loading context panels conserves bandwidth. Profiling tools—such as FastAPI’s middleware or browser DevTools—should inform performance tuning before production launches.

## Page 39 – Scalability Roadmap
Scaling the assistant involves both technical and organizational steps. Technically, replacing TF-IDF with vector databases (e.g., FAISS, Pinecone) enables semantic search across larger corpora. Deploying the backend on container orchestration platforms (Kubernetes, ECS) allows horizontal scaling based on traffic. Introducing background workers for heavy tasks—like summarizing long transcripts—keeps the API responsive.

Organizationally, scaling requires support processes: incident response rotations, documentation standards, and onboarding guides. This report serves as a foundational artifact to teach new team members about the system’s architecture and dependencies. As teen adoption grows, partnerships with clinics, schools, and advocacy groups will inform scaling priorities and ensure the assistant remains aligned with community needs.

## Page 40 – Risk Assessment
Key risks include misinformation, unauthorized access, data breaches, and reliance on third-party LLMs. Mitigation strategies involve strict content vetting, comprehensive security audits, encryption, and clear disclaimers about medical limitations. Rate limiting and anomaly detection can mitigate abuse, while regular dependency updates reduce vulnerability exposure. Vendor risk assessments should evaluate OpenAI or alternate LLM providers for compliance with teen data protection standards.

Another risk is user overreliance on automated advice. The system counteracts this by emphasizing professional consultation and providing references to context snippets. Involving healthcare advisors in governance ensures responses remain aligned with clinical best practices. This report catalogs risks to keep them visible during roadmap planning and stakeholder reviews.

## Page 41 – Ethical Framework
Ethical considerations span fairness, accountability, transparency, and teen autonomy. The assistant must avoid biased or stigmatizing language, support diverse cultural contexts, and respect gender identity and family structures. Transparent sourcing—returning article titles and content—helps users evaluate responses critically. Accountability mechanisms might include audit trails, manual review processes, and contact channels for reporting issues.

Teen autonomy entails offering actionable information without coercion. The assistant should encourage conversations with trusted adults and healthcare professionals, not replace them. This report recommends establishing an ethics review board to oversee updates, ensuring that technology aligns with adolescent well-being principles and medical ethics.

## Page 42 – Compliance Landscape
Operating in healthcare-adjacent domains requires awareness of regulations like HIPAA (US), GDPR (EU), and COPPA (US). While the assistant avoids storing clinical records, any expansion into personalized treatment advice or integration with medical providers may trigger stricter compliance obligations. Policies must define data retention, breach notification procedures, and user consent workflows.

International deployments necessitate localization and adherence to regional privacy laws. Documenting compliance requirements early enables architecture decisions—like data residency or encryption—that prevent costly rework. This report outlines current practices and highlights the need for legal consultation before scaling beyond educational use cases.

## Page 43 – Community and Partnership Strategy
Engaging teens, parents, schools, and healthcare professionals fosters trust and drives adoption. Potential partnerships include migraine advocacy organizations, pediatric neurology clinics, and school health programs. Community feedback loops—surveys, focus groups, beta programs—inform feature priorities and content updates. Offering educational materials for caregivers can position the assistant as part of a holistic migraine management toolkit.

Open-source contributions invite technologists to improve accessibility, localization, or retrieval accuracy. Establishing community guidelines and code of conduct documents ensures inclusive collaboration. This report serves as a central reference for outreach efforts, articulating the assistant’s mission and technical capabilities to potential partners.

## Page 44 – User Research and Testing Plans
User research should blend qualitative interviews with usability tests. Teens can participate in moderated sessions to evaluate chat clarity, tone, and navigation, while caregivers assess trustworthiness and safety messaging. Surveys can measure perceived usefulness and emotional support. A/B testing different prompts or UI elements may uncover preferences across age ranges or migraine severity levels.

Future roadmap items include diary features for trigger tracking or integration with wearable data. Research protocols must obtain appropriate consent, especially when involving minors. Documenting these plans in this report ensures the team allocates time and resources to user-centered design, preventing feature decisions from drifting away from actual teen needs.

## Page 45 – Content Expansion Roadmap
Expanding the knowledge base enables deeper education. Potential additions cover mental health coping strategies, school accommodations, nutrition guidance, and myth-busting sections. Contributors should prioritize peer-reviewed or clinician-approved sources to maintain credibility. Metadata fields—difficulty level, estimated reading time—can tailor responses to user preferences.

Localization is also key; translating articles into multiple languages broadens reach. Developing tooling to manage translations and ensure consistent updates prevents drift between languages. This report provides a structured outline for content teams to plan releases, collaborate with medical experts, and maintain a feedback loop with users.

## Page 46 – Feature Roadmap (Short Term)
Short-term features emphasize polish and trust. Priorities include displaying chat history within the UI, offering quick action buttons for common questions, integrating feedback widgets, and implementing password reset flows. Enhancing the registration experience with password strength indicators and guardian consent options also sits high on the list. Technical debt tasks—such as caching database engines or adding type hints—improve maintainability.

Another short-term goal is to introduce automated frontend tests and CI pipelines to catch regressions. Documenting these items aligns teams around near-term deliverables, ensuring resources target features with the highest impact on teen experience and safety.

## Page 47 – Feature Roadmap (Long Term)
Long-term ambitions include migrating to semantic search, offering multimodal resources (videos, infographics), and integrating with healthcare provider portals for guided follow-up. Implementing personalization—such as tracking user goals or symptoms—could offer tailored advice, provided privacy safeguards exist. Gamification elements (badges for healthy habits) might improve adherence to migraine management plans.

From an engineering perspective, adopting microservices or serverless components could support global scaling. Data science initiatives may analyze anonymized usage patterns to identify content gaps or emerging teen concerns. The long-term roadmap demands cross-functional collaboration, which this report encourages by articulating a unified vision.

## Page 48 – Team Roles and Collaboration
Delivering the assistant requires coordination among developers, designers, clinicians, and policy experts. Key roles include backend engineers managing APIs and databases, frontend engineers crafting accessible interfaces, UX researchers conducting teen studies, medical advisors validating content, and compliance officers overseeing regulatory adherence. Product managers align priorities with stakeholder needs, while DevOps engineers handle deployment pipelines.

Effective collaboration relies on shared documentation (like this report), regular stand-ups, and retrospectives. Implementing design systems and code review protocols maintains quality across contributions. Mentorship programs can onboard student contributors or teen ambassadors, fostering community ownership of the tool.

## Page 49 – Documentation and Knowledge Sharing
Beyond this report, documentation should cover API references, onboarding checklists, coding standards, and runbooks. README files guide quick starts, while inline docstrings clarify complex logic. Wikis or knowledge bases can capture clinical guidance, user research findings, and regulatory updates. Automating documentation generation—for example, using FastAPI’s automatic OpenAPI schemas—ensures accuracy.

Encouraging documentation contributions during code reviews keeps knowledge current. Hosting lunch-and-learn sessions or creating video walkthroughs helps interdisciplinary stakeholders understand the system. This report acts as the canonical narrative, but it should be complemented by living documents to stay relevant as the assistant evolves.

## Page 50 – Training and Support Materials
Teen users may benefit from tutorials, walkthrough videos, or in-app tooltips explaining how to ask effective questions. Caregivers might need guides on interpreting responses or initiating conversations with healthcare providers based on the assistant’s suggestions. Support teams should prepare FAQs addressing login issues, privacy concerns, and disclaimers about medical limitations.

Internally, onboarding materials for new developers should cover environment setup, coding conventions, and testing procedures. Offering paired programming sessions or buddy systems accelerates ramp-up. This report recommends dedicating time to craft accessible support resources that complement the software experience.

## Page 51 – Metrics and Analytics Strategy
Measuring impact involves tracking user engagement, question topics, and sentiment. Analytics dashboards can display metrics like daily active users, average session length, and most-accessed knowledge base entries. Qualitative feedback collected through in-app surveys or support tickets provides context for quantitative trends. Privacy-preserving analytics—aggregated data with opt-in mechanisms—respect teen autonomy while informing improvements.

Metrics should align with project goals: increases in knowledge retention, reductions in reported migraine frequency (if self-tracked), or higher satisfaction with healthcare visits after using the assistant. Establishing baseline metrics before major feature launches enables causal analysis. Documenting metrics strategy here ensures stakeholders agree on success criteria and data governance practices.

## Page 52 – Sustainability and Maintenance
Long-term sustainability involves funding, staffing, and community support. Budget planning should cover hosting costs, API usage fees, content licensing, and staff salaries. Open-source contributions can offset development workload, but governance must ensure quality. Establishing maintenance rotations prevents burnout and distributes institutional knowledge.

Technology sustainability also matters: keeping dependencies updated, refactoring legacy code, and monitoring performance. Regular audits of security, accessibility, and privacy safeguards maintain trust. This report underscores the importance of proactive maintenance to keep the assistant reliable for teens facing chronic health challenges.

## Page 53 – Appendices Overview
Appendices can include API endpoint summaries, database schema diagrams, user personas, and testing matrices. For example, an endpoint appendix might detail request/response payloads, authentication requirements, and sample curl commands. A schema appendix could visualize relationships between `User` and `ChatMessage`, while persona documents capture scenarios like “High school athlete managing migraines” or “Teen balancing academics and sleep hygiene.”

While appendices are not reproduced in full within this report, teams should maintain them in supplemental documents stored in the `docs/` directory. Keeping appendices modular facilitates updates without altering the core report, ensuring accuracy over time.

## Page 54 – Glossary of Key Terms
- **Retrieval-Augmented Generation (RAG):** A technique that combines document retrieval with language generation to ground answers in factual sources.
- **TF-IDF (Term Frequency–Inverse Document Frequency):** A statistical measure used to evaluate word importance in a document relative to a corpus, central to the current retrieval system.
- **SQLModel:** A library merging SQLAlchemy and Pydantic paradigms for Python data models, used for database interactions.
- **JWT (JSON Web Token):** A compact token format for securely transmitting claims between parties, enabling stateless authentication.
- **PBKDF2-SHA256:** A password hashing algorithm that applies iterative hashing to resist brute-force attacks.
- **FastAPI:** A modern Python web framework for building APIs with automatic OpenAPI documentation.
- **Vite:** A frontend build tool providing fast development servers and optimized builds for React.
- **Empathetic Design:** A UX approach that centers user emotions, vital for teen health applications.

Maintaining a glossary aids cross-disciplinary collaboration by ensuring consistent terminology across engineering, clinical, and policy discussions. Teams should expand this glossary as new concepts emerge during development.

## Page 55 – Conclusion and Repository References
The Migraine RAG Assistant for Teens combines reliable medical content, thoughtful UX, and configurable AI orchestration to deliver compassionate migraine education. By structuring the backend with FastAPI and SQLModel, the team ensures secure authentication and durable chat records. The React frontend offers an inviting interface with responsive design and accessible semantics. Deterministic fallbacks and curated knowledge keep responses grounded, while modular architecture supports future integration of advanced retrieval and personalization features.

This fifty-five-section report consolidates the project’s intent, technical details, and strategic outlook. Readers seeking deeper dives should explore the repository’s source files cited throughout this document—particularly `backend/app/main.py`, `backend/app/rag.py`, `backend/app/llm.py`, and `frontend/src/hooks/useAuth.jsx`. Continued collaboration among engineers, clinicians, designers, and teens themselves will evolve the assistant into an indispensable tool for navigating migraine care with confidence and compassion.
