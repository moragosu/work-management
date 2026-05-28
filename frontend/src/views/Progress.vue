<template>
  <div>
    <div class="page-header">
      <div>
        <h2>주간 진행 현황</h2>
        <div class="subtitle">주차별 과제 진행 상황 및 의견/질문</div>
      </div>
    </div>

    <div class="page-body">
      <!-- 주차 선택 + 인력 필터 -->
      <div class="filter-bar" style="flex-direction:column;align-items:flex-start;gap:10px">
        <div style="display:flex;align-items:center;gap:8px">
          <div class="week-nav" :class="{ 'week-nav-current': selectedWeek === getCurrentWeek() }">
            <button class="week-nav-btn" @click="prevWeek" :disabled="getCurrentWeekIndex() <= 0" data-tooltip="이전 주">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <div class="week-nav-info">
              <div style="display:flex;align-items:center;gap:6px">
                <span class="week-nav-label">{{ weekNavLabel }}</span>
                <span v-if="selectedWeek === getCurrentWeek()" class="week-current-badge">이번 주</span>
              </div>
              <span class="week-nav-range">지난주 | 이번주</span>
            </div>
            <button class="week-nav-btn" @click="nextWeek" :disabled="getCurrentWeekIndex() >= availableWeeks.length - 1" data-tooltip="다음 주">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
          </div>
          <button
            v-if="selectedWeek !== getCurrentWeek()"
            class="btn btn-ghost btn-sm week-today-btn"
            @click="goToCurrentWeek"
            data-tooltip="현재 주차로 이동"
          >이번 주</button>
        </div>
        <div v-if="staffList.length > 0" class="flex gap-6" style="align-items:center;flex-wrap:wrap">
          <span class="filter-label-sm">인력</span>
          <button
            v-for="s in staffList"
            :key="s.id"
            class="staff-chip"
            :class="{ 'staff-chip-active': selectedStaff.includes(s.name) }"
            @click="toggleStaff(s.name)"
          >{{ s.name }}</button>
          <button v-if="selectedStaff.length > 0" class="btn btn-ghost btn-xs" @click="selectedStaff = []" data-tooltip="인력 필터 초기화">전체 보기</button>
        </div>
      </div>

      <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
      <div v-else-if="!selectedWeek" class="empty-state">
        <span class="material-symbols-outlined empty-icon">calendar_today</span>
        <p>주차를 선택해주세요.</p>
      </div>

      <div v-else class="split-container">

        <!-- ══ 지난주 패널 복원 버튼 ══ -->
        <button
          v-if="panelState === 'right'"
          class="panel-restore-btn"
          @click="panelState = 'split'"
          title="지난주 패널 펼치기"
        >
          <span class="material-symbols-outlined">chevron_right</span>
        </button>

        <!-- ══ 지난주 패널 ══ -->
        <div v-show="panelState !== 'right'" class="split-panel split-left">
          <div class="panel-header">
            <span class="panel-title">
              <span class="material-symbols-outlined" style="font-size:15px;color:var(--text-muted)">history</span>
              지난주 · {{ leftWeekDisplay }}
            </span>
            <button class="panel-collapse-btn" @click="panelState = 'right'" title="지난주 패널 접기">
              <span class="material-symbols-outlined">chevron_left</span>
            </button>
          </div>

          <div v-for="task in filteredTasks" :key="'L-' + task.id" class="card mb-16" :style="{ borderLeft: '4px solid ' + getObjectiveColor(task.objective_id) }">
            <div class="card-header" style="flex-wrap:wrap;gap:8px">
              <div class="flex gap-8" style="align-items:center;flex:1;min-width:0">
                <h3 style="margin:0">{{ task.name }}</h3>
                <span class="badge" :style="{ background: getObjectiveColor(task.objective_id) + '22', color: getObjectiveColor(task.objective_id), border: '1px solid ' + getObjectiveColor(task.objective_id) + '55' }">{{ task.objective_id }}: {{ getObjectiveName(task.objective_id) }}</span>
                <span v-if="task.sub_tasks && task.sub_tasks.length > 0" class="badge badge-outline" style="font-size:11px">소과제 {{ task.sub_tasks.length }}개</span>
                <button
                  v-if="task.sub_tasks && task.sub_tasks.length > 0"
                  class="btn btn-ghost btn-xs subtask-toggle-all"
                  @click="toggleAllSubTasks(task)"
                  :data-tooltip="isAllSubTasksCollapsed(task) ? '소과제 전체 펼치기' : '소과제 전체 접기'"
                >
                  <span class="material-symbols-outlined" style="font-size:13px;vertical-align:-2px">{{ isAllSubTasksCollapsed(task) ? 'unfold_more' : 'unfold_less' }}</span>
                  {{ isAllSubTasksCollapsed(task) ? '전체 펼치기' : '전체 접기' }}
                </button>
              </div>
              <div class="member-badges">
                <template v-if="task.sub_tasks && task.sub_tasks.length > 0">
                  <span v-for="m in allTaskMembers(task)" :key="m.id" class="badge badge-gray" :title="m.role">{{ m.name }}</span>
                  <span v-if="allTaskMembers(task).length === 0" class="text-muted text-sm">담당자 미배정</span>
                </template>
                <template v-else>
                  <span v-for="m in taskMembers(task.id)" :key="m.id" class="badge badge-gray" :title="m.role">{{ m.name }}</span>
                  <span v-if="taskMembers(task.id).length === 0" class="text-muted text-sm">담당자 미배정</span>
                </template>
              </div>
            </div>

            <div class="card-body">
              <template v-if="task.sub_tasks && task.sub_tasks.length > 0">
                <div
                  v-for="st in task.sub_tasks"
                  :key="'L-' + st.id"
                  class="sub-task-section"
                  :class="{ 'sub-task-done': st.done }"
                >
                  <div
                    class="sub-task-header"
                    :class="{ 'sub-task-header-collapsed': !expandedSubTaskIds.has(st.id) }"
                    @click="toggleSubTaskCollapse(st.id)"
                  >
                    <div class="sub-task-title">
                      <span class="material-symbols-outlined sub-collapse-icon" :class="{ collapsed: !expandedSubTaskIds.has(st.id) }">expand_more</span>
                      <span class="sub-task-id-badge">{{ st.id }}</span>
                      <span class="sub-task-name">{{ st.name || '(이름 없음)' }}</span>
                      <template v-if="!expandedSubTaskIds.has(st.id)">
                        <span v-if="(leftIssueMap[st.id] || []).length > 0" class="subtask-sum-badge subtask-sum-issue">이슈 {{ (leftIssueMap[st.id] || []).length }}건</span>
                        <span v-if="getLeftQuestionsForTask(st.id).length > 0" class="subtask-sum-badge subtask-sum-qa">의견/질문 {{ getLeftQuestionsForTask(st.id).length }}건</span>
                      </template>
                    </div>
                    <div class="sub-task-meta" @click.stop>
                      <div class="member-badges">
                        <span v-for="m in subTaskMembers(st.id)" :key="m.id" class="badge badge-gray" :title="m.role">{{ m.name }}</span>
                        <span v-if="subTaskMembers(st.id).length === 0" class="text-muted text-sm">담당자 미배정</span>
                      </div>
                      <button
                        class="btn btn-xs sub-task-done-btn"
                        :class="st.done ? 'btn-success' : 'btn-ghost'"
                        @click="toggleSubTaskDone(task.id, st.id, !st.done)"
                        :data-tooltip="st.done ? '완료됨 — 클릭하여 진행중으로 변경' : '진행중 — 클릭하여 완료 처리'"
                      >
                        <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px">{{ st.done ? 'check_circle' : 'radio_button_unchecked' }}</span>
                        {{ st.done ? '완료' : '진행중' }}
                      </button>
                    </div>
                  </div>

                  <div
                    v-if="!expandedSubTaskIds.has(st.id) && getLeftTaskLink(st.id)"
                    class="sub-task-link-row sub-task-link-collapsed-preview"
                    @click.stop
                  >
                    <span class="material-symbols-outlined sub-task-link-icon">link</span>
                    <a :href="getLeftTaskLink(st.id).url" target="_blank" class="text-primary sub-task-link-text">{{ getLeftTaskLink(st.id).url }}</a>
                  </div>

                  <template v-if="expandedSubTaskIds.has(st.id)">
                    <div class="sub-task-link-row">
                      <button class="link-help-btn" :class="{ active: leftLinkHelpOpen.has(st.id) }" @click="toggleLeftLinkHelp(st.id)" data-tooltip="링크 가져오는 방법">?</button>
                      <span class="material-symbols-outlined sub-task-link-icon">link</span>
                      <template v-if="getLeftTaskLink(st.id) && !leftEditingLinkId[st.id]">
                        <a :href="getLeftTaskLink(st.id).url" target="_blank" class="text-primary sub-task-link-text">{{ getLeftTaskLink(st.id).url }}</a>
                        <button class="btn btn-ghost btn-xs" @click="startEditLeftLink(st.id)" data-tooltip="링크 수정">수정</button>
                        <button class="btn btn-danger btn-xs" @click="deleteLeftLink(st.id)" data-tooltip="링크 삭제">삭제</button>
                      </template>
                      <template v-else>
                        <input v-model="leftLinkInputs[st.id]" class="form-control sub-task-link-input" placeholder="컨플루언스 링크" @keyup.enter="saveLeftLink(st.id)" />
                        <button class="btn btn-primary btn-xs" @click="saveLeftLink(st.id)" :disabled="!leftLinkInputs[st.id]" data-tooltip="링크 저장">저장</button>
                        <button v-if="getLeftTaskLink(st.id)" class="btn btn-ghost btn-xs" @click="cancelEditLeftLink(st.id)" data-tooltip="수정 취소">취소</button>
                      </template>
                    </div>
                    <div v-if="leftLinkHelpOpen.has(st.id)" class="link-help-panel">
                      <div class="link-help-step"><span class="link-help-num">1</span><span>컨플루언스 페이지 우 상단 <strong>Share</strong> 버튼 클릭</span></div>
                      <div class="link-help-step"><span class="link-help-num">2</span><span>드롭다운에서 <strong>Share Link</strong> 생성 확인</span></div>
                      <div class="link-help-step"><span class="link-help-num">3</span><span><strong>Copy</strong> 버튼 클릭 → 아래 입력란에 붙여넣기</span></div>
                    </div>
                    <ProgressSection
                      :issues="leftIssueMap[st.id] || []"
                      :staff-list="staffList"
                      :task-id="st.id"
                      :week="leftWeek"
                      @update:issues="iss => onLeftIssuesUpdate(st.id, iss)"
                    />
                    <QASection
                      :questions="getLeftQuestionsForTask(st.id)"
                      :staff-list="staffList"
                      
                      :task-id="st.id"
                      :week="leftWeek"
                      @update:questions="qs => onLeftQuestionsUpdate(st.id, qs)"
                    />
                  </template>
                </div>
              </template>

              <template v-else>
                <div class="section-block">
                  <div class="section-label">
                    <button class="link-help-btn" :class="{ active: leftLinkHelpOpen.has(task.id) }" @click="toggleLeftLinkHelp(task.id)" data-tooltip="링크 가져오는 방법">?</button>
                    <span class="material-symbols-outlined section-icon">link</span>
                    컨플루언스
                  </div>
                  <div v-if="leftLinkHelpOpen.has(task.id)" class="link-help-panel">
                    <div class="link-help-step"><span class="link-help-num">1</span><span>컨플루언스 페이지 우 상단 <strong>Share</strong> 버튼 클릭</span></div>
                    <div class="link-help-step"><span class="link-help-num">2</span><span>드롭다운에서 <strong>Share Link</strong> 생성 확인</span></div>
                    <div class="link-help-step"><span class="link-help-num">3</span><span><strong>Copy</strong> 버튼 클릭 → 아래 입력란에 붙여넣기</span></div>
                  </div>
                  <div v-if="getLeftTaskLink(task.id) && !leftEditingLinkId[task.id]" class="flex gap-8" style="align-items:center">
                    <a :href="getLeftTaskLink(task.id).url" target="_blank" class="text-primary link-text">{{ getLeftTaskLink(task.id).url }}</a>
                    <button class="btn btn-ghost btn-xs" @click="startEditLeftLink(task.id)" data-tooltip="링크 수정">수정</button>
                    <button class="btn btn-danger btn-xs" @click="deleteLeftLink(task.id)" data-tooltip="링크 삭제">삭제</button>
                  </div>
                  <div v-else class="flex gap-8">
                    <input v-model="leftLinkInputs[task.id]" class="form-control" placeholder="링크를 입력하세요" style="flex:1" @keyup.enter="saveLeftLink(task.id)" />
                    <button class="btn btn-primary btn-xs" @click="saveLeftLink(task.id)" :disabled="!leftLinkInputs[task.id]" data-tooltip="링크 저장">저장</button>
                    <button v-if="getLeftTaskLink(task.id)" class="btn btn-ghost btn-xs" @click="cancelEditLeftLink(task.id)" data-tooltip="수정 취소">취소</button>
                  </div>
                </div>
                <ProgressSection
                  :issues="leftIssueMap[task.id] || []"
                  :staff-list="staffList"
                  :task-id="task.id"
                  :week="leftWeek"
                  @update:issues="iss => onLeftIssuesUpdate(task.id, iss)"
                />
                <QASection
                  :questions="getLeftQuestionsForTask(task.id)"
                  :staff-list="staffList"
                  
                  :task-id="task.id"
                  :week="leftWeek"
                  @update:questions="qs => onLeftQuestionsUpdate(task.id, qs)"
                />
              </template>
            </div>
          </div>
        </div>

        <!-- ══ 이번주 패널 복원 버튼 ══ -->
        <button
          v-if="panelState === 'left'"
          class="panel-restore-btn panel-restore-right"
          @click="panelState = 'split'"
          title="이번주 패널 펼치기"
        >
          <span class="material-symbols-outlined">chevron_left</span>
        </button>

        <!-- ══ 이번주 패널 ══ -->
        <div v-show="panelState !== 'left'" class="split-panel split-right">
          <div class="panel-header">
            <button class="panel-collapse-btn" @click="panelState = 'left'" title="이번주 패널 접기">
              <span class="material-symbols-outlined">chevron_right</span>
            </button>
            <span class="panel-title">
              <span class="material-symbols-outlined" style="font-size:15px;color:var(--text-muted)">today</span>
              이번주 · {{ rightWeekDisplay }}
              <span v-if="selectedWeek === getCurrentWeek()" class="week-current-badge">이번 주</span>
            </span>
          </div>

          <div v-for="task in filteredTasks" :key="task.id" :id="'task-' + task.id" class="card mb-16" :style="{ borderLeft: '4px solid ' + getObjectiveColor(task.objective_id) }">
            <div class="card-header" style="flex-wrap:wrap;gap:8px">
              <div class="flex gap-8" style="align-items:center;flex:1;min-width:0">
                <h3 style="margin:0">{{ task.name }}</h3>
                <span class="badge" :style="{ background: getObjectiveColor(task.objective_id) + '22', color: getObjectiveColor(task.objective_id), border: '1px solid ' + getObjectiveColor(task.objective_id) + '55' }">{{ task.objective_id }}: {{ getObjectiveName(task.objective_id) }}</span>
                <span v-if="task.sub_tasks && task.sub_tasks.length > 0" class="badge badge-outline" style="font-size:11px">소과제 {{ task.sub_tasks.length }}개</span>
                <button
                  v-if="task.sub_tasks && task.sub_tasks.length > 0"
                  class="btn btn-ghost btn-xs subtask-toggle-all"
                  @click="toggleAllSubTasks(task)"
                  :data-tooltip="isAllSubTasksCollapsed(task) ? '소과제 전체 펼치기' : '소과제 전체 접기'"
                >
                  <span class="material-symbols-outlined" style="font-size:13px;vertical-align:-2px">{{ isAllSubTasksCollapsed(task) ? 'unfold_more' : 'unfold_less' }}</span>
                  {{ isAllSubTasksCollapsed(task) ? '전체 펼치기' : '전체 접기' }}
                </button>
              </div>
              <div class="member-badges">
                <template v-if="task.sub_tasks && task.sub_tasks.length > 0">
                  <span
                    v-for="m in allTaskMembers(task)"
                    :key="m.id"
                    class="badge badge-gray"
                    :title="m.role"
                  >{{ m.name }}</span>
                  <span v-if="allTaskMembers(task).length === 0" class="text-muted text-sm">담당자 미배정</span>
                </template>
                <template v-else>
                  <span
                    v-for="m in taskMembers(task.id)"
                    :key="m.id"
                    class="badge badge-gray"
                    :title="m.role"
                  >{{ m.name }}</span>
                  <span v-if="taskMembers(task.id).length === 0" class="text-muted text-sm">담당자 미배정</span>
                </template>
              </div>
            </div>

            <div class="card-body">
              <template v-if="task.sub_tasks && task.sub_tasks.length > 0">
                <div
                  v-for="st in task.sub_tasks"
                  :key="st.id"
                  :id="'task-' + st.id"
                  class="sub-task-section"
                  :class="{ 'sub-task-done': st.done }"
                >
                  <div
                    class="sub-task-header"
                    :class="{ 'sub-task-header-collapsed': !expandedSubTaskIds.has(st.id) }"
                    @click="toggleSubTaskCollapse(st.id)"
                  >
                    <div class="sub-task-title">
                      <span class="material-symbols-outlined sub-collapse-icon" :class="{ collapsed: !expandedSubTaskIds.has(st.id) }">expand_more</span>
                      <span class="sub-task-id-badge">{{ st.id }}</span>
                      <span class="sub-task-name">{{ st.name || '(이름 없음)' }}</span>
                      <template v-if="!expandedSubTaskIds.has(st.id)">
                        <span v-if="(issueMap[st.id] || []).length > 0" class="subtask-sum-badge subtask-sum-issue">이슈 {{ (issueMap[st.id] || []).length }}건</span>
                        <span v-if="getQuestionsForTask(st.id).length > 0" class="subtask-sum-badge subtask-sum-qa">의견/질문 {{ getQuestionsForTask(st.id).length }}건</span>
                      </template>
                    </div>
                    <div class="sub-task-meta" @click.stop>
                      <div class="member-badges">
                        <span v-for="m in subTaskMembers(st.id)" :key="m.id" class="badge badge-gray" :title="m.role">{{ m.name }}</span>
                        <span v-if="subTaskMembers(st.id).length === 0" class="text-muted text-sm">담당자 미배정</span>
                      </div>
                      <button
                        class="btn btn-xs sub-task-done-btn"
                        :class="st.done ? 'btn-success' : 'btn-ghost'"
                        @click="toggleSubTaskDone(task.id, st.id, !st.done)"
                        :data-tooltip="st.done ? '완료됨 — 클릭하여 진행중으로 변경' : '진행중 — 클릭하여 완료 처리'"
                      >
                        <span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px">{{ st.done ? 'check_circle' : 'radio_button_unchecked' }}</span>
                        {{ st.done ? '완료' : '진행중' }}
                      </button>
                    </div>
                  </div>

                  <div
                    v-if="!expandedSubTaskIds.has(st.id) && getTaskLink(st.id)"
                    class="sub-task-link-row sub-task-link-collapsed-preview"
                    @click.stop
                  >
                    <span class="material-symbols-outlined sub-task-link-icon">link</span>
                    <a :href="getTaskLink(st.id).url" target="_blank" class="text-primary sub-task-link-text">{{ getTaskLink(st.id).url }}</a>
                  </div>

                  <template v-if="expandedSubTaskIds.has(st.id)">
                    <div class="sub-task-link-row">
                      <button class="link-help-btn" :class="{ active: linkHelpOpen.has(st.id) }" @click="toggleLinkHelp(st.id)" data-tooltip="링크 가져오는 방법">?</button>
                      <span class="material-symbols-outlined sub-task-link-icon">link</span>
                      <template v-if="getTaskLink(st.id) && !editingLinkId[st.id]">
                        <a :href="getTaskLink(st.id).url" target="_blank" class="text-primary sub-task-link-text">{{ getTaskLink(st.id).url }}</a>
                        <button class="btn btn-ghost btn-xs" @click="startEditLink(st.id)" data-tooltip="링크 수정">수정</button>
                        <button class="btn btn-danger btn-xs" @click="deleteLink(st.id)" data-tooltip="링크 삭제">삭제</button>
                      </template>
                      <template v-else>
                        <input
                          v-model="linkInputs[st.id]"
                          class="form-control sub-task-link-input"
                          placeholder="컨플루언스 링크"
                          @keyup.enter="saveLink(st.id)"
                        />
                        <button class="btn btn-primary btn-xs" @click="saveLink(st.id)" :disabled="!linkInputs[st.id]" data-tooltip="링크 저장">저장</button>
                        <button v-if="getTaskLink(st.id)" class="btn btn-ghost btn-xs" @click="cancelEditLink(st.id)" data-tooltip="수정 취소">취소</button>
                      </template>
                    </div>
                    <div v-if="linkHelpOpen.has(st.id)" class="link-help-panel">
                      <div class="link-help-step"><span class="link-help-num">1</span><span>컨플루언스 페이지 우 상단 <strong>Share</strong> 버튼 클릭</span></div>
                      <div class="link-help-step"><span class="link-help-num">2</span><span>드롭다운에서 <strong>Share Link</strong> 생성 확인</span></div>
                      <div class="link-help-step"><span class="link-help-num">3</span><span><strong>Copy</strong> 버튼 클릭 → 아래 입력란에 붙여넣기</span></div>
                    </div>

                    <ProgressSection
                      :issues="issueMap[st.id] || []"
                      :staff-list="staffList"
                      :task-id="st.id"
                      :week="selectedWeek"
                      @update:issues="iss => onIssuesUpdate(st.id, iss)"
                    />

                    <QASection
                      :questions="getQuestionsForTask(st.id)"
                      :staff-list="staffList"
                      
                      :task-id="st.id"
                      :week="selectedWeek"
                      @update:questions="qs => onQuestionsUpdate(st.id, qs)"
                    />
                  </template>
                </div>
              </template>

              <template v-else>
                <div class="section-block">
                  <div class="section-label">
                    <button class="link-help-btn" :class="{ active: linkHelpOpen.has(task.id) }" @click="toggleLinkHelp(task.id)" data-tooltip="링크 가져오는 방법">?</button>
                    <span class="material-symbols-outlined section-icon">link</span>
                    컨플루언스
                  </div>
                  <div v-if="linkHelpOpen.has(task.id)" class="link-help-panel">
                    <div class="link-help-step"><span class="link-help-num">1</span><span>컨플루언스 페이지 우 상단 <strong>Share</strong> 버튼 클릭</span></div>
                    <div class="link-help-step"><span class="link-help-num">2</span><span>드롭다운에서 <strong>Share Link</strong> 생성 확인</span></div>
                    <div class="link-help-step"><span class="link-help-num">3</span><span><strong>Copy</strong> 버튼 클릭 → 아래 입력란에 붙여넣기</span></div>
                  </div>
                  <div v-if="getTaskLink(task.id) && !editingLinkId[task.id]" class="flex gap-8" style="align-items:center">
                    <a :href="getTaskLink(task.id).url" target="_blank" class="text-primary link-text">
                      {{ getTaskLink(task.id).url }}
                    </a>
                    <button class="btn btn-ghost btn-xs" @click="startEditLink(task.id)" data-tooltip="링크 수정">수정</button>
                    <button class="btn btn-danger btn-xs" @click="deleteLink(task.id)" data-tooltip="링크 삭제">삭제</button>
                  </div>
                  <div v-else class="flex gap-8">
                    <input
                      v-model="linkInputs[task.id]"
                      class="form-control"
                      placeholder="링크를 입력하세요"
                      style="flex:1"
                      @keyup.enter="saveLink(task.id)"
                    />
                    <button class="btn btn-primary btn-xs" @click="saveLink(task.id)" :disabled="!linkInputs[task.id]" data-tooltip="링크 저장">저장</button>
                    <button v-if="getTaskLink(task.id)" class="btn btn-ghost btn-xs" @click="cancelEditLink(task.id)" data-tooltip="수정 취소">취소</button>
                  </div>
                </div>

                <ProgressSection
                  :issues="issueMap[task.id] || []"
                  :staff-list="staffList"
                  :task-id="task.id"
                  :week="selectedWeek"
                  @update:issues="iss => onIssuesUpdate(task.id, iss)"
                />

                <QASection
                  :questions="getQuestionsForTask(task.id)"
                  :staff-list="staffList"
                  
                  :task-id="task.id"
                  :week="selectedWeek"
                  @update:questions="qs => onQuestionsUpdate(task.id, qs)"
                />
              </template>
            </div>
          </div>
        </div>

      </div>
    </div>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useToast } from '../composables/useToast.js'
