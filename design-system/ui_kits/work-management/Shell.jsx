/* work-management UI Kit — app shell (sidebar + top bar) */

const NAV = [
  { key: 'dashboard', icon: 'dashboard', label: '대시보드' },
  { key: 'progress',  icon: 'assignment', label: '주간 진행 현황' },
  { key: 'admin',     icon: 'settings', label: '관리 도구' },
  { key: 'feedback',  icon: 'feedback', label: '피드백' },
  { key: 'help',      icon: 'help', label: '도움말' },
];

function LogoMark({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="5" />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none" />
    </svg>
  );
}

function Sidebar({ route, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo" onClick={() => onNavigate('dashboard')}>
        <div className="logo-badge"><LogoMark size={18} /></div>
        <div className="logo-text">
          <h1>설비혁신파트</h1>
          <span>협업 시스템</span>
        </div>
      </div>
      <nav className="sidebar-nav">
        {NAV.map(n => (
          <div key={n.key} className={'nav-item' + (route === n.key ? ' active' : '')}
            onClick={() => onNavigate(n.key)}>
            <span className="nav-icon material-symbols-outlined">{n.icon}</span>
            <span className="nav-text">{n.label}</span>
          </div>
        ))}
      </nav>
    </aside>
  );
}

function TopBar({ title, user, onLogout }) {
  return (
    <header className="top-header">
      <span className="page-title">{title}</span>
      <div className="header-right">
        <button className="icon-btn" title="알림">
          <Icon name="notifications" size={18} />
          <span className="notif-dot" />
        </button>
        <div className="header-divider" />
        <div className="user-info">
          <Avatar name={user.name} variant="grad" />
          <span className="user-name">{user.name}</span>
          <button className="icon-btn" title="로그아웃" onClick={onLogout}>
            <Icon name="logout" size={18} />
          </button>
        </div>
      </div>
    </header>
  );
}

Object.assign(window, { Sidebar, TopBar, LogoMark, NAV });
