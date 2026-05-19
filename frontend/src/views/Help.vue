<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">도움말</h2>
      <p class="page-subtitle">설비혁신파트 목표 관리 시스템 사용 가이드</p>
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
              <div class="menu-card-desc">주차별 이슈 등록 및 Q&A 관리 — 파트원들이 주로 사용하는 화면</div>
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

    <!-- ② 대시보드 -->
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
            상단 통계 카드 (4개)
          </div>
          <ul class="feature-list">
            <li><strong>미답변 Q&A</strong> — 전체 기간 중 아직 답변이 없는 질문 수. 주황색이면 확인 필요, 초록이면 양호</li>
            <li><strong>이번 주 이슈</strong> — 이번 주 등록된 이슈 수</li>
            <li><strong>미배정 과제</strong> — 담당자가 지정되지 않은 과제 수</li>
            <li><strong>컨플루언스 등록률</strong> — 이번 주 컨플루언스 링크를 등록한 과제 비율. 진행 바로 확인 가능</li>
          </ul>
        </div>

        <div class="feature-block">
          <div class="feature-label">
            <span class="badge-num">2</span>
            액션 패널 (3가지)
          </div>
          <ul class="feature-list">
            <li><strong>미답변 질문</strong> — 전체 기간 누적 미답변 목록. 항목에 <em>과제명 + 주차</em>가 표시되며, 클릭하면 해당 주차의 해당 Q&A 위치로 바로 이동합니다</li>
            <li><strong>이슈</strong> — 이번 주 등록된 이슈 목록. 클릭하면 해당 과제의 이슈 위치로 이동</li>
            <li><strong>미배정 과제</strong> — 담당자가 없는 과제 목록. 클릭하면 관리 도구 과제 탭으로 이동</li>
          </ul>
        </div>

        <div class="feature-block">
          <div class="feature-label">
            <span class="badge-num">3</span>
            파트원별 활동 현황
          </div>
          <ul class="feature-list">
            <li>각 파트원의 <strong>담당 과제 수 / 이슈 등록 수 / Q&A 답변 수</strong>를 막대 그래프로 비교</li>
            <li>가장 최근에 등록한 이슈도 함께 표시됩니다</li>
            <li>우측 상단에 <strong>파트원 N명</strong> 배지로 인원 수를 확인할 수 있습니다</li>
          </ul>
        </div>

        <div class="feature-block">
          <div class="feature-label">
            <span class="badge-num">4</span>
            주간 등록 현황 매트릭스
          </div>
          <ul class="feature-list">
            <li>과제(행) × 주차(열) 기준으로 <strong>컨플루언스 · 이슈 · Q&A</strong> 등록 여부를 한눈에 확인합니다</li>
            <li><span class="material-symbols-outlined" style="font-size:13px;vertical-align:middle;color:var(--primary)">link</span> <strong>링크 아이콘</strong>을 클릭하면 해당 컨플루언스 페이지가 바로 열립니다</li>
            <li>섹션 제목을 클릭하면 매트릭스를 접거나 펼칠 수 있습니다</li>
            <li>현재 주차 열은 파란색 배경으로 강조됩니다</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- ③ 주간 진행 현황 -->
    <section id="progress" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">assignment</span>
          <h3 class="section-title">주간 진행 현황</h3>
        </div>
        <p class="section-desc">파트원들이 매주 이슈를 등록하고, 서로 Q&A를 통해 소통하는 화면입니다.</p>

        <!-- 주차 선택 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px">calendar_month</span>
            주차 선택
          </div>
          <ul class="feature-list">
            <li>상단의 <strong>◀ ▶ 버튼</strong>으로 이전/다음 주차로 이동합니다</li>
            <li>날짜 범위(<em>예: 5/12 – 5/18</em>)와 주차 번호(<em>예: W20</em>)가 함께 표시됩니다</li>
            <li>현재 주차가 아닌 경우 <strong>"이번 주"</strong> 버튼이 나타납니다 — 클릭 시 현재 주로 이동</li>
          </ul>
          <div class="callout callout-tip">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>현재 주차는 파란색 테두리로 강조 표시됩니다. <strong>"이번 주"</strong> 배지가 날짜 옆에 표시되면 현재 주차입니다.</div>
          </div>
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
                <strong>등록자 선택 + 내용 작성</strong>
                <p>드롭다운에서 <strong>본인 이름을 반드시 선택</strong>하고, 이슈 내용을 작성합니다. 마크다운 형식을 지원합니다.</p>
              </div>
            </div>
            <div class="step">
              <div class="step-number">5</div>
              <div class="step-body">
                <strong>저장</strong>
                <p>등록자와 내용이 모두 입력되어야 저장 버튼이 활성화됩니다.</p>
              </div>
            </div>
          </div>

          <div class="callout callout-tip">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>과제당 이슈는 <strong>여러 건</strong> 등록할 수 있습니다. 등록된 이슈 목록 아래 <strong>"+ 이슈 등록"</strong> 버튼을 클릭해 이슈를 추가하세요.</div>
          </div>
        </div>

        <!-- Q&A -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px;color:var(--primary)">forum</span>
            Q&A 사용법
          </div>
          <ul class="feature-list">
            <li>과제 카드 하단 <strong>Q&A 섹션</strong>에서 <strong>"+ 질문 추가"</strong>를 클릭해 질문을 등록합니다</li>
            <li>답변이 없는 질문에는 <span class="inline-badge badge-green">A</span> 옆에 <strong>"답변 달기"</strong> 버튼이 표시됩니다</li>
            <li>답변 작성 시 <strong>작성자(본인 이름)를 반드시 선택</strong>해야 저장됩니다</li>
            <li>하나의 질문에 여러 명이 <strong>"+ 답변 추가"</strong>로 추가 답변을 달 수 있습니다</li>
            <li>질문 삭제 시 <span class="highlight-red">해당 질문의 모든 답변도 함께 삭제</span>됩니다 — 삭제 전 <strong>관리자 암호 입력</strong>이 필요합니다</li>
          </ul>
          <div class="callout callout-tip">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>대시보드의 <strong>미답변 질문 패널</strong>에서 항목을 클릭하면 해당 주차로 이동하며 Q&A 위치로 자동 스크롤됩니다. 소과제 질문이면 해당 소과제 카드가 자동으로 펼쳐집니다.</div>
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
            <li>각 소과제는 과제 카드 내부에 <strong>파란 왼쪽 테두리</strong>로 구분된 별도 섹션으로 표시되며, <strong>기본적으로 접힌 상태</strong>로 시작합니다</li>
            <li>소과제 헤더(상단 줄)를 <strong>클릭</strong>하면 내용이 펼쳐지거나 접힙니다. 헤더 우측의 완료 버튼·담당자 배지는 클릭해도 접히지 않습니다</li>
            <li>접힌 상태에서 이슈나 Q&A 내용이 있으면 헤더에 <strong>요약 배지</strong>가 표시됩니다 — <em>이슈 N건</em>, <em>Q&A N건</em></li>
            <li><strong>컨플루언스 링크</strong>는 소과제별로 독립 등록됩니다 — 소과제가 있으면 모과제 단위 링크 대신 각 소과제 섹션 내부에 링크 입력란이 표시됩니다</li>
            <li>이슈 등록과 Q&A도 <strong>소과제별로 독립적으로</strong> 관리됩니다</li>
            <li>소과제가 완료 처리되면 해당 섹션은 <strong>녹색 테두리</strong>로 바뀌고 흐릿하게 표시됩니다</li>
          </ul>
          <div class="callout callout-tip">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>모과제 헤더의 <strong>"전체 펼치기"</strong>를 누르면 해당 과제의 소과제를 한 번에 모두 펼칩니다. <strong>"전체 접기"</strong>로 다시 정리할 수 있습니다.</div>
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

    <!-- ④ 마크다운 -->
    <section id="markdown" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">edit_note</span>
          <h3 class="section-title">마크다운 작성법</h3>
        </div>
        <p class="section-desc">이슈 내용과 Q&A는 마크다운 형식을 지원합니다. 에디터 상단 툴바 버튼으로도 적용할 수 있습니다.</p>

        <div class="md-table">
          <div class="md-row md-header">
            <span>작성 방법</span>
            <span>결과</span>
          </div>
          <div v-for="item in markdownGuide" :key="item.syntax" class="md-row">
            <code class="md-syntax">{{ item.syntax }}</code>
            <span class="md-result" v-html="item.result"></span>
          </div>
        </div>
      </div>
    </section>

    <!-- ⑤ 관리 도구 -->
    <section id="admin" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">settings</span>
          <h3 class="section-title">관리 도구</h3>
        </div>
        <p class="section-desc">목표·과제·인력 데이터를 등록하고 관리하는 화면입니다. 총 4개의 탭으로 구성됩니다.</p>

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
            <div>소과제가 있는 과제는 <strong>주간 진행 현황</strong>에서 모과제 카드 안에 소과제별 섹션이 펼쳐집니다. 이슈·Q&A·컨플루언스 링크가 소과제 단위로 독립 관리됩니다.</div>
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
            <li>파트원 정보(이름·역할·기술·담당 과제)를 등록·수정·삭제합니다</li>
            <li>상단의 <strong>이름 칩</strong>을 클릭하면 해당 파트원만 필터링됩니다. 여러 명을 동시에 선택할 수 있습니다</li>
            <li>필터를 초기화하려면 <strong>"전체 보기"</strong> 버튼을 클릭합니다</li>
            <li>목록은 <strong>이름 가나다순</strong>으로 자동 정렬됩니다</li>
            <li>파트원을 삭제하면 담당 과제 연결도 자동으로 정리됩니다</li>
          </ul>
          <div class="callout callout-info">
            <span class="material-symbols-outlined callout-icon">lightbulb</span>
            <div>인력 추가 시 과제를 목표별로 그룹핑해서 선택할 수 있습니다. 목표에 연결되지 않은 과제는 <strong>"목표 없음"</strong> 그룹에 표시됩니다. 과제를 선택하면 연결된 목표가 자동으로 설정됩니다.</div>
          </div>
        </div>

        <!-- 설정 탭 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px">tune</span>
            설정 탭
          </div>
          <ul class="feature-list">
            <li><strong>관리자 모드</strong>: 비밀번호를 입력해 활성화하면 데이터 초기화 탭이 추가됩니다</li>
            <li>활성화된 관리자 모드는 브라우저를 닫아도 유지됩니다. 해제하려면 "관리자 모드 해제" 버튼을 클릭합니다</li>
            <li><strong>과제 적용 대상 관리</strong>: 관리자 모드에서만 표시됩니다. 기존 항목을 삭제하거나 새 항목을 추가할 수 있으며, 변경 내용은 과제 등록·수정 모달에 즉시 반영됩니다</li>
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
  { id: 'overview',  icon: 'info',      title: '시스템 소개' },
  { id: 'dashboard', icon: 'dashboard', title: '대시보드' },
  { id: 'progress',  icon: 'assignment', title: '주간 진행 현황' },
  { id: 'markdown',  icon: 'edit_note', title: '마크다운 작성법' },
  { id: 'admin',     icon: 'settings',  title: '관리 도구' },
  { id: 'faq',       icon: 'help',      title: 'FAQ' },
]

