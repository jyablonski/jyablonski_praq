# LLM Training: Data, Compute, and the Long Feedback Loop

Large language model training is a pipeline rather than one uninterrupted computation: acquire data, curate it, pre-train a base model, post-train it for behavior and capabilities, evaluate it, and repeat. The figures below are representative public reports, not universal requirements.

## 1. Where training data comes from

| Source | Typical role | Main constraint |
| --- | --- | --- |
| Public web crawls | Broad coverage of language, facts, code, and discussion | Noisy, duplicated, unevenly distributed, and subject to access and rights constraints |
| Licensed or first-party collections | Structured archives, feeds, private data, or specialized domains | Cost, contract scope, freshness, and jurisdiction |
| Public and open corpora | Encyclopedias, scientific papers, government records, public-domain books, and permissively licensed code | Coverage, license compatibility, and domain bias |
| Human-authored data | Instructions, demonstrations, preferences, expert judgments, and red-team examples | Expensive, slow, and difficult to scale consistently |
| Synthetic and verifiable data | Model-generated examples filtered by another model, a rule, a compiler, a test suite, or an environment | Error amplification and evaluator bias |

### Common Crawl

Common Crawl is a nonprofit public-web archive that has collected data since 2008. Its current site reports more than 300 billion pages across 15 years, while individual 2026 releases contain about 2 billion page captures and hundreds of tebibytes of uncompressed data. The archive provides WARC files for raw crawl records, WAT files for computed metadata, and WET files for extracted text. It is a sample of the web, not a complete copy of any site; CCBot checks robots.txt and does not generally log in or go behind paywalls. A public crawl is also not a blanket reuse license: the rights and terms attached to the underlying content still matter.

Common Crawl is an input, not a finished training set. Public derivatives include C4, RefinedWeb, Dolma, and FineWeb; each applies its own extraction, filtering, deduplication, and mixture choices.

### Licensing is not permission to scrape

A direct license can provide structured delivery, access to material that is not in a public crawl, contractual usage rights, and sometimes representations or indemnities. It does not have one standard form, and commercial terms are often confidential. The safe generalization is that a license changes the rights and delivery contract; it does not make every downstream use automatically lawful.

## 2. The data-processing pipeline

1. **Extraction** — Convert HTML, PDFs, scans, and other source formats into text or multimodal records.
1. **Language and heuristic filtering** — Detect language and remove malformed, repetitive, unsafe, or obviously low-value material.
1. **Quality scoring** — Use rules, classifiers, reference corpora, model scores, or combinations of these to rank or filter examples.
1. **Deduplication** — Remove exact duplicates and near-duplicates at URL, document, line, or n-gram level.
1. **Safety and privacy filtering** — Remove or minimize unsafe content, personal data, and other material that should not enter the training mix.
1. **Decontamination** — Search for overlap with evaluation and benchmark data; this is difficult and can be incomplete.
1. **Mixture design** — Choose proportions for domains, languages, quality tiers, repetition, upsampling, and late-stage annealing.

The last step is usually the least reproducible. Architecture and headline scale are public more often than the exact data mixture, filtering thresholds, and failed experiments.

The funnel is best understood qualitatively: a raw crawl becomes a smaller candidate corpus after extraction, language and quality filtering, and deduplication; the final training stream can be larger than the deduplicated pool because selected sources are deliberately upsampled or repeated.

Public scale examples are not interchangeable. GPT-3 used 300 billion training tokens, Llama 2 reported 1.8 trillion tokens, and Llama 3.1 405B reported 15.6 trillion text tokens. These numbers describe particular recipes, tokenizers, and model families rather than a universal target.

Human and synthetic post-training data are much smaller than pre-training corpora in token count, but they can be expensive per example and highly influential. Llama 3.1 reports more than 25 million synthetically generated fine-tuning examples in its model card, while its research paper describes human preference data, synthetic data, rejection sampling, and quality control as separate parts of the recipe.

## 3. Training phases and calendar time

