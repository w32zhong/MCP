source .env

# Official docs: https://docs.anthropic.com/en/api/messages
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     -d @test.json --no-buffer
