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

## 실행 흐름

1. 전체 사용자 목록 출력 (username, 이름, 직책, 관리자 여부)
2. 재설정할 username 입력
3. 새 비밀번호 입력 (6자 이상, 확인 입력 포함)
4. 완료

## 주의사항

- 서버 DB(`app.db`)가 존재해야 함
- 재설정된 비밀번호는 해당 사용자에게 직접 전달해야 함
- 사용자는 로그인 후 **설정 → 비밀번호 변경**에서 직접 변경 가능
