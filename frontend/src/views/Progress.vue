<template>
  <div>
    <div class="page-header">
      <div>
        <h2>주간 진행 현황</h2>
        <div class="subtitle">주차별 과제 진행 상황 및 Q&A</div>
      </div>
    </div>

    <div class="page-body">
      <!-- Week selector with arrow navigation -->
      <div class="filter-bar">
        <div class="flex gap-8" style="align-items: center;">
          <button class="btn btn-ghost btn-sm" @click="prevWeek" :disabled="!selectedWeek || getCurrentWeekIndex() <= 0">←</button>
          <select v-model="selectedWeek" class="form-control" @change="onWeekChange" style="min-width: 120px;">
            <option value="">주차 선택</option>
            <option v-for="week in availableWeeks" :key="week" :value="week">{{ week }}</option>
          </select>
          <button class="btn btn-ghost btn-sm" @click="nextWeek" :disabled="!selectedWeek || getCurrentWeekIndex() >= availableWeeks.length - 1">→</button>
        </div>
      </div>

      <div v-if="loading" class="loading-center"><div class="spinner"></div></div>
      <div v-else-if="!selectedWeek" class="empty-state">
        <div class="empty-icon">📋</div>
        <p>주차를 선택해주세요.</p>
      </div>
      <div v-else-if="tasksForSelectedWeek.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <p>해당 주차에 등록된 과제가 없습니다.</p>
      </div>

      <!-- Week content with Confluence link and Tasks -->
      <div v-else>
        <!-- Confluence link display -->
        <div v-if="confluenceLink" class="card card-body mb-16">
          <div class="flex gap-8" style="align-items: center;">
            <span class="badge badge-blue">📎</span>
            <a :href="confluenceLink" target="_blank" class="text-primary" style="flex: 1;">{{ confluenceLink }}</a>
            <button class="btn btn-ghost btn-xs" @click="openConfluenceLink">열기</button>
          </div>
        </div>

        <!-- Tasks with Q&A -->
        <div v-for="task in tasksForSelectedWeek" :key="task.id" class="card mb-16">
          <div class="card-header">
            <h3>{{ task.name }}</h3>
            <span class="badge badge-blue">{{ getObjectiveName(task.objective_id) }}</span>
          </div>
          
          <div class="card-body">
            <!-- Task-specific Confluence link -->
            <div v-if="getTaskConfluenceLink(task.id)" class="mb-16">
              <div class="flex gap-8" style="align-items: center;">
                <span class="badge badge-blue">📎</span>
                <a :href="getTaskConfluenceLink(task.id)" target="_blank" class="text-primary" style="flex: 1; font-size: 14px;">
                  {{ getTaskConfluenceLink(task.id) }}
                </a>
                <button class="btn btn-ghost btn-xs" @click="openTaskConfluenceLink(task.id)">열기</button>
              </div>
            </div>
            <div v-else class="mb-16">
              <div class="flex gap-8">
                <input 
                  :value="taskConfluenceLinks[task.id] || ''"
                  @input="updateTaskConfluenceLink(task.id, $event.target.value)"
                  class="form-control" 
                  placeholder="과제별 컨플루언스 링크를 입력하세요" 
                  style="flex: 1;"
                />
                <button class="btn btn-primary btn-xs" @click="saveTaskConfluenceLink(task.id)" :disabled="!taskConfluenceLinks[task.id]">저장</button>
              </div>
            </div>

            <!-- Questions and Answers -->
            <div v-for="qa in getQuestionsForTask(task.id)" :key="qa.id" class="mb-16">
              <div class="qa-item">
                <div class="question">
                  <span class="badge badge-orange">💬</span>
                  <strong>질문:</strong>
                  <span style="margin-left: 8px;">{{ qa.question }}</span>
                </div>
                <div v-if="qa.answer" class="answer mt-8">
                  <span class="badge badge-green">📝</span>
                  <strong>답변:</strong>
                  <span style="margin-left: 8px;">{{ qa.answer }}</span>
                  <span v-if="qa.answer_by" class="text-muted text-sm" style="margin-left: 8px;">({{ qa.answer_by }})</span>
                </div>
                <div v-else class="answer mt-8">
                  <span class="badge badge-gray">⏳</span>
                  <span class="text-muted">답변 대기중</span>
                </div>
              </div>
            </div>

            <!-- Add question form -->
            <div v-if="showQuestionForm === task.id" class="mt-16">
              <div class="form-group">
                <label class="form-label">새 질문</label>
                <textarea 
                  v-model="newQuestionText" 
                  class="form-control" 
                  rows="3" 
                  placeholder="과제에 대한 질문을 입력하세요..."
                ></textarea>
              </div>
              <div class="flex gap-8" style="justify-content: flex-end;">
                <button class="btn btn-ghost" @click="cancelQuestion">취소</button>
                <button class="btn btn-primary" @click="addQuestion(task.id)" :disabled="!newQuestionText">질문 추가</button>
              </div>
            </div>

            <div v-else class="mt-16">
              <button class="btn btn-ghost btn-sm" @click="openQuestionForm(task.id)">+ 질문 추가</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="toastMsg" class="toast">{{ toastMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// 새로운 데이터 구조
const tasks = ref([])
const objectives = ref([])
const staffList = ref([])
const loading = ref(false)
const toastMsg = ref('')

// Q&A 관련 상태
const questions = ref([])
const answers = ref([])

// 새로운 UI 상태
const selectedWeek = ref('')
const confluenceLink = ref('')
const taskConfluenceLinks = ref({}) // 과제별 컨플루언스 링크 저장
const showQuestionForm = ref('')
const newQuestionText = ref('')
const debounceTimers = {}

// 주차 관련 계산
const availableWeeks = computed(() => {
  // 현재 주차를 중심으로 앞뒤 4주 생성
  const currentWeekNum = getCurrentWeekNumber()
  const weeks = []
  for (let i = Math.max(1, currentWeekNum - 4); i <= currentWeekNum + 4; i++) {
    weeks.push(`W${i}`)
  }
  return weeks
})

const tasksForSelectedWeek = computed(() => {
  // 현재 선택된 주차에 해당하는 모든 과제 반환
  // 실제 구현에서는 progress 데이터에서 해당 주차의 과제를 필터링
  return tasks.value
})

function getCurrentWeekNumber() {
  const today = new Date()
  const firstDayOfYear = new Date(today.getFullYear(), 0, 1)
  const pastDaysOfYear = (today - firstDayOfYear) / 86400000
  return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7)
}

function getCurrentWeekIndex() {
  if (!selectedWeek.value) return -1
  return availableWeeks.value.indexOf(selectedWeek.value)
}

function prevWeek() {
  const currentIndex = getCurrentWeekIndex()
  if (currentIndex > 0) {
    selectedWeek.value = availableWeeks.value[currentIndex - 1]
    onWeekChange()
  }
}

function nextWeek() {
  const currentIndex = getCurrentWeekIndex()
  if (currentIndex < availableWeeks.value.length - 1) {
    selectedWeek.value = availableWeeks.value[currentIndex + 1]
    onWeekChange()
  }
}

function getObjectiveName(objectiveId) {
  const objective = objectives.value.find(obj => obj.id === objectiveId)
  return objective ? objective.name : objectiveId
}

function showToast(msg) {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = '' }, 2000)
}

