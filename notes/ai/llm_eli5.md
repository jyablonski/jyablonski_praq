## LLM ELI5

Imagine you send in a prompt to an LLM like `What color is the sky?`. Here's how it processes that prompt and generates a response:

______________________________________________________________________

**Step 1: Chop it into tokens**

The text gets split into little chunks called tokens. Words, parts of words, punctuation. So maybe: `["What", " color", " is", " the", " sky", "?"]`. This is just a lookup table, totally trivial.

______________________________________________________________________

**Step 2: Turn each token into a list of numbers**

Each token gets swapped out for a long list of numbers (a vector) based on a big lookup table the model learned during training. "sky" becomes something like `[0.2, -0.8, 1.3, 0.4 ...]` — hundreds or thousands of numbers. This is its starting "meaning."

______________________________________________________________________

**Step 3: Pass every token through many layers**

This is the bulk of the work. The model has dozens of layers stacked on top of each other. At each layer, every token looks at every other token and asks *"should I update my meaning based on yours?"* — that's the attention mechanism. "color" might lean heavily on "sky" and "What" to understand its role in the sentence. After each layer, every token's vector gets updated to carry more context.

This happens for all tokens in parallel during prefill — the GPU does it all at once as giant matrix multiplies.

______________________________________________________________________

**Step 4: After the last layer, look at the final token**

The model only needs to predict *what comes next*, so it looks at the last token's final vector (which by now is soaked in context from the whole prompt) and asks: *given everything, what token is most likely next?*

______________________________________________________________________

**Step 5: Pick the next token**

It runs that vector through one more lookup that scores every possible token in its vocabulary (~50k+ words/chunks). The highest scoring ones are candidates. It samples from them and picks one — say, `"The"`.

______________________________________________________________________

**Step 6: Repeat**

`"The"` gets appended. Now it predicts the next token given `"What color is the sky? The"`. Then `" sky"`, then `" is"`, then `" blue"`, then a stop token. Each step is one forward pass through all those layers, but now for just one new token at a time — which is why generation feels slower than the initial prompt processing.
