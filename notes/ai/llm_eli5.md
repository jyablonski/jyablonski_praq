# LLM ELI5

## How Requests get Processed

Imagine you send in a prompt to an LLM like `What color is the sky?`. Here's how it processes that prompt and generates a response:

______________________________________________________________________

Step 1: Chop it into tokens

The text gets split into little chunks called tokens. Words, parts of words, punctuation. So maybe: `["What", " color", " is", " the", " sky", "?"]`. This is just a lookup table, totally trivial.

______________________________________________________________________

Step 2: Turn each token into a list of numbers

Each token gets swapped out for a long list of numbers (a vector) based on a big lookup table called the embedding matrix that the model learned during training. "sky" becomes something like `[0.2, -0.8, 1.3, 0.4 ...]` — thousands of numbers. This is its starting "meaning."

This is somewhat similar to other usecases for vectors and embeddings like semantic search. In semantic search, you produce a single vector for an entire document or query, and then compare those vectors to find matches. Whereas in an LLM, you produce a vector for every token, and keep transforming those vectors through all of the layers, using the final one to predict the next token.

- It's essentially improving the meaning of each token by looking at the others, factoring in context. "sky" on its own has a certain meaning, but in the context of "What color is the sky?" it gets updated to reflect that we're probably talking about the blue sky we see outside, not some other meaning of "sky."

______________________________________________________________________

Step 3: Pass every token through many layers

This is the bulk of the work. The model has dozens of layers stacked on top of each other (often 80+ for frontier models). At each layer, every token computes three projections of itself:

- Q (Query): what it's looking for
- K (Key): what it advertises about itself
- V (Value): the actual information it contributes if attended to

Each token's Q gets compared against every other token's K (via dot product) to decide how much attention to pay to each. Those scores then mix the V vectors together. "color" might score high against "sky" and pull its V heavily, updating its own meaning to reflect that context.

After attention, the vector also passes through a feedforward network (more matrix multiplications against learned weights). Then on to the next layer, where it all happens again with different learned Q/K/V projections.

This happens for all tokens in parallel during prefill — the GPU does it all at once as giant matrix multiplies streaming weights from HBM.

______________________________________________________________________

Step 4: After the last layer, look at the final token

The model only needs to predict *what comes next*, so it looks at the last token's final vector (which by now is soaked in context from the whole prompt) and asks: *given everything, what token is most likely next?*

______________________________________________________________________

Step 5: Pick the next token

It multiplies that final vector by one last weight matrix called the unembedding (or LM head). This produces a raw score (logit) for every token in the vocabulary (~100k+ tokens) — essentially measuring how well the final vector aligns with each token's learned representation.

Softmax converts those scores into probabilities that sum to 1. Then it picks a token — usually the highest-probability one, though sampling strategies (temperature, top-k, top-p) often introduce some controlled randomness for variety. Say it picks `"The"`.

______________________________________________________________________

Step 6: Repeat (efficiently)

`"The"` gets appended. Now it predicts the next token given `"What color is the sky? The"`. But here's the trick: the K and V vectors for the original prompt tokens are saved in the KV cache so they don't get recomputed. Only the new token runs a fresh forward pass, attending against the cached KVs.

- K and V for past tokens are needed every future step (the new token's Q attends against them), so they're cached.
- Q for past tokens was used once at the step that token was generated, then never needed again. Causal attention means token 5's Q only ever looked at tokens 1-5; nothing later cares about it.

Then `" sky"`, then `" is"`, then `" blue"`, then a special EOS (end-of-sequence) token that tells the server to stop.

Each step is one full forward pass through all those layers — hundreds of billions of multiply-adds, all the model's weights streamed from HBM — which is why generation feels slower than the initial prompt processing and why HBM bandwidth is the main bottleneck.

## Harness

An LLM harness is the surrounding software layer that wraps a language model and turns it from a raw text-completion API into something useful for a specific task, especially agentic coding. The model itself is just a function that takes tokens in and produces tokens out. The harness is everything else: the system prompt, the tool definitions, the agent loop, context management, file editing strategies, permission systems, terminal integration, and so on.

You can think of it as the difference between an engine and a car. The model is the engine. Two cars with the same engine can feel completely different to drive depending on the transmission, suspension, dashboard, and controls. That is the harness.

The core responsibilities usually break down into a few areas. The agent loop decides when to call tools, when to stop, and how to handle errors or retries. Tool design determines what the model can actually do (read files, run shell commands, search the web, edit code with diffs vs full rewrites, etc.) and how those tools are described to the model.

Context management decides what goes into the context window: which files, how much git history, which past tool results to keep or summarize, and when to compact. The system prompt encodes the harness's opinions about how the model should behave. Permission and safety layers gate destructive actions. UI and integration determines whether you live in a terminal, an IDE, a web app, or somewhere else.

Two harnesses pointed at the same underlying model can produce dramatically different experiences because they make different choices at each of these layers.

## Terminology

Token: The atomic unit an LLM operates on. A subword chunk - could be a whole word, a word piece, punctuation, or whitespace. ~1 token =~ 0.75 English words.

Vocabulary: The full set of tokens the model knows (~100k+ for modern models). Every input/output token comes from this set.

Embedding: The lookup table that converts a token ID into a vector of numbers. The starting "meaning" of a token before any context is applied.

Vector: A list of numbers (often thousands long) representing a token's meaning at some point in the pipeline. Gets updated as it flows through layers.

Weights: The billions of numbers the model learned during training. Stored as matrices and used at every step of inference.

Layer: One repeating block of the model. Each layer has its own attention mechanism and feedforward network. Frontier models stack 80+ of these.

Attention: The mechanism that lets tokens "look at" each other and update their meaning based on context. Implemented via Q, K, V projections.

Q (Query): What the current token is looking for. "I need info about X."

K (Key): What each token advertises about itself. Like an index entry.

V (Value): The actual content a token contributes if attended to.

Feedforward network (FFN): The other major component of each layer. A few matrix multiplications applied to each token's vector after attention.

Logit: The raw score the model assigns to a token before converting to probability.

Softmax: The function that converts raw logits into probabilities that sum to 1.

Unembedding (LM head): The final weight matrix that scores every vocabulary token based on the last layer's output. Often tied to the embedding matrix.

Forward pass: One full trip through all the model's layers, producing one output token.

Prefill: The first phase of inference, where the entire input prompt is processed in parallel through the model. Compute-heavy.

Decode: The second phase, where output tokens are generated one at a time. Memory-bandwidth-heavy.

Autoregressive: Generating output one token at a time, where each new token depends on all previous ones.

KV cache: Stored K and V vectors for every prior token, at every layer. Lets decode skip recomputing past work. Lives in HBM.

EOS (end-of-sequence): A special token the model emits when it considers the response complete. Tells the server to stop generating.

HBM (high-bandwidth memory): The GPU's main memory pool where weights and KV cache live. Bandwidth here is the dominant bottleneck for decode.

Batching: Running many requests through the same forward pass to amortize the cost of loading weights from HBM.

Continuous batching: A scheduling strategy where requests join and leave the batch every decode step, rather than waiting for all to finish.

Quantization: Storing weights in lower precision (FP8, INT4, etc.) to shrink memory footprint and speed up inference.
