<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">도움말</h2>
      <p class="page-subtitle">설비혁신파트 협업 시스템 사용 가이드</p>
    </div>

    <!-- 목차 -->
    <div class="toc-card card">
      <div class="card-body">
        <p class="toc-label">바로가기</p>
        <div class="toc-grid">
          <a v-for="item in toc" :key="item.id" :href="'#' + item.id" class="toc-item">
            <span class="material-symbols-outlined toc-icon">{{ item.icon }}</span>
            <span>{{ item.title }}</span>
          </a>
        </div>
      </div>
    </div>

    <!-- ① 시스템 소개 -->
    <section id="overview" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">info</span>
          <h3 class="section-title">시스템 소개</h3>
        </div>

        <p class="section-desc">
          이 시스템은 <strong>OKR(목표 및 핵심 결과)</strong> 방식으로 파트의 목표와 과제를 관리하고,
          주간 단위로 진행 현황을 공유하기 위한 도구입니다.
        </p>

        <div class="callout callout-info">
          <span class="material-symbols-outlined callout-icon">lightbulb</span>
          <div>
            <strong>OKR이란?</strong>
            <span class="text-secondary"> — Objectives(목표)와 Key Results(핵심 결과)의 약자입니다. 달성하고 싶은 목표를 정의하고, 그 달성 여부를 측정할 수 있는 핵심 지표로 연결하는 방식입니다.</span>
          </div>
        </div>

        <div class="menu-cards">
          <div class="menu-card">
            <span class="material-symbols-outlined menu-card-icon icon-blue">account_circle</span>
            <div>
              <div class="menu-card-title">계정 및 로그인</div>
              <div class="menu-card-desc">개인 계정으로 로그인 — 역할에 따라 접근 가능한 기능이 달라집니다</div>
            </div>
          </div>
          <div class="menu-card">
            <span class="material-symbols-outlined menu-card-icon icon-purple">notifications</span>
            <div>
              <div class="menu-card-title">알림</div>
              <div class="menu-card-desc">질문 태그·답변 등록·이슈 배정 등 중요한 이벤트를 상단 알림 벨로 실시간 수신</div>
            </div>
          </div>
          <div class="menu-card">
            <span class="material-symbols-outlined menu-card-icon icon-blue">dashboard</span>
            <div>
              <div class="menu-card-title">대시보드</div>
              <div class="menu-card-desc">파트 전체 목표 현황과 파트원별 활동 통계를 한눈에 확인</div>
            </div>
          </div>
          <div class="menu-card">
            <span class="material-symbols-outlined menu-card-icon icon-orange">assignment</span>
            <div>
              <div class="menu-card-title">주간 진행 현황</div>
              <div class="menu-card-desc">주차별 이슈 등록·과제 댓글 관리 — 파트원들이 주로 사용하는 화면</div>
            </div>
          </div>
          <div class="menu-card">
            <span class="material-symbols-outlined menu-card-icon icon-teal">rate_review</span>
            <div>
              <div class="menu-card-title">피드백</div>
              <div class="menu-card-desc">시스템 개선 의견·건의사항을 카테고리별로 자유롭게 작성하고 공유</div>
            </div>
          </div>
          <div class="menu-card">
            <span class="material-symbols-outlined menu-card-icon icon-purple">manage_search</span>
            <div>
              <div class="menu-card-title">이슈 히스토리</div>
              <div class="menu-card-desc">삭제된 이슈·댓글 스냅샷 조회 — 그룹장·파트장·관리자 전용</div>
            </div>
          </div>
          <div class="menu-card">
            <span class="material-symbols-outlined menu-card-icon icon-teal">summarize</span>
            <div>
              <div class="menu-card-title">보고서 내보내기</div>
              <div class="menu-card-desc">주간 이슈를 텍스트 보고서로 추출 — 그룹장·파트장·관리자 전용</div>
            </div>
          </div>
          <div class="menu-card">
            <span class="material-symbols-outlined menu-card-icon icon-gray">settings</span>
            <div>
              <div class="menu-card-title">관리 도구</div>
              <div class="menu-card-desc">파트원·목표·과제 정보 등록 및 수정 (관리자 전용)</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ② 계정 및 로그인 -->
    <section id="account" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">account_circle</span>
          <h3 class="section-title">계정 및 로그인</h3>
        </div>
        <p class="section-desc">시스템을 사용하려면 개인 계정으로 로그인해야 합니다. 계정은 관리자가 미리 생성해 드립니다.</p>

        <!-- 로그인 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">login</span>
            로그인
          </div>
          <ul class="feature-list">
            <li><strong>사용자 이름</strong>과 <strong>비밀번호</strong>를 입력하고 로그인 버튼을 클릭합니다</li>
            <li>로그인 상태는 브라우저에 유지되며, <strong>로그아웃</strong>하거나 세션이 만료될 때까지 자동으로 유지됩니다</li>
            <li>로그아웃은 왼쪽 사이드바 하단의 <strong>로그아웃</strong> 버튼을 클릭합니다</li>
          </ul>
          <div class="callout callout-warning">
            <span class="material-symbols-outlined callout-icon">info</span>
            <div><strong>첫 로그인 시 비밀번호 변경이 강제됩니다.</strong> 관리자가 설정한 임시 비밀번호로 로그인하면 즉시 비밀번호 변경 화면으로 이동합니다. 새 비밀번호를 설정한 뒤 정상 이용이 가능합니다.</div>
          </div>
        </div>

        <!-- 비밀번호 변경 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">lock_reset</span>
            비밀번호 변경
          </div>
          <ul class="feature-list">
            <li>왼쪽 사이드바 하단의 사용자 이름 옆 <strong>설정</strong> 아이콘을 통해 비밀번호를 변경할 수 있습니다</li>
            <li>비밀번호를 잊어버린 경우 <strong>관리자에게 문의</strong>하면 임시 비밀번호로 초기화해 드립니다</li>
          </ul>
        </div>

        <!-- 역할 체계 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">badge</span>
            역할 체계
          </div>
          <p class="section-desc" style="margin-bottom:12px">계정마다 역할이 부여되며, 역할에 따라 사용할 수 있는 기능이 달라집니다.</p>
          <div class="role-table">
            <div class="role-row role-header">
              <span>역할</span>
              <span>설명</span>
              <span>주요 권한</span>
            </div>
            <div class="role-row">
              <span><span class="role-badge role-member">파트원</span></span>
              <span>일반 파트원</span>
              <span>이슈 등록·수정, 답변 작성</span>
            </div>
            <div class="role-row">
              <span><span class="role-badge role-leader">그룹장/파트장</span></span>
              <span>그룹장 또는 파트장</span>
              <span>이슈·댓글 전체 기능 + 답변 요구 지정</span>
            </div>
            <div class="role-row">
              <span><span class="role-badge role-admin">관리자</span></span>
              <span>시스템 관리자</span>
              <span>전체 기능 + 관리 도구 + 계정 관리</span>
            </div>
          </div>
          <div class="callout callout-info" style="margin-top:12px">
            <span class="material-symbols-outlined callout-icon">info</span>
            <div><strong>과제 댓글</strong>은 모든 파트원이 작성할 수 있습니다. 다만 댓글에 <strong>답변 요구</strong>를 지정하는 기능은 그룹장·파트장·관리자만 사용할 수 있습니다.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ③ 알림 -->
    <section id="notify" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">notifications</span>
          <h3 class="section-title">알림</h3>
        </div>
        <p class="section-desc">질문 태그·답변 등록 등 나와 관련된 이벤트가 발생하면 상단 헤더 우측의 <strong>알림 벨(🔔)</strong>에 배지로 표시됩니다.</p>

        <!-- 알림 종류 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">category</span>
            알림 종류
          </div>
          <div class="notify-table">
            <div class="notify-row notify-header">
              <span>종류</span>
              <span>발생 조건</span>
            </div>
            <div class="notify-row">
              <span><span class="material-symbols-outlined" style="font-size:14px;color:#7c3aed;vertical-align:middle">mark_chat_unread</span> 댓글 태그</span>
              <span>이슈 댓글 또는 과제 댓글에서 나를 @태그하고 <strong>답변 요구</strong>로 지정할 때</span>
            </div>
            <div class="notify-row">
              <span><span class="material-symbols-outlined" style="font-size:14px;color:#0ea5e9;vertical-align:middle">chat_bubble</span> 이슈 댓글</span>
              <span>내가 담당한 이슈에 일반 댓글이 달릴 때</span>
            </div>
            <div class="notify-row">
              <span><span class="material-symbols-outlined" style="font-size:14px;color:#d97706;vertical-align:middle">warning</span> 이슈 배정</span>
              <span>나를 담당자로 지정한 이슈가 등록될 때</span>
            </div>
            <div class="notify-row">
              <span><span class="material-symbols-outlined" style="font-size:14px;color:#2563eb;vertical-align:middle">campaign</span> 공지 업데이트</span>
              <span>관리자가 공지 내용을 변경할 때</span>
            </div>
          </div>

          <!-- 알림 항목 미리보기 -->
          <div class="mini-ui-preview" style="margin-top:12px">
            <div class="mini-preview-label">알림 항목 미리보기</div>
            <div class="mini-notify-item">
              <span class="mini-unread-dot"></span>
              <span class="material-symbols-outlined" style="font-size:15px;color:#7c3aed;flex-shrink:0">mark_chat_unread</span>
              <div class="mini-notify-text"><strong>홍길동</strong>님이 <em>T1 과제 댓글</em>에서 회원님을 태그하고 답변을 요청했습니다</div>
              <span class="mini-unread-badge">1</span>
            </div>
            <div class="mini-notify-item mini-read">
              <span class="mini-unread-dot mini-dot-read"></span>
              <span class="material-symbols-outlined" style="font-size:15px;color:#0ea5e9;flex-shrink:0">chat_bubble</span>
              <div class="mini-notify-text"><em>T2-1 이슈</em>에 <strong>김철수</strong>님이 댓글을 달았습니다</div>
            </div>
            <div class="mini-notify-item mini-read">
              <span class="mini-unread-dot mini-dot-read"></span>
              <span class="material-symbols-outlined" style="font-size:15px;color:#d97706;flex-shrink:0">warning</span>
              <div class="mini-notify-text">회원님을 담당자로 지정한 이슈가 등록되었습니다 — <em>T3 과제</em></div>
            </div>
          </div>
        </div>

        <!-- 알림 확인 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">notifications_active</span>
            알림 확인 및 관리
          </div>
          <ul class="feature-list">
            <li>상단 헤더 우측의 <strong>알림 벨</strong>을 클릭하면 최근 알림 목록이 드롭다운으로 표시됩니다</li>
            <li>읽지 않은 알림은 파란 점으로 표시되며, 벨 아이콘에 <strong>숫자 배지</strong>로 미읽음 수가 표시됩니다 (최대 99+)</li>
            <li>알림 항목을 클릭하면 <strong>해당 주차의 해당 위치로 바로 이동</strong>합니다</li>
            <li>드롭다운 상단의 <strong>"모두 읽음"</strong> 버튼으로 전체 읽음 처리할 수 있습니다</li>
            <li>개별 알림은 우측 <strong>×</strong> 버튼으로 삭제할 수 있습니다</li>
            <li>전체 알림 목록은 알림 드롭다운 하단 링크 또는 <strong>/알림</strong> 경로에서 확인할 수 있습니다</li>
          </ul>
          <div class="callout callout-warning">
            <span class="material-symbols-outlined callout-icon">info</span>
            <div><strong>답변 요구 댓글 태그 알림</strong>은 해당 댓글에 대댓글(답변)이 달리기 전까지 삭제되지 않습니다. 답변이 작성되어 자동으로 "답변됨" 처리된 후에야 삭제할 수 있습니다. — 답변 요구를 놓치지 않기 위한 보호 규칙입니다.</div>
          </div>
          <div class="callout callout-tip">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>알림은 <strong>SSE(실시간 스트림)</strong>으로 즉시 수신됩니다. 댓글 등록·이슈 배정 등 이벤트 발생 즉시 벨에 배지가 표시됩니다.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ④ 대시보드 -->
    <section id="dashboard" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">dashboard</span>
          <h3 class="section-title">대시보드</h3>
        </div>
        <p class="section-desc">홈 화면입니다. 파트 전체 현황과 지금 당장 확인해야 할 항목을 한눈에 파악할 수 있습니다.</p>

        <div class="feature-block">
          <div class="feature-label">
            <span class="badge-num">1</span>
            상단 통계 카드 (3개)
          </div>
          <ul class="feature-list">
            <li><strong>미확인 답변 현황</strong> — 전체 기간 누적 중 아직 답변이 달리지 않은 "답변 요구" 댓글 수. 주황색이면 확인 필요, 초록이면 양호</li>
            <li><strong>이번 주 이슈</strong> — 이번 주 등록된 이슈 수</li>
            <li><strong>컨플루언스 등록률</strong> — 이번 주 컨플루언스 링크를 등록한 과제 비율. 진행 바로 확인 가능</li>
          </ul>
        </div>

        <div class="feature-block">
          <div class="feature-label">
            <span class="badge-num">2</span>
            액션 패널 (2가지)
          </div>
          <ul class="feature-list">
            <li><strong>답변 현황</strong> — <strong>이번주 / 지난주</strong> 탭으로 주차를 전환하고, <strong>미답변 / 답변완료 / 전체</strong> 필터를 함께 사용할 수 있습니다. 이슈 댓글·과제 댓글 중 "답변 요구"로 등록된 항목이 표시되며, 클릭하면 해당 댓글 상세를 확인할 수 있습니다</li>
            <li><strong>이슈</strong> — <strong>이번주 / 지난주</strong> 탭으로 전환하며 해당 주 이슈 목록을 확인합니다. 클릭하면 해당 과제의 이슈 위치로 이동</li>
          </ul>
        </div>

        <div class="feature-block">
          <div class="feature-label">
            <span class="badge-num">3</span>
            파트원별 활동 현황
          </div>
          <ul class="feature-list">
            <li>상단의 <strong>이번주 / 지난주</strong> 탭으로 기준 주차를 전환합니다</li>
            <li>각 파트원의 <strong>담당 과제 수</strong>(누적)와 해당 주의 <strong>이슈 수 / 답변 요구 완료 수 / 미완료 수</strong>를 막대 그래프로 비교합니다</li>
            <li>우측 상단에 <strong>파트원 N명</strong> 배지로 인원 수를 확인할 수 있습니다</li>
          </ul>
        </div>

        <div class="feature-block">
          <div class="feature-label">
            <span class="badge-num">4</span>
            주간 등록 현황 매트릭스
          </div>
          <ul class="feature-list">
            <li>과제(행) × 주차(열) 기준으로 <strong>컨플루언스 · 이슈 · 답변 현황</strong> 등록 여부를 한눈에 확인합니다</li>
            <li><span class="material-symbols-outlined" style="font-size:13px;vertical-align:middle;color:var(--primary)">link</span> <strong>링크 아이콘</strong>을 클릭하면 해당 컨플루언스 페이지가 바로 열립니다</li>
            <li>섹션 제목을 클릭하면 매트릭스를 접거나 펼칠 수 있습니다</li>
            <li>현재 주차 열은 파란색 배경으로 강조됩니다</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- ⑤ 주간 진행 현황 -->
    <section id="progress" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">assignment</span>
          <h3 class="section-title">주간 진행 현황</h3>
        </div>
        <p class="section-desc">파트원들이 매주 이슈를 등록하고, 서로 의견/질문을 통해 소통하는 화면입니다.</p>

        <!-- 2분할 뷰 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px">splitscreen</span>
            지난주 / 이번주 2분할 보기
          </div>
          <ul class="feature-list">
            <li>화면이 <strong>지난주(왼쪽) | 이번주(오른쪽)</strong> 2개 패널로 분할되어 한 화면에서 비교할 수 있습니다</li>
            <li>각 패널 헤더의 <strong>← / →</strong> 버튼을 클릭하면 해당 패널이 접힙니다 — <strong>같은 버튼을 다시 클릭</strong>하면 2분할 상태로 복원됩니다</li>
            <li>패널 <strong>헤더 바 전체가 클릭 영역</strong>입니다 — 헤더 어디를 클릭해도 접기/펼치기가 작동합니다</li>
            <li>양쪽 패널 모두 <strong>이슈 등록·수정·삭제</strong>와 <strong>과제 댓글 작성·답변</strong> 등 전체 편집이 가능합니다</li>
          </ul>
        </div>

        <!-- 주차 선택 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px">calendar_month</span>
            주차 선택
          </div>
          <ul class="feature-list">
            <li>상단의 <strong>◀ ▶ 버튼</strong>으로 이전/다음 주차로 이동합니다 — 이번주 패널 기준으로 이동하며 지난주 패널도 함께 이동합니다</li>
            <li>날짜 범위(<em>예: 5/12 – 5/18</em>)와 주차 번호(<em>예: W20</em>)가 함께 표시됩니다</li>
            <li>현재 주차가 아닌 경우 <strong>"이번 주"</strong> 버튼이 나타납니다 — 클릭 시 현재 주로 이동</li>
          </ul>
          <div class="callout callout-tip">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>현재 주차는 파란색 테두리로 강조 표시됩니다. <strong>"이번 주"</strong> 배지가 날짜 옆에 표시되면 현재 주차입니다.</div>
          </div>
        </div>

        <!-- 과제 카드 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">style</span>
            과제 카드 구분
          </div>
          <ul class="feature-list">
            <li>각 메인과제 카드 왼쪽에 <strong>Objective별 고유 색상 줄</strong>이 표시됩니다 — 같은 Objective 소속 카드끼리는 같은 색으로 묶여 한눈에 구분됩니다</li>
            <li>카드 헤더의 Objective 배지도 동일한 색상으로 표시됩니다</li>
            <li>과제 카드는 <strong>기본적으로 소과제가 모두 펼쳐진 상태</strong>로 시작합니다. "전체 접기" 버튼으로 정리할 수 있습니다</li>
            <li>상단의 <strong>이름 칩</strong>을 클릭하면 해당 파트원이 담당한 과제만 필터링됩니다 — 여러 명 동시 선택 가능</li>
          </ul>
        </div>

        <!-- 이슈 등록 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--warning)">warning</span>
            이슈 등록 방법
          </div>

          <div class="steps">
            <div class="step">
              <div class="step-number">1</div>
              <div class="step-body">
                <strong>주차 확인</strong>
                <p>상단 주차 네비게이터에서 현재 주차인지 확인합니다.</p>
              </div>
            </div>
            <div class="step">
              <div class="step-number">2</div>
              <div class="step-body">
                <strong>과제 찾기</strong>
                <p>목표 → KR → 과제 순으로 나열된 목록에서 이슈를 등록할 과제를 찾습니다. 상단의 이름 칩을 클릭하면 해당 파트원의 과제만 필터링됩니다. 여러 명 동시 선택도 가능합니다.</p>
              </div>
            </div>
            <div class="step">
              <div class="step-number">3</div>
              <div class="step-body">
                <strong>"+ 이슈 등록" 클릭</strong>
                <p>과제 카드 하단의 이슈 섹션에서 버튼을 클릭합니다.</p>
              </div>
            </div>
            <div class="step">
              <div class="step-number">4</div>
              <div class="step-body">
                <strong>내용 작성</strong>
                <p>등록자는 <strong>로그인 계정으로 자동 입력</strong>됩니다. 이슈 내용을 작성합니다. 마크다운 형식을 지원합니다.</p>
              </div>
            </div>
            <div class="step">
              <div class="step-number">5</div>
              <div class="step-body">
                <strong>저장</strong>
                <p>내용이 입력되면 저장 버튼이 활성화됩니다.</p>
              </div>
            </div>
          </div>

          <div class="callout callout-tip">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>과제당 이슈는 <strong>여러 건</strong> 등록할 수 있습니다. 등록된 이슈 목록 아래 <strong>"+ 이슈 등록"</strong> 버튼을 클릭해 이슈를 추가하세요.</div>
          </div>
          <div class="callout callout-info">
            <span class="material-symbols-outlined callout-icon">link</span>
            <div><strong>메신저 공유</strong> — 이슈 우측의 <span class="material-symbols-outlined" style="font-size:13px;vertical-align:middle">link</span> 버튼을 클릭하면 해당 이슈로 바로 이동하는 단축 링크가 클립보드에 복사됩니다. 메신저에 붙여넣어 공유하면 받는 사람이 클릭 시 해당 주차·해당 이슈 위치로 바로 이동합니다.</div>
          </div>
        </div>

        <!-- 이슈 댓글 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">comment</span>
            이슈 댓글 / 대댓글
          </div>
          <ul class="feature-list">
            <li>이슈 하단의 <strong>"+ 댓글"</strong> 버튼으로 댓글을 작성할 수 있습니다 — 이슈 본문과 동일한 <strong>WYSIWYG 에디터</strong>를 사용하며 서식·이미지 첨부가 가능합니다</li>
            <li>등록된 댓글의 <strong>"↩ 답글"</strong> 버튼을 클릭하면 해당 댓글에 대한 대댓글을 작성할 수 있습니다 (2단계까지 지원)</li>
            <li>댓글·대댓글 작성자는 <strong>로그인 계정으로 자동 입력</strong>됩니다</li>
            <li>본인이 작성한 댓글은 <strong>수정·삭제</strong>할 수 있습니다</li>
            <li>댓글 입력 폼 상단의 <strong>이름 칩</strong>을 클릭하면 해당 파트원을 <strong>답변 요구 대상(타겟)으로 지정</strong>할 수 있으며, 댓글 본문에 <code class="md-syntax">@이름</code>이 자동으로 삽입됩니다</li>
            <li>칩 배치 순서: <strong>이슈 담당자(주황색)</strong> → 그룹장·파트장 → <strong>해당 과제원(파란색)</strong> → 나머지 파트원 순으로 표시됩니다</li>
            <li>그룹장·파트장·관리자는 <strong>"답변 요구"</strong> 체크박스를 켜서 해당 댓글에 응답을 요청할 수 있습니다 — 태그된 파트원에게 알림이 발송되며, 댓글 카드에 <strong>"답변 대기"</strong> 배지가 표시됩니다</li>
            <li>답변 요구 댓글에 대댓글이 달리면 자동으로 <strong>"답변됨"</strong> 처리됩니다</li>
          </ul>

          <!-- 댓글 카드 미리보기 -->
          <div class="mini-ui-preview" style="margin-top:14px">
            <div class="mini-preview-label">댓글 카드 미리보기</div>
            <div class="mini-comment-card">
              <div class="mini-cc-header">
                <span class="mini-avatar">홍</span>
                <span class="mini-author-name">홍길동</span>
                <span class="mini-badge-pending">답변 대기</span>
                <span class="mini-time">2분 전</span>
              </div>
              <div class="mini-cc-body"><span class="mini-at-tag">@김철수</span> T1 이슈 관련 내용 확인 부탁드립니다.</div>
              <div class="mini-cc-actions">
                <span class="mini-action-btn">↩ 답글</span>
              </div>
            </div>
            <div class="mini-comment-card mini-indent">
              <div class="mini-cc-header">
                <span class="mini-avatar mini-avatar-green">김</span>
                <span class="mini-author-name">김철수</span>
                <span class="mini-badge-answered">답변됨</span>
                <span class="mini-time">1분 전</span>
              </div>
              <div class="mini-cc-body">확인했습니다. 처리하겠습니다.</div>
            </div>
          </div>
        </div>

        <!-- 과제 댓글 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">forum</span>
            과제 댓글
          </div>
          <ul class="feature-list">
            <li>이슈와 별개로, 과제 카드 하단의 <strong>"과제 댓글"</strong> 섹션에서 과제 전반에 대한 의견·질문을 남길 수 있습니다</li>
            <li><strong>모든 파트원</strong>이 댓글을 작성할 수 있습니다</li>
            <li>댓글 입력 폼 위의 <strong>이름 칩</strong>을 클릭하면 해당 파트원을 <strong>답변 요구 대상(타겟)으로 지정</strong>할 수 있으며, 본문에 <code class="md-syntax">@이름</code>이 자동으로 삽입됩니다</li>
            <li>칩 배치 순서: <strong>그룹장·파트장</strong> → <strong>해당 과제원(파란색)</strong> → 나머지 파트원 순으로 표시됩니다</li>
            <li>그룹장·파트장·관리자는 <strong>"답변 요구"</strong> 체크박스로 특정 파트원에게 응답을 요청할 수 있습니다 — 태그된 파트원에게 알림이 발송되며, 대댓글이 달리면 자동으로 <strong>"답변됨"</strong> 처리됩니다</li>
            <li>댓글 카드에는 작성자·태그된 대상자·답변 상태(<strong>답변 대기 / 답변됨</strong>) 배지가 표시됩니다</li>
            <li>과제 댓글은 <strong>주차 단위</strong>로 저장됩니다 — 지난주·이번주 패널에서 각 주차의 댓글을 독립적으로 확인할 수 있습니다</li>
            <li>본인이 작성한 댓글은 <strong>수정·삭제</strong>가 가능합니다</li>
          </ul>

          <!-- 과제 댓글 폼 미리보기 -->
          <div class="mini-ui-preview" style="margin-top:14px">
            <div class="mini-preview-label">댓글 입력 폼 미리보기</div>
            <div class="mini-form-preview">
              <div class="mini-tag-row">
                <span class="mini-tag-label">@태그</span>
                <span class="mini-person-chip mini-chip-active">홍길동</span>
                <span class="mini-person-chip">김철수</span>
                <span class="mini-person-chip">이영희</span>
              </div>
              <div class="mini-editor-placeholder">댓글 내용을 입력하세요…&nbsp;<span class="mini-at-tag">@홍길동</span></div>
              <div class="mini-form-row">
                <span class="mini-req-check">
                  <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary);font-variation-settings:'FILL' 1">check_box</span>
                  답변 요구
                </span>
                <span style="flex:1"></span>
                <span class="mini-submit-btn">등록</span>
              </div>
            </div>
          </div>
          <div class="callout callout-tip">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>대시보드의 <strong>답변 현황 패널</strong>에서 "답변 요구"로 등록된 댓글을 주차별로 확인하고, 클릭하면 상세 내용을 볼 수 있습니다. 파트원별 답변 완료/미완료 현황도 활동 통계에서 확인할 수 있습니다.</div>
          </div>
        </div>

        <!-- 소과제 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">account_tree</span>
            소과제가 있는 과제
          </div>
          <ul class="feature-list">
            <li>소과제가 있는 과제 카드는 상단에 <strong>"소과제 N개"</strong> 배지와 <strong>"전체 펼치기 / 전체 접기"</strong> 버튼이 표시됩니다</li>
            <li>각 소과제는 과제 카드 내부에 <strong>파란 왼쪽 테두리</strong>로 구분된 별도 섹션으로 표시되며, <strong>기본적으로 펼쳐진 상태</strong>로 시작합니다</li>
            <li>소과제 헤더(상단 줄)를 <strong>클릭</strong>하면 내용이 펼쳐지거나 접힙니다. 헤더 우측의 완료 버튼·담당자 배지는 클릭해도 접히지 않습니다</li>
            <li>접힌 상태에서 이슈나 댓글 내용이 있으면 헤더에 <strong>요약 배지</strong>가 표시됩니다 — <em>이슈 N건</em>, <em>댓글 N건</em></li>
            <li><strong>컨플루언스 링크</strong>는 소과제별로 독립 등록됩니다 — 소과제가 있으면 모과제 단위 링크 대신 각 소과제 섹션 내부에 링크 입력란이 표시됩니다</li>
            <li>이슈 등록과 댓글도 <strong>소과제별로 독립적으로</strong> 관리됩니다</li>
            <li>소과제가 완료 처리되면 해당 섹션은 <strong>녹색 테두리</strong>로 바뀌고 흐릿하게 표시됩니다</li>
          </ul>
          <div class="callout callout-tip">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>모과제 헤더의 <strong>"전체 펼치기"</strong>를 누르면 해당 과제의 소과제를 한 번에 모두 펼칩니다. <strong>"전체 접기"</strong>로 다시 정리할 수 있습니다.</div>
          </div>

          <!-- 소과제 접힌 상태 미리보기 -->
          <div class="mini-ui-preview" style="margin-top:14px">
            <div class="mini-preview-label">소과제 접힌 상태 미리보기</div>
            <div class="mini-subtask-row">
              <span class="material-symbols-outlined" style="font-size:15px;color:var(--text-muted)">chevron_right</span>
              <span class="mini-subtask-name">T1-1 · 현황 분석</span>
              <span class="mini-cnt-badge mini-cnt-issue">이슈 3건</span>
              <span class="mini-cnt-badge mini-cnt-comment">댓글 2건</span>
              <span style="flex:1"></span>
              <span class="mini-person-tag">홍길동</span>
            </div>
            <div class="mini-subtask-row mini-subtask-done">
              <span class="material-symbols-outlined" style="font-size:15px;color:var(--success)">check_circle</span>
              <span class="mini-subtask-name mini-name-done">T1-2 · 개선안 도출</span>
              <span class="mini-cnt-badge mini-cnt-done">완료</span>
              <span style="flex:1"></span>
              <span class="mini-person-tag">김철수</span>
            </div>
          </div>
        </div>

        <!-- 컨플루언스 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px">link</span>
            컨플루언스 링크
          </div>
          <ul class="feature-list">
            <li>과제(또는 소과제) 카드의 컨플루언스 섹션에서 관련 문서 URL을 등록합니다</li>
            <li>등록된 링크는 클릭 시 새 탭으로 열리며, 수정·삭제 버튼으로 언제든 변경 가능합니다</li>
            <li>링크 입력란 옆 <strong>?</strong> 버튼을 클릭하면 링크 가져오는 방법이 표시됩니다</li>
          </ul>

          <div class="sub-section-title" style="margin-top:16px">
            <span class="material-symbols-outlined" style="font-size:15px">share</span>
            컨플루언스 Share Link 가져오는 방법
          </div>
          <div class="steps">
            <div class="step">
              <div class="step-number">1</div>
              <div class="step-body">
                <strong>Share 버튼 클릭</strong>
                <p>컨플루언스 페이지 <strong>우 상단</strong>의 <strong>Share</strong> 버튼을 클릭합니다.</p>
              </div>
            </div>
            <div class="step">
              <div class="step-number">2</div>
              <div class="step-body">
                <strong>Share Link 확인</strong>
                <p>드롭다운이 펼쳐지면 <strong>Share Link</strong>가 생성된 것을 확인합니다.</p>
              </div>
            </div>
            <div class="step">
              <div class="step-number">3</div>
              <div class="step-body">
                <strong>Copy 후 붙여넣기</strong>
                <p><strong>Copy</strong> 버튼을 눌러 링크를 복사한 뒤, 시스템의 컨플루언스 링크 입력란에 붙여넣고 저장합니다.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ⑤-2 과제 이력 -->
    <section id="history" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">history</span>
          <h3 class="section-title">과제 이력</h3>
        </div>
        <p class="section-desc">특정 과제의 전체 주차별 이슈·댓글·컨플루언스 링크를 한 페이지에서 시간 순으로 확인하는 화면입니다.</p>

        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">open_in_new</span>
            이력 화면 열기
          </div>
          <ul class="feature-list">
            <li>주간 진행 현황의 과제 카드 상단 우측에 있는 <strong>이력</strong> 버튼(<span class="material-symbols-outlined" style="font-size:13px;vertical-align:middle">history</span>)을 클릭하면 해당 과제의 이력 페이지로 이동합니다</li>
            <li>상단에 <strong>← 뒤로</strong> 버튼과 과제 이름이 표시됩니다</li>
            <li>소과제 필터 칩을 클릭하면 해당 소과제의 이력만 필터링됩니다</li>
          </ul>
        </div>

        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">view_week</span>
            주차별 이력 구성
          </div>
          <ul class="feature-list">
            <li>최신 주차가 맨 위에 표시되며, 각 주차 카드는 <strong>클릭하면 접기/펼치기</strong>가 가능합니다 — 최근 2개 주차는 기본으로 펼쳐진 상태로 시작합니다</li>
            <li>주차 카드 헤더에는 해당 주차의 <strong>컨플루언스 · 이슈</strong> 수가 배지로 요약됩니다</li>
            <li>각 주차 안에서 컨플루언스 링크 → 이슈 순서로 섹션이 구분됩니다</li>
          </ul>
        </div>

        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">ads_click</span>
            이슈 · 질문 바로가기
          </div>
          <ul class="feature-list">
            <li>이력 화면에서 <strong>이슈 카드를 클릭</strong>하면, 해당 주차의 주간 진행 현황으로 이동하며 해당 이슈 위치로 자동 스크롤됩니다</li>
            <li>카드에 마우스를 올리면 배경이 강조되고 <span class="material-symbols-outlined" style="font-size:13px;vertical-align:middle">open_in_new</span> 아이콘이 표시됩니다</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- ⑤-3 삭제된 이슈 히스토리 -->
    <section id="issue-history" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">manage_search</span>
          <h3 class="section-title">이슈 히스토리</h3>
        </div>
        <p class="section-desc">삭제된 이슈와 댓글의 스냅샷을 조회하는 화면입니다. 왼쪽 사이드바의 <strong>이슈 히스토리</strong> 메뉴에서 접근할 수 있으며, <strong>그룹장·파트장·관리자</strong>만 볼 수 있습니다.</p>

        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">history</span>
            주요 기능
          </div>
          <ul class="feature-list">
            <li>이슈가 삭제될 때 해당 이슈와 댓글 전체가 <strong>자동으로 스냅샷</strong>으로 저장됩니다</li>
            <li>상단의 <strong>주차</strong>·<strong>과제</strong> 필터로 원하는 기간·과제의 삭제 이력만 조회할 수 있습니다</li>
            <li>각 히스토리 카드를 클릭하면 삭제 당시의 이슈 내용과 댓글을 펼쳐서 확인할 수 있습니다</li>
            <li>관리자는 저장된 스냅샷을 <strong>영구 삭제</strong>할 수 있습니다</li>
          </ul>
          <div class="callout callout-info">
            <span class="material-symbols-outlined callout-icon">info</span>
            <div>이슈 히스토리는 <strong>복구 기능이 아닙니다</strong> — 삭제된 이슈를 다시 시스템에 되살리는 것은 지원하지 않으며, 내용을 확인·참고하는 용도로만 사용합니다.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ⑤-4 보고서 내보내기 -->
    <section id="export" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">summarize</span>
          <h3 class="section-title">보고서 내보내기</h3>
        </div>
        <p class="section-desc">주간 이슈 내용과 컨플루언스 링크를 정해진 텍스트 포맷으로 추출하는 기능입니다. 왼쪽 사이드바의 <strong>보고서 내보내기</strong> 메뉴에서 접근할 수 있으며, <strong>그룹장·파트장·관리자</strong>만 사용할 수 있습니다.</p>

        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">edit_note</span>
            사용 방법
          </div>
          <div class="steps">
            <div class="step">
              <div class="step-number">1</div>
              <div class="step-body">
                <strong>파트명 입력</strong>
                <p>보고서 헤더에 사용할 파트명을 입력합니다. 마지막 입력값이 자동으로 기억됩니다.</p>
              </div>
            </div>
            <div class="step">
              <div class="step-number">2</div>
              <div class="step-body">
                <strong>주차 선택</strong>
                <p>이슈가 등록된 주차 목록이 자동으로 표시됩니다. 보고서에 포함할 주차를 체크합니다 — 기본으로 최근 4개 주차가 선택됩니다.</p>
              </div>
            </div>
            <div class="step">
              <div class="step-number">3</div>
              <div class="step-body">
                <strong>"미리보기 생성" 클릭</strong>
                <p>선택한 주차의 이슈 내용이 텍스트 보고서로 생성됩니다.</p>
              </div>
            </div>
            <div class="step">
              <div class="step-number">4</div>
              <div class="step-body">
                <strong>복사 또는 다운로드</strong>
                <p><strong>"클립보드 복사"</strong>로 즉시 붙여넣기 하거나, <strong>"파일 다운로드"</strong>로 .txt 파일을 저장합니다.</p>
              </div>
            </div>
          </div>
        </div>

        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">article</span>
            출력 포맷
          </div>
          <ul class="feature-list">
            <li>주차가 최신순으로 출력되며, 각 주차는 <code class="md-syntax">[N주차 파트명 이슈사항]</code> 헤더로 시작합니다</li>
            <li>각 과제는 <code class="md-syntax">□ 과제명</code>으로 표시되며, 해당 주차에 등록된 이슈 내용이 들여쓰기 형식으로 이어집니다</li>
            <li>이슈 내용의 1단계 목록은 <code class="md-syntax">  - </code>, 2단계 목록은 <code class="md-syntax">    ‧ </code>으로 자동 변환됩니다</li>
            <li>컨플루언스 링크가 등록된 경우 <code class="md-syntax">  - 링크 : URL</code> 형식으로 각 과제 블록 아래에 추가됩니다</li>
            <li>같은 과제의 여러 이슈는 하나의 <code class="md-syntax">□</code> 블록으로 합쳐집니다</li>
          </ul>

          <div class="callout callout-info" style="margin-top:12px">
            <span class="material-symbols-outlined callout-icon">info</span>
            <div>보고서 내용은 주간 진행 현황에 등록된 <strong>이슈 항목</strong>과 <strong>컨플루언스 링크</strong>를 기반으로 생성됩니다. 과제 댓글 내용은 포함되지 않습니다.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ⑥ 피드백 -->
    <section id="feedback" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">rate_review</span>
          <h3 class="section-title">피드백</h3>
        </div>
        <p class="section-desc">시스템 개선 의견·건의사항을 카테고리별로 자유롭게 작성하고 공유하는 공간입니다. 왼쪽 사이드바의 <strong>피드백</strong> 메뉴에서 접근할 수 있습니다.</p>

        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">add_circle</span>
            피드백 작성
          </div>
          <ul class="feature-list">
            <li>우측 상단의 <strong>"+ 새 피드백"</strong> 버튼을 클릭하면 작성 모달이 열립니다</li>
            <li><strong>카테고리</strong>를 선택하고 <strong>제목</strong>과 <strong>내용</strong>을 입력합니다 — 내용은 WYSIWYG 에디터를 사용합니다</li>
            <li>작성자는 로그인 계정으로 자동 기록됩니다</li>
          </ul>
        </div>

        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">filter_list</span>
            목록 조회 및 필터
          </div>
          <ul class="feature-list">
            <li>등록된 피드백은 카드 형태로 목록에 표시됩니다 — 카테고리 배지, 제목, 작성자, 날짜가 함께 표시됩니다</li>
            <li>상단 카테고리 탭을 클릭하면 해당 카테고리의 피드백만 필터링됩니다</li>
            <li>본인이 작성한 피드백은 <strong>수정·삭제</strong>가 가능합니다</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- ⑦ 에디터 사용법 -->
    <section id="markdown" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">edit_note</span>
          <h3 class="section-title">에디터 사용법</h3>
        </div>
        <p class="section-desc">이슈·과제 댓글·피드백 작성에 WYSIWYG 에디터를 사용합니다. 툴바 버튼으로 서식을 적용하거나, 마크다운 단축키(<code class="md-syntax">**굵게**</code>, <code class="md-syntax"># 제목</code> 등)를 직접 입력해도 자동으로 변환됩니다.</p>

        <!-- 툴바 기능 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">toolbar</span>
            툴바 기능
          </div>
          <div class="md-table">
            <div class="md-row md-header">
              <span>버튼</span>
              <span>기능</span>
            </div>
            <div v-for="item in toolbarGuide" :key="item.name" class="md-row">
              <span style="display:flex;align-items:center;gap:6px">
                <span class="material-symbols-outlined" style="font-size:15px;color:var(--text-secondary)">{{ item.icon }}</span>
                <strong style="font-size:12px">{{ item.name }}</strong>
              </span>
              <span class="md-result" style="font-size:12px;color:var(--text-secondary)">{{ item.desc }}</span>
            </div>
          </div>
          <div class="callout callout-tip" style="margin-top:12px">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>단축키도 사용할 수 있습니다 — <strong>Ctrl+B</strong> 굵게 / <strong>Ctrl+I</strong> 기울임 / <strong>Ctrl+U</strong> 밑줄 / <strong>Ctrl+Z</strong> 실행취소</div>
          </div>
        </div>

        <!-- 이미지 삽입 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">image</span>
            이미지 삽입
          </div>
          <ul class="feature-list">
            <li>클립보드 이미지를 에디터에 <strong>Ctrl+V</strong>로 바로 붙여넣기 할 수 있습니다 — 스크린샷 캡처 후 즉시 붙여넣기 가능</li>
            <li>이미지가 업로드되면 에디터 안에 <strong>즉시 삽입</strong>되고, 이미지 바로 아래에 <strong>크기·테두리 조절 바</strong>가 나타납니다</li>
            <li>크기 조절 바에서 원하는 크기를 선택합니다:
              <ul style="margin-top:4px;display:flex;flex-direction:column;gap:3px">
                <li><strong>S</strong> — 300px 너비</li>
                <li><strong>M</strong> — 500px 너비</li>
                <li><strong>L</strong> — 700px 너비</li>
                <li><strong>원본</strong> — 이미지 원래 크기 그대로</li>
                <li><strong>px 직접 입력</strong> — 숫자 입력 후 <em>적용</em> 버튼 클릭</li>
              </ul>
            </li>
            <li><strong>테두리</strong> 버튼을 클릭하면 이미지에 회색 실선 테두리가 추가됩니다. 다시 클릭하면 테두리가 제거됩니다 — 저장 후 미리보기에서도 동일하게 표시됩니다</li>
            <li>이미지 바깥을 클릭하면 조절 바가 사라집니다. 이미지를 다시 클릭하면 조절 바가 다시 표시됩니다</li>
            <li>툴바의 <span class="material-symbols-outlined" style="font-size:13px;vertical-align:middle">image</span> <strong>이미지 버튼</strong>을 클릭해 파일 선택으로도 업로드할 수 있습니다</li>
          </ul>
          <div class="callout callout-info">
            <span class="material-symbols-outlined callout-icon">info</span>
            <div>이미지를 붙여넣고 <strong>저장하지 않은 채 취소</strong>하면 업로드된 이미지 파일은 서버에서 자동으로 삭제됩니다.</div>
          </div>
        </div>

        <!-- 전체화면 편집 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">open_in_full</span>
            크게 보기 (전체화면 편집)
          </div>
          <ul class="feature-list">
            <li>에디터 툴바 맨 왼쪽의 <span class="material-symbols-outlined" style="font-size:13px;vertical-align:middle">open_in_full</span> 버튼을 클릭하면 <strong>전체화면 편집 모달</strong>이 열립니다</li>
            <li>모달에서 작성한 내용은 <strong>원본 에디터와 실시간으로 동기화</strong>됩니다</li>
            <li><strong>닫기</strong> — 모달에서 작성한 내용을 그대로 유지하고 모달을 닫습니다</li>
            <li><strong>취소</strong> — 모달을 열기 전 원래 내용으로 되돌리고 모달을 닫습니다</li>
            <li>이미지 붙여넣기와 크기 조절도 전체화면 모달 안에서 동일하게 작동합니다</li>
          </ul>
          <div class="callout callout-tip">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>전체화면 모달에서 <strong>취소</strong>를 누르면 모달을 열기 전 상태로 완전히 복원됩니다. 작성 내용을 반영하려면 <strong>닫기</strong>를 눌러야 합니다.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ⑦ 관리 도구 -->
    <section id="admin" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">settings</span>
          <h3 class="section-title">관리 도구</h3>
        </div>
        <p class="section-desc">목표·과제·인력 데이터를 등록하고 관리하는 화면입니다. <strong>목표 · 과제 · 인력 · 설정</strong> 4개 탭으로 구성되며, 관리자에게는 <strong>사용자 관리</strong> 탭이 추가로 표시됩니다.</p>

        <!-- 목표 탭 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">bar_chart</span>
            목표(Objective) 탭
          </div>
          <ul class="feature-list">
            <li>목표(Objective)와 각 목표에 딸린 <strong>Key Result(핵심 결과)</strong>를 등록·수정·삭제합니다</li>
            <li>목표 카드에서 <strong>참여 인력</strong>을 확인할 수 있습니다 — 해당 목표의 과제를 담당하는 파트원이 자동으로 표시됩니다</li>
            <li>목록은 <strong>ID 오름차순</strong>으로 자동 정렬됩니다</li>
            <li>상단의 <strong>이름 칩</strong>을 클릭하면 해당 파트원이 참여한 목표만 필터링됩니다</li>
          </ul>
          <div class="callout callout-warning">
            <span class="material-symbols-outlined callout-icon">info</span>
            <div>목표를 삭제하면 연결된 과제의 목표 연결이 자동으로 해제됩니다. 과제 자체나 파트원 데이터는 삭제되지 않습니다.</div>
          </div>
        </div>

        <!-- 과제 탭 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--warning)">assignment</span>
            과제(Task) 탭
          </div>
          <ul class="feature-list">
            <li>과제를 등록하고 목표와 연결합니다</li>
            <li>과제 등록 시 <strong>적용 대상</strong>을 지정할 수 있습니다 — MX / VD / DA / 공통 등 설정에서 관리되는 항목 중 선택</li>
            <li>목록은 <strong>ID 오름차순</strong>으로 자동 정렬됩니다</li>
            <li>상단의 <strong>이름 칩</strong>을 클릭하면 해당 파트원이 담당한 과제만 필터링됩니다</li>
            <li>행 앞의 <strong>체크박스</strong>로 여러 과제를 선택하면 상단에 일괄 적용 툴바가 나타납니다 — 적용 대상을 한 번에 설정할 수 있습니다</li>
            <li>과제의 <strong>연결 목표를 변경</strong>하면, 해당 과제 담당 파트원의 참여 목표(OKR) 정보가 자동으로 업데이트됩니다 — 기존 목표 연결이 끊기고 새 목표가 자동으로 연결됩니다</li>
            <li>과제를 삭제하면 파트원의 담당 과제 목록에서도 자동으로 제거됩니다</li>
            <li>삭제된 과제와 연결된 주간 진행 현황 이력은 과제명이 텍스트로 보존됩니다</li>
          </ul>
          <div class="callout callout-tip">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>헤더의 체크박스를 클릭하면 현재 표시된 과제를 <strong>전체 선택/해제</strong>할 수 있습니다. 인력 필터와 함께 사용하면 특정 파트원의 과제만 선택해 일괄 적용할 수 있습니다.</div>
          </div>

          <div class="sub-section-title" style="margin-top:18px">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">account_tree</span>
            소과제(Sub-task) 관리
          </div>
          <ul class="feature-list">
            <li>과제 수정 모달에서 <strong>"소과제 추가"</strong> 버튼으로 소과제를 등록합니다. 소과제 ID는 <code class="md-syntax">T1-1</code>, <code class="md-syntax">T1-2</code> 형식으로 자동 부여됩니다</li>
            <li>각 소과제에 <strong>이름</strong>을 입력할 수 있으며, 소과제별로 완료 여부를 체크할 수 있습니다</li>
            <li>소과제가 있는 과제는 테이블에서 <strong>모과제 행 아래에 들여쓰기 서브 행</strong>으로 표시됩니다 — <code class="md-syntax">└ T1-1</code> 형식으로 ID, 소과제명, 담당자, 완료 상태를 한눈에 확인할 수 있습니다</li>
            <li>소과제 ID를 파트원의 <strong>담당 과제</strong>로 선택하면 소과제별 담당자를 지정할 수 있습니다</li>
            <li>모과제를 삭제하면 소과제 ID도 파트원 담당 목록에서 자동 제거됩니다</li>
          </ul>
          <div class="callout callout-info">
            <span class="material-symbols-outlined callout-icon">lightbulb</span>
            <div>소과제가 있는 과제는 <strong>주간 진행 현황</strong>에서 모과제 카드 안에 소과제별 섹션이 펼쳐집니다. 이슈·의견/질문·컨플루언스 링크가 소과제 단위로 독립 관리됩니다.</div>
          </div>
        </div>

        <!-- ID 정책 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px">tag</span>
            ID 부여 방식
          </div>
          <ul class="feature-list">
            <li>목표는 <strong>O1, O2, O3…</strong>, 과제는 <strong>T1, T2, T3…</strong> 형식으로 순차 자동 부여됩니다</li>
            <li>항목을 삭제해도 카운터는 유지됩니다 — 예: O1·O2·O3이 있을 때 O2를 삭제하면 다음 생성 ID는 O4입니다</li>
            <li>삭제로 생긴 빈 번호(O2)는 <strong>재사용 가능한 ID</strong>로 추가 창에 표시됩니다. 클릭하면 해당 ID를 선택할 수 있습니다</li>
          </ul>
          <div class="callout callout-tip">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>ID는 직접 입력도 가능합니다. 이미 사용 중인 ID를 입력하면 중복 경고가 표시됩니다.</div>
          </div>
        </div>

        <!-- 인력 탭 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:#6b7280">group</span>
            인력(Staff) 탭
          </div>
          <ul class="feature-list">
            <li>파트원 정보(이름·역할·기술·담당 과제)를 등록하고 수정합니다</li>
            <li>상단의 <strong>이름 칩</strong>을 클릭하면 해당 파트원만 필터링됩니다. 여러 명을 동시에 선택할 수 있습니다</li>
            <li>필터를 초기화하려면 <strong>"전체 보기"</strong> 버튼을 클릭합니다</li>
            <li>목록은 <strong>이름 가나다순</strong>으로 자동 정렬됩니다</li>
            <li>상단의 <strong>CSV 다운로드</strong> 버튼으로 파트원 목록을 파일로 내보낼 수 있습니다</li>
          </ul>
          <div class="callout callout-info">
            <span class="material-symbols-outlined callout-icon">lightbulb</span>
            <div>인력 추가 시 과제를 목표별로 그룹핑해서 선택할 수 있습니다. 목표에 연결되지 않은 과제는 <strong>"목표 없음"</strong> 그룹에 표시됩니다. 과제를 선택하면 연결된 목표가 자동으로 설정됩니다.</div>
          </div>
          <div class="callout callout-warning">
            <span class="material-symbols-outlined callout-icon">info</span>
            <div>계정 삭제는 <strong>사용자 관리</strong> 탭에서 처리합니다. 인력 탭은 파트원 프로필 정보 관리 전용입니다.</div>
          </div>
        </div>

        <!-- 사용자 관리 탭 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">manage_accounts</span>
            사용자 관리 탭 <span style="font-size:11px;font-weight:400;color:var(--text-muted);margin-left:4px">(관리자 전용)</span>
          </div>
          <ul class="feature-list">
            <li>로그인 계정 목록을 조회하고 <strong>역할</strong>과 <strong>관리자 권한</strong>을 변경할 수 있습니다</li>
            <li><strong>비밀번호 초기화</strong>: 임시 비밀번호가 자동 생성되며, 해당 계정은 다음 로그인 시 비밀번호 변경이 강제됩니다</li>
            <li><strong>계정 삭제</strong>: 해당 사용자의 로그인 계정을 영구 삭제합니다 — 삭제해도 이슈·질문 등 작성 이력은 유지됩니다</li>
          </ul>
          <div class="callout callout-warning">
            <span class="material-symbols-outlined callout-icon">info</span>
            <div>계정 삭제는 복구되지 않습니다. 파트원 프로필(이름·담당 과제 등)을 유지하면서 로그인만 막으려면 삭제 대신 역할을 변경하거나 비밀번호를 초기화하세요.</div>
          </div>
        </div>

        <!-- 설정 탭 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px">tune</span>
            설정 탭
          </div>
          <ul class="feature-list">
            <li><strong>과제 적용 대상 관리</strong>: 기존 항목을 삭제하거나 새 항목을 추가할 수 있으며, 변경 내용은 과제 등록·수정 모달에 즉시 반영됩니다</li>
            <li><strong>데이터 초기화</strong> (관리자 전용): 목표·과제·인력·진행도 데이터를 전체 삭제할 수 있습니다 — 복구 불가이므로 주의</li>
          </ul>
          <div class="callout callout-warning">
            <span class="material-symbols-outlined callout-icon">info</span>
            <div>적용 대상 항목을 삭제해도 이미 해당 대상으로 지정된 과제는 영향을 받지 않습니다. 이후 등록·수정 시에만 목록에서 사라집니다.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section id="faq" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">help</span>
          <h3 class="section-title">자주 묻는 질문</h3>
        </div>
        <div v-for="faq in faqs" :key="faq.q" class="faq-item" @click="faq.open = !faq.open">
          <div class="faq-question">
            <span class="material-symbols-outlined faq-q-icon">quiz</span>
            <span>{{ faq.q }}</span>
            <span class="material-symbols-outlined faq-chevron" :class="{ open: faq.open }">expand_more</span>
          </div>
          <div v-if="faq.open" class="faq-answer">{{ faq.a }}</div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { reactive } from 'vue'

