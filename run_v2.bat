@echo off
echo 🚀 Starting Ultra AI DJ (Port 8001)...
start "AI Backend v2" cmd /k "python server/api.py"
cd client
start "Ultra UI" cmd /k "npm run dev"
echo Done! Please close old windows and check the new browser tab.
