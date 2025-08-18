# Setup

## Setup database

```bash
docker network create mcp-network
docker run -d \
  --name mcp_test_db \
  --network mcp-network \
  -e POSTGRES_USER=user@email.com \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=mcp_test \
  -p 5432:5432 \
  -v /Users/xxx/data/postgres/mcp_test:/var/lib/postgresql/data \
  postgres

```

## Tool calling with local llama.cpp LLM

### Install llama.cpp

```bash
brew update
brew upgrade llama.cpp
brew list --versions llama.cpp

brew upgrade llama.cpp # if need to update.

llama-server --jinja -hf ggml-org/gemma-3-1b-it-GGUF # --jinja flag needed for tool calling

```