| Phase | What it does | Typical planning reality |
| --- | --- | --- |
| Data pipeline | Collects, cleans, scores, deduplicates, and mixes data | Continuous and often shared across model generations |
| Pre-training | Learns next-token or related foundational objectives | Weeks to months at large cluster scale, depending on model, token budget, and hardware |
| Continued or mid-training | Adapts context length, data mixture, domain coverage, or objectives | Often days to weeks, but can be a major training stage |
| Post-training | Adds instruction following, preferences, reasoning, tool use, and safety behavior | Iterative; individual runs may be short while the overall program continues |
| Evaluation and red-teaming | Measures quality, safety, robustness, and contamination | Runs throughout development and can send the recipe back for another iteration |

There is no reliable universal “generation takes X months” rule. Calendar time depends on the available cluster, utilization, failures, checkpointing, queueing, data readiness, and how many post-training and evaluation loops are required.

## 4. The compute math

For a dense decoder-only Transformer, a useful first estimate is:

```text
C ≈ 6 × N × D
N = trainable parameters
D = training tokens

wall-clock time ≈ C / (G × P_peak × MFU)
G = accelerator count
P_peak = peak floating-point throughput per accelerator
MFU = model FLOPs utilization
```

The 6ND rule is an approximation. Attention, embeddings, vocabulary projection, sequence length, activation checkpointing, evaluation, data movement, and other system work can move the actual cost materially; sparse MoE models also need a different interpretation of N.

For Llama 3.1 405B, 6 × 405B × 15.6T ≈ 3.8 × 10²⁵ FLOPs. Meta reports 38–43% BF16 MFU for its 405B pre-training configurations, up to 16,384 H100 GPUs. The model card reports 30.84 million cumulative H100 GPU-hours for the 405B model and 39.3 million for the 8B, 70B, and 405B family combined.

| Model | Reported training metric | Scope and caveat |
| --- | --- | --- |
| Llama 3.1 8B | 1.46M H100 GPU-hours | Model-card figure |
| Llama 3.1 70B | 7.0M H100 GPU-hours | Model-card figure |
| Llama 3.1 405B | 30.84M H100 GPU-hours | Model-card figure; 405B model |
| DeepSeek-V3 | 2.788M H800 GPU-hours | Full training report; 671B total parameters, 37B active per token, 14.8T tokens |

The reported DeepSeek-V3 number is about 11 times lower in GPU-hours than the reported Llama 3.1 405B number, but that is not evidence of 11 times less compute. The hardware, model architecture, utilization, training scope, and accounting conventions differ, so GPU-hours are not an apples-to-apples compute metric.

MFU below 100% is expected. The gap includes communication and synchronization, pipeline bubbles, memory-bound operations, kernel and framework overhead, checkpointing, recomputation, and failures. It is not valid to assign every missing percentage to one cause. At fixed work and with all other factors held constant, increasing MFU from 40% to 55% would imply about 27% less accelerator time, not a 35% cost reduction.

Large synchronous jobs also fail. In a 54-day Llama 3 405B snapshot, Meta reports 466 interruptions: 47 planned and 419 unexpected. About 78% of the unexpected interruptions were attributed to confirmed or suspected hardware-related causes, yet effective training time remained above 90% and only three incidents required significant manual intervention. Checkpoints and automated recovery turn failures into lost work and operational overhead rather than necessarily lost runs.

## 5. Why training takes so long

- **The optimizer is sequential across updates.** Data, tensor, pipeline, and context parallelism can spread work within a step, but the next update depends on the previous update. More accelerators can shorten a step while also increasing communication and synchronization costs.
- **A token budget is not a unique-data budget.** Mixtures can upsample or repeat selected sources, and the best repetition policy depends on data quality, model size, and objective. There is no universal single-epoch rule.
- **Many learning-rate schedules assume a horizon.** A cosine schedule is usually designed around a planned number of steps and a final decay. Warmup-stable-decay schedules are one alternative that keeps a stable phase so training can be continued before a final cooldown.
- **Scaling returns are sublinear.** More parameters, data, and FLOPs usually improve validation loss, but each additional unit buys less than the previous one. Downstream capability gains can be nonlinear and benchmark-dependent, so loss changes should not be translated directly into a percentage of “intelligence.”
- **Operations are part of the training algorithm.** Numerical stability, monitoring, checkpoint frequency, storage throughput, network behavior, recovery time, and data quality checks determine how much of the nominal cluster capacity becomes useful training.

## 6. Why the step count is often around one million

The basic relationship is:

```text
steps ≈ total training tokens (D) / tokens per global batch (B)
```

