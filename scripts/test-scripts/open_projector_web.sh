#!/bin/bash
# Open projector web interface in Chrome with authentication
# This script opens Chrome with the authenticated session
#
# Usage:
#   open_projector_web.sh [IP] [USERNAME] [PASSWORD]
#   Or set environment variables: PROJECTOR_IP, PROJECTOR_USERNAME, PROJECTOR_PASSWORD
#   Or create .env file with PROJECTOR_PASSWORD (and optionally other variables)

# Load .env file if it exists (from project root or current directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
for env_file in "$PROJECT_ROOT/.env" "$(pwd)/.env" "$HOME/.config/projector-trigger/.env"; do
    if [ -f "$env_file" ]; then
        # Source .env file, ignoring comments and empty lines
        set -a
        source <(grep -v '^#' "$env_file" | grep -v '^$')
        set +a
        break
    fi
done

PROJECTOR_IP="${1:-${PROJECTOR_IP:-192.168.1.100}}"
USERNAME="${2:-${PROJECTOR_USERNAME:-root}}"
PASSWORD="${3:-${PROJECTOR_PASSWORD:-Projector}}"

echo "Opening projector web interface..."
echo "IP: $PROJECTOR_IP"
echo "Username: $USERNAME"
echo ""

# Method 1: Use Python to fetch the page and save it, then open in browser
# This won't work for interactive pages, but shows the content

# Method 2: Use curl to get cookies and then open browser
# Unfortunately, Digest auth doesn't work well with this approach

# Method 3: Open browser and let user enter credentials manually
# Chrome will prompt for credentials when accessing a Digest-protected site

echo "Opening Chrome..."
echo "When prompted, enter:"
echo "  Username: $USERNAME"
echo "  Password: $PASSWORD"
echo ""

# Open Chrome with the URL
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open -a "Google Chrome" "http://$PROJECTOR_IP/"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    google-chrome "http://$PROJECTOR_IP/" 2>/dev/null || chromium "http://$PROJECTOR_IP/" 2>/dev/null || xdg-open "http://$PROJECTOR_IP/"
else
    echo "Please open http://$PROJECTOR_IP/ in your browser manually"
fi

