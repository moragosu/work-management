/* work-management UI Kit — Dashboard view */
const { useState: useDashState, useMemo } = React;

function Dashboard() {
  const D = window.KIT_DATA;
  const [qWeek, setQWeek] = useDashState('this');
  const [qStatus, setQStatus] = useDashState('unanswered');
  const [issWeek, setIssWeek] = useDashState('this');
  const [actWeek, setActWeek] = useDashState('this');
  const [qOpen, setQOpen] = useDashState(false);
  const [issOpen, setIssOpen] = useDashState(false);
  const [activityOpen, setActivityOpen] = useDashState(true);
  const [matrixOpen, setMatrixOpen] = useDashState(true);
  const [modal, setModal] = useDashState(null); // {type, item}

  const weekOf = sel => (sel === 'last' ? D.lastWeek : D.currentWeek);

  // flat task rows (sub-tasks flattened)
  const flatRows = useMemo(() => {
    const rows = [];
    D.tasks.forEach(t => {
      if (t.sub_tasks && t.sub_tasks.length) t.sub_tasks.forEach(st => rows.push({ id: st.id, selfName: st.name, parentName: t.name }));
      else rows.push({ id: t.id, selfName: t.name, parentName: null });
    });
    return rows;
  }, []);

  function taskName(id) {
    const direct = D.tasks.find(t => t.id === id);
    if (direct) return direct.name;
    for (const t of D.tasks) { const st = (t.sub_tasks || []).find(s => s.id === id); if (st) return `${t.name} › ${st.name}`; }
    return id;
  }

  const unanswered = D.questions.filter(q => !q.answers.length);
  const weekIssues = D.issues.filter(i => i.week === D.currentWeek);
  const confThisWeek = flatRows.filter(r => D.confluence.some(c => c.task_id === r.id && c.week === D.currentWeek)).length;

  const filteredQ = D.questions.filter(q => q.week === weekOf(qWeek)).filter(q =>
    qStatus === 'answered' ? q.answers.length : qStatus === 'all' ? true : !q.answers.length);
  const filteredIss = D.issues.filter(i => i.week === weekOf(issWeek));

  // member stats
  const memberStats = useMemo(() => {
    const w = weekOf(actWeek);
    const map = {};
    D.staff.forEach(s => {
      const received = D.questions.filter(q => q.week === w && q.targets.includes(s.name));
      const answered = received.filter(q => q.answers.length).length;
      map[s.name] = {
        tasks: (s.task_ids || []).length,
        issues: D.issues.filter(i => i.week === w && i.assignee === s.name).length,
        answered, unanswered: received.length - answered,
      };
    });
    return map;
  }, [actWeek]);
  const maxTasks = Math.max(1, ...D.staff.map(s => memberStats[s.name].tasks));
  const maxIssues = Math.max(1, ...D.staff.map(s => memberStats[s.name].issues));

  function matrixCell(rowId, w) {
    const conf = D.confluence.some(c => c.task_id === rowId && c.week === w);
    const iss = D.issues.some(i => i.task_id === rowId && i.week === w);
    const qn = D.questions.filter(q => q.task_id === rowId && q.week === w).length;
    return { conf, iss, qn };
  }

  const strip = t => (t || '').replace(/<[^>]+>/g, '').replace(/\*\*/g, '');

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>대시보드</h2>
          <div className="subtitle">{D.currentWeek} · 2026년 5월 21일 목요일</div>
        </div>
        <Button variant="ghost" size="sm" icon="refresh">새로고침</Button>
      </div>

      <div className="page-body">
        {/* KPIs */}
        <div className="grid-3" style={{ marginBottom: 24 }}>
          <Card className={'stat-accent ' + (unanswered.length ? 'stat-accent-orange' : 'stat-accent-green')}>
            <div className="card-body stat-card">
              <Icon name="quiz" fill className={unanswered.length ? 'stat-icon stat-icon-orange' : 'stat-icon stat-icon-green'} size={28} />
              <div className="stat-value" style={{ color: unanswered.length ? 'var(--orange)' : 'var(--success)' }}>{unanswered.length}</div>
              <div className="stat-label">미답변 의견/질문 (전체)</div>
            </div>
          </Card>
          <Card className={'stat-accent ' + (weekIssues.length ? 'stat-accent-yellow' : 'stat-accent-green')}>
            <div className="card-body stat-card">
              <Icon name="warning" fill className={weekIssues.length ? 'stat-icon stat-icon-yellow' : 'stat-icon stat-icon-green'} size={28} />
              <div className="stat-value" style={{ color: weekIssues.length ? 'var(--warning)' : 'var(--success)' }}>{weekIssues.length}</div>
              <div className="stat-label">이번 주 진행 현황 및 이슈</div>
            </div>
          </Card>
          <Card className="stat-accent stat-accent-blue">
            <div className="card-body stat-card">
              <Icon name="link" fill className="stat-icon stat-icon-blue" size={28} />
              <div className="stat-value" style={{ color: 'var(--primary)' }}>{confThisWeek}<span className="stat-denom">/{flatRows.length}</span></div>
              <div className="stat-label">컨플루언스 등록</div>
              <div className="stat-mini-bar"><div className="stat-mini-fill" style={{ width: Math.round(confThisWeek / flatRows.length * 100) + '%' }} /></div>
            </div>
          </Card>
        </div>

        {/* Notice */}
        <Card className="notice-card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <div className="panel-title">
              <span className="panel-icon" style={{ background: '#eff6ff', color: 'var(--primary)' }}><Icon name="campaign" size={16} /></span>
              파트 공지
            </div>
            <Button variant="ghost" size="xs">수정</Button>
          </div>
          <div className="card-body" style={{ padding: 16 }}>
            <div className="prose" dangerouslySetInnerHTML={{ __html: D.notice }} />
          </div>
        </Card>

        {/* Action panels */}
        <div className="grid-2" style={{ marginBottom: 24, alignItems: 'start' }}>
          <Card className="action-panel">
            <div className="card-header panel-header-toggle" onClick={() => setQOpen(!qOpen)}>
              <div className="panel-title">
                <span className="panel-icon" style={{ background: '#fff7ed', color: 'var(--orange)' }}><Icon name="forum" size={16} /></span>
                의견/질문
              </div>
              <div onClick={e => e.stopPropagation()}>
                <FilterGroup value={qWeek} onChange={setQWeek} options={[{ value: 'last', label: '지난주' }, { value: 'this', label: '이번주' }]} />
              </div>
              <div onClick={e => e.stopPropagation()}>
                <FilterGroup value={qStatus} onChange={setQStatus} options={[{ value: 'unanswered', label: '미답변' }, { value: 'answered', label: '답변완료' }, { value: 'all', label: '전체' }]} />
              </div>
              <Badge kind={filteredQ.length ? (qStatus === 'answered' ? 'green' : 'orange') : 'gray'}>{filteredQ.length}건</Badge>
              <Icon name="expand_more" className={'section-chevron' + (qOpen ? ' open' : '')} />
            </div>
            <div className="card-body panel-body">
              {filteredQ.length === 0 ? (
                <div className="panel-empty">{qStatus === 'answered' ? '답변 완료된 의견/질문이 없습니다' : '미답변 의견/질문이 없습니다 👍'}</div>
              ) : (
                <ul className={'panel-list' + (qOpen ? ' panel-list-expanded' : '')}>
                  {filteredQ.map(q => (
                    <li key={q.id} className="panel-item panel-item-link" onClick={() => setModal({ type: 'question', item: q })}>
                      <div className="q-targets-row">
                        <Badge kind="purple" style={{ fontSize: 11 }}>{q.questioner}</Badge>
                        <Icon name="arrow_forward" className="q-targets-icon" size={13} />
                        {q.targets.map(t => <span key={t} className="q-target-badge">{t}</span>)}
                      </div>
                      <div className="panel-item-main">{strip(q.question)}</div>
                      <div className="panel-item-sub">
                        <Badge kind="blue">{taskName(q.task_id)}</Badge>
                        <Badge kind="gray">{formatWeekLabel(q.week)}</Badge>
                        <span className="panel-goto">상세보기 →</span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </Card>

          <Card className="action-panel">
            <div className="card-header panel-header-toggle" onClick={() => setIssOpen(!issOpen)}>
              <div className="panel-title">
                <span className="panel-icon" style={{ background: '#fff7ed', color: 'var(--warning)' }}><Icon name="construction" size={16} /></span>
                진행 현황 및 이슈
              </div>
              <div onClick={e => e.stopPropagation()}>
                <FilterGroup value={issWeek} onChange={setIssWeek} options={[{ value: 'last', label: '지난주' }, { value: 'this', label: '이번주' }]} />
              </div>
              <Badge kind={filteredIss.length ? 'yellow' : 'gray'}>{filteredIss.length}건</Badge>
              <Icon name="expand_more" className={'section-chevron' + (issOpen ? ' open' : '')} />
            </div>
            <div className="card-body panel-body">
              {filteredIss.length === 0 ? (
                <div className="panel-empty">등록된 진행 현황 및 이슈가 없습니다 👍</div>
              ) : (
                <ul className={'panel-list' + (issOpen ? ' panel-list-expanded' : '')}>
                  {filteredIss.map(p => (
                    <li key={p.id} className="panel-item panel-item-link" onClick={() => setModal({ type: 'issue', item: p })}>
                      <div className="panel-item-main">{strip(p.issue)}</div>
                      <div className="panel-item-sub">
                        <Badge kind="blue">{taskName(p.task_id)}</Badge>
                        <Badge kind="gray">{p.assignee}</Badge>
                        <span className="panel-goto">상세보기 →</span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </Card>
        </div>

        {/* Side-by-side: activity + matrix */}
        <div className="side-panel-grid">
          <div className="side-panel-col">
            <div className="section-header section-header-toggle" onClick={() => setActivityOpen(!activityOpen)}>
              <span className="section-header-title">파트원별 활동 현황</span>
              <span className="panel-count-badge">파트원 {D.staff.length}명</span>
              <div onClick={e => e.stopPropagation()} style={{ marginLeft: 8 }}>
                <FilterGroup value={actWeek} onChange={setActWeek} options={[{ value: 'last', label: '지난주' }, { value: 'this', label: '이번주' }]} />
              </div>
              <Icon name="expand_more" className={'section-chevron' + (activityOpen ? ' open' : '')} />
            </div>
            {activityOpen && (
              <Card className="panel-card">
                <div className="activity-scroll">
                  <table>
                    <thead><tr><th>파트원</th><th>담당 과제</th><th>이슈</th><th>답변 현황</th></tr></thead>
                    <tbody>
                      {D.staff.map(s => {
                        const m = memberStats[s.name];
                        const tot = m.answered + m.unanswered;
                        return (
                          <tr key={s.username} style={{ cursor: 'default' }}>
                            <td style={{ verticalAlign: 'middle' }}>
                              <div className="member-cell"><Avatar name={s.name} /><div><div className="member-name">{s.name}</div><div className="member-role">{s.job_title}</div></div></div>
                            </td>
                            <td style={{ verticalAlign: 'middle' }}><div className="stat-bar-row"><span className="stat-num">{m.tasks}</span><div className="stat-bar"><div className="stat-fill" style={{ width: barW(m.tasks, maxTasks), background: 'var(--primary)' }} /></div></div></td>
                            <td style={{ verticalAlign: 'middle' }}><div className="stat-bar-row"><span className="stat-num">{m.issues}</span><div className="stat-bar"><div className="stat-fill" style={{ width: barW(m.issues, maxIssues), background: 'var(--orange)' }} /></div></div></td>
                            <td style={{ verticalAlign: 'middle' }}><div className="stat-bar-row"><span className="stat-num" style={{ color: '#059669' }}>{m.answered}</span><div className="stat-bar stat-bar-dual"><div className="stat-fill" style={{ width: tot ? (m.answered / tot * 100) + '%' : 0, background: 'var(--success)' }} /><div className="stat-fill" style={{ width: tot ? (m.unanswered / tot * 100) + '%' : 0, background: '#f97316' }} /></div><span className="stat-num" style={{ color: '#f97316' }}>{m.unanswered}</span></div></td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </Card>
            )}
          </div>

          <div className="side-panel-col">
            <div className="section-header section-header-toggle" onClick={() => setMatrixOpen(!matrixOpen)}>
              <span className="section-header-title">주간 등록 현황</span>
              <span className="panel-count-badge">과제 {flatRows.length}건</span>
              <div className="matrix-legend-inline">
                <Icon name="link" fill className="matrix-icon matrix-icon-link" size={13} /><span>컨플루언스</span>
                <Icon name="warning" fill className="matrix-icon matrix-icon-issue" size={13} /><span>이슈</span>
                <span className="matrix-count" style={{ minWidth: 16, height: 16, fontSize: 10 }}>N</span><span>질문</span>
              </div>
              <Icon name="expand_more" className={'section-chevron' + (matrixOpen ? ' open' : '')} />
            </div>
            {matrixOpen && (
              <Card className="panel-card" style={{ overflow: 'hidden' }}>
                <div className="matrix-wrap">
                  <table className="matrix-table">
                    <thead><tr><th className="matrix-task-th">과제</th>{D.weeks.map(w => <th key={w} className={'matrix-week-th' + (w === D.currentWeek ? ' matrix-col-current' : '')}>{formatWeekLabel(w)}</th>)}</tr></thead>
                    <tbody>
                      {flatRows.map(row => (
                        <tr key={row.id}>
                          <td className="matrix-task-td">{row.parentName && <span className="matrix-parent">{row.parentName} › </span>}{row.selfName}</td>
                          {D.weeks.map(w => {
                            const c = matrixCell(row.id, w);
                            const empty = !c.conf && !c.iss && !c.qn;
                            return (
                              <td key={w} className={'matrix-cell' + (w === D.currentWeek ? ' matrix-col-current' : '')}>
                                <div className="matrix-cell-icons">
                                  {c.conf && <Icon name="link" fill className="matrix-icon matrix-icon-link" size={14} />}
                                  {c.iss && <Icon name="warning" fill className="matrix-icon matrix-icon-issue" size={14} />}
                                  {c.qn > 0 && <span className="matrix-count">{c.qn}</span>}
                                  {empty && <span className="matrix-dot-no">–</span>}
                                </div>
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            )}
          </div>
        </div>

        {/* Objectives */}
        <div className="section-header" style={{ marginTop: 32, marginBottom: 12 }}>
          <span className="section-header-title">목표 현황</span>
        </div>
        <div className="grid-2" style={{ gap: 16 }}>
          {D.objectives.map(obj => (
            <Card key={obj.id} className="obj-card">
              <div className="card-header">
                <div className="flex-center gap-8" style={{ minWidth: 0, flex: 1 }}>
                  <span className="obj-id-badge">{obj.id}</span>
                  <span className="obj-name">{obj.name}</span>
                </div>
                <span className={statusBadgeClass(obj.status)} style={{ flexShrink: 0 }}>{obj.status}</span>
              </div>
              <div className="card-body" style={{ padding: '12px 16px' }}>
                <div className="kr-section-title">Key Results <span className="text-muted">({obj.key_results.length})</span></div>
                <div className="kr-list">
                  {obj.key_results.map(kr => (
                    <div key={kr.id} className="kr-item">
                      <Badge kind="blue" style={{ width: 40, justifyContent: 'center' }}>{kr.id}</Badge>
                      <span className="text-sm">{kr.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {modal && <DetailModal modal={modal} taskName={taskName} onClose={() => setModal(null)} />}
    </div>
  );
}

function barW(v, max) { return !v ? '0%' : Math.max(3, Math.round(v / max * 100)) + '%'; }

function DetailModal({ modal, taskName, onClose }) {
  const it = modal.item;
  return (
    <Modal title={modal.type === 'issue' ? '진행 현황 및 이슈 상세' : '질문 상세'} onClose={onClose} width={580}
      footer={<><Button variant="ghost" size="sm" onClick={onClose}>닫기</Button><Button variant="primary" size="sm">진행현황에서 보기 →</Button></>}>
      <div className="modal-meta">
        <Badge kind="blue">{taskName(it.task_id)}</Badge>
        {it.assignee && <Badge kind="gray">{it.assignee}</Badge>}
        {it.questioner && <Badge kind="purple">{it.questioner}</Badge>}
        {it.targets && it.targets.map(t => <Badge key={t} kind="blue">{t}</Badge>)}
        <Badge kind="gray">{formatWeekLabel(it.week)}</Badge>
      </div>
      <div className="modal-body">
        {modal.type === 'issue' ? (
          <div className="prose">{it.issue}</div>
        ) : (
          <>
            <div className="prose" style={{ marginBottom: 16 }}>{it.question}</div>
            {it.answers.length ? (
              <>
                <div className="modal-a-label">답변</div>
                {it.answers.map(a => <div key={a.id} className="prose answer-block">{a.answer}</div>)}
              </>
            ) : <div className="no-answer">아직 답변이 없습니다.</div>}
          </>
        )}
      </div>
    </Modal>
  );
}

Object.assign(window, { Dashboard });
