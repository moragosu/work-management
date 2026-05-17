<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">도움말</h2>
      <p class="page-subtitle">설비혁신파트 목표 관리 시스템 사용 가이드</p>
    </div>

    <!-- 목차 -->
    <div class="toc-card card">
      <div class="card-body">
        <div class="toc-grid">
          <a v-for="section in sections" :key="section.id" :href="'#' + section.id" class="toc-item">
            <span class="material-symbols-outlined toc-icon">{{ section.icon }}</span>
            <span>{{ section.title }}</span>
          </a>
        </div>
      </div>
    </div>

    <!-- 섹션들 -->
    <div v-for="section in sections" :key="section.id" :id="section.id" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">{{ section.icon }}</span>
          <h3 class="section-title">{{ section.title }}</h3>
        </div>
        <p v-if="section.desc" class="section-desc">{{ section.desc }}</p>

        <div v-for="block in section.blocks" :key="block.title" class="block">
          <h4 class="block-title">
            <span v-if="block.icon" class="material-symbols-outlined block-icon">{{ block.icon }}</span>
            {{ block.title }}
          </h4>
          <ul class="block-list">
            <li v-for="item in block.items" :key="item">{{ item }}</li>
          </ul>
        </div>

        <!-- 단계별 가이드 -->
        <div v-if="section.steps" class="steps">
          <div v-for="(step, i) in section.steps" :key="i" class="step">
            <div class="step-number">{{ i + 1 }}</div>
            <div class="step-body">
              <strong>{{ step.title }}</strong>
              <p v-if="step.desc">{{ step.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- FAQ -->
    <div id="faq" class="help-section card">
      <div class="card-body">
        <div class="section-heading">
          <span class="material-symbols-outlined section-icon-lg">help</span>
          <h3 class="section-title">자주 묻는 질문</h3>
        </div>
        <div v-for="faq in faqs" :key="faq.q" class="faq-item" @click="faq.open = !faq.open">
          <div class="faq-question">
            <span>{{ faq.q }}</span>
            <span class="material-symbols-outlined faq-chevron" :class="{ open: faq.open }">expand_more</span>
          </div>
          <div v-if="faq.open" class="faq-answer">{{ faq.a }}</div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { reactive } from 'vue'

const sections = [
  {
    id: 'overview',
    icon: 'info',
    title: '시스템 소개',
    desc: '설비혁신파트 목표 관리 시스템은 OKR(목표 및 핵심 결과) 방식으로 파트의 목표와 과제를 관리하고, 주간 진행 현황을 공유하는 도구입니다.',
    blocks: [
      {
        title: '주요 메뉴',
        items: [
          '대시보드 — 파트 전체 목표(OKR) 현황과 파트원별 활동 통계를 한눈에 확인',
          '주간 진행 현황 — 주차별 이슈 등록 및 Q&A 관리',
          '관리 도구 — 파트원, 목표, 과제 정보 설정 (관리자용)',
        ],
      },
    ],
  },
  {
    id: 'dashboard',
    icon: 'dashboard',
    title: '대시보드',
    desc: '파트의 전체 목표(OKR) 진행 상황과 파트원별 활동 현황을 확인할 수 있습니다.',
    blocks: [
      {
        title: 'OKR 현황 카드',
        items: [
          '각 목표(Objective)별로 카드가 표시됩니다',
          '목표 아래 연결된 핵심 결과(KR)와 세부 과제를 확인할 수 있습니다',
          '컨플루언스 링크가 있는 과제는 링크 아이콘을 클릭해 상세 문서로 이동할 수 있습니다',
        ],
      },
      {
        title: '파트원별 활동 현황',
        items: [
          '각 파트원의 담당 과제 수, 이슈 등록 수, Q&A 답변 수를 확인합니다',
          '최근 등록한 이슈 내용도 요약해서 표시됩니다',
          '섹션 헤더를 클릭하면 접거나 펼칠 수 있습니다',
        ],
      },
    ],
  },
  {
    id: 'progress',
    icon: 'assignment',
    title: '주간 진행 현황',
    desc: '주차별로 이슈를 등록하고 Q&A를 통해 소통할 수 있습니다.',
    blocks: [
      {
        icon: 'warning',
        title: '이슈 등록',
        items: [
          '화면 상단의 주차 이동 버튼(< >)으로 원하는 주차를 선택합니다',
          '과제 목록에서 이슈를 등록할 과제를 찾습니다',
          '"+ 이슈 등록" 버튼을 클릭하면 등록자 선택과 이슈 내용 입력창이 나타납니다',
          '등록자(본인 이름)를 선택하고, 이슈 내용을 마크다운 형식으로 작성한 뒤 저장합니다',
          '이미 등록된 이슈는 "수정" 또는 "삭제" 버튼으로 관리할 수 있습니다',
        ],
      },
      {
        icon: 'forum',
        title: 'Q&A',
        items: [
          '각 과제 하단의 Q&A 섹션에서 질문을 등록할 수 있습니다',
          '"+ 질문 추가" 버튼으로 질문을 작성합니다',
          '질문에 답변이 없으면 "답변 달기" 버튼이 표시됩니다',
          '답변 작성 시 작성자(본인 이름)를 반드시 선택해야 합니다',
          '기존 답변이 있어도 "+ 답변 추가" 버튼으로 추가 답변을 달 수 있습니다',
        ],
      },
    ],
    steps: [
      { title: '주차 선택', desc: '상단 주차 네비게이터에서 현재 주차를 확인합니다. 날짜 범위와 W# 번호로 표시됩니다.' },
      { title: '과제 찾기', desc: '목표(Objective) > 핵심결과(KR) > 과제 순서로 펼쳐진 목록에서 담당 과제를 찾습니다.' },
      { title: '이슈 작성', desc: '"+ 이슈 등록" 클릭 → 본인 이름 선택 → 이슈 내용 입력 → 저장.' },
    ],
  },
]

const faqs = reactive([
  { q: '이슈 내용에는 어떤 형식으로 작성하나요?', a: '마크다운 형식을 지원합니다. **굵게**, *기울임*, - 목록, ```코드블록``` 등을 사용할 수 있습니다. 에디터 상단 툴바 버튼을 활용하면 편리합니다.', open: false },
  { q: '주차는 어떻게 계산되나요?', a: '연도 기준 ISO 주차(W#)를 사용합니다. 화면에 날짜 범위(예: 5/12 ~ 5/18)와 함께 표시되므로 현재 주차를 쉽게 확인할 수 있습니다.', open: false },
  { q: '다른 사람의 이슈를 수정할 수 있나요?', a: '등록자 제한 기능은 없습니다. 오입력이 발생한 경우 수정 버튼으로 내용을 정정하거나 담당자에게 요청하세요.', open: false },
  { q: '이슈를 삭제하면 복구가 되나요?', a: '삭제된 이슈는 복구되지 않습니다. 삭제 전 확인 팝업이 표시되니 신중하게 결정해 주세요.', open: false },
  { q: '컨플루언스 링크는 어디서 설정하나요?', a: '관리 도구 > 과제 탭에서 각 과제의 컨플루언스 URL을 입력할 수 있습니다. 관리자에게 요청하세요.', open: false },
  { q: '파트원 정보나 목표가 잘못 표시되면?', a: '관리 도구 메뉴에서 파트원, 목표(Objective), 핵심결과(KR), 과제 정보를 수정할 수 있습니다. 권한이 없다면 관리자에게 문의하세요.', open: false },
])
</script>

<style scoped>
.page-header { margin-bottom: 24px; }
.page-title { font-size: 20px; font-weight: 700; color: var(--text-primary); margin: 0 0 4px; }
.page-subtitle { font-size: 13px; color: var(--text-muted); margin: 0; }

/* 목차 */
.toc-card { margin-bottom: 24px; }
.toc-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.toc-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  background: var(--gray-50);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.toc-item:hover { background: var(--primary-light); color: var(--primary); }
.toc-icon { font-size: 16px; width: 16px; height: 16px; }

/* 섹션 */
.help-section { margin-bottom: 20px; scroll-margin-top: 24px; }
.section-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--outline);
}
.section-icon-lg {
  font-size: 20px; width: 20px; height: 20px;
  color: var(--primary);
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
.section-title { font-size: 16px; font-weight: 700; color: var(--text-primary); margin: 0; }
.section-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 16px; }

