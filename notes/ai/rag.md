# Retrieval-Augmented Generation (RAG)

RAG is a design pattern that optimizes LLM output by referencing an authoritative knowledge base outside of its training data _before_ generating a response.

The Problem:

- Knowledge Cutoff: LLMs don't know about events that happened after they were trained.
- Private Data: LLMs don't know your internal company documents.
- Hallucinations: LLMs might make up facts if they don't have a source.

The Solution (The RAG Workflow):

1. Retrieve: The user asks a question. The system searches a vector database (or API) for relevant text chunks.
1. Augment: The system takes those text chunks and pastes them into the prompt (usually as "System Context").
1. Generate: The LLM answers the question using _only_ the provided context.

#### RAG Implementation Strategies

You can implement RAG in two ways:

1. The "Hard-Coded" Way: A Python script that queries a Vector DB (Pinecone/Milvus), gets text, concatenates strings, and calls the OpenAI API.
1. The MCP Way (Modern): You expose a Resource or Tool (e.g., `search_internal_docs`) via an MCP Server. The LLM decides _when_ it needs to perform RAG.

#### The "Contract" Advantage (RAG + MCP)

When you wrap your RAG pipeline in an MCP Server, you decouple the data source from how the LLM accesses it.

- The Interface: You promise the LLM a tool called `query_policy_docs(query: str)`.
- The Backend Swap:
  - _Day 1:_ The tool searches a Pinecone Vector DB.
  - _Day 30:_ You migrate to Notion. You rewrite the Python tool to search Notion instead.
  - _Result:_ The LLM doesn't know the difference. You improved the backend without breaking the agent or changing the prompt.

______________________________________________________________________

### The Bridge: Discovery & Decision

How does the LLM actually know that `query_policy_docs` exists for RAG? And what makes it leverage the RAG option instead of just saying "I can't do that" to the client?

#### A. Discovery (The "Hidden" Context)

When you connect an MCP server, the Host App (e.g., Claude Desktop) performs a handshake behind the scenes.

1. The Handshake: The Host asks the MCP server, "List your tools."
1. The Injection: The Host takes those tool definitions (name, description, and arguments) and silently injects them into the System Prompt of the LLM.

To the LLM, your conversation actually looks like this (simplified):

> System: You are a helpful assistant. You have access to these tools:
>
> - `get_ticket(id)`: Fetches ticket details.
> - `delete_ticket(id)`: Permanently removes a ticket.
>
> User: Please delete ticket 123.

#### B. The Decision (Semantic Matching)

The LLM does not "think" like a human; it matches patterns.

1. Intent Analysis: The LLM analyzes the user's text ("delete ticket") and compares it against the descriptions provided in the System Prompt.
1. The Trigger: When the statistical probability of a tool matching the request is high enough, the LLM stops generating normal text.
1. The Structured Output: Instead of writing English, it outputs a specific Stop Sequence or JSON blob (e.g., `<tool_use name="delete_ticket">`) that the Host App is programmed to catch.

Key Takeaway: The "Description" field in your MCP tool definition is actually a prompt. If you write a bad description, the LLM won't know when to use your tool.

### Comparison Summary

| Feature | RAG (Pattern) | MCP (Protocol) |
| :------------- | :-------------------------------- | :-------------------------------------------------- |
| Primary Goal | Give the AI Knowledge. | Give the AI Capabilities (Tools & Data). |
| Primary Action | Reading/Retrieving. | connecting & Executing. |
| Relation | You use RAG to _find_ the answer. | You use MCP to _connect_ the RAG system to the LLM. |
