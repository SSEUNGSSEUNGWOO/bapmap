#!/bin/bash
pkill -f "Google Chrome" 2>/dev/null
sleep 3
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222 --no-first-run
