# Model Distillation

## What it is

Model distillation trains a smaller student model to reproduce useful behavior from a larger teacher model.

You run prompts through a strong LLM model, save its outputs or probability distributions, and train a new, smaller model on those targets instead of relying only on raw web text. The student learns to approximate the teacher's behavior rather than rediscovering every capability from scratch.

For sequence-level distillation, the training stage is ordinary supervised fine-tuning. Logit distillation adds a loss that makes the student match the teacher's probability distribution, not just its sampled text.

## The pipeline

```
prompt set
    │
    ▼
teacher model ──(generate)──▶ raw targets ──(filter)──▶ clean dataset ──(fine-tune)──▶ student model
                                                                                              ▲
                                                                                  open base model
```

1. Collect prompts — use curated datasets, permitted usage data, or synthetic prompts with the coverage you need
1. Generate — run the prompts through the teacher and save the completions or distributions
1. Filter — discard wrong, low-quality, unsafe, or malformed targets
1. Fine-tune — continue training an existing base model on the survivors
1. Evaluate — check that the target behavior improved without unacceptable loss of general ability

A full fine-tune usually produces a new checkpoint with the same architecture as the base model and updated parameter values. Adapter training instead produces separate adapter weights, and quantization can change the stored representation.

## Two variants

| Variant | Access needed | Signal quality | Notes |
| --------------------------- | ------------------------------------------ | -------------- | ---------------------------------------------------------------------------------------------------------------- |
| Logit distillation | Teacher probabilities or weights | Higher | The student matches the teacher's full probability distribution for each next token, not just the chosen token. |
| Sequence-level distillation | Any interface that returns teacher outputs | Lower | The student is fine-tuned on the teacher's text output; this is often what people mean by response distillation. |

Sequence-level distillation can be done through an API, but an API is not required if the teacher can generate locally. Logit distillation generally requires access to token-level probabilities and compatible tokenization or a way to align the teacher's distribution with the student's vocabulary.

## Teacher and student are independent roles

The teacher supplies training targets. The base model supplies the student's starting weights, architecture, tokenizer, and capacity. For sequence-level distillation, the teacher and student do not need to share an architecture or tokenizer because the transfer happens through text.

```
DeepSeek-R1 ──(reasoning samples)──▶ Qwen2.5-32B base ──(SFT)──▶ DeepSeek-R1-Distill-Qwen-32B
  teacher                              student base                 student
```

The same teacher traces can be used with multiple base models and model sizes. A closed teacher can work too, provided its terms allow the intended use and its outputs are accessible.

## Why it is used

Cost. Teacher generation and student fine-tuning still cost money and compute, but they can be much cheaper than pretraining a model from scratch. The student starts from finished weights and needs a comparatively small, targeted training run.

Deployability. A large frontier or mixture-of-experts model may require multiple GPUs or nodes for practical inference. A distilled 8B–32B model can often run on a single consumer GPU, especially when quantized. Distillation is one important path for making advanced behavior available on more modest hardware.

Specialization. You choose the prompt distribution, so you choose what receives the most training signal. Collect mostly SQL examples and you can produce a small model that is strong at SQL rather than mediocre at everything.

Consistency. Labs can distill behavior from a larger model into smaller members of the same product family so they share useful response patterns.

## On the data question

Distillation does not remove the data problem; it changes it from a pretraining-scale problem into a targeted data-engineering problem.

For a basic sequence-level distill, you no longer need to assemble and clean a multi-trillion-token pretraining corpus or build the full pretraining mixture. You also do not need to reproduce the teacher's reinforcement-learning environments and reward models unless you choose to use those methods for the student.

You still need to:

- Source a prompt set with adequate coverage; the student only learns what the prompts and targets expose.
- Filter aggressively because teacher mistakes become training data. Verification can include executing code, checking math, using reference answers, or sampling multiple responses and measuring agreement.
- Guard against overfitting because training too long or too narrowly can degrade general ability.

The honest framing is that you trade a research-scale data problem for an engineering-scale one. That is still real work, but it is often tractable for a small team.

## Limits

- Knowledge does not transfer perfectly. The student does not receive the teacher's internal state or all of its learned knowledge; transfer depends on the examples, the student's capacity, and the target task.
- The teacher usually sets the practical ceiling for faithful imitation, although the student can outperform it on particular benchmarks through its base model or generalization.
- Error inheritance. Teacher hallucinations and undesirable habits can be reproduced confidently.
- Narrowing. Coverage gaps in the prompt set become capability gaps in the student.
- Hidden reasoning. If the teacher does not expose intermediate reasoning, the student cannot train directly on those traces. Many deployed reasoning systems expose final answers or abbreviated summaries rather than their full internal computation, which can provide a weaker distillation signal.
- Terms and licenses. The rules are provider- and model-specific. Some commercial-service terms prohibit automatic extraction or using outputs to develop competing models, while open-weight licenses can impose their own use or redistribution restrictions. Check the applicable terms before collecting or training on outputs.

## Reference points

- Alpaca (2023) — a landmark early example: a 7B model fine-tuned from LLaMA 7B on 52K instruction-following demonstrations generated by OpenAI's text-davinci-003. The data-generation run cost less than $500 according to Stanford's report.
- DeepSeek-R1-Distill family (2025) — six dense models trained from Qwen2.5-family and Llama-family bases using samples generated by DeepSeek-R1. The Qwen 1.5B–32B variants were fine-tuned on 800K curated samples; the released recipe used supervised fine-tuning for the distilled models rather than a new reinforcement-learning stage.
- Phi and Gemma — examples of large labs using synthetic data and teacher-model supervision, although their public training details differ and should not be treated as identical recipes.
- Community fine-tunes — open models trained on collected frontier-model outputs, often with the teacher named in the model title.

## Strategic note

Open weights hand over the artifact but not the factory. Distillation is a leak in that arrangement: it does not reveal the recipe, but it can provide a large supply of the recipe's outputs, and for behavior those outputs may be much of what you need.
