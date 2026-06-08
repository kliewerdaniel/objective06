# Local Models Interface

This interface defines how SELF interacts with local language and embedding models (e.g., via Ollama, vLLM, or llama.cpp).

## Purpose
The Local Models interface abstracts the specific model implementation from the rest of the system (Extractor, Synthesis, etc.). It handles model selection, request batching, retries, and observability.

## Capabilities
- **Inference**: Text generation (for extraction, synthesis, and conversational responses).
- **Embeddings**: Generating dense vectors for semantic search and persona updates.
- **Multi-Model Support**: Ability to route different tasks to different models (e.g., a small model for extraction, a large one for synthesis).
- **Streaming**: (Optional) Support for streaming text generation for the Digital Twin.

## Inputs
- **Prompt Template**: The ID of the template to use.
- **Context**: Any relevant context (e.g., previous conversation turns, knowledge objects).
- **Parameters**: Temperature, top_p, max_tokens, etc.

## Outputs
- **Completion**: The generated text.
- **Logprobs**: Probability scores for tokens (where available).
- **Embeddings**: A vector representation of the input text.
- **Metadata**: Model name, version, and usage statistics.

## Governance
- **Privacy**: All data sent to local models remains on the local machine.
- **Auditability**: Every request is logged with the prompt, output, model ID, and timestamp.
- **Failure Mode**: If the local model service is down, the system should fail gracefully or switch to a secondary model if configured.

## Recommended Embedding Models
The following models are recommended for local operation via Ollama:
- **nomic-embed-text** (Ollama, 768 dims, default for memory-constrained systems)
- **mxbai-embed-large** (Ollama, 1024 dims, balanced)
- **llama-embed-nemotron-8b** (Ollama, 4096 dims, high-fidelity but slow on CPU)
All three are available via `ollama pull`.

## Implementations
- **Ollama**: Integration with the Ollama API.
- **vLLM**: Integration with the vLLM inference server.
- **llama.cpp**: Direct integration with llama.cpp via a local wrapper.
