# Calibrating discovery and iterations

These examples illustrate decisions, not fixed scripts or a required number of turns.

## Vague intent: ask before choosing the product

User: "I want an AI assistant for our operations team. Plan it."

Useful first question: "Which recurring task should it help an operator complete first? For example, explaining a failed run and taking a recovery action have different access and correctness requirements."

Do not begin by selecting a model, database, UI framework, or a backlog. The first uncertainty is the intended job. If the answer is "handle incidents automatically", clarify a representative incident and what actions it may take. Once that boundary is settled, inspect existing incident workflows and ask only about remaining consequential choices.

An answer such as "read failed-run logs and explain likely causes; operators take all actions" already resolves much of the autonomy question. Do not separately ask about every possible write permission. Surface any ambiguity in what makes an explanation useful, then focus on the evidence needed to evaluate it.

## Sufficient context: synthesize and move on

User: "Plan a read-only failed-run explainer for operators in our existing CLI. It should use logs we can already retrieve, link claims to log evidence, and say when the cause is unknown. No recovery actions or new UI. Start with one job family; we'll evaluate against our saved incidents before expanding. Reuse current authentication. First we need to choose an acceptable evaluation gate."

The user has already supplied the consumer, journey, boundaries, first scope, and evaluation source. Ask about the evaluation gate with a concrete recommendation and its tradeoffs. After the answer, summarize the agreed plan and produce iterations if no material contradiction remains. Do not ask the user to repeat the scope, choose internal class names, or approve every phase.

If the evaluation gate were already supplied too, no interview round would be needed. Inspection may still reveal a consequential gap; ask about that gap specifically.

## Mixed uncertainty: intent versus evidence

- "Should operators receive suggestions or should the system execute recovery?" is an intent decision that may change the entire design. Resolve it conversationally before settling that design.
- "Do the available logs contain enough evidence to explain failures reliably?" is an empirical question. Plan a bounded evaluation with a sample, output evidence, and decision rule. Asking the user repeatedly cannot establish that fact.
- "What timeout should an internal fetch use?" may be a reversible implementation choice once operational constraints are known. Follow established practice or state an assumption unless it changes the promised behavior.

If the user says "stop asking and draft it", present a provisional approach and identify the unresolved autonomy boundary. A suggested read-only first iteration can be a proposal; do not record that as an agreed permanent product decision.

## Iterations contain outcomes and learning

For the failed-run explainer, after the above intent is settled:

| Iteration | Useful outcome and scope | Evidence and review | What follows |
|---|---|---|---|
| I1: Establish feasibility | Produce evidence-linked explanations for a bounded saved-incident sample from one job family. No live operator rollout. | Evaluate against the agreed correctness, evidence support, and unknown-cause criteria; inspect errors with the operational owner where judgment is needed. | If the gate is met, proceed to the CLI pilot. Otherwise use the errors to decide between a bounded revision, improved source evidence, or stopping. |
| I2: Pilot the real workflow | Operators request an explanation for that job family through the existing CLI and identity boundary. | Demonstrate live log retrieval, evidence links, unknown-cause behavior, and unavailable-log handling; evaluate usefulness in the agreed pilot. | Expand only if the pilot supports it; revise the interaction or source handling if those are the limiting factors. |
| I3: Extend supported coverage | Add the remaining agreed job families or scenarios. Exact order depends on earlier evidence. | Apply the same evaluation contract to each added population and check prior supported cases. | Retain explicit unsupported cases where evidence remains insufficient; revisit the agreed scope if necessary. |

I2 could contain two issues: one complete CLI request-to-explanation path for available logs, and one complete unavailable-log/retry interaction. Each must work with its prerequisites; neither may depend on a future ticket for essential access control or truthful failure handling. The iteration ends when the combined workflow is ready for the pilot review.

For predictable work, an iteration's review can simply demonstrate that the agreed behavior works before expanding scope. Do not impose research metrics or a new human approval gate on every iteration.

## When to resume interviewing

If evaluation shows that a source cannot support the promised behavior, surface the implication and ask about the resulting scope or tradeoff when user intent is needed. Do not reopen settled choices unrelated to that evidence. Update the affected iteration and conditional follow-up work together.
