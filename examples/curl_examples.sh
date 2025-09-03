#!/bin/bash

# openmcp API Examples using curl
# Make sure to replace YOUR_API_KEY with your actual API key

API_KEY="bmcp_your-api-key-here"
BASE_URL="http://localhost:8000"

echo "openmcp API Examples"
echo "===================="

# Health check (no auth required)
echo -e "\n1. Health Check:"
curl -s "$BASE_URL/health" | jq .

# List services
echo -e "\n2. List Services:"
curl -s -H "Authorization: Bearer $API_KEY" \
     "$BASE_URL/api/v1/services" | jq .

# List browseruse tools
echo -e "\n3. List Browseruse Tools:"
curl -s -H "Authorization: Bearer $API_KEY" \
     "$BASE_URL/api/v1/services/browseruse/tools" | jq .

# Create browser session
echo -e "\n4. Create Browser Session:"
SESSION_RESPONSE=$(curl -s -X POST \
     -H "Authorization: Bearer $API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"tool_name": "create_session", "arguments": {"headless": true, "timeout": 30}}' \
     "$BASE_URL/api/v1/services/browseruse/call")

echo "$SESSION_RESPONSE" | jq .

# Extract session ID
SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r '.result.session_id')

if [ "$SESSION_ID" != "null" ] && [ "$SESSION_ID" != "" ]; then
    echo "Session ID: $SESSION_ID"
    
    # Navigate to a website
    echo -e "\n5. Navigate to Website:"
    curl -s -X POST \
         -H "Authorization: Bearer $API_KEY" \
         -H "Content-Type: application/json" \
         -d "{\"tool_name\": \"navigate\", \"arguments\": {\"url\": \"https://httpbin.org\"}, \"session_id\": \"$SESSION_ID\"}" \
         "$BASE_URL/api/v1/services/browseruse/call" | jq .
    
    # Get page info
    echo -e "\n6. Get Page Info:"
    curl -s -X POST \
         -H "Authorization: Bearer $API_KEY" \
         -H "Content-Type: application/json" \
         -d "{\"tool_name\": \"get_page_info\", \"arguments\": {}, \"session_id\": \"$SESSION_ID\"}" \
         "$BASE_URL/api/v1/services/browseruse/call" | jq .
    
    # Find elements
    echo -e "\n7. Find Elements:"
    curl -s -X POST \
         -H "Authorization: Bearer $API_KEY" \
         -H "Content-Type: application/json" \
         -d "{\"tool_name\": \"find_elements\", \"arguments\": {\"selector\": \"h1\", \"by\": \"css\"}, \"session_id\": \"$SESSION_ID\"}" \
         "$BASE_URL/api/v1/services/browseruse/call" | jq .
    
    # Take screenshot
    echo -e "\n8. Take Screenshot:"
    SCREENSHOT_RESPONSE=$(curl -s -X POST \
         -H "Authorization: Bearer $API_KEY" \
         -H "Content-Type: application/json" \
         -d "{\"tool_name\": \"take_screenshot\", \"arguments\": {}, \"session_id\": \"$SESSION_ID\"}" \
         "$BASE_URL/api/v1/services/browseruse/call")
    
    # Save screenshot to file
    echo "$SCREENSHOT_RESPONSE" | jq -r '.result.screenshot' | base64 -d > screenshot.png
    echo "Screenshot saved to screenshot.png"
    
    # Close session
    echo -e "\n9. Close Session:"
    curl -s -X POST \
         -H "Authorization: Bearer $API_KEY" \
         -H "Content-Type: application/json" \
         -d "{\"tool_name\": \"close_session\", \"arguments\": {}, \"session_id\": \"$SESSION_ID\"}" \
         "$BASE_URL/api/v1/services/browseruse/call" | jq .
else
    echo "Failed to create session"
fi

echo -e "\n10. Service Status:"
curl -s -H "Authorization: Bearer $API_KEY" \
     "$BASE_URL/api/v1/services/browseruse/status" | jq .

echo -e "\nDone!"
