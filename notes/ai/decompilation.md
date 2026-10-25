# Reverse Engineering and Decompilation

## What it is

Reverse engineering works backward from an existing program to understand its implementation and behavior, often without its source code.

Decompilation is one technique within that process: translating compiled code into an approximation of higher-level source. Disassembly stops at assembly instructions; decompilation reconstructs loops, conditions, and function calls.

Compilation loses comments and often names and types. Optimizations can rearrange or eliminate code. Multiple sources can produce identical instructions, so a binary cannot uniquely identify the author's original source.

## How it works

1. **Map the program.** Identify its architecture, entry points, library calls, strings, and any surviving symbols or debug information.
1. **Recover structure.** Disassemble instructions and use a decompiler such as [Ghidra](https://ghidra.re/ghidra_docs/GhidraClass/Beginner/Introduction_to_Ghidra_Student_Guide.html) to produce source-like pseudocode.
1. **Explain behavior.** Trace calls, inspect memory, and observe execution with a debugger. Infer what functions and data structures represent.
1. **Reconstruct what is needed.** Correct types and names. If rebuilding is the goal, turn pseudocode into compilable source with the right interfaces and dependencies.
1. **Verify and repeat.** Compare against the original, investigate differences, and revise. Evidence about one function often clarifies others.

## Why it is used

Reverse engineering supports security audits, malware analysis, interoperability, debugging, preservation, and software ports or modifications when source is unavailable.

The scope follows the goal. Understanding a file format or changing a movement mechanic may require only a few functions. Rebuilding an entire game requires far more work; a mod or mashup does not imply full decompilation.

## How correctness is checked

**Behavioral reconstruction** aims to reproduce what the program does. Run the original and reconstruction on the same inputs and compare outputs and side effects. Passing tests supports agreement on those cases; untested behavior can still differ. Compiling alone says little about correctness.

**Matching decompilation** targets identical machine code, typically by reproducing the original compiler, settings, and build layout. Projects such as [Super Mario 64](https://github.com/n64decomp/sm64/blob/master/README.md) verify rebuilt ROMs against reference hashes. Function-level instruction comparisons provide feedback before the full rebuild matches.

A complete binary match verifies reconstruction fidelity, including original bugs. A function match still depends on correct surrounding data and interfaces. Neither proves that inferred names or explanations are accurate.

## Why AI agents are effective

Models can recognize code patterns, propose names and types, and draft source from assembly or pseudocode. [LLM4Decompile](https://arxiv.org/abs/2403.05286) demonstrates improvements in decompiler output's readability and executability.

The practical advantage for agents is the feedback loop: **inspect → propose source → compile → compare → revise**. Tools provide concrete evidence for each attempt, letting an agent explore many candidates without a person reviewing every edit.

Matching provides especially strong feedback because the target instructions are available for comparison. Behavioral reconstruction depends on test coverage. The reference binary and verifier must remain independent of the agent's edits.

## Why it parallelizes

Once function boundaries, shared types, and calling conventions are understood, many functions become bounded tasks. Agents can reconstruct separate functions simultaneously, each with relevant assembly, dependencies, and its own check. Smaller tasks also require less context.

Shared structures, global state, and cross-function assumptions still create dependencies. Establish common interfaces, isolate edits, share verified findings, and validate the integrated build. Speedup depends on how much work is independent; compiler quirks and integration still need expert judgment.
