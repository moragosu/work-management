# 배포 매뉴얼

## 사내 서버 구조

| 경로 | 용도 |
|------|------|
| `~/work-management/` | 코드 저장소. git sync, dev 서버 실행 |
| `/var/www/okr-app/` | 운영 배포 경로. 실제 서비스가 여기서 동작 |

### Git Remote 구성

```
origin    https://github.sec.samsung.net/...  (사내 git — 외부 접속 불가)
external  https://github.com/moragosu/...     (사외 git — 코드 수신용)
```

---

## 개발 브랜치 테스트 배포

사외 git에 새 커밋이 올라온 경우 사내 서버에서 동기화 후 배포합니다.

```bash
cd ~/work-management

# 1. 사외 git에서 최신 코드 받기
git fetch external

# 2. 현재 코드를 사외 브랜치에 맞춤
sudo git reset --hard external/feat/login-notification

# 3. 운영 환경에 배포
sudo bash deploy.sh
```

---

## 운영 배포 (main 반영 후)

테스트가 완료되어 사외 git에서 `main`으로 rebase가 완료된 경우에 실행합니다.

```bash
cd ~/work-management

# 1. 사외 git main 동기화
git fetch external

# 2. main에 맞춤
sudo git reset --hard external/main

# 3. 운영 배포
sudo bash deploy.sh
```

---

## 최초 배포 시: 관리자 계정 생성

> **최초 1회만 실행합니다.** 계정이 이미 있으면 건너뜁니다.

`sudo bash deploy.sh` 실행 후, 운영 경로에서 계정 생성 스크립트를 실행합니다.

```bash
cd /var/www/okr-app/backend
DATA_DIR=/var/www/okr-app/data .venv/bin/python create_admin.py
```

프롬프트에서 사용자명·이름·비밀번호를 입력하면 관리자 계정이 생성됩니다.

### 파트원 계정 일괄 생성 (선택)

`~/work-management/backend/staff_accounts.json`을 편집한 뒤 배포하면
`/var/www/okr-app/backend/staff_accounts.json`에 반영됩니다. 그 후 실행합니다.

```bash
cd /var/www/okr-app/backend
DATA_DIR=/var/www/okr-app/data .venv/bin/python create_staff_accounts.py
```

> 생성된 계정은 첫 로그인 시 비밀번호 변경이 강제됩니다.

---

## 개발 서버 실행 (운영 전 로컬 확인용)

운영에 반영하기 전에 사내 서버에서 직접 동작을 확인하고 싶을 때 사용합니다.

```bash
cd ~/work-management
bash dev.sh
```

- 백엔드: `http://localhost:8001`
- 프론트엔드: `http://localhost:5174`

> `~/work-management/data/`를 데이터 경로로 사용하므로 운영 데이터(`/var/www/okr-app/data/`)와 **완전히 분리**됩니다.

---

## 참고

### 서비스 관리

```bash
sudo systemctl status okr-app    # 상태 확인
sudo systemctl restart okr-app   # 재시작
sudo journalctl -u okr-app -f    # 실시간 로그
```

### 기본 설정값

| 항목 | 값 |
|------|----|
| 운영 포트 | `8080` (변경 시: `sudo bash deploy.sh 9090`) |
| 운영 데이터 경로 | `/var/www/okr-app/data/` |
| DB 파일 | `/var/www/okr-app/data/app.db` |

### DB 마이그레이션

서비스 시작 시 자동으로 처리됩니다. 별도 명령 불필요.