const markdownGuide = [
  { syntax: '**굵게**',           result: '<strong>굵게</strong>' },
  { syntax: '*기울임*',           result: '<em>기울임</em>' },
  { syntax: '~~취소선~~',         result: '<s>취소선</s>' },
  { syntax: '# 제목 1 / ## 제목 2', result: '<strong>제목</strong> (크기 조절)' },
  { syntax: '- 항목 1',           result: '• 항목 1 (목록)' },
  { syntax: '1. 첫번째',          result: '1. 첫번째 (번호 목록)' },
  { syntax: '`인라인 코드`',      result: '<code style="background:#f3f4f6;padding:1px 5px;border-radius:3px">인라인 코드</code>' },
  { syntax: '> 인용문',           result: '<span style="border-left:3px solid #d1d5db;padding-left:8px;color:#6b7280">인용문</span>' },
]

const faqs = reactive([
  {
    q: '이슈 내용은 어떤 형식으로 작성하나요?',
    a: '마크다운 형식을 지원합니다. 에디터 상단의 툴바 버튼을 클릭하거나, 직접 **굵게**, - 목록 등의 문법을 입력할 수 있습니다.',
    open: false,
  },
  {
    q: '주차(W#)는 어떻게 계산되나요?',
    a: '연도 기준 주차를 사용합니다. 날짜 범위(예: 5/12 – 5/18)와 주차 번호(예: 2026년 W21)가 함께 표시됩니다. 연도가 달라지면 자동으로 연도가 함께 표시되어 혼동 없이 이전 연도 데이터를 구분할 수 있습니다.',
    open: false,
  },
  {
    q: '다른 사람의 이슈나 답변을 수정할 수 있나요?',
    a: '접근 제한 기능은 없습니다. 오입력이 발생한 경우 수정 버튼으로 내용을 정정하거나, 담당자에게 요청하세요.',
    open: false,
  },
  {
    q: '이슈나 질문을 삭제하면 복구되나요?',
    a: '삭제된 항목은 복구되지 않습니다. 질문 삭제는 관리자 암호를 입력해야 진행할 수 있으며, 삭제 시 해당 질문의 모든 답변도 함께 삭제됩니다. 이슈 삭제는 별도 암호 없이 가능합니다.',
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
    q: '인력 탭에서 특정 파트원만 보고 싶을 때는?',
    a: '인력 탭 상단의 이름 칩을 클릭하면 해당 파트원만 필터링됩니다. 여러 명을 동시에 선택할 수 있으며, "전체 보기" 버튼으로 필터를 초기화할 수 있습니다.',
    open: false,
  },
  {
    q: '소과제란 무엇이고 어떻게 추가하나요?',
    a: '소과제는 하나의 과제를 세부 작업 단위로 나눈 것입니다. 관리 도구 → 과제 탭에서 수정 모달을 열면 하단에 "소과제 추가" 버튼이 표시됩니다. 소과제 ID는 T1-1, T1-2 형식으로 자동 부여되며, 각 소과제를 파트원의 담당 과제로 지정할 수 있습니다. 주간 진행 현황에서는 소과제별 이슈와 Q&A를 독립적으로 관리할 수 있습니다.',
    open: false,
  },
  {
    q: '소과제를 삭제하면 어떻게 되나요?',
    a: '소과제를 삭제하면 해당 소과제 ID가 파트원의 담당 과제 목록에서 자동으로 제거됩니다. 기존에 해당 소과제로 등록된 이슈 이력은 과제명이 텍스트로 보존됩니다. 모과제를 삭제하면 모든 소과제도 함께 삭제되며, 동일하게 연결된 데이터가 정리됩니다.',
    open: false,
  },
  {
    q: '여러 과제의 적용 대상을 한 번에 바꾸려면?',
    a: '과제 탭에서 행 앞의 체크박스로 과제를 선택하면 상단에 일괄 적용 툴바가 나타납니다. 적용 대상을 선택하고 "일괄 적용" 버튼을 클릭하면 선택된 과제 전체에 동시 적용됩니다. 인력 필터와 함께 사용하면 특정 파트원의 과제만 추려 일괄 적용할 수 있습니다.',
    open: false,
  },
  {
    q: '적용 대상 항목(MX/VD/DA/공통)을 추가하거나 삭제하려면?',
    a: '관리 도구 → 설정 탭에서 관리자 모드를 활성화하면 "과제 적용 대상 관리" 섹션이 표시됩니다. 기존 항목을 삭제하거나 새 항목을 추가할 수 있으며, 변경 내용은 즉시 과제 등록·수정 화면에 반영됩니다.',
    open: false,
  },
])
</script>

