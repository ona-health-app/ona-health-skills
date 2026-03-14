# ona-health-skills

Repository for building and maintaining two healthcare agent skills: **prescriptions** and **insurance-claims**. Uses the [skill-creator](.agents/skills/skill-creator/) workflow for drafting, testing, benchmarking, and packaging.

## Directory layout

```
ona-health-skills/
├── prescriptions/              # Prescriptions skill
│   ├── SKILL.md                # Skill definition (when to use, instructions)
│   ├── scripts/                # Bundled scripts for deterministic tasks
│   ├── references/             # Domain docs loaded into context as needed
│   └── assets/                 # Templates, icons, etc.
├── prescriptions-workspace/    # Eval run outputs (iteration-1/, iteration-2/, …)
├── insurance-claims/           # Insurance claims skill (same structure)
├── insurance-claims-workspace/
├── evals/                      # Starter test prompts
│   ├── prescriptions-evals.json
│   └── insurance-claims-evals.json
├── .agents/skills/             # Installed utility skills (find-skills, skill-creator)
└── skills-lock.json            # Lockfile for installed skills
```

- **Skill dirs** (`prescriptions/`, `insurance-claims/`): Edit `SKILL.md` and add scripts/references/assets as the skill grows.
- **Workspaces**: Used by the skill-creator eval loop. Results go under `*-workspace/iteration-N/` (with-skill vs baseline outputs, grading, benchmark).
- **evals/**: JSON files with test prompts. Copy or merge into `evals/evals.json` inside each skill when running the full eval workflow, or point the skill-creator at these files.

## Quick start

1. **Edit a skill**  
   Update `prescriptions/SKILL.md` or `insurance-claims/SKILL.md` (description + body). Use the skill-creator skill in Cursor to draft, refine, and add assertions.

2. **Run the eval loop**  
   With the skill-creator workflow: spawn test runs (with-skill and baseline), grade assertions, aggregate into `benchmark.json`, then run the eval viewer:
   ```bash
   python .agents/skills/skill-creator/eval-viewer/generate_review.py \
     <workspace>/iteration-N --skill-name "prescriptions" --benchmark <workspace>/iteration-N/benchmark.json
   ```
   Use `prescriptions-workspace` or `insurance-claims-workspace` as the workspace. See the skill-creator’s SKILL.md for the full sequence (evals, grading, analyst pass, viewer).

3. **Package a finished skill**  
   From the repo root (pass the path to the skill folder):
   ```bash
   cd .agents/skills/skill-creator && python -m scripts.package_skill ../../../prescriptions
   cd .agents/skills/skill-creator && python -m scripts.package_skill ../../../insurance-claims
   ```
   This produces `.skill` files in the skill-creator directory (e.g. for installation via `npx skills add` or Cursor).

## Evals

Starter prompts live in `evals/prescriptions-evals.json` and `evals/insurance-claims-evals.json`. Customize prompts, add `files` and `expectations`, then use them in the skill-creator loop (e.g. copy into each skill’s `evals/evals.json` or wire your runs to these files).
