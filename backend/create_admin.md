# create_admin.py

초기 admin 계정을 생성하거나 기존 계정을 admin으로 승격하는 스크립트.

## 개발 환경

```bash
cd backend
uv run python create_admin.py
```

## 운영 환경 (prod)

배포 후 서버에서 실행:

```bash
sudo DATA_DIR=/var/www/okr-app/data \
  /var/www/okr-app/backend/.venv/bin/python \
  /var/www/okr-app/backend/create_admin.py
```

## 실행 흐름

1. username 입력 (기본값: `admin`)
2. 표시 이름 입력 (기본값: `관리자`)
3. 비밀번호 입력 (6자 이상, 확인 입력 포함)
4. 동일 username이 이미 존재하면 덮어쓸지 확인

## 주의사항

- 서버를 한 번 이상 실행해 DB(`app.db`)가 생성된 상태여야 함
- `DATA_DIR` 환경변수를 지정하지 않으면 `../data`를 기본값으로 사용
