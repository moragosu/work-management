/* work-management UI Kit — Admin (관리 도구) view */
const { useState: useAdminState } = React;

function Admin() {
  const D = window.KIT_DATA;
  const [tab, setTab] = useAdminState('objectives');
  const [adminMode, setAdminMode] = useAdminState(true);

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>관리 도구</h2>
          <div className="subtitle">목표 · 과제 · 파트원 정보를 관리합니다</div>
        </div>
        <div className="flex-center gap-8">
          <span className="text-sm text-muted">관리자 모드</span>
          <Toggle on={adminMode} onChange={setAdminMode} />
        </div>
      </div>

      <div className="page-body">
        <div className="tabs">
          <button className={'tab' + (tab === 'objectives' ? ' active' : '')} onClick={() => setTab('objectives')}>목표 · KR</button>
          <button className={'tab' + (tab === 'tasks' ? ' active' : '')} onClick={() => setTab('tasks')}>과제</button>
          <button className={'tab' + (tab === 'staff' ? ' active' : '')} onClick={() => setTab('staff')}>파트원</button>
        </div>

        {tab === 'objectives' && (
          <Card>
            <div className="card-header">
              <h3>목표 (Objectives)</h3>
              <Button variant="primary" size="sm" icon="add">목표 추가</Button>
            </div>
            <div className="table-wrap">
              <table>
                <thead><tr><th style={{ width: 70 }}>ID</th><th>목표명</th><th>Key Results</th><th style={{ width: 90 }}>상태</th><th style={{ width: 90 }}>관리</th></tr></thead>
                <tbody>
                  {D.objectives.map(o => (
                    <tr key={o.id}>
                      <td style={{ verticalAlign: 'middle' }}><span className="obj-id-badge" style={{ width: 30, height: 30, fontSize: 12 }}>{o.id}</span></td>
                      <td style={{ verticalAlign: 'middle', fontWeight: 600 }}>{o.name}</td>
                      <td><div className="flex" style={{ flexDirection: 'column', gap: 4 }}>{o.key_results.map(k => <div key={k.id} className="flex-center gap-8"><Badge kind="blue" style={{ width: 40, justifyContent: 'center' }}>{k.id}</Badge><span className="text-sm">{k.name}</span></div>)}</div></td>
                      <td style={{ verticalAlign: 'middle' }}><span className={statusBadgeClass(o.status)}>{o.status}</span></td>
                      <td style={{ verticalAlign: 'middle' }}><div className="flex gap-4"><Button variant="ghost" size="xs">수정</Button></div></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {tab === 'tasks' && (
          <Card>
            <div className="card-header">
              <h3>과제 · 소과제</h3>
              <Button variant="primary" size="sm" icon="add">과제 추가</Button>
            </div>
            <div className="table-wrap">
              <table>
                <thead><tr><th style={{ width: 70 }}>ID</th><th>과제명</th><th style={{ width: 120 }}>연결 목표</th><th style={{ width: 90 }}>담당</th><th style={{ width: 90 }}>관리</th></tr></thead>
                <tbody>
                  {D.tasks.map(t => (
                    <React.Fragment key={t.id}>
                      <tr>
                        <td style={{ verticalAlign: 'middle' }}><span className="badge badge-gray" style={{ fontFamily: 'var(--font-mono)' }}>{t.id}</span></td>
                        <td style={{ verticalAlign: 'middle', fontWeight: 600 }}>{t.name}</td>
                        <td style={{ verticalAlign: 'middle' }}><Badge kind="blue">{t.objective_id}</Badge></td>
                        <td style={{ verticalAlign: 'middle' }}>{t.owner}</td>
                        <td style={{ verticalAlign: 'middle' }}><Button variant="ghost" size="xs">수정</Button></td>
                      </tr>
                      {(t.sub_tasks || []).map(st => (
                        <tr key={st.id} className="subtask-row">
                          <td style={{ verticalAlign: 'middle' }}><span className="badge badge-gray" style={{ fontFamily: 'var(--font-mono)' }}>{st.id}</span></td>
                          <td style={{ verticalAlign: 'middle' }}><span className="subtask-indent">└</span>{st.name}</td>
                          <td></td>
                          <td style={{ verticalAlign: 'middle' }}>{st.owner}</td>
                          <td style={{ verticalAlign: 'middle' }}><Button variant="ghost" size="xs">수정</Button></td>
                        </tr>
                      ))}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {tab === 'staff' && (
          <Card>
            <div className="card-header">
              <h3>파트원</h3>
              <Button variant="primary" size="sm" icon="person_add">파트원 추가</Button>
            </div>
            <div className="table-wrap">
              <table>
                <thead><tr><th>이름</th><th>직급</th><th>아이디</th><th>담당 과제 수</th><th style={{ width: 90 }}>관리</th></tr></thead>
                <tbody>
                  {D.staff.map(s => (
                    <tr key={s.username}>
                      <td style={{ verticalAlign: 'middle' }}><div className="member-cell"><Avatar name={s.name} /><span className="member-name">{s.name}</span></div></td>
                      <td style={{ verticalAlign: 'middle' }}>{s.job_title}</td>
                      <td style={{ verticalAlign: 'middle', fontFamily: 'var(--font-mono)', fontSize: 13 }}>{s.username}</td>
                      <td style={{ verticalAlign: 'middle' }}><Badge kind="gray">{(s.task_ids || []).length}건</Badge></td>
                      <td style={{ verticalAlign: 'middle' }}><div className="flex gap-4"><Button variant="ghost" size="xs">수정</Button><Button variant="danger" size="xs">삭제</Button></div></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}

Object.assign(window, { Admin });
