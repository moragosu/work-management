# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 개발 서버 실행

```bash
bash dev.sh
```

- **백엔드**: `http://localhost:8001` (FastAPI, `--reload` 모드)
- **프론트엔드**: `http://localhost:5174` (Vite)
- **API 문서**: `http://localhost:8001/docs`

환경변수 `DATA_DIR`이 설정되지 않으면 `../data`를 기본 경로로 사용한다.

## 백엔드 명령어

```bash
cd backend

# 의존성 설치
uv sync --python 3.12

# 서버 단독 실행
DATA_DIR=../data uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# 스크립트 실행 예시
DATA_DIR=../data uv run python create_admin.py
DATA_DIR=../data uv run python create_staff_accounts.py [--force]
```

## 프론트엔드 명령어

```bash
cd frontend
npm install
npm run dev      # 개발 서버
npm run build    # dist/ 로 프로덕션 빌드
```

## 배포

```bash
sudo bash deploy.sh [PORT]   # 기본 포트 8080
```

Gunicorn + Nginx + Systemd 조합으로 배포된다. 서비스명: `okr-app`.

---

## 아키텍처

### 전체 구조

```
backend/          FastAPI (Python 3.12, uv)
frontend/         Vue 3 + Vite + Pinia
data/             SQLite DB (app.db) + 업로드 파일
dist/             프론트엔드 빌드 결과 (운영 서빙용)
```

### 백엔드

**`data_store.py`가 모든 DB 접근의 단일 진입점이다.**

- `get_conn()`: WAL 모드 SQLite 연결 반환
- `init_db()`: 스키마 생성 + 마이그레이션 (서버 시작 시 `main.py`에서 호출)
- `load(filename)` / `save(filename, data)`: JSON 호환 인터페이스 (레거시 패턴, 내부적으로 SQLite 사용)
- `insert_notification()`: 알림 삽입 + 사용자당 50개 초과 시 오래된 것 자동 삭제 (미답변 question_tagged는 제외)
- `get_username_for_notification(name)`: staff_id 조인 → users.name fallback 순서로 username 조회

**인증 흐름:**

1. `dependencies.py:get_current_user()` — Bearer 토큰 검증 → DB에서 사용자 조회
2. `dependencies.py:require_admin()` — `is_admin=1` 체크
3. `users` 테이블: `role`(member/group_leader/part_leader) + `is_admin`(0/1) 분리

**라우터 등록**: `main.py`에서 `/api/{prefix}` 형태로 일괄 등록.

**staff ↔ users 연결**: `users.staff_id → staff.id`. 이름 기반 매칭은 사용하지 않는다.

### 프론트엔드

**`src/main.js`**: Pinia, Router 초기화 후 `authStore.initAxiosAuth()`로 localStorage 토큰을 Axios 기본 헤더에 설정.

**라우터 가드** (`router/index.js`):
- 미로그인 → `/login` 리다이렉트
- `force_password_change=true` → `/change-password` 강제 이동

**`src/stores/auth.js`**:
- `user`, `token` → localStorage 영속
- `isAdmin`: `user.is_admin` 기반
- `isLeader`: role이 group_leader/part_leader이거나 is_admin인 경우
- `mustChangePassword`: `force_password_change` 플래그

**Progress.vue** (주간 진행 현황): 가장 복잡한 뷰. 지난주/이번주 패널, 상단 토글 버튼(`panelState: 'split'|'left'|'right'`), 소과제 접기/펼치기, 알림 딥링크(`?week=...&focusQuestion=...`), 인력 필터를 관리한다.

**알림**: `window.dispatchEvent(new Event('refresh-notifications'))`로 `NotificationBell.vue`에 즉시 갱신 요청.

---

## 주요 패턴

### 알림 규칙
- `question_tagged` 알림: 해당 질문에 답변이 없으면 수동 삭제 불가
- 답변 삭제 시 질문이 다시 미답변 상태가 되면 대상자에게 알림 재발송

### 이미지 업로드
- `POST /api/upload` → `/data/uploads/` 저장 → `/uploads/{filename}` URL 반환
- `useImageCleanup.js` 컴포저블로 고아 이미지 정리

### ID 생성
- `backend/utils/id_generator.py:short_uuid(prefix)` — S/I/Q/A/R/C + UUID 앞 8자리

### 초기 계정 관리 스크립트
| 스크립트 | 용도 |
|---------|------|
| `create_admin.py` | 관리자 계정 생성/업데이트 |
| `create_staff_accounts.py` | staff 목록 기반 일괄 계정 생성 (`--force`로 기존 계정 초기화) |
| `staff_accounts.json` | username 매핑 파일 (`default_password` + staff 배열) |

신규 계정은 `force_password_change=1`로 생성되어 첫 로그인 시 비밀번호 변경을 강제한다.

---

## 디자인 시스템

이 저장소의 모든 UI 작업은 `design-system/`의 규칙을 따른다.

- **토큰**: `design-system/colors_and_type.css` — 색상·타입스케일·여백·라운드·그림자 CSS 변수 정의. `frontend/src/style.css`의 `:root`에 이미 통합되어 있다.
- **스펙**: `design-system/README.md` — 카피 톤·비주얼 파운데이션·아이코노그래피 전체 규칙.
- **컴포넌트 참조**: `design-system/ui_kits/work-management/` — React로 작성된 **시각 참조**. 실제 앱은 Vue이므로 JSX를 그대로 복사하지 말고, 동일한 클래스명·구조·값으로 Vue SFC에 구현한다.
- **통합 가이드**: `design-system/CLAUDE_CODE_GUIDE.md` — 단계별 적용 절차 및 붙여넣기용 프롬프트.

### 지켜야 할 규칙 (위반 금지)

| 항목 | 규칙 |
|------|------|
| 색상 | `--primary`, `--success`, `--warning` 등 기존 토큰만 사용. 임의의 hex 값 신규 추가 금지 |
| 타입스케일 | `--fs-md`(14px), `--fs-sm`(13px), `--fs-xs`(12px) 등 변수 사용. 하드코딩 금지 |
| 아이콘 | Material Symbols Outlined 전용. 두 번째 아이콘 패밀리·직접 그린 SVG 추가 금지 |
| 폰트 | Pretendard (`--font-sans`). 새 폰트 추가 금지 |
| 여백 | `--space-xs`(4px) ~ `--space-2xl`(48px) 4배수 스케일 사용 |
| 라디우스 | 버튼·입력 `--radius-sm`(4px), 카드 `--radius-md`(8px), 모달 `--radius-lg`(12px) |
| 컴포넌트 클래스 | `.card`, `.btn`, `.badge`, `.form-control`, `.tabs`, `.q-filter-group` 등 기존 글로벌 클래스 재사용 |
| 언어·카피 | 100% 한국어, 합쇼체(-습니다). 이모지는 긍정 빈 상태(👍)에만 |