import { parseIds } from '../utils/parseIds.js'
import { getCurrentWeek, getWeekDateRange, addWeeks } from '../utils/week.js'
import { getTaskMembers, getAllTaskMembers } from '../utils/staff.js'
import ProgressSection from '../components/progress/ProgressSection.vue'
import QASection from '../components/progress/QASection.vue'

const route = useRoute()

const tasks = ref([])
const objectives = ref([])
const staffList = ref([])
const loading = ref(false)
const { toastMsg, showToast, toastError } = useToast()

// ── 패널 상태: 'split' | 'left' | 'right' ──
const panelState = ref('split')

// ── 인력 필터 ──
const selectedStaff = ref([])
const filteredTasks = computed(() => {
  if (selectedStaff.value.length === 0) return tasks.value
  return tasks.value.filter(task =>
    getAllTaskMembers(task, staffList.value).some(m => selectedStaff.value.includes(m.name))
  )
})
function toggleStaff(name) {
  const idx = selectedStaff.value.indexOf(name)
  if (idx === -1) selectedStaff.value.push(name)
  else selectedStaff.value.splice(idx, 1)
}

// ── 주차 (selectedWeek = 이번주 패널, leftWeek = 지난주 패널) ──
const selectedWeek = ref('')
const leftWeek = computed(() => addWeeks(selectedWeek.value, -1))

