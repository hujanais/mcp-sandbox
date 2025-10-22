### Tool calling with local llama.cpp LLM

## Install llama.cpp
```
brew update
brew upgrade llama.cpp
brew list --versions llama.cpp

brew upgrade llama.cpp # if need to update.

llama-server --jinja -hf ggml-org/gemma-3-1b-it-GGUF # --jinja flag needed for tool calling

```

### Graphing MCP
https://github.com/antvis/mcp-server-chart