Llama 3.1 405B did not use one fixed batch size. Its published recipe started at 4M tokens, increased to 8M after 252M tokens, and increased to 16M after 2.87T tokens; the initial pre-training schedule decayed over 1.2M steps. Dividing 15.6T by the final 16M batch gives about 975,000 steps, but that is only a rough intuition because the batch changed and the recipe also included long-context training and annealing.

The numerator is a design choice. Chinchilla’s experiments found that, under their compute-optimal assumptions, model size and training tokens should grow at roughly the same rate. Deployment can justify a different choice: Llama 3 explicitly trained smaller models for much longer than compute-optimal because smaller models are cheaper to serve.

The denominator is constrained from both sides. It must be large enough to keep the parallel system busy, but beyond the critical batch size, larger batches reduce the number of updates with diminishing token and compute efficiency. Critical batch size is empirical and changes during training; it should not be reduced to a universal 1/√B rule.

More steps are usually easy to obtain by shrinking the batch, although that may hurt throughput. Fewer steps are harder because they require a larger useful batch, a stable optimization path, and enough independent gradient signal per update.

### Three different token quantities

| Quantity | Llama 3.1 405B example | What limits it |
| --- | --- | --- |
| Total training tokens | 15.6T text tokens | Data, compute, objective, and quality |
| Tokens per global batch | 4M → 8M → 16M | Hardware, memory, communication, and critical batch size |
| Context length | 8K initial pre-training → 128K continued pre-training | Attention cost, memory, architecture, and long-context data |

At a 16M-token batch and an 8K context, the batch contains roughly 2,000 full-length sequences. Batch size and context length are independent quantities; confusing them produces incorrect step and memory estimates.

## 7. Is data the moat?

Data is one moat, but not the moat. The most defensible generalization is that advantage comes from the interaction of data, compute, optimization, infrastructure, evaluation, and product feedback.

1. **Pre-training data is partly reproducible.** Public corpora and open curation tools have narrowed the gap in access to basic web text, but quality, freshness, multilingual coverage, filtering, rights, and mixture design remain differentiated.
1. **Post-training signals can be higher leverage per token.** Human preferences, expert demonstrations, synthetic data, verifiable environments, and tool traces can shape behavior that raw web text does not provide. Their value depends on task quality and evaluator reliability, not merely on count.
1. **Infrastructure execution compounds.** Utilization, reliability, parallelism, numerical stability, storage, and recovery determine how much of a nominal compute budget reaches the model. A small efficiency difference can become a large absolute difference on a multi-million-GPU-hour run.
1. **Legal and commercial capacity affects the feasible data mixture.** Direct licenses, rights management, privacy processes, and the ability to absorb contractual or litigation risk can matter even when the underlying research is public.

The sharpest conclusion is not that data stopped mattering. It is that the bottleneck moves: broad pre-training data can be increasingly commoditized while high-quality post-training signals, rights-cleared data, reliable infrastructure, and evaluation become more important differentiators.

## Sources

The quantitative claims were checked against the following primary or first-party sources on 2026-08-22; reported GPU-hours are retained as source-specific figures rather than normalized compute.

- [Common Crawl homepage](https://commoncrawl.org/), [overview](https://commoncrawl.org/overview), [FAQ](https://commoncrawl.org/faq), and [June 2026 crawl archive](https://commoncrawl.org/blog/june-2026-crawl-archive-now-available)
- [The Llama 3 Herd of Models](https://arxiv.org/html/2407.21783v3) and the [Llama 3.1 405B model card](https://huggingface.co/meta-llama/Llama-3.1-405B-Instruct)
- [DeepSeek-V3 Technical Report](https://arxiv.org/html/2412.19437)
- [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556) and [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)
- [Understanding Warmup-Stable-Decay Learning Rates](https://proceedings.iclr.cc/paper_files/paper/2025/hash/6a1fe80a9e2dcda0b3e5fd0fd87eb097-Abstract-Conference.html)
- [Critical Batch Size Revisited](https://arxiv.org/abs/2505.23971)
- [C4](https://jmlr.org/papers/v21/20-074.html), [RefinedWeb](https://arxiv.org/abs/2306.01116), [Dolma](https://arxiv.org/abs/2402.00159), and [FineWeb](https://arxiv.org/abs/2406.17557)
