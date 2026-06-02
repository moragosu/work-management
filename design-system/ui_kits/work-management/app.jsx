/* work-management UI Kit — app entry: login + routing */
const { useState: useAppState } = React;

const PAGE_TITLE = {
  dashboard: '대시보드', progress: '주간 진행 현황', admin: '관리 도구',
  feedback: '피드백', help: '도움말',
};

function Placeholder({ icon, title, desc }) {
  return (
    <div className="placeholder-view">
      <Icon name={icon} />
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>
  );
}

function App() {
  const [loggedIn, setLoggedIn] = useAppState(false);
  const [route, setRoute] = useAppState('dashboard');
  const D = window.KIT_DATA;

  if (!loggedIn) return <Login onLogin={() => setLoggedIn(true)} />;

  let view;
  if (route === 'dashboard') view = <Dashboard />;
  else if (route === 'progress') view = <Progress />;
  else if (route === 'admin') view = <Admin />;
  else if (route === 'feedback') view = <Placeholder icon="feedback" title="피드백" desc="파트 운영과 협업 시스템에 대한 자유로운 의견을 남기는 공간입니다. (이 화면은 UI 키트에 포함되지 않았습니다)" />;
  else view = <Placeholder icon="help" title="도움말" desc="협업 시스템 사용 가이드입니다. (이 화면은 UI 키트에 포함되지 않았습니다)" />;

  return (
    <div className="layout">
      <Sidebar route={route} onNavigate={setRoute} />
      <div className="main-wrap">
        <TopBar title={PAGE_TITLE[route]} user={D.user} onLogout={() => setLoggedIn(false)} />
        <main className="main-content">{view}</main>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
