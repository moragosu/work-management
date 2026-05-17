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
        <p class="section-desc">접속 시 가장 먼저 보이는 화면입니다. 파트 전체 현황을 빠르게 파악할 수 있습니다.</p>

        <div class="feature-block">
          <div class="feature-label">
            <span class="badge-num">1</span>
            상단 통계 카드
          </div>
          <ul class="feature-list">
            <li><strong>전체 목표</strong> — 등록된 목표(Objective)의 총 개수</li>
            <li><strong>진행중 / 완료 / 위험</strong> — 각 상태별 목표 수. <span class="highlight-red">위험 상태는 즉각적인 조치가 필요한 목표를 의미합니다</span></li>
          </ul>
        </div>

        <div class="feature-block">
          <div class="feature-label">
            <span class="badge-num">2</span>
            액션 패널 (3가지)
          </div>
          <ul class="feature-list">
            <li><strong>미답변 질문</strong> — 이번 주 등록된 질문 중 아직 답변이 없는 항목. <em>클릭하면 해당 과제 위치로 바로 이동합니다</em></li>
            <li><strong>이슈</strong> — 이번 주 등록된 이슈 목록. 클릭하면 해당 과제로 이동</li>
            <li><strong>미배정 과제</strong> — 담당자가 지정되지 않은 과제 목록</li>
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
            <li>섹션 제목을 <strong>클릭</strong>하면 접거나 펼칠 수 있습니다</li>
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
                <p>목표 → KR → 과제 순으로 나열된 목록에서 이슈를 등록할 과제를 찾습니다. 이름 칩을 클릭하면 해당 파트원 과제만 필터링됩니다.</p>
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

          <div class="callout callout-warning">
            <span class="material-symbols-outlined callout-icon">info</span>
            <div>과제당 <strong>이슈는 1건</strong>만 등록됩니다. 기존 이슈가 있으면 수정 버튼으로 내용을 업데이트하세요.</div>
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
            <li>질문 삭제 시 <span class="highlight-red">해당 질문의 모든 답변도 함께 삭제</span>됩니다</li>
          </ul>
          <div class="callout callout-tip">
            <span class="material-symbols-outlined callout-icon">star</span>
            <div>대시보드의 <strong>미답변 질문 패널</strong>에서 항목을 클릭하면 해당 Q&A 위치로 자동 스크롤됩니다.</div>
          </div>
        </div>

        <!-- 컨플루언스 -->
        <div class="sub-section">
          <div class="sub-section-title">
            <span class="material-symbols-outlined" style="font-size:15px">link</span>
            컨플루언스 링크
          </div>
          <ul class="feature-list">
            <li>과제 카드 상단 컨플루언스 섹션에서 관련 문서 URL을 등록할 수 있습니다</li>
            <li>등록된 링크는 클릭 시 새 탭으로 열립니다</li>
            <li>수정·삭제 버튼으로 언제든 변경 가능합니다</li>
          </ul>
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
    a: '연도 기준 ISO 주차를 사용합니다. 화면에 날짜 범위(예: 5/12 – 5/18)와 W# 번호가 함께 표시되므로 현재 주차를 쉽게 확인할 수 있습니다.',
    open: false,
  },
  {
    q: '다른 사람의 이슈나 답변을 수정할 수 있나요?',
    a: '접근 제한 기능은 없습니다. 오입력이 발생한 경우 수정 버튼으로 내용을 정정하거나, 담당자에게 요청하세요.',
    open: false,
  },
  {
    q: '이슈나 질문을 삭제하면 복구되나요?',
    a: '삭제된 항목은 복구되지 않습니다. 삭제 전 확인 팝업이 표시되니 신중하게 결정해 주세요. 특히 질문 삭제 시 모든 답변도 함께 삭제됩니다.',
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
