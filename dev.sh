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

# node/npm 설치 확인
if ! command -v node &>/dev/null || ! command -v npm &>/dev/null; then
  echo "Node.js가 없습니다. nvm으로 설치 중..."
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  nvm install 20
  nvm use 20
else
  # nvm이 있는 환경이면 로드
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
fi

# Backend
echo "백엔드 시작 (포트 8001)..."
cd "$REPO_DIR/backend"
export DATA_DIR="$REPO_DIR/data"
uv sync --quiet --python 3.12 --native-tls
uv run --python 3.12 uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
echo "  PID: $BACKEND_PID"

# Frontend
echo "프론트엔드 시작 (포트 5174)..."
cd "$REPO_DIR/frontend"
if [ ! -f "node_modules/.bin/vite" ]; then
  npm install
fi
npm run dev &
FRONTEND_PID=$!
echo "  PID: $FRONTEND_PID"

echo ""
echo "✅ 개발 서버 실행 중"
echo "   프론트엔드: http://localhost:5174"
echo "   API:        http://localhost:8001/docs"
echo ""
echo "종료: Ctrl+C"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
