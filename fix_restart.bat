@echo off
echo 🧹 Cleaning up old processes...
taskkill /F /IM python.exe
taskkill /F /IM node.exe
echo ✅ Cleanup complete.

echo 🚀 Starting Ultra AI DJ Fresh...
start "AI Backend" cmd /k "python server/api.py"
cd client
call npm install
start "Ultra UI" cmd /k "npm run dev"
echo Done! Check your browser.
