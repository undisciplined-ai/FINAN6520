# Context Pollution in LLM-Assisted Document Generation

## The Core Problem

Large Language Models treat all information in their context window as relevant input. They do not distinguish between:

- Information meant to **guide** the drafting process
- Information meant to **appear** in the deliverable

This creates a failure mode: context that helps you think about a project bleeds into the output document, producing deliverables that read like internal notes rather than professional documents.

---

## Symptoms of Context Pollution

A polluted deliverable often includes:

- References to project phases, versions, or timelines ("In v1.0, we focused on...")
- Justifications for brevity or scope ("This section is intentionally limited to...")
- Team-specific details ("Given our small team...")
- Tool or resource constraints ("Without dedicated software, we...")
- Methodology explanations ("Applying the 80/20 rule...")
- Apologetic or tentative language ("We will expand this later...")

These are appropriate for internal documentation. They are inappropriate for professional deliverables.

---

## How LLMs Process Context

### 1. Context is weighted, not filtered

LLMs assign attention to all tokens in the context window. There is no built-in mechanism to mark certain information as "background only" or "do not include in output." Everything present is available for use.

### 2. Inclusion signals relevance

If information appears in the context, the model treats it as potentially relevant to the task. The more prominent or recent the information, the more likely it influences the output.

### 3. LLMs optimize for coherence, not audience

LLMs generate text that is coherent with the context provided. They do not inherently optimize for what a specific audience needs to see. If your context discusses project constraints, the output may reference those constraints—even when the audience has no need to know them.

---

## The Two-Audience Problem

Most LLM-assisted projects involve at least two audiences:

| Audience | Needs to Know | Should NOT Appear in Deliverable |
|----------|---------------|----------------------------------|
| **You / Project Team** | Constraints, rationale, methodology, timeline, team composition, trade-offs | (This is your working context) |
| **Deliverable Reader** | Procedures, requirements, standards, actionable content | Your constraints, methodology, timeline, trade-offs |

When both types of information exist in the same context, the LLM conflates them. The result: deliverables that explain *why* you made certain choices instead of simply presenting the choices.

---

## Why This Happens

### The "Helpful Context" Trap

When working with LLMs, the instinct is to provide more context. More context usually improves output quality. This creates a pattern:

1. Add context to help LLM understand the situation
2. LLM produces better output
3. Reinforce behavior: add even more context next time

The trap: context that helps the LLM *understand your situation* is not the same as context that should *appear in the output*. But the LLM doesn't know the difference.

### The Compounding Effect

Context pollution compounds across iterations:

1. Initial context includes project methodology
2. First draft references methodology
3. You edit the draft but miss some references
4. Next iteration builds on polluted draft
5. Pollution becomes embedded in document structure

Fixing pollution late in a project requires reviewing every section. Prevention is significantly cheaper than correction.

### The Governing Document Problem

Most LLM-assisted projects begin with a context document—a project overview, requirements spec, or brief that establishes scope, constraints, and objectives. This document serves as the foundation for all subsequent work.

**This is the highest-risk location for context pollution.**

If the governing document contains pollution, every deliverable drafted from it inherits that pollution. The LLM will reference the governing document throughout the project, compounding the problem with each iteration.

Example: A project overview that explains "we're using the Pareto principle to keep this lean" will produce deliverables that reference brevity, trade-offs, and scope limitations—none of which belong in a professional output.

**The principle:** Clean the governing document *before* beginning any drafting. Time spent removing pollution from the foundation saves exponentially more time than fixing it in every downstream deliverable.

---

## The Solution: Intentional Context Management

The goal is to prevent drafting context from appearing in deliverables. This requires separating "information that helps you work" from "information that belongs in the output"—but the mechanism for achieving this separation can vary.

### Principle 1: Separate concerns, not necessarily files

The distinction between working context and deliverable content must exist somewhere. Options include:

- **Conversation memory**: Working context stays in the conversation; only deliverable-relevant content is written into documents the LLM will reference during drafting.
- **Embedded filtering rules**: A single governing document contains both context and explicit rules defining what belongs in deliverables. The rules act as the specification.
- **Physical document separation**: Separate files for project context and deliverable specification.

The first two approaches work well when the primary user is also the author. Physical separation is useful when working context must be documented for team reference or handoff.

### Principle 2: Explicit filtering rules

Establish clear criteria for what belongs in the deliverable. Make these rules visible—either in the governing document or as part of review criteria.

Example filtering tests:

1. **Time Test**: Would this still be valid in 5 years?
2. **Audience Test**: Would an external reader question why this is included?
3. **Specificity Test**: Does this reference current constraints or project state?
4. **Professional Test**: Does this sound like institutional documentation or project notes?

