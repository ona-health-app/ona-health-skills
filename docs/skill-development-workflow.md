# Skill Development & Improvement Workflow

This guide walks through the full lifecycle of developing a skill in this repo, from first draft through iterative improvement to packaging.

## Overview

The core loop is: **draft -> test -> review -> improve -> repeat**.

You write a skill, run it against realistic prompts, compare the output to a baseline (no skill), review the results with the eval viewer, and revise. Each pass through the loop is an "iteration" and produces a directory of artifacts in the workspace.

```
┌─────────────┐
│  Draft or    │
│  improve     │
│  SKILL.md    │
│              │
└──────┬───────┘
       │
       ▼
┌─────────────┐
│  Run evals   │  with-skill + baseline, in parallel
│  (subagents) │
└──────┬───────┘
       │
       ▼
┌─────────────┐
│  Grade &     │  assertions, timing, benchmark.json
│  aggregate   │
└──────┬───────┘
       │
       ▼
┌─────────────┐
│  Review in   │  eval viewer (Outputs tab + Benchmark tab)
│  browser     │
└──────┬───────┘
       │
       ▼
┌─────────────┐     not happy
│  Happy with  │──────────────────┐
│  results?    │                  │
└──────┬───────┘                  │
       │ yes                      │
       ▼                          ▼
┌─────────────┐          back to top
│  Optimize    │
│  description │
│  & package   │
└─────────────┘
```

---

## Step 0: Understand the skill's purpose

Before writing anything, nail down:

- **What** should the skill enable an agent to do?
- **When** should it trigger? (what user phrases, file types, or contexts)
- **What** does good output look like?

If the answers to these aren't clear yet, talk it through with the skill-creator (invoke it with `/skill-creator` in Cursor) -- it will interview you and help narrow things down.

---

## Step 1: Write or edit the SKILL.md

Each skill lives in its own directory with a `SKILL.md` at the root:

```
prescriptions/
├── SKILL.md          # The skill definition
├── scripts/          # Helper scripts the skill can call
├── references/       # Domain docs loaded on demand
└── assets/           # Templates, icons, etc.
```

The `SKILL.md` has two parts:

1. **YAML frontmatter** -- `name` and `description` (the description is the primary trigger mechanism; make it specific and a bit pushy so the agent actually uses the skill when it should).
2. **Markdown body** -- the actual instructions the agent follows when the skill is activated.

Tips for writing the body:
- Keep it under ~500 lines. If it's getting long, move detail into `references/` files and point to them.
- Explain *why* things matter, not just *what* to do. The agent is smart and responds better to reasoning than rigid rules.
- Use imperative form ("Extract the claim number" not "You should extract the claim number").
- Include examples of input/output where it helps.

---

## Step 2: Write test prompts

Create 2-3 realistic prompts -- the kind of thing a real user would type. Save them in the evals directory:

**File:** `evals/<skill-name>-evals.json`

```json
{
  "skill_name": "prescriptions",
  "evals": [
    {
      "id": 1,
      "prompt": "A realistic user request...",
      "expected_output": "What success looks like",
      "files": [],
      "expectations": []
    }
  ]
}
```

- `prompt`: The task as a user would phrase it.
- `expected_output`: A human-readable description of what good output looks like.
- `files`: Any input files the prompt references (paths relative to repo root).
- `expectations`: Leave empty for now -- you'll add assertions in step 4.

---

## Step 3: Run evals (with-skill and baseline)

For each test prompt, launch two runs in parallel:

| Run | What it does | Output path |
|-----|-------------|-------------|
| **with_skill** | Agent has access to your skill | `<skill>-workspace/iteration-N/eval-<ID>/with_skill/outputs/` |
| **baseline** | Agent has no skill (or old skill version) | `<skill>-workspace/iteration-N/eval-<ID>/without_skill/outputs/` |

Running both lets you see whether the skill actually helps vs. the agent's default behavior.

Each eval directory also gets an `eval_metadata.json`:

```json
{
  "eval_id": 1,
  "eval_name": "drug-interaction-summary",
  "prompt": "The user's task prompt...",
  "assertions": []
}
```

Give each eval a descriptive name (not just "eval-1") so it's easy to identify in the benchmark viewer.

---

## Step 4: Draft assertions

While runs are in progress, draft quantitative assertions -- objectively verifiable checks on the output. Good assertions have descriptive names and are things you can answer yes/no:

- "Output contains a table with columns: drug_name, interaction, severity"
- "At least one item is flagged for pharmacist review"
- "Output is valid CSV"

Add these to the `expectations` array in both `evals/<skill>-evals.json` and each `eval_metadata.json`.

Not everything needs assertions. Subjective quality (tone, style, layout) is better judged by eye in the viewer. Only assert on things that can be checked programmatically or with clear pass/fail criteria.

