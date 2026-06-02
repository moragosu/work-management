/* work-management UI Kit — Login screen */
const { useState: useLoginState } = React;

function Login({ onLogin }) {
  const [username, setUsername] = useLoginState('kim.dy');
  const [password, setPassword] = useLoginState('demo1234');
  const [error, setError] = useLoginState('');
  const [loading, setLoading] = useLoginState(false);

  function submit(e) {
    e.preventDefault();
    setError('');
    if (!username.trim() || !password) { setError('아이디와 비밀번호를 입력하세요'); return; }
    setLoading(true);
    setTimeout(() => { setLoading(false); onLogin(); }, 650);
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <div className="auth-logo" style={{ color: 'var(--primary)' }}>
          <LogoMark size={28} />
          <span style={{ color: 'var(--text-secondary)' }}>설비혁신파트 협업 시스템</span>
        </div>
        <h2 className="auth-title">로그인</h2>
        <form onSubmit={submit}>
          <div className="auth-field">
            <label>아이디</label>
            <input value={username} onChange={e => setUsername(e.target.value)} placeholder="아이디 입력" autoComplete="username" />
          </div>
          <div className="auth-field">
            <label>비밀번호</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="비밀번호 입력" autoComplete="current-password" />
          </div>
          {error && <div className="auth-error">{error}</div>}
          <button type="submit" className="btn btn-primary auth-btn" disabled={loading}>
            {loading ? '로그인 중...' : '로그인'}
          </button>
        </form>
        <p className="auth-link">계정이 없으신가요? <a onClick={e => e.preventDefault()} href="#">회원가입</a></p>
      </div>
    </div>
  );
}

Object.assign(window, { Login });