### Principle 3: Role-based language as a forcing function

Require deliverables to use institutional voice:

- "The function shall..." instead of "We will..."
- "Personnel must..." instead of "Our team should..."
- "The department" instead of "Our department"

This syntactic constraint makes pollution obvious. "Our 4-person team shall..." is clearly wrong in a way that "We have a 4-person team" might not be.

### Principle 4: Iterative hardening

Do not assume the governing document is clean after initial drafting. Review it explicitly before beginning deliverable work, remove or relocate polluting content, and repeat after significant changes. Each review cycle hardens the document against pollution.

### Principle 5: Review for pollution indicators

Before finalizing, specifically search for pollution patterns:

- First-person plural ("we", "our", "us")
- Version references ("v1", "v2", "future")
- Constraint language ("given", "limited", "without")
- Methodology terms (project-specific jargon)
- Temporal references ("currently", "for now", "initially")

---

## Practical Workflow: LLM-Assisted Pollution Review

The most effective way to identify context pollution is to use the LLM itself—but with a specific workflow that leverages how LLMs weight context.

### Step 1: Prime Before Review

Do not simply ask the LLM to "review for context pollution." First, ask the LLM to articulate *why* context pollution matters for this specific project and phase.

**Why this works:** LLMs weight recent context more heavily. By having the LLM explain the problem immediately before conducting the review, you load the relevant concepts into the high-attention portion of the context window.

**Example prompt sequence:**
> "Before we review this document, articulate back to me why context pollution is a concern at this phase of the project."

The LLM's response reinforces:
- The distinction between drafting context and deliverable content
- The specific risks for this project
- The compounding effect if not addressed now

Only after this priming step do you request the actual review.

### Step 2: Conduct the Review

Ask the LLM to review the governing document with explicit framing:

> "Review this document using a 'what you see is all there is' approach—as if this is the only context you have. Identify any context pollution or content that would be inappropriate in the deliverable."

**Why "what you see is all there is":** This framing forces the LLM to evaluate the document as a standalone artifact rather than filling in gaps from conversation history. It surfaces content that relies on unstated context to make sense.

### Step 3: Make Corrections

Apply the identified changes systematically. For each correction:

- Remove or relocate the polluting content
- Ensure removals don't leave orphaned references
- Verify replacements use appropriate institutional language

Do not assume corrections are automatically clean.

### Step 4: Second Review with Critical Thinking Check

After corrections, request a second review with an additional constraint:

> "Review again, and use critical thinking to ensure the fixes don't introduce new pollution."

**Why this matters:** Corrections often introduce new problems:
- Removing one phrase may leave an orphaned reference
- Rewording may introduce different polluting language
- Structural changes may create new inconsistencies

The explicit instruction to evaluate fixes for secondary pollution catches these issues.

### Step 5: Commit Clean State

After the second review passes, commit the clean document as a checkpoint. This creates a known-good baseline for diffing if pollution is introduced later.

---

## Implementation Patterns

### For Single-Document Projects

Add a filtering section at the top of your context that explicitly states:

1. What information is for understanding only
2. What information should appear in output
3. What language patterns to use
4. What language patterns to avoid

### For Multi-Document Projects

Separate documents entirely:

```
project/
├── PROJECT_CONTEXT.md      # Constraints, methodology, team, timeline
├── DELIVERABLE_SPEC.md     # Structure and content requirements only
└── output/
    └── deliverable.md      # Clean output
```

The LLM should primarily reference the specification when drafting. Context document is for your understanding and for answering clarifying questions.

### For Iterative Projects

Commit clean checkpoints. If pollution is introduced, you can diff against a known-clean state to identify what was added.

---

## Summary

| Concept | Description |
|---------|-------------|
| **Context Pollution** | Drafting context bleeding into deliverable content |
| **Root Cause** | LLMs weight all context without distinguishing purpose |
| **Primary Symptom** | Deliverables that explain project decisions to readers who don't need them |
| **Governing Document Risk** | Pollution in the foundation compounds into all downstream deliverables |
| **Prevention** | Separate concerns via conversation memory, embedded rules, or document separation |
| **Hardening** | Iterative review and scrubbing before drafting begins |
| **Detection** | Primed LLM review with "what you see is all there is" framing |
| **Validation** | Second review checking that fixes don't introduce new pollution |

---

## Key Insight

More context helps LLMs understand your situation.  
Less context in deliverables helps your audience understand what matters.

These are in tension. Managing that tension deliberately—rather than hoping the LLM figures it out—is the core skill.