---

## Step 5: Grade and aggregate

Once all runs finish:

1. **Grade each run** against its assertions. Results go in `grading.json` inside each run directory. The grading file uses this format for each assertion:

   ```json
   { "text": "Output contains a severity column", "passed": true, "evidence": "Found column 'severity' in row 1" }
   ```

2. **Aggregate into a benchmark** by running (from the skill-creator directory):

   ```bash
   cd .agents/skills/skill-creator
   python -m scripts.aggregate_benchmark ../../../<skill>-workspace/iteration-N --skill-name "<skill>"
   ```

   This produces `benchmark.json` and `benchmark.md` with pass rates, timing, and token usage for with-skill vs baseline, including mean +/- standard deviation.

3. **Analyst pass** -- look at the benchmark for patterns: assertions that always pass regardless of skill (not useful), high-variance results (possibly flaky tests), time/token tradeoffs.

---

## Step 6: Review in the eval viewer

Launch the viewer:

```bash
python .agents/skills/skill-creator/eval-viewer/generate_review.py \
  <skill>-workspace/iteration-N \
  --skill-name "<skill>" \
  --benchmark <skill>-workspace/iteration-N/benchmark.json
```

For iteration 2+, add `--previous-workspace <skill>-workspace/iteration-<N-1>` to see side-by-side comparisons with the last round.

The viewer has two tabs:

- **Outputs** -- shows each test case one at a time: the prompt, the output files rendered inline, formal grades (if graded), and a text box for your feedback.
- **Benchmark** -- aggregate stats: pass rates, timing, tokens for each configuration.

Navigate with prev/next buttons or arrow keys. Type feedback for anything that needs improvement. Click "Submit All Reviews" when done -- this saves a `feedback.json` file.

---

## Step 7: Improve the skill

Read the feedback and revise the SKILL.md. Key principles:

- **Generalize, don't overfit.** You're iterating on a few examples, but the skill will be used on many. Don't add narrow patches; find the underlying issue.
- **Keep it lean.** If something in the skill isn't pulling its weight (check the run transcripts -- is the agent spending time on unproductive steps?), remove it.
- **Explain the why.** Instead of rigid ALWAYS/NEVER rules, explain the reasoning so the agent can adapt to novel situations.
- **Bundle repeated work.** If every test run independently wrote a similar helper script, that's a signal to write it once, put it in `scripts/`, and reference it from the skill.

---

## Step 8: Repeat

Go back to step 3. Run evals into a new `iteration-<N+1>/` directory. Launch the viewer with `--previous-workspace` pointing at the last iteration. Review again. Keep going until:

- Feedback is all empty (everything looks good).
- You're satisfied with the benchmark numbers.
- You're not making meaningful progress.

---

## Step 9: Optimize the description (optional)

The `description` field in the SKILL.md frontmatter determines whether the agent activates the skill. After the skill itself is solid, you can optimize the description for better triggering accuracy:

1. Generate ~20 eval queries (mix of should-trigger and should-not-trigger).
2. Review them in the HTML template (the skill-creator can generate this for you).
3. Run the optimization loop:

   ```bash
   cd .agents/skills/skill-creator
   python -m scripts.run_loop \
     --eval-set <path-to-eval-set.json> \
     --skill-path <path-to-skill> \
     --model <model-id> \
     --max-iterations 5 \
     --verbose
   ```

4. Apply the best description from the output.

---

## Step 10: Package

When the skill is ready for distribution:

```bash
cd .agents/skills/skill-creator
python -m scripts.package_skill ../../../prescriptions
```

This creates a `.skill` file (a zip archive) that can be installed elsewhere.

---

## Directory structure during development

After a couple of iterations, your workspace looks like this:

```
prescriptions-workspace/
├── iteration-1/
│   ├── drug-interaction-summary/
│   │   ├── eval_metadata.json
│   │   ├── with_skill/
│   │   │   ├── outputs/          # Files the skill produced
│   │   │   ├── grading.json      # Assertion results
│   │   │   └── timing.json       # Tokens and duration
│   │   └── without_skill/
│   │       ├── outputs/
│   │       ├── grading.json
│   │       └── timing.json
│   ├── benchmark.json
│   └── benchmark.md
├── iteration-2/
│   └── ...
└── feedback.json
```

---

## Quick reference: key files

| File | Purpose |
|------|---------|
| `<skill>/SKILL.md` | The skill definition (frontmatter + instructions) |
| `evals/<skill>-evals.json` | Test prompts and assertions |
| `<skill>-workspace/iteration-N/` | Outputs, grades, and benchmarks for one iteration |
| `<skill>-workspace/feedback.json` | Your review comments from the eval viewer |
| `.agents/skills/skill-creator/` | The skill-creator tooling (grader, viewer, aggregator, packager) |
