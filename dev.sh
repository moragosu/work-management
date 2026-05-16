#!/bin/bash
# 개발 서버 실행 스크립트 (로컬 개발용)
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

# uv 설치 확인
if ! command -v uv &>/dev/null; then
  echo "uv가 없습니다. 설치 중..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

# Backend
echo "백엔드 시작 (포트 8000)..."
cd "$REPO_DIR/backend"
export DATA_DIR="$REPO_DIR/data"
uv sync --quiet --python 3.12
uv run --python 3.12 python main.py &
BACKEND_PID=$!
echo "  PID: $BACKEND_PID"

# Frontend
echo "프론트엔드 시작 (포트 5173)..."
cd "$REPO_DIR/frontend"
if [ ! -d "node_modules" ]; then
  npm install
fi
npm run dev &
FRONTEND_PID=$!
echo "  PID: $FRONTEND_PID"

echo ""
echo "✅ 개발 서버 실행 중"
echo "   프론트엔드: http://localhost:5173"
echo "   API:        http://localhost:8000/docs"
echo ""
echo "종료: Ctrl+C"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
