# Most of your experiment findings are already dead

You ran the experiment. You got a result. The result is in a JSON file somewhere.
You wrote a one-line verdict in the docstring. Six months later, nobody — including
you — can answer the question *"what did we actually establish?"* without re-reading
the code.

That finding is dead. Not wrong. Dead. And the tools you use to track experiments
cannot see it die.

## The number that made me build this

I audited a research codebase — 532 experiments, each producing a result file. Of
those, **80% had no structured finding at all.** The other 20% emitted findings in
ad-hoc, mutually incompatible formats: one used `summary.verdict`, another a
top-level `conclusion`, another a `poc_status`, another free text. The parser that
tried to aggregate them fell back through **six candidate keys in priority order**
and still missed most.

The findings weren't lost because the experiments failed. They were lost because the
*finding* — the verdict, the claim about what was established — was never structured
in the first place. It lived in prose docstrings and ad-hoc JSON, and prose rots
faster than code.

## Knowledge dies two deaths

Watch the failure modes and a pattern falls out. A finding dies one of two ways:

1. **It's faked.** The verdict isn't grounded in evidence — it's lens-dressed, an
   interpretation dressed as a result. It *sounds* right. It collapses the moment
   someone loads it: tries to act on it, reproduce it, cite it. This is the finding
   that says "CONFIRMED" with no evidence behind it.

2. **It's orphaned.** The finding is real and correct — but it reaches nobody. It
   sits in a result file nothing queries, references no decision, informs no action.
   Correct and uninfluential. This is the experiment that CONFIRMED something and
   then informed nothing for two years.

The first can't carry truth. The second can't carry it anywhere. Both are dead. And
here's the thing the tracking tools miss: **MLflow, W&B, DVC, Weights & Biases —
none of them operate at the finding layer at all.** They track metrics, parameters,
artifacts, runs. They do not track *what was established.* The verdict — the actual
claim the experiment makes about the world — has no home in any of them. (I checked.
Forty-plus tools and metadata standards. The verdict layer is empty everywhere.)

So the finding leaks. It leaks the way a signal leaks: not destroyed, just
un-encoded into anything that survives.

## The one property that stops it

A finding survives only when it carries **both** of two properties, and the absence
of either is fatal:

- **True-checkable.** The verdict is grounded in evidence you can point at. A reader
  can verify the claim without trusting the author. Without this, it's faked — it
  collapses under load.
- **Connected-queryable.** The finding has a stable identity and a known verdict, so
  a downstream consumer (a decision, a metabolism step, the next experiment) can find
  it and act on it. Without this, it's orphaned — correct but unreachable.

Most findings have neither. Some have one. Almost none are structured to guarantee
both. That's why 80% die.

## What a surviving finding looks like

A finding that resists both deaths needs five things, and not six:

```
finding_id   — a stable, citable identifier (so it can be found and referenced)
claim        — the declarative assertion (what was established)
verdict      — CONFIRMED | PARTIAL | REFUTED | INCONCLUSIVE | UNDECIDABLE
evidence     — what backs the claim, and where to find it (type + summary + ref)
scope        — the conditions under which the claim holds (env, population, axioms)
```

That's it. Five fields. The verdict is a closed five-state vocabulary — derived
across eight experimental domains (statistics, clinical trials, ML benchmarking,
systematic reviews, replication, formal verification, physics, pre-registration),
because the *difference between "unsettled" and "proven-unsettlable"* is real and
collapsing them loses information. (`UNDECIDABLE`, the formal-methods state, is not
the same as `INCONCLUSIVE` — one means we lack data, the other means we proved no
data can settle it.)

This isn't a tracking schema. It's a *verdict* schema — the layer nothing else
covers. It sits alongside your MLflow/W&B; it doesn't replace them.

## Does it actually work?

I built a validator (`findcheck`) and ran it on the real corpus. **170 actual
findings** — 100 experiments + 70 decisions — migrated from the ad-hoc formats into
the schema, every one validating clean. Clinical trial results and ML benchmark
ablations migrated losslessly too; the structure is genuinely cross-domain, not
shaped to one project.

```bash
pip install findcheck
findcheck validate your-findings.json     # exit 0 valid, 1 invalid
```

Honest scope, because overselling is one of the deaths: this catches *structural*
findings — the verdict, the evidence, the scope. It does **not** adjudicate whether
a citation *supports* a claim (that's semantic, probabilistic, and inherently
false-positive-prone — a different problem). It does not track metrics over time
(use MLflow). It declares the finding; it doesn't run the experiment. Narrow on
purpose.

## The part that's not about tools

Here's the deeper thing, and why I'm writing this instead of just shipping the repo.
**Findings leak because signal leaks, and signal leaks unless it's encoded to resist
its own death.** A raw quantum bit decoheres — its state bleeds into the environment
and is gone. You don't fix that by being careful; you fix it by *encoding* the
signal redundantly so the structure itself detects and corrects the corruption. The
encoded bit — a *logical* qubit — survives specifically because the encoding refuses
to let the signal die either way: it can't be silently corrupted (the code detects
it) and it can't be lost (the encoding holds it).

A finding is the same. Left raw — prose, ad-hoc JSON, a docstring — it decoheres.
The verdict drifts, the evidence detaches, the scope gets over-generalized, and six
months later it's either faked-up or orphaned. The schema is the error-correcting
code: it refuses to let the finding die either death. It forces the verdict to be
grounded (can't fake) and it gives the finding a stable identity (can't orphan).

Knowledge doesn't survive because you're careful. It survives because you encoded it
to survive. Most experiment findings are already dead because nobody encoded them at
all.

---

*The schema, validator, and a query tool are at
[github.com/patchwright/finding-declaration](https://github.com/patchwright/finding-declaration).
`pip install findcheck`. The 5-field structure and 5-state verdict vocabulary are
documented in the spec. It's MIT, it's narrow, and it catches the layer your
tracking tools can't see.*
