# reset_password.py

관리자가 특정 사용자의 비밀번호를 재설정하는 스크립트.

## 개발 환경

```bash
cd backend
uv run python reset_password.py
```

## 운영 환경 (prod 서버)

```bash
sudo DATA_DIR=/var/www/okr-app/data \
  /var/www/okr-app/backend/.venv/bin/python \
  /var/www/okr-app/backend/reset_password.py
```

## 워크플로우

1. 사용자가 비밀번호 분실 → 관리자에게 재설정 요청
2. 관리자가 스크립트 실행 → 임시 비밀번호 입력 (6자 이상)
3. 사용자 목록에서 재설정할 username 입력 (여러 명 연속 처리 가능)
4. 임시 비밀번호를 해당 사용자에게 전달
5. 사용자가 임시 비밀번호로 로그인 후 **설정 → 비밀번호 변경**에서 직접 변경

## 주의사항

- 서버 DB(`app.db`)가 존재해야 함
- 임시 비밀번호는 안전한 경로(메신저 DM 등)로 전달할 것
- 사용자가 비밀번호를 변경하기 전까지 임시 비밀번호로 로그인 가능