const toc = [
  { id: 'overview',  icon: 'info',           title: '시스템 소개' },
  { id: 'account',   icon: 'account_circle',  title: '계정 및 로그인' },
  { id: 'notify',    icon: 'notifications',   title: '알림' },
  { id: 'dashboard', icon: 'dashboard',       title: '대시보드' },
  { id: 'progress',  icon: 'assignment',      title: '주간 진행 현황' },
  { id: 'history',       icon: 'history',         title: '과제 이력' },
  { id: 'issue-history', icon: 'manage_search',   title: '이슈 히스토리' },
  { id: 'export',        icon: 'summarize',       title: '보고서 내보내기' },
  { id: 'feedback',      icon: 'rate_review',     title: '피드백' },
  { id: 'markdown',  icon: 'edit_note',       title: '에디터 사용법' },
  { id: 'admin',     icon: 'settings',        title: '관리 도구' },
  { id: 'faq',       icon: 'help',            title: 'FAQ' },
]

const toolbarGuide = [
  { icon: 'format_bold',        name: '굵게',       desc: '선택한 텍스트를 굵게 표시 (Ctrl+B)' },
  { icon: 'format_italic',      name: '기울임',     desc: '선택한 텍스트를 기울여 표시 (Ctrl+I)' },
  { icon: 'format_underlined',  name: '밑줄',       desc: '선택한 텍스트에 밑줄 추가 (Ctrl+U)' },
  { icon: 'strikethrough_s',    name: '취소선',     desc: '선택한 텍스트에 취소선 추가' },
  { icon: 'code',               name: '인라인 코드', desc: '선택한 텍스트를 코드 스타일로 표시' },
  { icon: 'subscript',          name: '아래 첨자',  desc: '선택한 텍스트를 아래 첨자로 표시 (H₂O 등)' },
  { icon: 'superscript',        name: '위 첨자',    desc: '선택한 텍스트를 위 첨자로 표시 (x² 등)' },
  { icon: 'ink_highlighter',    name: '형광펜',     desc: '선택한 텍스트에 노란 형광펜 효과 적용' },
  { icon: 'format_color_text',  name: '글자색',     desc: '선택한 텍스트의 색상 변경 — 색상 클릭으로 피커 열기' },
  { icon: 'title',              name: '제목 H1~H6', desc: 'H1(가장 큼)~H6(가장 작음) 중 원하는 크기 선택' },
  { icon: 'format_align_left',  name: '정렬',       desc: '왼쪽 / 가운데 / 오른쪽 / 양쪽 정렬 선택' },
  { icon: 'format_list_bulleted', name: '글머리 목록', desc: '• 기호 목록 생성 (마크다운: - 또는 *)' },
  { icon: 'format_list_numbered', name: '번호 목록', desc: '1. 2. 3. 번호 목록 생성 (마크다운: 1.)' },
  { icon: 'checklist',          name: '체크박스 목록', desc: '체크 가능한 할 일 목록 생성' },
  { icon: 'format_quote',       name: '인용문',     desc: '블록 인용문 형식 적용 (마크다운: >)' },
  { icon: 'data_object',        name: '코드 블록',  desc: '여러 줄 코드를 코드 블록으로 표시' },
  { icon: 'horizontal_rule',    name: '구분선',     desc: '가로 구분선(---) 삽입' },
  { icon: 'table_chart',        name: '표',         desc: '3×3 표 삽입 — 삽입 후 열·행 추가/삭제 가능' },
  { icon: 'link',               name: '링크',       desc: '선택한 텍스트에 URL 링크 연결' },
  { icon: 'image',              name: '이미지',     desc: '파일 선택으로 이미지 업로드 (Ctrl+V 붙여넣기도 가능)' },
  { icon: 'undo',               name: '실행취소',   desc: '마지막 작업 취소 (Ctrl+Z)' },
  { icon: 'redo',               name: '다시실행',   desc: '취소한 작업 다시 실행 (Ctrl+Y)' },
  { icon: 'format_clear',       name: '서식 초기화', desc: '선택한 텍스트의 모든 서식(굵기·색상·정렬 등) 제거' },
]

