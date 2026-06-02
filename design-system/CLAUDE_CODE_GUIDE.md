# Claude Code로 디자인 시스템 적용하기 — 가이드

이 문서는 **Claude Code가 이 디자인 시스템을 `work-management` 저장소에 적용**하도록 만드는 전체 과정을 담았습니다. 순서대로 따라 하세요.

---

## 0. 준비물
- 로컬에 git, Node.js(18+), npm 설치
- Claude Code 설치: `npm install -g @anthropic-ai/claude-code` (또는 공식 안내대로)
- 이 패키지(zip) 압축 해제

---

## 1. 저장소 클론 & 브랜치 생성
```bash
git clone https://github.com/moragosu/work-management.git
cd work-management
git checkout -b design-system
```

## 2. 디자인 시스템 폴더를 저장소에 복사
압축 푼 `design_handoff_design_system/design-system/` 폴더를 저장소 루트에 `design-system/` 으로 복사합니다.
```bash
# 예시 (경로는 본인 환경에 맞게)
cp -R ~/Downloads/design_handoff_design_system/design-system ./design-system
git add design-system && git commit -m "docs: add design system bundle"
```

## 3. Claude Code가 항상 디자인 규칙을 따르도록 설정 (권장)
저장소 루트의 `CLAUDE.md` 파일에 아래 블록을 추가하세요. (없으면 새로 생성)
Claude Code는 모든 작업에서 이 파일을 자동으로 읽습니다.

```markdown
## 디자인 시스템
이 저장소의 UI 작업은 `design-system/`의 규칙을 따른다.
- 토큰: `design-system/colors_and_type.css` (색상/타입/여백/라운드/그림자 CSS 변수)
- 스펙: `design-system/README.md` (카피 톤·비주얼 파운데이션·아이코노그래피)
- 컴포넌트 참조: `design-system/ui_kits/work-management/` (React로 작성된 **시각 참조**.
  실제 앱은 Vue이므로 그대로 복사하지 말고, 동일한 클래스/구조로 Vue에 구현한다)
- 색·폰트·여백은 위 토큰에서만 사용하고 임의의 새 색을 만들지 않는다.
- 아이콘은 Material Symbols Outlined만 사용한다.
```

## 4. Claude Code 실행 & 지시
저장소 루트에서:
```bash
claude
```
그리고 아래 프롬프트를 그대로 붙여넣으세요 (목적에 맞게 하나 선택):

### 옵션 A — 토큰만 비파괴적으로 통합 (안전)
```
design-system/README.md 와 design-system/colors_and_type.css 를 먼저 읽어줘.
그다음 frontend/src/style.css 에 디자인 토큰을 통합해줘. 핸드오프 가이드대로:
- 기존 :root 값은 동일하니 건드리지 말고, 빠져 있는 새 시맨틱 변수/클래스
  (--fs-*, --fw-*, --lh-*, .ds-* 등)만 추가
- colors_and_type.css 를 frontend 에서 import 하는 구조로 연결
변경 후 `cd frontend && npm install && npm run build` 로 빌드가 깨지지 않는지 확인하고,
문제 없으면 커밋해줘.
```

### 옵션 B — 특정 화면을 디자인 시스템 기준으로 재정비
```
design-system/ 의 토큰과 ui_kits/work-management/ 컴포넌트 참조를 읽고,
frontend/src/views/<대상>.vue 를 디자인 시스템 규칙에 맞게 정리해줘.
새 색/폰트를 만들지 말고 기존 토큰과 글로벌 클래스(.card .btn .badge 등)만 사용해줘.
빌드 확인 후 커밋해줘.
```

## 5. 검증
Claude Code가 끝나면 직접 확인:
```bash
cd frontend
npm run dev          # 로컬에서 화면 확인 (http://localhost:5174)
```
디자인 시스템 탭/specimen은 `design-system/ui_kits/work-management/index.html` 을 브라우저로 열어 비교.

## 6. 푸시 & PR
```bash
git push origin design-system
```
GitHub에서 `design-system → main` **Pull Request** 생성 후 리뷰·머지.
(Claude Code에게 "이 변경으로 PR 설명문 한국어로 써줘" 라고 시켜도 됩니다.)

---

## 자주 막히는 포인트
- **React를 Vue에 그대로 붙이지 말 것.** `ui_kits/*.jsx`는 픽셀 참조용. 클래스명·구조·값만 가져와 Vue로 구현.
- **폰트:** Pretendard는 저장소에 없어 CDN으로 불러옴. 운영에서는 `frontend/public/fonts/`에 `woff2`를 넣고 `@font-face`로 self-host 후 CDN import 제거 권장.
- **값은 이미 앱과 동일.** colors_and_type.css는 기존 style.css의 :root를 정리·확장한 것이라, 통합은 충돌 없이 안전합니다.
- **항상 브랜치 + PR.** main에 직접 푸시하지 말고 `design-system` 브랜치로.
```