const qnaList = ref([])
const linkMap = ref({})
const issueMap = ref({})
const linkInputs = ref({})
const editingLinkId = ref({})
const linkHelpOpen = ref(new Set())
const expandedSubTaskIds = ref(new Set())

// ── 지난주 패널 데이터 ──
const leftQnA = ref([])
const leftLinkMap = ref({})
const leftIssueMap = ref({})
const leftLinkInputs = ref({})
const leftEditingLinkId = ref({})
const leftLinkHelpOpen = ref(new Set())

// ── 주차 표시 ──
const leftWeekNum = computed(() => parseInt(leftWeek.value?.match(/-W(\d+)$/)?.[1] || '0'))
const rightWeekNum = computed(() => parseInt(selectedWeek.value?.match(/-W(\d+)$/)?.[1] || '0'))
const leftWeekYear = computed(() => leftWeek.value?.match(/^(\d{4})/)?.[1] || '')
const rightWeekYear = computed(() => selectedWeek.value?.match(/^(\d{4})/)?.[1] || '')

const weekNavLabel = computed(() => {
  if (!leftWeek.value || !selectedWeek.value) return ''
  if (leftWeekYear.value === rightWeekYear.value) {
    return `${leftWeekYear.value}년 W${leftWeekNum.value} | W${rightWeekNum.value}`
  }
  return `${leftWeekYear.value}년 W${leftWeekNum.value} | ${rightWeekYear.value}년 W${rightWeekNum.value}`
})
const leftWeekDisplay = computed(() => `W${leftWeekNum.value} (${getWeekDateRange(leftWeek.value)})`)
const rightWeekDisplay = computed(() => `W${rightWeekNum.value} (${getWeekDateRange(selectedWeek.value)})`)

