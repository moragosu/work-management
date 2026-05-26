#!/bin/bash
# OKR Management System - Deployment Script
# Usage: sudo bash deploy.sh [PORT]
# Example: sudo bash deploy.sh 8080
set -e

APP_DIR="/var/www/okr-app"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${1:-8080}"

echo "=== OKR 관리 시스템 배포 시작 ==="

# 1. System packages
echo "[1/7] 시스템 패키지 설치..."

install_nodejs() {
  local version=20
  if command -v apt-get &>/dev/null; then
    apt-get update -q
    apt-get install -y -q curl nginx
    curl -fsSL https://deb.nodesource.com/setup_${version}.x | bash -
    apt-get install -y -q nodejs
  elif command -v dnf &>/dev/null; then
    dnf install -y curl nginx
    curl -fsSL https://rpm.nodesource.com/setup_${version}.x | bash -
    dnf install -y nodejs
  elif command -v yum &>/dev/null; then
    yum install -y curl nginx
    curl -fsSL https://rpm.nodesource.com/setup_${version}.x | bash -
    yum install -y nodejs
  else
    echo "지원하지 않는 패키지 매니저입니다. node, npm, nginx를 수동으로 설치해주세요."
    exit 1
  fi
}

if ! command -v node &>/dev/null || ! command -v nginx &>/dev/null; then
  install_nodejs
fi

# uv 설치 (시스템 전역)
if ! command -v uv &>/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="/root/.local/bin:$PATH"
fi
# uv를 시스템 PATH에 복사 (systemd 서비스에서 접근 가능하도록)
if [ ! -f /usr/local/bin/uv ]; then
  cp "$(command -v uv)" /usr/local/bin/uv
fi

# 2. App directory
echo "[2/7] 앱 디렉토리 구성..."
mkdir -p "$APP_DIR/data/uploads" "$APP_DIR/backend" "$APP_DIR/dist"

# 기존 backend/uploads 파일 마이그레이션 (있을 경우)
if [ -d "$APP_DIR/backend/uploads" ] && [ "$(ls -A "$APP_DIR/backend/uploads" 2>/dev/null)" ]; then
  echo "[마이그레이션] 기존 업로드 파일 이동 중..."
  cp -n "$APP_DIR/backend/uploads/"* "$APP_DIR/data/uploads/" 2>/dev/null || true
fi
mkdir -p /var/log/okr-app

# 3. Python 환경 (uv)
echo "[3/7] Python 환경 설정 (uv)..."
cp -r "$REPO_DIR/backend/." "$APP_DIR/backend/"
cd "$APP_DIR/backend"
# sudo 실행 시 HOME이 호출자 홈으로 유지되는 문제 방지
export HOME=/root
export UV_PYTHON_INSTALL_DIR=/usr/local/share/uv-python
mkdir -p /usr/local/share/uv-python
rm -rf .venv  # 기존 venv 삭제 후 재생성
uv sync --no-dev --python 3.12 --native-tls
chmod -R a+rX /usr/local/share/uv-python

# 4. Frontend (pre-built dist 복사)
echo "[4/7] 프론트엔드 배포 (pre-built)..."
rm -rf "$APP_DIR/dist"
mkdir -p "$APP_DIR/dist"
cp -r "$REPO_DIR/dist/." "$APP_DIR/dist/"

# 5. Systemd service
echo "[5/7] Systemd 서비스 등록..."
mkdir -p /var/cache/okr-app/uv
chown -R www-data:www-data /var/cache/okr-app
cat > /etc/systemd/system/okr-app.service <<EOF
[Unit]
Description=OKR Management FastAPI App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR/backend
Environment="DATA_DIR=$APP_DIR/data"
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="UV_CACHE_DIR=/var/cache/okr-app/uv"
Environment="UV_PYTHON_INSTALL_DIR=/usr/local/share/uv-python"
ExecStart=$APP_DIR/backend/.venv/bin/gunicorn -c $APP_DIR/backend/gunicorn.conf.py main:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 6. Nginx config
echo "[6/7] Nginx 설정 (포트: $PORT)..."
cat > /etc/nginx/sites-available/okr-app <<NGINXEOF
server {
    listen $PORT;
    server_name _;

    root $APP_DIR/dist;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location ^~ /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 60s;
    }

    location ^~ /uploads/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location ^~ /go/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    gzip_min_length 1024;
}
NGINXEOF
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
echo "   접속 주소: http://$(hostname -I | awk '{print $1}'):$PORT"
echo "   서비스 상태: systemctl status okr-app"
echo "   로그 확인:   journalctl -u okr-app -f"
