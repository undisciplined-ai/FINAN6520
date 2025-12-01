# KG Pipeline Development Notes

Date: 2025-12-01

## Overview: Purpose, Functionality, Intent
- Purpose: Convert long-form media (audio/PDF/text) into a cohesive knowledge graph and persona artifacts to enable richer, context-aware interactions and evaluation of persona performance.
- Functionality: 
  - Phase 0–1: Transcribe/ingest and chunk content for LLM-friendly processing.
  - Phase 2–3: Extract entities (nodes), relationships (edges), and resolve canonical identities across sources.
  - Phase 4: Generate structured persona sheets (values, motivations, reasoning styles) informed by KG evidence.
  - Config-driven runs: Models, prompts, and thresholds set via `config/run_config.yaml`; parallelization and token reporting included.
- Intent: Build a high-signal, durable KG that supports adaptive prompting and persona evaluation, emphasizing clarity, consistency, and cross-book alignment while controlling cost.

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

## Worker Autoscaling Policy
- **Phase 0 (Whisper transcription)**: Workers autoscale based on chunk count (<60→4, 60-180→8, >180→16) capped at 80% of OpenAI tier RPM (Tier 1: 500 RPM → max 6 workers/sec).
- **Phase 2 (Node extraction)**: Same heuristic applied to LLM extraction chunks, conservative 2500 RPM estimate for Anthropic via Vercel Gateway.
- **Manual override**: Set `parallel.max_workers` in `config/run_config.yaml` to bypass autoscaling.
- **Telemetry**: Phase 0 logs 429 rate limits, 5xx errors, and retry counts to inform threshold tuning.
- **Backoff**: Exponential backoff (2^n seconds) on 429/5xx errors prevents retry cascades.
- **Rationale**: Balance throughput with API stability; large corpus jobs (100+ hours) finish faster without triggering rate limits.

## Incremental Multi-Book Workflow
- **Fresh mode** (`python scripts/run_pipeline.py --input book.m4b`): Wipes outputs/, processes from scratch
- **Append mode** (`python scripts/run_pipeline.py --input book2.m4b --append`): Adds to existing KG
  - Phase 0: Chunk-level caching reuses successful transcriptions; `--retry-failed` flag only retranscribes `[MISSING CHUNK N]` markers
  - Phase 1: Auto-increments doc### IDs, appends to chunks.jsonl
  - Phase 2: Skips already-processed chunks (tracked in `.manifest.json`), appends new nodes
  - Phase 2.5: Re-deduplicates ALL nodes (existing canonical + new) for cross-book trait merging
  - Phase 3: Appends new edges, deduplicates against existing edges
- **Checkpointing**: `.manifest.json` tracks processed chunks, doc counter, and phase status to avoid redundant work
- **Rationale**: Build a unified KG across 15-20 books iteratively; tweak prompts mid-corpus without losing progress

## Jungian Archetype Framework (v1.0)
- **Purpose**: Layer psychological archetypes into the KG for richer persona navigation and assembly. Enables filtering/scoring personas by archetypal alignment (e.g., "show me Hero-dominant personas").
- **Architecture**: Two-stage design separates **extraction** (evidence-grounded trait tagging) from **interpretation** (archetype scoring):
  1. **Phase 2 Extraction**: LLM tags nodes with observable traits from controlled vocabulary (`config/jungian_traits.yaml`). Each node gets `jungian_traits` field with 6 arrays: desires, fears, strategies, talents, weaknesses, themes.
  2. **Downstream Scoring**: Phase 2.5/4 map trait patterns to 12 archetypes via `config/jungian_archetype_mapping.yaml` using weighted overlap scoring.
- **12 Archetypes**: Innocent, Everyman, Hero, Caregiver, Explorer, Rebel, Lover, Creator, Jester, Sage, Magician, Ruler.
- **4 Cardinal Orientations**: Ego (safety/belonging), Order (structure/mastery), Social (connection/change), Freedom (liberation/transcendence).
- **Trait Vocabulary**: ~60 trait tags organized across 5 dimensions:
  - Desires: Core motivations (paradise, belonging, prove_worth, protect_others, authenticity, revolution, intimacy, creation, joy, truth, transformation, control)
  - Fears: Fundamental anxieties (punishment, exclusion, weakness, selfishness, conformity, powerlessness, isolation, mediocrity, boredom, deception, stagnation, chaos)
  - Strategies: Behavioral approaches (faith, conformity, courage, generosity, autonomy, disruption, devotion, innovation, humor, wisdom, alchemy, responsibility)
  - Talents: Core competencies (optimism, realism, determination, empathy, curiosity, independence, passion, imagination, levity, insight, vision, leadership)
  - Weaknesses: Shadow aspects (naivety, cynicism, arrogance, martyrdom, isolation, destructiveness, codependency, impracticality, irresponsibility, detachment, manipulation, tyranny)
- **Trait Extraction Rules**:
  - At least one trait tag required per node (across all 6 categories combined)
  - Empty arrays allowed per category, but cannot have all categories empty
  - Tags must exist in `config/jungian_traits.yaml` vocabulary
  - LLMs extract traits "clearly evident in the source text" (not speculative)
- **Token Optimization**: Compact trait vocabulary formatting (`category: trait_id: description`) minimizes prompt overhead; typical injection ~500 tokens.
- **Phase 2.5 Enhancement**: Added archetype-aware similarity scoring using trait overlap to improve entity resolution clustering. Nodes with similar trait profiles merge even if text similarity is moderate.
- **Validation**: `scripts/validate_outputs.py` now checks:
  - `jungian_traits` field present on all nodes
  - All 6 categories present (desires/fears/strategies/talents/weaknesses/themes)
  - Trait IDs exist in vocabulary
  - At least one non-empty trait array per node
- **Stability Commitment**: Trait vocabulary is stable post-launch; additions allowed but deletions/renames require migration scripts to avoid breaking historical KG data.
- **Downstream Usage** (Phase 4):
  - Score personas against archetype signatures: Sum weighted trait overlap per archetype (e.g., Hero: high prove_worth + courage + determination)
  - Filter persona assembly by archetype affinity: "Assemble a Sage persona" → select nodes with high wisdom/insight/truth traits
  - Visualize archetype distribution across corpus: Histogram of dominant archetypes per book
  - Track archetype consistency: Monitor whether recurring characters maintain trait patterns across books
- **Design Rationale**:
  - **Grounded extraction**: LLMs tag observable traits, not abstract archetype labels, reducing hallucination risk
  - **Flexible interpretation**: Same traits can map to multiple archetypes with different weights (e.g., "courage" appears in Hero, Rebel, Magician)
  - **Cross-book alignment**: Trait-based deduplication in Phase 2.5 preserves psychological continuity (e.g., "Vimes" entities merge via shared duty/cynicism/determination traits)
  - **Prompt minimalism**: Compact vocabulary format avoids bloated prompts while maintaining semantic clarity
  - **Sunk cost avoidance**: Two-stage architecture allows tweaking archetype scoring without re-extracting nodes from source text

## Configuration Files
- `config/persona_schema.yaml`: Node/edge type definitions + required fields + jungian_traits schema
- `config/jungian_traits.yaml`: Controlled vocabulary of 60 traits with descriptions (stable post-launch)
- `config/jungian_archetype_mapping.yaml`: 12 archetypes with trait signatures and scoring weights
- `config/run_config.yaml`: Model selection, parallel workers, thresholds, autoscaling overrides

Notes: This document summarizes current decisions to prevent context loss and will be updated as the pipeline evolves.
