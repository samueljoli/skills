---
name: mental-model-builder
description: "Turn abstract concepts into concrete visual artifacts that support understanding, mental simulation, and prediction."
---

# Visual Mental Model Builder

## Purpose

Convert abstract concepts into concrete visual artifacts. Optimize for **understanding and mental simulation**, not exhaustive explanation.

## Core Rule

Choose the visualization based on the question being answered:

| When you need to understand…             | Create…                      |
| ---------------------------------------- | ---------------------------- |
| What things exist?                       | Concept map / object map     |
| How things are structurally connected?   | Boxes-and-arrows diagram     |
| What happens over time?                  | Sequence diagram             |
| What states something can occupy?        | State machine                |
| How information transforms?              | Data-flow / pipeline diagram |
| How something is nested/composed?        | Tree diagram                 |
| Why a decision happens?                  | Decision tree / flowchart    |
| What actually happens to a real example? | Execution trace / simulation |

## Workflow

For any concept:

1. **Identify the question.** Determine what aspect of the concept is difficult to visualize.
2. **Choose the artifact.** Select the representation from the table above.
3. **Extract the primitives.** Identify objects, relationships, states, events, inputs, outputs, and boundaries relevant to that representation.
4. **Visualize.** Create the smallest diagram that preserves the important mechanics.
5. **Make it concrete.** Use realistic names and values instead of `A`, `B`, and `foo` when possible.
6. **Add motion.** If behavior matters, walk one example through the diagram step-by-step.
7. **Test the model.** Present a scenario and require the learner to predict what happens next.

## Principles

* Prefer diagrams over paragraphs when spatial relationships matter.
* Prefer sequences over static diagrams when time matters.
* Prefer state machines when behavior depends on current state.
* Prefer concrete traces when an abstraction still feels opaque.
* Introduce complexity progressively; do not show the entire system at once.
* Keep terminology attached to visible objects or actions.
* Use multiple representations when one artifact cannot explain the concept.
* A mental model is successful when the learner can **predict system behavior**, not merely repeat its definition.

## Output

Default to:

**Plain-language model → appropriate visual artifact → concrete example → step-by-step trace → prediction test.**