function toggleLinkHelp(id) {
  const next = new Set(linkHelpOpen.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  linkHelpOpen.value = next
}
function toggleSubTaskCollapse(stId) {
  const next = new Set(expandedSubTaskIds.value)
  if (next.has(stId)) next.delete(stId)
  else next.add(stId)
  expandedSubTaskIds.value = next
}
function isAllSubTasksCollapsed(task) {
  return (task.sub_tasks || []).every(st => !expandedSubTaskIds.value.has(st.id))
}
function toggleAllSubTasks(task) {
  const next = new Set(expandedSubTaskIds.value)
  if (isAllSubTasksCollapsed(task)) {
    task.sub_tasks.forEach(st => next.add(st.id))
  } else {
    task.sub_tasks.forEach(st => next.delete(st.id))
  }
  expandedSubTaskIds.value = next
}

// ── 주차 네비게이션 ──
const availableWeeks = computed(() => {
  const center = selectedWeek.value || getCurrentWeek()
  return [-4, -3, -2, -1, 0, 1, 2, 3, 4].map(d => addWeeks(center, d))
})

function getCurrentWeekIndex() { return availableWeeks.value.indexOf(selectedWeek.value) }
function prevWeek() { selectedWeek.value = addWeeks(selectedWeek.value, -1); onWeekChange() }
function nextWeek() { selectedWeek.value = addWeeks(selectedWeek.value, 1); onWeekChange() }
function goToCurrentWeek() { selectedWeek.value = getCurrentWeek(); onWeekChange() }

function initLinkInputs() {
  const ids = []
  tasks.value.forEach(t => {
    ids.push(t.id)
    ;(t.sub_tasks || []).forEach(st => ids.push(st.id))
  })
  linkInputs.value = Object.fromEntries(ids.map(id => [id, '']))
  leftLinkInputs.value = Object.fromEntries(ids.map(id => [id, '']))
}

async function onWeekChange() {
  if (!selectedWeek.value) return
  initLinkInputs()
  editingLinkId.value = {}
  leftEditingLinkId.value = {}
  await Promise.all([
    loadQnA(), loadLinks(), loadIssues(),
    loadLeftQnA(), loadLeftLinks(), loadLeftIssues(),
  ])
}

// ── 헬퍼 ──
const OBJECTIVE_COLORS = ['#4f8ef7','#10b981','#f59e0b','#8b5cf6','#ef4444','#06b6d4']
function getObjectiveColor(objectiveId) {
  const idx = objectives.value.findIndex(o => o.id === objectiveId)
  return OBJECTIVE_COLORS[(idx < 0 ? 0 : idx) % OBJECTIVE_COLORS.length]
}
function getObjectiveName(id) { return objectives.value.find(o => o.id === id)?.name ?? id }
function taskMembers(taskId) { return getTaskMembers(taskId, staffList.value) }
function subTaskMembers(subTaskId) { return getTaskMembers(subTaskId, staffList.value) }
function allTaskMembers(task) { return getAllTaskMembers(task, staffList.value) }
function getQuestionsForTask(taskId) { return qnaList.value.filter(q => q.task_id === taskId) }
function getTaskLink(taskId) { return linkMap.value[taskId] || null }
function getLeftQuestionsForTask(taskId) { return leftQnA.value.filter(q => q.task_id === taskId) }
function getLeftTaskLink(taskId) { return leftLinkMap.value[taskId] || null }

async function toggleSubTaskDone(taskId, subTaskId, done) {
  try {
    await axios.put(`/api/tasks/${taskId}/sub-tasks/${subTaskId}`, { done })
    tasks.value = tasks.value.map(t => {
      if (t.id !== taskId) return t
      return { ...t, sub_tasks: t.sub_tasks.map(st => st.id === subTaskId ? { ...st, done } : st) }
    })
    showToast(done ? '소과제가 완료 처리되었습니다' : '진행중으로 변경되었습니다')
  } catch (e) { toastError(e, '소과제 상태 변경 실패') }
}

// ── 이번주 업데이트 핸들러 ──
function onQuestionsUpdate(taskId, newQuestions) {
  const others = qnaList.value.filter(q => q.task_id !== taskId)
  qnaList.value = [...others, ...newQuestions]
}
function onIssuesUpdate(taskId, newIssues) {
  issueMap.value = { ...issueMap.value, [taskId]: newIssues }
}

// ── 지난주 업데이트 핸들러 ──
function onLeftQuestionsUpdate(taskId, newQuestions) {
  const others = leftQnA.value.filter(q => q.task_id !== taskId)
  leftQnA.value = [...others, ...newQuestions]
}
function onLeftIssuesUpdate(taskId, newIssues) {
  leftIssueMap.value = { ...leftIssueMap.value, [taskId]: newIssues }
}

// ── 컨플루언스 링크 ──
async function loadLinks() {
  const { data } = await axios.get('/api/confluence', { params: { week: selectedWeek.value } })
  const map = {}
  data.forEach(l => { map[l.task_id] = l })
  linkMap.value = map
}
function startEditLink(taskId) {
  editingLinkId.value = { ...editingLinkId.value, [taskId]: true }
  linkInputs.value = { ...linkInputs.value, [taskId]: linkMap.value[taskId]?.url || '' }
}
function cancelEditLink(taskId) {
  const updated = { ...editingLinkId.value }; delete updated[taskId]; editingLinkId.value = updated
}
async function saveLink(taskId) {
  const url = linkInputs.value[taskId]?.trim()
  if (!url) return
  try {
    const existing = linkMap.value[taskId]
    const saved = existing
      ? (await axios.put(`/api/confluence/${existing.id}`, { url })).data
      : (await axios.post('/api/confluence', { week: selectedWeek.value, task_id: taskId, url })).data
    linkMap.value = { ...linkMap.value, [taskId]: saved }
    linkInputs.value[taskId] = ''
    cancelEditLink(taskId)
    showToast('링크가 저장되었습니다')
  } catch (e) { toastError(e, '링크 저장 실패') }
}
async function deleteLink(taskId) {
  if (!confirm('링크를 삭제하시겠습니까?')) return
  try {
    const existing = linkMap.value[taskId]
    if (existing) await axios.delete(`/api/confluence/${existing.id}`)
    const updated = { ...linkMap.value }; delete updated[taskId]; linkMap.value = updated
    showToast('삭제되었습니다')
  } catch (e) { toastError(e, '링크 삭제 실패') }
}

// ── 이번주 로드 ──
async function loadQnA() {
  const { data } = await axios.get('/api/qna/questions', { params: { week: selectedWeek.value } })
  qnaList.value = data
}
async function loadIssues() {
  const { data } = await axios.get('/api/issues', { params: { week: selectedWeek.value } })
  const map = {}
  data.forEach(iss => {
    if (!map[iss.task_id]) map[iss.task_id] = []
    map[iss.task_id].push(iss)
  })
  issueMap.value = map
}

// ── 지난주 컨플루언스 링크 ──
function toggleLeftLinkHelp(id) {
  const next = new Set(leftLinkHelpOpen.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  leftLinkHelpOpen.value = next
}
function startEditLeftLink(taskId) {
  leftEditingLinkId.value = { ...leftEditingLinkId.value, [taskId]: true }
  leftLinkInputs.value = { ...leftLinkInputs.value, [taskId]: leftLinkMap.value[taskId]?.url || '' }
}
function cancelEditLeftLink(taskId) {
  const updated = { ...leftEditingLinkId.value }; delete updated[taskId]; leftEditingLinkId.value = updated
}
async function saveLeftLink(taskId) {
  const url = leftLinkInputs.value[taskId]?.trim()
  if (!url) return
  try {
    const existing = leftLinkMap.value[taskId]
    const saved = existing
      ? (await axios.put(`/api/confluence/${existing.id}`, { url })).data
      : (await axios.post('/api/confluence', { week: leftWeek.value, task_id: taskId, url })).data
    leftLinkMap.value = { ...leftLinkMap.value, [taskId]: saved }
    leftLinkInputs.value[taskId] = ''
    cancelEditLeftLink(taskId)
    showToast('링크가 저장되었습니다')
  } catch (e) { toastError(e, '링크 저장 실패') }
}
async function deleteLeftLink(taskId) {
  if (!confirm('링크를 삭제하시겠습니까?')) return
  try {
    const existing = leftLinkMap.value[taskId]
    if (existing) await axios.delete(`/api/confluence/${existing.id}`)
    const updated = { ...leftLinkMap.value }; delete updated[taskId]; leftLinkMap.value = updated
    showToast('삭제되었습니다')
  } catch (e) { toastError(e, '링크 삭제 실패') }
}

// ── 지난주 로드 ──
async function loadLeftQnA() {
  const { data } = await axios.get('/api/qna/questions', { params: { week: leftWeek.value } })
  leftQnA.value = data
}
async function loadLeftLinks() {
  const { data } = await axios.get('/api/confluence', { params: { week: leftWeek.value } })
  const map = {}
  data.forEach(l => { map[l.task_id] = l })
  leftLinkMap.value = map
}
async function loadLeftIssues() {
  const { data } = await axios.get('/api/issues', { params: { week: leftWeek.value } })
  const map = {}
  data.forEach(iss => {
    if (!map[iss.task_id]) map[iss.task_id] = []
    map[iss.task_id].push(iss)
  })
  leftIssueMap.value = map
}

// ── 포커스 이동 ──
async function handleFocusQuery() {
  const { focusQuestion, focusIssue, focusIssueId, focusTask } = route.query
  if (!focusQuestion && !focusIssue && !focusIssueId && !focusTask) return

  if (focusQuestion) {
    const q = qnaList.value.find(q => q.id === focusQuestion)
    if (q && q.task_id.includes('-')) {
      expandedSubTaskIds.value = new Set([...expandedSubTaskIds.value, q.task_id])
    }
  }
  if (focusIssue && focusIssue.includes('-')) {
    expandedSubTaskIds.value = new Set([...expandedSubTaskIds.value, focusIssue])
  }
  if (focusIssueId) {
    const iss = Object.values(issueMap.value).flat().find(i => i.id === focusIssueId)
    if (iss?.task_id.includes('-')) {
      expandedSubTaskIds.value = new Set([...expandedSubTaskIds.value, iss.task_id])
    }
  }
  if (focusTask) {
    const isSubTask = tasks.value.some(t => (t.sub_tasks || []).some(st => st.id === focusTask))
    if (isSubTask) {
      expandedSubTaskIds.value = new Set([...expandedSubTaskIds.value, focusTask])
    }
  }

  await nextTick()
  await new Promise(r => setTimeout(r, 80))

  const targetId = focusQuestion
    ? `qa-${focusQuestion}`
    : focusIssueId
      ? `issue-${focusIssueId}`
      : `task-${focusIssue || focusTask}`

  let el = document.getElementById(targetId)
  if (!el) {
    await nextTick()
    await new Promise(r => setTimeout(r, 200))
    el = document.getElementById(targetId)
  }
  if (!el) return
  el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  el.classList.add('highlight-focus')
  setTimeout(() => el?.classList.remove('highlight-focus'), 2200)
}

async function fetchAll() {
  loading.value = true
  try {
    const [tRes, oRes, sRes, stRes] = await Promise.all([
      axios.get('/api/tasks'), axios.get('/api/okrs'), axios.get('/api/staff'),
      axios.get('/api/settings').catch(() => ({ data: {} })),
    ])
    tasks.value = tRes.data
    objectives.value = oRes.data
    staffList.value = sRes.data
    // 소과제 전체 기본 펼침
    const allSubIds = new Set()
    tRes.data.forEach(t => (t.sub_tasks || []).forEach(st => allSubIds.add(st.id)))
    expandedSubTaskIds.value = allSubIds
    initLinkInputs()
    selectedWeek.value = route.query.week || getCurrentWeek()
    await onWeekChange()
  } finally { loading.value = false }
  await handleFocusQuery()
}

onMounted(fetchAll)
</script>

<style scoped>
.gap-6 { gap: 6px; }

.filter-label-sm {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
}

/* ── 주차 네비게이터 ── */
.week-nav {
  display: inline-flex;
  align-items: stretch;
  background: var(--surface);
  border: 1px solid var(--outline);
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
  overflow: hidden;
}
.week-nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--text-secondary);
  transition: background 0.15s, color 0.15s;
}
.week-nav-btn:hover:not(:disabled) { background: var(--gray-100); color: var(--text-primary); }
.week-nav-btn:disabled { opacity: 0.25; cursor: not-allowed; }
.week-nav-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 20px;
  border-left: 1px solid var(--outline);
  border-right: 1px solid var(--outline);
  min-width: 180px;
  gap: 2px;
}
.week-nav-label { font-size: 14px; font-weight: 700; color: var(--text-primary); letter-spacing: 0.01em; }
.week-nav-range { font-size: 11px; color: var(--text-muted); letter-spacing: 0.03em; }
.week-nav-current { border-color: var(--color-primary, #4f8ef7); box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-primary, #4f8ef7) 15%, transparent); }
.week-nav-current .week-nav-btn { color: var(--color-primary, #4f8ef7); }
.week-nav-current .week-nav-btn:hover:not(:disabled) { background: color-mix(in srgb, var(--color-primary, #4f8ef7) 8%, transparent); }
.week-nav-current .week-nav-info { border-color: var(--color-primary, #4f8ef7); }
.week-nav-current .week-nav-label { color: var(--color-primary, #4f8ef7); }
.week-current-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 999px;
  background: var(--color-primary, #4f8ef7);
  color: #fff;
  letter-spacing: 0.02em;
  line-height: 1.6;
}
.week-today-btn {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 6px;
  color: var(--color-primary, #4f8ef7);
  border-color: var(--color-primary, #4f8ef7);
}

/* ── 인력 칩 ── */
.staff-chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid var(--outline);
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
  background: var(--surface);
  color: var(--text-secondary);
  transition: all 0.15s;
}
.staff-chip:hover { border-color: var(--primary); color: var(--primary); }
.staff-chip-active { background: var(--primary-light); color: var(--primary); border-color: var(--primary); font-weight: 600; }

.member-badges { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }

/* ── 분할 화면 ── */
.split-container {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}
.split-panel {
  flex: 1 1 0;
  min-width: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--gray-50, #f9fafb);
  border: 1px solid var(--outline);
  border-radius: 8px;
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  position: sticky;
  top: 0;
  z-index: 10;
}
.panel-title {
  display: flex;
  align-items: center;
  gap: 6px;
}
.panel-collapse-btn {
  display: flex;
  align-items: center;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  padding: 4px;
  border-radius: 4px;
  transition: background 0.15s, color 0.15s;
}
.panel-collapse-btn:hover {
  background: var(--gray-200, #e5e7eb);
  color: var(--text-primary);
}
.panel-restore-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  flex-shrink: 0;
  align-self: stretch;
  min-height: 120px;
  background: var(--gray-50, #f9fafb);
  border: 1px solid var(--outline);
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-muted);
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.panel-restore-btn:hover {
  background: var(--primary-light, #eff6ff);
  color: var(--primary, #4f8ef7);
  border-color: var(--primary, #4f8ef7);
}

/* ── 컨텐츠 ── */
.section-block {
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--outline);
}
.link-text { flex: 1; font-size: 14px; word-break: break-all; }

.sub-task-section {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid var(--outline);
  border-left: 3px solid var(--color-primary, #4f8ef7);
  border-radius: 8px;
  background: var(--gray-50, #fafafa);
  transition: opacity 0.2s;
}
.sub-task-section.sub-task-done {
  border-left-color: var(--color-success, #22c55e);
  opacity: 0.75;
}
.sub-task-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  border-radius: 6px;
  margin: -4px -4px 12px;
  padding: 4px;
  transition: background 0.15s;
}
.sub-task-header:hover { background: color-mix(in srgb, var(--color-primary, #4f8ef7) 6%, transparent); }
.sub-task-header-collapsed { margin-bottom: 4px !important; }

.sub-task-link-collapsed-preview {
  margin-bottom: 0;
  background: transparent;
  border-color: transparent;
  padding: 3px 4px;
}
.sub-task-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}
.sub-task-id-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 7px;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 700;
  font-family: monospace;
  background: color-mix(in srgb, var(--color-primary, #4f8ef7) 12%, transparent);
  color: var(--color-primary, #4f8ef7);
  white-space: nowrap;
  flex-shrink: 0;
}
.sub-task-done .sub-task-id-badge {
  background: color-mix(in srgb, var(--color-success, #22c55e) 12%, transparent);
  color: var(--color-success, #22c55e);
}
.sub-task-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  word-break: break-all;
}
.sub-task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.sub-task-done-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  white-space: nowrap;
}
.sub-collapse-icon {
  font-size: 18px;
  color: var(--text-muted);
  flex-shrink: 0;
  transition: transform 0.2s;
}
.sub-collapse-icon.collapsed { transform: rotate(-90deg); }

.subtask-sum-badge {
  display: inline-flex;
  align-items: center;
  padding: 1px 7px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 600;
  flex-shrink: 0;
}
.subtask-sum-issue {
  background: color-mix(in srgb, #f59e0b 12%, transparent);
  color: #b45309;
}
.subtask-sum-qa {
  background: color-mix(in srgb, var(--color-primary, #4f8ef7) 12%, transparent);
  color: var(--color-primary, #4f8ef7);
}

.subtask-toggle-all {
  font-size: 11px;
  padding: 2px 8px;
  color: var(--text-muted);
  border-color: var(--outline);
}

.link-help-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1px solid var(--outline);
  background: var(--surface);
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  line-height: 1;
  padding: 0;
}
.link-help-btn:hover,
.link-help-btn.active {
  background: var(--primary-light);
  color: var(--primary);
  border-color: var(--primary);
}

.link-help-panel {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
  padding: 10px 12px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  font-size: 12px;
  color: #1d4ed8;
}
.link-help-step {
  display: flex;
  align-items: center;
  gap: 8px;
  line-height: 1.5;
}
.link-help-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #2563eb;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  flex-shrink: 0;
}

.sub-task-link-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 7px 10px;
  background: var(--surface);
  border: 1px solid var(--outline);
  border-radius: 6px;
}
.sub-task-link-icon {
  font-size: 15px;
  color: var(--text-muted);
  flex-shrink: 0;
}
.sub-task-link-text {
  flex: 1;
  font-size: 13px;
  word-break: break-all;
}
.sub-task-link-input {
  flex: 1;
  font-size: 13px;
  padding: 4px 8px;
  height: auto;
}
</style>

<style>
.md-preview-inline.md-editor-previewOnly { background: transparent !important; padding: 0 !important; }
.md-preview-inline .md-editor-preview-wrapper { padding: 4px 0 !important; }
.md-preview-inline .md-editor-preview { font-size: 14px; line-height: 1.6; color: var(--text-primary); }
.md-preview-inline .md-editor-preview > p:first-child { margin-top: 0; }
.md-preview-inline .md-editor-preview > p:last-child { margin-bottom: 0; }
.md-preview-inline .md-editor-preview img { max-width: 100%; border-radius: 4px; margin: 6px 0; display: block; }
</style>
