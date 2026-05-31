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

## 업데이트 배포

```bash
cd ~/work-management
git fetch external
sudo git reset --hard external/main
sudo bash deploy.sh
```

`deploy.sh`가 코드 복사 → 의존성 설치 → 서비스 재시작까지 자동 처리하고,
서비스 시작 시 DB 마이그레이션도 자동 실행됩니다.

---

## 최초 배포 시만 필요한 추가 작업

> 현재 운영 중이라면 이미 완료된 단계입니다. 건너뜁니다.

### 관리자 계정 생성

```bash
cd /var/www/okr-app/backend
DATA_DIR=/var/www/okr-app/data .venv/bin/python create_admin.py
```

### 파트원 계정 일괄 생성

`~/work-management/backend/staff_accounts.json`을 편집한 뒤:

```bash
cd /var/www/okr-app/backend
DATA_DIR=/var/www/okr-app/data .venv/bin/python create_staff_accounts.py
```

---

## 개발 서버 (운영 전 확인용)

```bash
cd ~/work-management
bash dev.sh
```

- 프론트엔드: `http://localhost:5174`
- 백엔드: `http://localhost:8001`

> 개발 서버는 `~/work-management/data/`를 사용하므로 운영 데이터와 분리됩니다.

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
| 운영 포트 | `8080` (변경: `sudo bash deploy.sh 9090`) |
| 운영 데이터 경로 | `/var/www/okr-app/data/` |
| DB 파일 | `/var/www/okr-app/data/app.db` |
