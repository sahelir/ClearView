#!/usr/bin/env bash
# Test script for Workspace and Source API endpoints.
# Run with: ./scripts/test_workspaces_and_sources.sh
# Requires: API running at http://localhost:8000, PostgreSQL with tables created

set -e
BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "=== 1. Health check ==="
curl -s "${BASE_URL}/health" | jq .

echo -e "\n=== 2. Create a workspace ==="
WORKSPACE_RESPONSE=$(curl -s -X POST "${BASE_URL}/workspaces" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "description": "A test workspace"}')
echo "$WORKSPACE_RESPONSE" | jq .
WORKSPACE_ID=$(echo "$WORKSPACE_RESPONSE" | jq -r '.id')
echo "Created workspace ID: $WORKSPACE_ID"

echo -e "\n=== 3. List workspaces ==="
curl -s "${BASE_URL}/workspaces" | jq .

echo -e "\n=== 4. Create a text source ==="
TEXT_BODY=$(printf 'Sample document text. %.0s' {1..120})
TEXT_SOURCE_RESPONSE=$(curl -s -X POST "${BASE_URL}/sources/text" \
  -H "Content-Type: application/json" \
  -d "{\"workspace_id\": \"${WORKSPACE_ID}\", \"title\": \"Sample notes\", \"raw_text\": \"${TEXT_BODY}\"}")
echo "$TEXT_SOURCE_RESPONSE" | jq .
TEXT_SOURCE_ID=$(echo "$TEXT_SOURCE_RESPONSE" | jq -r '.id')

echo -e "\n=== 5. Create a URL source ==="
URL_SOURCE_RESPONSE=$(curl -s -X POST "${BASE_URL}/sources/url" \
  -H "Content-Type: application/json" \
  -d "{\"workspace_id\": \"${WORKSPACE_ID}\", \"title\": \"Example\", \"url\": \"https://example.com\"}")
echo "$URL_SOURCE_RESPONSE" | jq .
URL_SOURCE_ID=$(echo "$URL_SOURCE_RESPONSE" | jq -r '.id')

echo -e "\n=== 6. List sources in the workspace ==="
curl -s "${BASE_URL}/workspaces/${WORKSPACE_ID}/sources" | jq .

echo -e "\n=== 7. Get text source details ==="
curl -s "${BASE_URL}/sources/${TEXT_SOURCE_ID}" | jq .

echo -e "\n=== 8. List text source chunks ==="
curl -s "${BASE_URL}/chunks/${TEXT_SOURCE_ID}" | jq .

echo -e "\n=== 9. Delete URL source ==="
curl -s -X DELETE "${BASE_URL}/sources/${URL_SOURCE_ID}"
echo "Deleted URL source"

echo -e "\n=== All tests completed successfully ==="
