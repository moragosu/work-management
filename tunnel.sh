#!/bin/bash
# Cloudflare Quick Tunnel — 개발 서버를 외부에서 접근 가능하게 만들기
# 사전 조건: dev.sh가 실행 중이어야 함 (프론트 포트 5174)

CLOUDFLARED="$HOME/.local/bin/cloudflared"

if [ ! -f "$CLOUDFLARED" ]; then
  echo "cloudflared 설치 중..."
  curl -L "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64" -o "$CLOUDFLARED"
  chmod +x "$CLOUDFLARED"
fi

echo "Cloudflare 터널 시작 중 (http://localhost:5174)..."
echo "URL이 나타나면 해당 주소로 접속하세요."
echo "종료: Ctrl+C"
echo ""

"$CLOUDFLARED" tunnel --url http://localhost:5174
