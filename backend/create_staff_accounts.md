# create_staff_accounts.py

`staff_accounts.json`에 정의된 파트원 목록을 읽어 계정을 일괄 생성하는 스크립트.

## 사전 준비

`backend/staff_accounts.json`에서 각 인원의 `username`과 초기 비밀번호(`default_password`)를 채운다.

```json
{
  "default_password": "초기비밀번호",
  "staff": [
    { "name": "김경산", "username": "gks01" },
    { "name": "박태준", "username": "ptj99" }
  ]
}
```

- `username`이 하나라도 비어 있으면 실행이 중단된다.
- 이미 같은 `username` 또는 같은 `name`의 계정이 있으면 해당 인원은 건너뛴다.

---

## 개발 환경 (로컬 PC)

```bash
cd backend

# 신규 계정 생성
uv run python create_staff_accounts.py

# 이미 존재하는 계정도 비밀번호 초기화 + 변경 강제
uv run python create_staff_accounts.py --force
```

> `DATA_DIR`을 별도로 지정하지 않으면 `../data`를 자동으로 사용한다.

---

## 운영 환경 (사내 서버)

서버에 SSH 접속 후 아래 명령 실행.

**1단계 — 매핑 파일을 서버에 복사** (로컬 PC에서)

```bash
scp backend/staff_accounts.json user@서버IP:/var/www/okr-app/backend/
```

**2단계 — 스크립트 실행** (서버에서)

```bash
# 신규 계정 생성
sudo DATA_DIR=/var/www/okr-app/data \
  /var/www/okr-app/backend/.venv/bin/python \
  /var/www/okr-app/backend/create_staff_accounts.py

# 기존 계정도 초기화
sudo DATA_DIR=/var/www/okr-app/data \
  /var/www/okr-app/backend/.venv/bin/python \
  /var/www/okr-app/backend/create_staff_accounts.py --force
```

---

## 실행 후

- 출력된 초기 비밀번호를 파트원에게 전달한다.
- 파트원은 로그인 후 **설정 → 비밀번호 변경**에서 직접 변경한다.
- `role`은 기본값 `member`로 생성되며, 필요 시 관리자 페이지에서 변경한다.
