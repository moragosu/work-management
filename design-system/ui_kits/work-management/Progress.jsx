/* work-management UI Kit — Progress (주간 진행 현황) view */
const { useState: useProgState } = React;

function Progress() {
  const D = window.KIT_DATA;
  const [week, setWeek] = useProgState(D.currentWeek);
  const [issues, setIssues] = useProgState(D.issues);
  const [questions, setQuestions] = useProgState(D.questions);
  const [toast, setToast] = useProgState('');
  const [addingFor, setAddingFor] = useProgState(null);
  const [draft, setDraft] = useProgState('');
  const [answeringFor, setAnsweringFor] = useProgState(null);
  const [answerDraft, setAnswerDraft] = useProgState('');

  const weekIdx = D.weeks.indexOf(week);
  function shiftWeek(d) { const i = weekIdx + d; if (i >= 0 && i < D.weeks.length) setWeek(D.weeks[i]); }
  function flash(m) { setToast(m); setTimeout(() => setToast(''), 1800); }

  const flatRows = [];
  D.tasks.forEach(t => {
    if (t.sub_tasks && t.sub_tasks.length) t.sub_tasks.forEach(st => flatRows.push({ id: st.id, name: st.name, parent: t.name, owner: st.owner }));
    else flatRows.push({ id: t.id, name: t.name, parent: null, owner: t.owner });
  });

  function addIssue(taskId) {
    if (!draft.trim()) return;
    const it = { id: 'I-' + Date.now(), task_id: taskId, week, assignee: D.user.name, issue: draft.trim(), created_at: '방금 전', comments: [] };
    setIssues([...issues, it]); setDraft(''); setAddingFor(null); flash('이슈가 등록되었습니다');
  }
  function submitAnswer(qId) {
    if (!answerDraft.trim()) return;
    setQuestions(questions.map(q => q.id === qId ? { ...q, answers: [...q.answers, { id: 'A-' + Date.now(), answer: answerDraft.trim(), answered_by: D.user.name, created_at: '방금 전' }] } : q));
    setAnswerDraft(''); setAnsweringFor(null); flash('답변이 등록되었습니다');
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>주간 진행 현황</h2>
          <div className="subtitle">과제별 진행 현황 · 이슈 · 의견/질문을 주차별로 관리합니다</div>
        </div>
        <div className="week-nav">
          <button className="icon-btn" onClick={() => shiftWeek(-1)} disabled={weekIdx <= 0}><Icon name="chevron_left" size={18} /></button>
          <span className="week-label">{formatWeekLabel(week)}</span>
          <button className="icon-btn" onClick={() => shiftWeek(1)} disabled={weekIdx >= D.weeks.length - 1}><Icon name="chevron_right" size={18} /></button>
        </div>
      </div>

      <div className="page-body">
        <div className="prog-list">
          {flatRows.map(row => {
            const taskIssues = issues.filter(i => i.task_id === row.id && i.week === week);
            const taskQs = questions.filter(q => q.task_id === row.id && q.week === week);
            return (
              <Card key={row.id} className="prog-task-card">
                <div className="prog-task-head">
                  <div className="flex-center gap-8" style={{ minWidth: 0 }}>
                    {row.parent && <span className="matrix-parent">{row.parent} › </span>}
                    <span className="prog-task-name">{row.name}</span>
                    <Badge kind="gray">{row.owner}</Badge>
                  </div>
                  <a className="conf-link" href="#" onClick={e => e.preventDefault()}><Icon name="link" size={14} />컨플루언스</a>
                </div>

                {/* Issues section */}
                <div className="prog-section">
                  <div className="section-label"><Icon name="warning" className="section-icon" size={14} />진행 현황 및 이슈</div>
                  {taskIssues.length === 0 && addingFor !== row.id && <div className="prog-empty">등록된 이슈가 없습니다</div>}
                  {taskIssues.map(iss => (
                    <div key={iss.id} className="issue-block">
                      <div className="issue-box"><div className="prose">{iss.issue}</div></div>
                      <div className="meta-row">
                        <Badge kind="gray">{iss.assignee}</Badge>
                        <span className="meta-date">{iss.created_at}</span>
                      </div>
                      {(iss.comments || []).map(c => (
                        <div key={c.id} className="comment-item">
                          <div className="meta-row"><Badge kind="gray">{c.comment_by}</Badge><span className="meta-date">{c.created_at}</span></div>
                          <div className="prose comment-text">{c.comment}</div>
                          {(c.replies || []).map(r => (
                            <div key={r.id} className="reply-item">
                              <div className="reply-line" />
                              <div style={{ flex: 1 }}>
                                <div className="meta-row"><Badge kind="gray">{r.comment_by}</Badge><span className="meta-date">{r.created_at}</span></div>
                                <div className="prose comment-text">{r.comment}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ))}
                      <AddButton icon="chat_bubble_outline" onClick={() => flash('댓글 입력 (데모)')}>댓글</AddButton>
                    </div>
                  ))}
                  {addingFor === row.id ? (
                    <div className="editor-box">
                      <textarea className="form-control" rows={3} value={draft} onChange={e => setDraft(e.target.value)} placeholder="이번 주 진행 현황 및 이슈를 입력하세요..." autoFocus />
                      <div className="flex gap-8" style={{ justifyContent: 'flex-end', marginTop: 8 }}>
                        <Button variant="ghost" size="sm" onClick={() => { setAddingFor(null); setDraft(''); }}>취소</Button>
                        <Button variant="primary" size="sm" disabled={!draft.trim()} onClick={() => addIssue(row.id)}>저장</Button>
                      </div>
                    </div>
                  ) : (
                    <div style={{ marginTop: 8 }}><AddButton onClick={() => { setAddingFor(row.id); setDraft(''); }}>진행 현황 및 이슈 등록</AddButton></div>
                  )}
                </div>

                {/* Q&A section */}
                <div className="prog-section" style={{ borderBottom: 'none', marginBottom: 0, paddingBottom: 0 }}>
                  <div className="section-label"><Icon name="forum" className="section-icon" size={14} />의견/질문</div>
                  {taskQs.length === 0 && <div className="prog-empty">등록된 의견/질문이 없습니다</div>}
                  {taskQs.map(q => (
                    <div key={q.id} className="qna-block">
                      <div className="q-targets-row">
                        <Badge kind="purple">{q.questioner}</Badge>
                        <Icon name="arrow_forward" className="q-targets-icon" size={13} />
                        {q.targets.map(t => <span key={t} className="q-target-badge">{t}</span>)}
                      </div>
                      <div className="prose q-text">{q.question}</div>
                      {q.answers.map(a => (
                        <div key={a.id} className="answer-block-prog">
                          <div className="meta-row"><Badge kind="green">{a.answered_by}</Badge><span className="meta-date">{a.created_at}</span></div>
                          <div className="prose">{a.answer}</div>
                        </div>
                      ))}
                      {answeringFor === q.id ? (
                        <div className="editor-box">
                          <textarea className="form-control" rows={2} value={answerDraft} onChange={e => setAnswerDraft(e.target.value)} placeholder="답변을 입력하세요..." autoFocus />
                          <div className="flex gap-8" style={{ justifyContent: 'flex-end', marginTop: 8 }}>
                            <Button variant="ghost" size="sm" onClick={() => { setAnsweringFor(null); setAnswerDraft(''); }}>취소</Button>
                            <Button variant="primary" size="sm" disabled={!answerDraft.trim()} onClick={() => submitAnswer(q.id)}>등록</Button>
                          </div>
                        </div>
                      ) : (
                        <div style={{ marginTop: 6 }}><AddButton icon="reply" onClick={() => { setAnsweringFor(q.id); setAnswerDraft(''); }}>답변하기</AddButton></div>
                      )}
                    </div>
                  ))}
                </div>
              </Card>
            );
          })}
        </div>
      </div>
      <Toast message={toast} />
    </div>
  );
}

Object.assign(window, { Progress });
