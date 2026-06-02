/* work-management UI Kit — demo data (fake, realistic Korean OKR domain) */
window.KIT_DATA = {
  currentWeek: '2026-W21',
  lastWeek: '2026-W20',
  weeks: ['2026-W19', '2026-W20', '2026-W21'],
  user: { name: '김도윤', job_title: '파트장', role: 'part_leader', is_admin: true },

  notice:
    '<p>이번 주 <strong>주간 진행 현황</strong>은 <strong>금요일 15시</strong>까지 등록 부탁드립니다. ' +
    'OEE 향상 목표 관련 컨플루언스 링크는 과제별로 빠짐없이 연결해 주세요. ' +
    '미답변 의견/질문은 다음 회의 전까지 정리하겠습니다.</p>',

  staff: [
    { username: 'kim.dy',   name: '김도윤', job_title: '파트장',   task_ids: ['T-5'] },
    { username: 'lee.sy',   name: '이서연', job_title: '그룹장',   task_ids: ['T-4'] },
    { username: 'park.mj',  name: '박민준', job_title: '책임',     task_ids: ['T-1', 'T-1-1', 'T-1-2'] },
    { username: 'jung.he',  name: '정하은', job_title: '선임',     task_ids: ['T-2'] },
    { username: 'choi.wj',  name: '최우진', job_title: '선임',     task_ids: ['T-3', 'T-3-1', 'T-3-2'] },
  ],

  objectives: [
    { id: 'O-1', name: '설비 종합효율(OEE) 향상', status: '진행중',
      key_results: [
        { id: 'K-01', name: 'OEE 82% → 88% 달성' },
        { id: 'K-02', name: '비계획 정지시간 30% 감축' },
      ] },
    { id: 'O-2', name: '예지보전(PdM) 체계 구축', status: '진행중',
      key_results: [
        { id: 'K-03', name: '주요 설비 50대 진동센서 설치' },
        { id: 'K-04', name: '고장 예측 정확도 85% 달성' },
      ] },
    { id: 'O-3', name: '디지털 작업표준 전환', status: '위험',
      key_results: [
        { id: 'K-05', name: '현장 작업표준 200건 디지털화' },
      ] },
    { id: 'O-4', name: '설비 에너지 사용량 절감', status: '완료',
      key_results: [
        { id: 'K-06', name: '단위 에너지 원단위 12% 절감' },
      ] },
  ],

  tasks: [
    { id: 'T-1', name: 'OEE 데이터 수집 자동화', objective_id: 'O-1', owner: '박민준',
      sub_tasks: [
        { id: 'T-1-1', name: '설비 IoT 게이트웨이 설치', owner: '박민준' },
        { id: 'T-1-2', name: 'MES 실시간 연동', owner: '박민준' },
      ] },
    { id: 'T-2', name: '비계획 정지 원인 분석', objective_id: 'O-1', owner: '정하은', sub_tasks: [] },
    { id: 'T-3', name: '진동센서 예지보전 파일럿', objective_id: 'O-2', owner: '최우진',
      sub_tasks: [
        { id: 'T-3-1', name: '센서 모델 선정 및 발주', owner: '최우진' },
        { id: 'T-3-2', name: '베어링 진단 알고리즘 검증', owner: '최우진' },
      ] },
    { id: 'T-4', name: '작업표준 디지털화', objective_id: 'O-3', owner: '이서연', sub_tasks: [] },
    { id: 'T-5', name: '에너지 모니터링 대시보드', objective_id: 'O-4', owner: '김도윤', sub_tasks: [] },
  ],

  issues: [
    { id: 'I-01', task_id: 'T-1-1', week: '2026-W21', assignee: '박민준',
      issue: '게이트웨이 12대 중 9대 설치 완료. 노후 라인 3대는 전원 공사 일정 협의 중으로 다음 주 설치 예정입니다.',
      created_at: '2026-05-19 10:24:00', comments: [
        { id: 'C-1', comment_by: '김도윤', comment: '전원 공사는 설비보전팀과 협의되었나요? 일정 확정되면 공유 부탁합니다.', created_at: '2026-05-19 14:02:00', replies: [
          { id: 'R-1', comment_by: '박민준', comment: '네, 수요일 오전으로 협의 완료했습니다.', created_at: '2026-05-19 15:10:00' },
        ] },
      ] },
    { id: 'I-02', task_id: 'T-3-2', week: '2026-W21', assignee: '최우진',
      issue: '베어링 진단 알고리즘 1차 검증 결과 정확도 78%. 정상/이상 라벨링 데이터가 부족하여 추가 수집이 필요합니다.',
      created_at: '2026-05-20 09:40:00', comments: [] },
    { id: 'I-03', task_id: 'T-4', week: '2026-W20', assignee: '이서연',
      issue: '작업표준 디지털화 진척이 더딥니다. 현장 검토 인력 부족으로 일정 재조정이 필요합니다. (위험)',
      created_at: '2026-05-13 16:12:00', comments: [] },
    { id: 'I-04', task_id: 'T-2', week: '2026-W20', assignee: '정하은',
      issue: '비계획 정지 상위 3개 원인 도출 완료. 1순위는 자재 공급 지연으로 확인되었습니다.',
      created_at: '2026-05-14 11:05:00', comments: [] },
  ],

  questions: [
    { id: 'Q-01', task_id: 'T-1-2', week: '2026-W21', questioner: '김도윤', targets: ['박민준'],
      question: 'MES 연동 시 데이터 적재 주기는 어떻게 설정할 예정인가요? 실시간 OEE 산출에 영향이 있을 것 같습니다.',
      answers: [] },
    { id: 'Q-02', task_id: 'T-3-1', week: '2026-W21', questioner: '이서연', targets: ['최우진'],
      question: '센서 발주 예산이 당초 계획 대비 초과되지 않았는지 확인 부탁드립니다.',
      answers: [] },
    { id: 'Q-03', task_id: 'T-2', week: '2026-W20', questioner: '김도윤', targets: ['정하은'],
      question: '자재 공급 지연 건은 구매팀과 공유되었나요?',
      answers: [
        { id: 'A-1', answer: '네, 구매팀에 공식 요청서를 전달했고 안전재고 기준 상향을 검토 중입니다.', answered_by: '정하은', created_at: '2026-05-15 09:30:00' },
      ] },
    { id: 'Q-04', task_id: 'T-1-1', week: '2026-W20', questioner: '이서연', targets: ['박민준'],
      question: '게이트웨이 설치 시 라인 가동 중단이 필요한가요?',
      answers: [
        { id: 'A-2', answer: '비가동 시간대에 설치하여 라인 중단 없이 진행했습니다.', answered_by: '박민준', created_at: '2026-05-14 13:20:00' },
      ] },
  ],

  confluence: [
    { task_id: 'T-1',   week: '2026-W21', url: '#' },
    { task_id: 'T-1-1', week: '2026-W21', url: '#' },
    { task_id: 'T-3',   week: '2026-W21', url: '#' },
    { task_id: 'T-5',   week: '2026-W21', url: '#' },
    { task_id: 'T-1',   week: '2026-W20', url: '#' },
    { task_id: 'T-2',   week: '2026-W20', url: '#' },
    { task_id: 'T-3',   week: '2026-W19', url: '#' },
  ],
};