// Q&A 관련 함수
function getQuestionsForTask(taskId) {
  // 특정 과제에 대한 모든 질문과 답변 반환
  const taskQuestions = questions.value.filter(q => q.task_id === taskId)
  return taskQuestions.map(q => {
    const answer = answers.value.find(a => a.question_id === q.id)
    return {
      ...q,
      answer: answer ? answer.answer : '',
      answer_by: answer ? answer.answer_by : ''
    }
  })
}

function openQuestionForm(taskId) {
  showQuestionForm.value = taskId
  newQuestionText.value = ''
}

function cancelQuestion() {
  showQuestionForm.value = ''
  newQuestionText.value = ''
}

async function addQuestion(taskId) {
  if (!newQuestionText.value.trim()) return
  
  try {
    const questionData = {
      task_id: taskId,
      question: newQuestionText.value,
      created_at: new Date().toISOString()
    }
    
    // 실제 구현에서는 API 호출
    const newQuestion = {
      id: `Q${Date.now()}`,
      ...questionData
    }
    questions.value.push(newQuestion)
    
    showToast('질문이 추가되었습니다')
    cancelQuestion()
  } catch {
    showToast('질문 추가 실패')
  }
}

function onWeekChange() {
  // 주차 변경 시 컨플루언스 링크 로드
  loadConfluenceLink()
}

function loadConfluenceLink() {
  // 실제 구현에서는 해당 주차의 컨플루언스 링크를 API에서 로드
  confluenceLink.value = ''
}

function debounceSaveConfluenceLink() {
  clearTimeout(debounceTimers.confluence)
  debounceTimers.confluence = setTimeout(saveConfluenceLink, 1000)
}

async function saveConfluenceLink() {
  if (!selectedWeek.value || !confluenceLink.value) return
  
  try {
    // 실제 구현에서는 API 호출로 컨플루언스 링크 저장
    showToast('컨플루언스 링크가 저장되었습니다')
  } catch {
    showToast('링크 저장 실패')
  }
}

function openConfluenceLink() {
  if (confluenceLink.value) {
    window.open(confluenceLink.value, '_blank')
  }
}

// 과제별 컨플루언스 링크 관련 함수
function getTaskConfluenceLink(taskId) {
  // 실제 구현에서는 API에서 과제별 컨플루언스 링크를 로드
  return taskConfluenceLinks.value[taskId] || ''
}

function updateTaskConfluenceLink(taskId, link) {
  taskConfluenceLinks.value[taskId] = link
}

function saveTaskConfluenceLink(taskId) {
  if (!taskConfluenceLinks.value[taskId]) return
  
  try {
    // 실제 구현에서는 API 호출로 과제별 컨플루언스 링크 저장
    showToast('과제 컨플루언스 링크가 저장되었습니다')
  } catch {
    showToast('링크 저장 실패')
  }
}

function openTaskConfluenceLink(taskId) {
  const link = getTaskConfluenceLink(taskId)
  if (link) {
    window.open(link, '_blank')
  }
}

async function fetchAll() {
  loading.value = true
  try {
    const [tRes, oRes, sRes] = await Promise.all([
      axios.get('/api/tasks'),
      axios.get('/api/okrs'),
      axios.get('/api/staff'),
    ])
    tasks.value = tRes.data
    objectives.value = oRes.data
    staffList.value = sRes.data
    
    // 기본으로 현재 주차 선택
    selectedWeek.value = `W${getCurrentWeekNumber()}`
    loadConfluenceLink()
  } finally {
    loading.value = false
  }
}

onMounted(fetchAll)
</script>
