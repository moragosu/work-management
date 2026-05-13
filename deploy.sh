#!/bin/bash
# OKR Management System - Deployment Script
# Usage: sudo bash deploy.sh
set -e

APP_DIR="/var/www/okr-app"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== OKR 관리 시스템 배포 시작 ==="

# 1. System packages
echo "[1/7] 시스템 패키지 설치..."
apt-get update -q
apt-get install -y -q python3 nodejs npm nginx curl

# uv 설치 (시스템 전역)
if ! command -v uv &>/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="/root/.local/bin:$PATH"
fi

# 2. App directory
echo "[2/7] 앱 디렉토리 구성..."
mkdir -p "$APP_DIR/data" "$APP_DIR/backend"
mkdir -p /var/log/okr-app

# 3. Python 환경 (uv)
echo "[3/7] Python 환경 설정 (uv)..."
cp -r "$REPO_DIR/backend/"* "$APP_DIR/backend/"
cp -r "$REPO_DIR/data/"*.json "$APP_DIR/data/" 2>/dev/null || true
cd "$APP_DIR/backend"
uv sync --no-dev

# 4. Frontend build
echo "[4/7] 프론트엔드 빌드..."
cd "$REPO_DIR/frontend"
npm install --silent
npm run build
cp -r "$REPO_DIR/dist/"* "$APP_DIR/dist/" 2>/dev/null || \
  (mkdir -p "$APP_DIR/dist" && cp -r "$REPO_DIR/dist/"* "$APP_DIR/dist/")

# 5. Systemd service
echo "[5/7] Systemd 서비스 등록..."
cat > /etc/systemd/system/okr-app.service <<EOF
[Unit]
Description=OKR Management FastAPI App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR/backend
Environment="DATA_DIR=$APP_DIR/data"
Environment="PATH=/root/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=uv run gunicorn -c $APP_DIR/backend/gunicorn.conf.py main:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 6. Nginx config
echo "[6/7] Nginx 설정..."
cp "$REPO_DIR/nginx/okr-app.conf" /etc/nginx/sites-available/okr-app
ln -sf /etc/nginx/sites-available/okr-app /etc/nginx/sites-enabled/okr-app
rm -f /etc/nginx/sites-enabled/default
nginx -t

# 7. Start services
echo "[7/7] 서비스 시작..."
chown -R www-data:www-data "$APP_DIR"
chown -R www-data:www-data /var/log/okr-app
systemctl daemon-reload
systemctl enable okr-app
systemctl restart okr-app
systemctl reload nginx

echo ""
echo "✅ 배포 완료!"
echo "   접속 주소: http://$(hostname -I | awk '{print $1}')/"
echo "   서비스 상태: systemctl status okr-app"
echo "   로그 확인: journalctl -u okr-app -f"