/* 블록 */
.block { margin-bottom: 16px; }
.block-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px;
}
.block-icon { font-size: 15px; width: 15px; height: 15px; color: var(--text-muted); }
.block-list {
  margin: 0;
  padding-left: 18px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.block-list li { font-size: 13px; color: var(--text-secondary); line-height: 1.6; }

/* 단계별 */
.steps { display: flex; flex-direction: column; gap: 10px; margin-top: 16px; }
.step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  background: var(--gray-50);
  border-radius: 8px;
}
.step-number {
  width: 24px; height: 24px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  font-size: 12px;
  font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.step-body { flex: 1; }
.step-body strong { font-size: 13px; color: var(--text-primary); }
.step-body p { margin: 4px 0 0; font-size: 12px; color: var(--text-muted); line-height: 1.6; }

/* FAQ */
.faq-item {
  border-bottom: 1px solid var(--outline);
  cursor: pointer;
  padding: 4px 0;
}
.faq-item:last-child { border-bottom: none; }
.faq-question {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 4px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}
.faq-question:hover { color: var(--primary); }
.faq-chevron {
  font-size: 18px; width: 18px; height: 18px;
  color: var(--text-muted);
  transition: transform 0.2s;
  flex-shrink: 0;
}
.faq-chevron.open { transform: rotate(180deg); }
.faq-answer {
  padding: 0 4px 14px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
}
</style>
