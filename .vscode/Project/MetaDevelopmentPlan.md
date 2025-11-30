# Development Plan Meta-Schema

> **Note**: This document is a reusable template (meta-schema) for structuring multi-phase development work. Duplicate the "Phase N" block for each major component or feature vertical. Populate Goal, What-to-do, Implementation, and Checks sections with concrete details for your project.

---

# Phase 0 — Foundations

Before building features, establish the foundation:

- **Data contracts & schemas**: Define input/output formats, validation rules, and schema versioning (e.g., JSONL structure, API contracts, type definitions)
- **Environment configuration**: Set up secrets management, configuration files (YAML/JSON), environment variables, and development/production boundaries
- **Entity registration in existing systems**: Register resources with external services (API keys, database schemas, vector indexes, gateway registrations)
- **Type boundaries**: Define clear interfaces between components; document expected types, error handling contracts, and data flow

---

# Phase N — [Feature Vertical Slice]
**Goal:** [One sentence]

**What to do:**
- Server: [data/logic layer]
- Client: [UI/interaction layer]
- Integration: [connection points]
- References: [source implementations]

**Implementation plan:**
1. [Step with rationale]
2. [Step with breadcrumbs]

**Checks:**
- Goal achieved: [functional criteria]
- No regressions: [existing features verified]

# Final Phase — Production Hardening
- Security
- Quotas & rate limits
- Observability
- Error handling
- Lifecycle management