const faqs = reactive([
  {
    q: '비밀번호를 잊어버렸을 때는?',
    a: '관리자에게 문의하면 임시 비밀번호로 초기화해 드립니다. 임시 비밀번호로 로그인하면 즉시 새 비밀번호 설정 화면으로 이동합니다.',
    open: false,
  },
  {
    q: '처음 로그인 시 비밀번호 변경 화면으로 이동하는 이유는?',
    a: '관리자가 생성한 계정은 모두 임시 비밀번호가 설정되어 있으며, 첫 로그인 시 본인만 아는 비밀번호로 변경하도록 강제됩니다. 새 비밀번호를 설정하면 정상 이용이 가능합니다.',
    open: false,
  },
  {
    q: '"답변 요구" 체크박스가 보이지 않는 이유는?',
    a: '답변 요구 지정은 그룹장·파트장·관리자만 사용할 수 있습니다. 일반 파트원도 댓글 작성은 가능하지만 답변 요구 체크박스는 표시되지 않습니다. 역할 변경이 필요하면 관리자에게 문의하세요.',
    open: false,
  },
  {
    q: '답변 요구 댓글 태그 알림이 삭제되지 않는 이유는?',
    a: '답변 요구 댓글의 태그 알림은 해당 댓글에 대댓글(답변)이 달려 자동으로 "답변됨" 처리되기 전까지 보호됩니다. 담당자가 답변 요구를 놓치지 않도록 하기 위한 규칙입니다. 답변이 작성되어 "답변됨" 처리되면 알림을 삭제할 수 있습니다.',
    open: false,
  },
  {
    q: '이슈 링크를 메신저로 공유하려면?',
    a: '이슈 우측의 링크(🔗) 버튼을 클릭하면 단축 링크가 클립보드에 복사됩니다. 메신저에 붙여넣어 공유하면 받는 사람이 클릭 시 해당 주차·해당 위치로 바로 이동합니다. 링크 형식은 "http://서버주소/go/{ID}" 형태입니다.',
    open: false,
  },
  {
    q: '이슈 내용은 어떤 형식으로 작성하나요?',
    a: 'WYSIWYG 에디터를 사용합니다. 툴바 버튼으로 굵게·기울임·제목·정렬·형광펜·글자색·목록·표 등 다양한 서식을 적용할 수 있습니다. 마크다운 단축키(**굵게**, # 제목, - 목록 등)를 직접 입력하면 자동으로 변환됩니다.',
    open: false,
  },
  {
    q: '주차(W#)는 어떻게 계산되나요?',
    a: '연도 기준 주차를 사용합니다. 날짜 범위(예: 5/12 – 5/18)와 주차 번호(예: 2026년 W21)가 함께 표시됩니다. 연도가 달라지면 자동으로 연도가 함께 표시되어 혼동 없이 이전 연도 데이터를 구분할 수 있습니다.',
    open: false,
  },
  {
    q: '지난주 / 이번주 패널을 다시 2분할로 복원하려면?',
    a: '접힌 패널의 헤더 바(또는 접기 버튼)를 다시 클릭하면 2분할 상태로 복원됩니다. 접기 버튼이 토글 방식으로 작동하므로, 같은 버튼으로 접기와 펼치기를 반복할 수 있습니다.',
    open: false,
  },
  {
    q: '과제 이력은 어디서 볼 수 있나요?',
    a: '주간 진행 현황의 과제 카드 상단 우측에 있는 "이력" 버튼(시계 아이콘)을 클릭하면 해당 과제의 전체 주차별 이력 페이지로 이동합니다. 이력 페이지에서 이슈 카드를 클릭하면 해당 주차의 주간 진행 현황으로 바로 이동합니다.',
    open: false,
  },
  {
    q: '이슈를 삭제하면 복구되나요?',
    a: '삭제된 이슈는 직접 복구되지 않습니다. 다만 이슈 삭제 시 내용과 댓글이 스냅샷으로 저장되어, 그룹장·파트장·관리자는 사이드바의 "이슈 히스토리" 메뉴에서 삭제된 이슈 내용을 확인할 수 있습니다. 과제 댓글 삭제는 복구 및 히스토리 기록이 없으므로 주의하세요.',
    open: false,
  },
  {
    q: '컨플루언스 링크는 누가 입력하나요?',
    a: '주간 진행 현황 페이지에서 해당 과제의 컨플루언스 섹션에 직접 입력할 수 있습니다. 또는 관리 도구에서 관리자가 설정할 수도 있습니다.',
    open: false,
  },
  {
    q: '파트원 정보나 목표가 잘못 표시되면?',
    a: '관리 도구 메뉴에서 파트원, 목표(Objective), 핵심결과(KR), 과제 정보를 수정할 수 있습니다. 권한이 없다면 관리자에게 문의하세요.',
    open: false,
  },
  {
    q: '목표 O2를 삭제한 뒤 새로 만들면 ID가 O4가 되나요?',
    a: '네. ID 카운터는 삭제해도 초기화되지 않습니다. 다음 생성 ID는 기존 최댓값 +1입니다. 다만 삭제로 생긴 빈 번호(O2·O3)는 추가 화면에 재사용 가능 ID로 표시되므로 필요하면 선택해 재사용할 수 있습니다.',
    open: false,
  },
  {
    q: '목표를 삭제하면 연결된 과제와 인력 데이터도 사라지나요?',
    a: '과제와 파트원 데이터는 삭제되지 않습니다. 목표 삭제 시 과제의 목표 연결만 해제됩니다. 과제를 삭제할 경우에는 파트원의 담당 과제 목록에서 자동으로 제거되고, 기존 이슈 이력에는 과제명이 텍스트로 보존됩니다.',
    open: false,
  },
  {
    q: '소과제란 무엇이고 어떻게 추가하나요?',
    a: '소과제는 하나의 과제를 세부 작업 단위로 나눈 것입니다. 관리 도구 → 과제 탭에서 수정 모달을 열면 하단에 "소과제 추가" 버튼이 표시됩니다. 소과제 ID는 T1-1, T1-2 형식으로 자동 부여되며, 각 소과제를 파트원의 담당 과제로 지정할 수 있습니다. 주간 진행 현황에서는 소과제별 이슈와 댓글을 독립적으로 관리할 수 있습니다.',
    open: false,
  },
  {
    q: '여러 과제의 적용 대상을 한 번에 바꾸려면?',
    a: '과제 탭에서 행 앞의 체크박스로 과제를 선택하면 상단에 일괄 적용 툴바가 나타납니다. 적용 대상을 선택하고 "일괄 적용" 버튼을 클릭하면 선택된 과제 전체에 동시 적용됩니다. 인력 필터와 함께 사용하면 특정 파트원의 과제만 추려 일괄 적용할 수 있습니다.',
    open: false,
  },
])
</script>

