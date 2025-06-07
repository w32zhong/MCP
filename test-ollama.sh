source .env

# Official docs: https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-chat-completion
curl http://yetiarch:11434/api/chat \
     --header "content-type: application/json" \
     -d @test-ollama.json --no-buffer
