#!/bin/bash
# Rovothome IR Manager — 시작 스크립트
# 사용법: ./start.sh

echo "🚀 Rovothome IR Manager 시작..."
echo ""

# Start Python backend
echo "  [1/2] 백엔드 서버 시작 (port 8000)..."
cd "$(dirname "$0")/backend"
python3 server.py &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
sleep 2

# Start React frontend
echo "  [2/2] 프론트엔드 시작 (port 3000)..."
cd "$(dirname "$0")/frontend"
npx vite --port 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ 실행 완료!"
echo "   브라우저에서 http://localhost:3000 열어주세요"
echo ""
echo "   종료: Ctrl+C"

# Handle cleanup
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
