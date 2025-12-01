# KG Pipeline Development Notes

Date: 2025-12-01

Purpose: Capture decisions and plan for building a cohesive knowledge graph (KG) focused on persona creation and evaluation, including a Discworld-heavy corpus and a staged rollout under a $2/book budget.

## Pilot Corpus Strategy
- Target size: 8–12 books to establish a reliable baseline.
- Composition:
  - 6–8 Terry Pratchett titles (Watch/Witches/Moist/Tiffany arcs) for dialogue-rich, value-laden personas.
  - 2–4 nonfiction titles (e.g., Atomic Habits, Peak, Thinking, Fast and Slow) to anchor concrete attributes (habits, cognition, decision styles).
- Budget alignment: Pilot ($16–$24), second batch ($14–$20), cap near $40 for ~20 books total.

## Recommended Discworld Set (examples available in library)
- Guards! Guards!
- Men at Arms
- Feet of Clay
- Thud!
- Small Gods
- Going Postal
- Making Money
- The Wee Free Men
- Alternates: The Truth, Lords and Ladies, Witches Abroad, Reaper Man, The Shepherd’s Crown

## Nonfiction Anchors
- Atomic Habits — behaviors, routines, trait extraction
- Peak — skill acquisition, practice structure
- Thinking, Fast and Slow — cognitive styles, biases, decision modes
- Optional: The Goal, Ultralearning

## Cohesive KG Criteria
- Coverage: Major entities across titles captured and canonically resolved (`nodes_canonical.jsonl`).
- Connectivity: Recurring relationship motifs (duty, persuasion, mentorship) with consistent polarity/direction.
- Consistency: Deduplicated entities (e.g., "Samuel Vimes" vs "Vimes").
- Persona Alignment: Durable traits and motivations backed by edges and chunk evidence.

## Pipeline Execution Plan (Phases 0–4)
1) Phase 0–1: Transcribe/ingest and chunk the pilot; spot-check `outputs/transcripts` and `chunks.jsonl` for dialogue boundaries and dense sections.
2) Phase 2–3: Extract nodes and relationships; resolve entities → `nodes.jsonl`, `edges.jsonl`, `nodes_canonical.jsonl`.
3) Phase 4: Generate persona sheets → `persona_sheets.json` and templates; review 10–15 samples for density and attribute coverage.

## Dynamic System Prompt (Adaptive)
- Add logic keyed on genre and signal features:
  - Fiction, high-dialogue: Emphasize speaker attribution, relationship polarity, value/motivation cues.
  - Nonfiction, structured: Emphasize habits, cognitive styles, goals/actions.
- Update `prompts/phase1_extraction.txt`, `prompts/phase2_relationships.txt`, and persona templates accordingly.
- Implement selection in `scripts/ai_gateway_wrapper.mjs` or pipeline scripts.

## Baseline Metrics (KPIs)
- Node density: Nodes per 1k tokens, monitored per genre.
- Edge density & polarity: Edges per 1k tokens; % with clear polarity/intent.
- Entity resolution: Spot-check precision/recall on top entities; duplicate reduction rate.
- Persona attribute coverage: % personas with core fields (values, motivations, skills, weaknesses, affective-governor).
- Cross-book consistency: Recurring entities retain traits/relationships across titles.

## Scaling Plan
- After pilot metrics stabilize, process 7–10 more books (total 15–20).
- Prioritize persona-diverse titles; monitor drift and re-run small subsets after prompt tweaks.

## Actionable Next Steps
- Create an input manifest mapping titles → file paths in `kg_pipeline/inputs/`.
- Run Phases 0–4 on two representatives (e.g., Guards! Guards! + Atomic Habits) to produce a quick benchmark report.
- Add dynamic prompt switch and re-run 2–3 books to validate KPI improvements.

## TODO Snapshot (from chat plan)
- Select pilot corpus (8–12)
- Prep input manifests
- Run Phase 0–1 on pilot
- Run Phase 2–3 entities/edges
- Generate persona sheets
- Implement dynamic system prompt
- Define baseline metrics
- Evaluate and tweak prompts
- Scale to 15–20 books
- Baseline report + checklist

Notes: This document summarizes current decisions to prevent context loss and will be updated as the pipeline evolves.