<style scoped>
.page-header { margin-bottom: 24px; }
.page-title { font-size: 20px; font-weight: 700; color: var(--text-primary); margin: 0 0 4px; }
.page-subtitle { font-size: 13px; color: var(--text-muted); margin: 0; }

/* 목차 */
.toc-card { margin-bottom: 24px; }
.toc-label { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; }
.toc-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.toc-item {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  background: var(--gray-50);
  color: var(--text-secondary);
  font-size: 13px; font-weight: 500;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.toc-item:hover { background: var(--primary-light); color: var(--primary); }
.toc-icon { font-size: 15px; width: 15px; height: 15px; }

/* 섹션 */
.help-section { margin-bottom: 20px; scroll-margin-top: 24px; }
.section-heading {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 14px; padding-bottom: 14px;
  border-bottom: 1px solid var(--outline);
}
.section-icon-lg {
  font-size: 20px; width: 20px; height: 20px;
  color: var(--primary);
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
.section-title { font-size: 16px; font-weight: 700; color: var(--text-primary); margin: 0; }
.section-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.75; margin-bottom: 18px; }

/* Callout 박스 */
.callout {
  display: flex; gap: 10px; align-items: flex-start;
  padding: 12px 14px;
  border-radius: 8px;
  font-size: 13px; line-height: 1.65;
  margin: 14px 0;
}
.callout-icon {
  font-size: 17px; width: 17px; height: 17px;
  flex-shrink: 0; margin-top: 1px;
}
.callout-info { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.callout-info .callout-icon { color: #2563eb; }
.callout-tip  { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.callout-tip .callout-icon { color: #16a34a; }
.callout-warning { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
.callout-warning .callout-icon { color: #d97706; }

/* 메뉴 카드 3종 */
.menu-cards { display: flex; flex-direction: column; gap: 8px; margin-top: 16px; }
.menu-card {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 12px 14px;
  background: var(--gray-50);
  border-radius: 8px;
  border: 1px solid var(--outline);
}
.menu-card-icon {
  font-size: 20px; width: 20px; height: 20px; flex-shrink: 0; margin-top: 1px;
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
.icon-blue { color: var(--primary); }
.icon-orange { color: var(--warning); }
.icon-gray { color: var(--text-muted); }
.menu-card-title { font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.menu-card-desc { font-size: 12px; color: var(--text-muted); line-height: 1.6; }

/* 기능 블록 */
.feature-block { margin-bottom: 18px; }
.feature-label {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 600; color: var(--text-primary);
  margin-bottom: 8px;
}
.badge-num {
  width: 20px; height: 20px;
  background: var(--primary); color: white;
  border-radius: 50%;
  font-size: 11px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.feature-list {
  margin: 0; padding-left: 18px;
  display: flex; flex-direction: column; gap: 6px;
}
.feature-list li { font-size: 13px; color: var(--text-secondary); line-height: 1.7; }

/* 서브 섹션 */
.sub-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--outline);
}
.sub-section:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.sub-section-title {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; font-weight: 600; color: var(--text-primary);
  margin-bottom: 10px;
}

/* 강조 */
.highlight-red { color: var(--danger); font-weight: 500; }
.inline-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 20px; height: 20px; border-radius: 4px;
  font-size: 11px; font-weight: 700;
}
.badge-green { background: var(--success-light); color: var(--success); }

/* 단계별 */
.steps { display: flex; flex-direction: column; gap: 2px; margin: 14px 0; }
.step { display: flex; align-items: flex-start; gap: 12px; padding: 10px 0; }
.step + .step { border-top: 1px solid var(--outline); }
.step-number {
  width: 24px; height: 24px; border-radius: 50%;
  background: var(--primary); color: white;
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 1px;
}
.step-body { flex: 1; }
.step-body strong { font-size: 13px; color: var(--text-primary); }
.step-body p { margin: 3px 0 0; font-size: 12px; color: var(--text-secondary); line-height: 1.65; }

/* 마크다운 가이드 테이블 */
.md-table { border: 1px solid var(--outline); border-radius: 8px; overflow: hidden; }
.md-row {
  display: grid; grid-template-columns: 1fr 1fr;
  padding: 9px 14px; font-size: 12px;
  border-bottom: 1px solid var(--outline);
}
.md-row:last-child { border-bottom: none; }
.md-header { background: var(--gray-50); font-weight: 600; color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; }
.md-syntax { font-family: monospace; background: var(--gray-100); padding: 2px 6px; border-radius: 3px; font-size: 12px; color: var(--text-primary); }
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
  font-size: 13px; font-weight: 500; color: var(--text-primary);
  user-select: none;
}
.faq-question:hover { color: var(--primary); }
.faq-q-icon { font-size: 16px; width: 16px; height: 16px; color: var(--primary); flex-shrink: 0; }
.faq-chevron {
  font-size: 18px; width: 18px; height: 18px;
  color: var(--text-muted); margin-left: auto;
  transition: transform 0.2s; flex-shrink: 0;
}
.faq-chevron.open { transform: rotate(180deg); }
.faq-answer {
  padding: 0 4px 14px 28px;
  font-size: 13px; color: var(--text-secondary); line-height: 1.75;
}
</style>
