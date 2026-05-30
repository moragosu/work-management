# 사내 배포 매뉴얼

> 현재 사내 운영 버전: `2949398`  
> 최신 개발 브랜치: `feat/login-notification`

---

## 개요

이 매뉴얼은 개발 서버(로컬 또는 개발 PC)의 변경사항을 사내 운영 서버에 적용하는 절차를 설명합니다.

---

## 1단계 — 개발 PC: 원격 push

변경사항이 커밋되어 있는 상태에서 원격 저장소로 push합니다.

```bash
git push origin feat/login-notification
```

---

## 2단계 — 사내 서버: 코드 업데이트

사내 서버에 SSH로 접속한 뒤 프로젝트 디렉토리로 이동합니다.

```bash
cd /path/to/okr-app   # 실제 배포 경로로 변경
git fetch origin
git checkout feat/login-notification
git pull origin feat/login-notification
```

---

## 3단계 — 사내 서버: 백엔드 의존성 설치

패키지가 변경된 경우 실행합니다. 변경이 없으면 생략해도 됩니다.

```bash
cd backend
uv sync --python 3.12
cd ..
```

---

## 4단계 — 최초 배포 시: 관리자 계정 생성

> **최초 1회만 실행합니다.** 이미 계정이 있는 경우 건너뜁니다.

로그인 없이는 시스템을 사용할 수 없으므로, **서버 기동 전** 관리자 계정을 먼저 생성합니다.

```bash
cd backend
DATA_DIR=../data uv run python create_admin.py
```

프롬프트에서 사용자명·이름·비밀번호를 입력합니다.

### 파트원 계정 일괄 생성 (선택)

`backend/staff_accounts.json`을 편집한 뒤 실행합니다.

```bash
DATA_DIR=../data uv run python create_staff_accounts.py
```

`--force` 옵션을 추가하면 기존 계정을 초기화(임시 비밀번호 재설정)합니다.

```bash
DATA_DIR=../data uv run python create_staff_accounts.py --force
```

> 신규 계정은 첫 로그인 시 비밀번호 변경을 강제합니다. 파트원들에게 사전 안내하세요.

---

## 5단계 — 배포 실행

프로젝트 루트에서 배포 스크립트를 실행합니다.

```bash
cd ..   # 프로젝트 루트로 이동
sudo bash deploy.sh
```

`deploy.sh`는 다음을 순서대로 처리합니다.

1. 프론트엔드 빌드 (`npm run build`)
2. Gunicorn 프로세스 재시작
3. Nginx 리로드

> `dist/` 디렉토리가 이미 커밋에 포함된 경우 빌드 단계를 건너뛸 수 있습니다. `deploy.sh` 내부 로직을 확인하세요.

---

## 6단계 — 배포 확인

브라우저에서 사내 서버 주소에 접속하여 정상 동작을 확인합니다.

- 로그인 화면 표시 여부
- 관리자 계정으로 로그인 성공 여부
- 주간 진행 현황 및 관리 도구 접근 여부

---

## 데이터베이스 마이그레이션 안내

서버 기동 시 `init_db()`가 자동으로 스키마를 업데이트합니다. 별도 마이그레이션 명령은 필요 없습니다.

신규 추가되는 테이블:

| 테이블 | 용도 |
|--------|------|
| `users` | 로그인 계정 관리 |
| `notifications` | 알림 |
| `answer_replies` | Q&A 답글 |
| `issue_comments` | 이슈 댓글 |

기존 이슈·Q&A·컨플루언스 데이터는 그대로 유지됩니다.

---

## 서비스 관리 명령어

```bash
# 서비스 상태 확인
sudo systemctl status okr-app

# 서비스 재시작
sudo systemctl restart okr-app

# 로그 확인
sudo journalctl -u okr-app -f
```

---

## 문제 해결

### 로그인이 안 될 때

관리자 계정이 생성되지 않은 경우입니다. [4단계](#4단계--최초-배포-시-관리자-계정-생성)를 실행합니다.

### 의존성 오류 발생 시

```bash
cd backend
uv sync --python 3.12 --reinstall
```

### 포트 충돌 시

`deploy.sh`에 포트 인자를 전달합니다.

```bash
sudo bash deploy.sh 8080
```