<style scoped>
.page-header { margin-bottom: 24px; }
.page-title { font-size: var(--fs-h1); font-weight: var(--fw-bold); color: var(--text-primary); margin: 0 0 4px; }
.page-subtitle { font-size: var(--fs-sm); color: var(--text-muted); margin: 0; }

/* 목차 */
.toc-card { margin-bottom: 24px; }
.toc-label { font-size: var(--fs-2xs); font-weight: var(--fw-semibold); color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; }
.toc-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.toc-item {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  background: var(--gray-50);
  color: var(--text-secondary);
  font-size: var(--fs-sm); font-weight: var(--fw-medium);
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.toc-item:hover { background: var(--primary-light); color: var(--primary); }
.toc-icon { font-size: var(--fs-base); width: 15px; height: 15px; }

/* 섹션 */
.help-section { margin-bottom: 20px; scroll-margin-top: 24px; }
.section-heading {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 14px; padding-bottom: 14px;
  border-bottom: 1px solid var(--outline);
}
.section-icon-lg {
  font-size: var(--fs-h1); width: 20px; height: 20px;
  color: var(--primary);
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
.section-title { font-size: var(--fs-h3); font-weight: var(--fw-bold); color: var(--text-primary); margin: 0; }
.section-desc { font-size: var(--fs-sm); color: var(--text-secondary); line-height: 1.75; margin-bottom: 18px; }

/* Callout 박스 */
.callout {
  display: flex; gap: 10px; align-items: flex-start;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  font-size: var(--fs-sm); line-height: 1.65;
  margin: 14px 0;
}
.callout-icon {
  font-size: 17px; width: 17px; height: 17px;
  flex-shrink: 0; margin-top: 1px;
}
.callout-info { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.callout-info .callout-icon { color: #2563eb; }
.callout-tip  { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.callout-tip .callout-icon { color: var(--success); }
.callout-warning { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
.callout-warning .callout-icon { color: var(--warning); }

/* 메뉴 카드 3종 */
.menu-cards { display: flex; flex-direction: column; gap: 8px; margin-top: 16px; }
.menu-card {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 12px 14px;
  background: var(--gray-50);
  border-radius: var(--radius-md);
  border: 1px solid var(--outline);
}
.menu-card-icon {
  font-size: var(--fs-h1); width: 20px; height: 20px; flex-shrink: 0; margin-top: 1px;
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
.icon-blue { color: var(--primary); }
.icon-orange { color: var(--warning); }
.icon-gray { color: var(--text-muted); }
.icon-purple { color: #7c3aed; }
.icon-teal { color: #0d9488; }
.menu-card-title { font-size: var(--fs-sm); font-weight: var(--fw-semibold); color: var(--text-primary); margin-bottom: 2px; }
.menu-card-desc { font-size: var(--fs-xs); color: var(--text-muted); line-height: 1.6; }

/* 기능 블록 */
.feature-block { margin-bottom: 18px; }
.feature-label {
  display: flex; align-items: center; gap: 8px;
  font-size: var(--fs-sm); font-weight: var(--fw-semibold); color: var(--text-primary);
  margin-bottom: 8px;
}
.badge-num {
  width: 20px; height: 20px;
  background: var(--primary); color: white;
  border-radius: 50%;
  font-size: var(--fs-2xs); font-weight: var(--fw-bold);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.feature-list {
  margin: 0; padding-left: 18px;
  display: flex; flex-direction: column; gap: 6px;
}
.feature-list li { font-size: var(--fs-sm); color: var(--text-secondary); line-height: 1.7; }

/* 서브 섹션 */
.sub-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--outline);
}
.sub-section:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.sub-section-title {
  display: flex; align-items: center; gap: 6px;
  font-size: var(--fs-sm); font-weight: var(--fw-semibold); color: var(--text-primary);
  margin-bottom: 10px;
}

/* 강조 */
.highlight-red { color: var(--danger); font-weight: var(--fw-medium); }
.inline-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 20px; height: 20px; border-radius: var(--radius-sm);
  font-size: var(--fs-2xs); font-weight: var(--fw-bold);
}
.badge-green { background: var(--success-light); color: var(--success); }

/* 단계별 */
.steps { display: flex; flex-direction: column; gap: 2px; margin: 14px 0; }
.step { display: flex; align-items: flex-start; gap: 12px; padding: 10px 0; }
.step + .step { border-top: 1px solid var(--outline); }
.step-number {
  width: 24px; height: 24px; border-radius: 50%;
  background: var(--primary); color: white;
  font-size: var(--fs-xs); font-weight: var(--fw-bold);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 1px;
}
.step-body { flex: 1; }
.step-body strong { font-size: var(--fs-sm); color: var(--text-primary); }
.step-body p { margin: 3px 0 0; font-size: var(--fs-xs); color: var(--text-secondary); line-height: 1.65; }

/* 마크다운 가이드 테이블 */
.md-table { border: 1px solid var(--outline); border-radius: var(--radius-md); overflow: hidden; }
.md-row {
  display: grid; grid-template-columns: 1fr 1fr;
  padding: 9px 14px; font-size: var(--fs-xs);
  border-bottom: 1px solid var(--outline);
}
.md-row:last-child { border-bottom: none; }
.md-header { background: var(--gray-50); font-weight: var(--fw-semibold); color: var(--text-muted); font-size: var(--fs-2xs); text-transform: uppercase; letter-spacing: 0.05em; }
.md-syntax { font-family: monospace; background: var(--gray-100); padding: 2px 6px; border-radius: 3px; font-size: var(--fs-xs); color: var(--text-primary); }
.md-result { color: var(--text-secondary); display: flex; align-items: center; }

/* FAQ */
.faq-item {
  border-bottom: 1px solid var(--outline);
  cursor: pointer;
}
.faq-item:last-child { border-bottom: none; }
.faq-question {
  display: flex; align-items: center; gap: 8px;
  padding: 13px 4px;
  font-size: var(--fs-sm); font-weight: var(--fw-medium); color: var(--text-primary);
  user-select: none;
}
.faq-question:hover { color: var(--primary); }
.faq-q-icon { font-size: var(--fs-h3); width: 16px; height: 16px; color: var(--primary); flex-shrink: 0; }
.faq-chevron {
  font-size: var(--fs-h2); width: 18px; height: 18px;
  color: var(--text-muted); margin-left: auto;
  transition: transform 0.2s; flex-shrink: 0;
}
.faq-chevron.open { transform: rotate(180deg); }
.faq-answer {
  padding: 0 4px 14px 28px;
  font-size: var(--fs-sm); color: var(--text-secondary); line-height: 1.75;
}

/* 역할 테이블 */
.role-table { border: 1px solid var(--outline); border-radius: var(--radius-md); overflow: hidden; }
.role-row {
  display: grid; grid-template-columns: 120px 1fr 1fr;
  padding: 9px 14px; font-size: var(--fs-xs);
  border-bottom: 1px solid var(--outline);
  align-items: center;
}
.role-row:last-child { border-bottom: none; }
.role-header { background: var(--gray-50); font-weight: var(--fw-semibold); color: var(--text-muted); font-size: var(--fs-2xs); text-transform: uppercase; letter-spacing: 0.05em; }
.role-badge {
  display: inline-flex; align-items: center;
  padding: 2px 8px; border-radius: 10px;
  font-size: var(--fs-2xs); font-weight: var(--fw-semibold);
}
.role-member { background: #f1f5f9; color: #475569; }
.role-leader { background: #eff6ff; color: #2563eb; }
.role-admin  { background: var(--warning-light); color: #92400e; }

/* 알림 테이블 */
.notify-table { border: 1px solid var(--outline); border-radius: var(--radius-md); overflow: hidden; }
.notify-row {
  display: grid; grid-template-columns: 140px 1fr;
  padding: 9px 14px; font-size: var(--fs-xs);
  border-bottom: 1px solid var(--outline);
  align-items: center; gap: 8px;
}
.notify-row:last-child { border-bottom: none; }
.notify-header { background: var(--gray-50); font-weight: var(--fw-semibold); color: var(--text-muted); font-size: var(--fs-2xs); text-transform: uppercase; letter-spacing: 0.05em; }

/* === 미니 UI 미리보기 공통 === */
.mini-ui-preview {
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: var(--radius-md);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.mini-preview-label {
  font-size: 10px;
  font-weight: var(--fw-semibold);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.07em;
  margin-bottom: 2px;
}

/* 미니 알림 항목 */
.mini-notify-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  background: white;
  border-radius: var(--radius-sm);
  border: 1px solid var(--outline);
}
.mini-notify-item.mini-read { opacity: 0.55; }
.mini-unread-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--primary);
  flex-shrink: 0;
}
.mini-unread-dot.mini-dot-read { background: transparent; }
.mini-notify-text {
  flex: 1;
  font-size: var(--fs-xs);
  color: var(--text-secondary);
  line-height: 1.45;
}
.mini-unread-badge {
  width: 16px; height: 16px;
  border-radius: 50%;
  background: var(--danger);
  color: white;
  font-size: 9px;
  font-weight: var(--fw-bold);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

/* 미니 댓글 카드 */
.mini-comment-card {
  background: white;
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.mini-comment-card.mini-indent {
  margin-left: 22px;
  border-left: 2px solid var(--primary-light);
}
.mini-cc-header { display: flex; align-items: center; gap: 6px; }
.mini-avatar {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: var(--primary-light);
  color: var(--primary);
  font-size: 10px;
  font-weight: var(--fw-bold);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.mini-avatar.mini-avatar-green { background: var(--success-light); color: var(--success); }
.mini-author-name { font-size: var(--fs-xs); font-weight: var(--fw-semibold); color: var(--text-primary); }
.mini-badge-pending {
  font-size: 10px; font-weight: var(--fw-semibold);
  padding: 1px 7px; border-radius: 10px;
  background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa;
}
.mini-badge-answered {
  font-size: 10px; font-weight: var(--fw-semibold);
  padding: 1px 7px; border-radius: 10px;
  background: var(--success-light); color: var(--success); border: 1px solid #bbf7d0;
}
.mini-time { font-size: 10px; color: var(--text-muted); margin-left: auto; }
.mini-cc-body { font-size: var(--fs-xs); color: var(--text-secondary); line-height: 1.55; }
.mini-at-tag {
  display: inline;
  font-size: var(--fs-xs); font-weight: var(--fw-semibold);
  color: var(--primary); background: var(--primary-light);
  padding: 1px 5px; border-radius: 3px;
}
.mini-cc-actions { display: flex; gap: 6px; }
.mini-action-btn {
  font-size: var(--fs-2xs); color: var(--text-muted);
  padding: 2px 8px; border-radius: var(--radius-sm);
  border: 1px solid var(--outline); background: var(--gray-50);
  cursor: default;
}

/* 미니 댓글 입력 폼 */
.mini-form-preview {
  background: white;
  border: 1px solid var(--outline);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.mini-tag-row { display: flex; align-items: center; gap: 5px; flex-wrap: wrap; }
.mini-tag-label { font-size: 10px; color: var(--text-muted); margin-right: 2px; }
.mini-person-chip {
  font-size: 10px; padding: 2px 8px;
  border-radius: 12px; border: 1px solid var(--outline);
  background: var(--gray-50); color: var(--text-secondary); cursor: default;
}
.mini-person-chip.mini-chip-active {
  background: var(--primary-light); border-color: var(--primary);
  color: var(--primary); font-weight: var(--fw-semibold);
}
.mini-editor-placeholder {
  font-size: var(--fs-xs); color: var(--text-secondary);
  border: 1px solid var(--outline); border-radius: var(--radius-sm);
  padding: 7px 10px; background: white; min-height: 32px;
}
.mini-form-row { display: flex; align-items: center; gap: 8px; }
.mini-req-check {
  display: flex; align-items: center; gap: 3px;
  font-size: var(--fs-xs); color: var(--text-secondary); cursor: default;
}
.mini-submit-btn {
  font-size: var(--fs-xs); padding: 4px 14px;
  border-radius: var(--radius-sm);
  background: var(--primary); color: white;
  font-weight: var(--fw-medium); cursor: default;
}

/* 미니 소과제 항목 */
.mini-subtask-row {
  display: flex; align-items: center; gap: 7px;
  padding: 8px 10px;
  background: white; border-radius: var(--radius-sm);
  border: 1px solid var(--outline);
  border-left: 3px solid var(--primary-light);
}
.mini-subtask-row.mini-subtask-done { border-left-color: var(--success); opacity: 0.8; }
.mini-subtask-name { font-size: var(--fs-xs); font-weight: var(--fw-medium); color: var(--text-primary); }
.mini-subtask-name.mini-name-done { color: var(--text-muted); text-decoration: line-through; }
.mini-cnt-badge {
  font-size: 10px; font-weight: var(--fw-semibold);
  padding: 1px 6px; border-radius: 9px;
}
.mini-cnt-badge.mini-cnt-issue  { background: #fff7ed; color: #92400e; }
.mini-cnt-badge.mini-cnt-comment { background: #eff6ff; color: #1d4ed8; }
.mini-cnt-badge.mini-cnt-done   { background: var(--success-light); color: var(--success); }
.mini-person-tag {
  font-size: 10px; color: var(--text-muted);
  background: var(--gray-100); padding: 2px 7px; border-radius: 10px;
}
</style>
