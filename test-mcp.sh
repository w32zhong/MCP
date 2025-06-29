# See https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle

curl -L http://localhost:8989/mcp \
     --header "Accept: application/json, text/event-stream" \
     --header "Content-Type: application/json" \
     -D dump-response-header.txt \
     -d @test-mcp-init.json --no-buffer

session_id=$(cat dump-response-header.txt | grep -i "mcp-session-id" | awk '{print $2}' | tr -d '\r')
echo "Session ID = $session_id"

curl -L http://localhost:8989/mcp \
     --header "Accept: application/json, text/event-stream" \
     --header "Content-Type: application/json" \
     --header "mcp-session-id: $session_id" \
     -d @test-mcp-init-done.json --no-buffer
echo "Initialized."

curl -L http://localhost:8989/mcp \
     --header "Accept: application/json, text/event-stream" \
     --header "Content-Type: application/json" \
     --header "mcp-session-id: $session_id" \
     -d @test-mcp-list.json --no-buffer

curl -L http://localhost:8989/mcp \
     --header "Accept: application/json, text/event-stream" \
     --header "Content-Type: application/json" \
     --header "mcp-session-id: $session_id" \
     -d @test-mcp-list2.json --no-buffer

curl -L http://localhost:8989/mcp \
     --header "Accept: application/json, text/event-stream" \
     --header "Content-Type: application/json" \
     --header "mcp-session-id: $session_id" \
     -d @test-mcp-call.json --no-buffer

curl -L http://localhost:8989/mcp \
     --header "Accept: application/json, text/event-stream" \
     --header "Content-Type: application/json" \
     --header "mcp-session-id: $session_id" \
     -d @test-mcp-read.json --no-buffer

curl -L http://localhost:8989/mcp \
     --header "Accept: application/json, text/event-stream" \
     --header "Content-Type: application/json" \
     --header "mcp-session-id: $session_id" \
     -d @test-mcp-call-img.json --no-buffer
