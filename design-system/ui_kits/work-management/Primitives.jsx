/* work-management UI Kit — shared primitive components */
const { useState } = React;

function Icon({ name, fill, size, style, className = '' }) {
  return (
    <span
      className={'material-symbols-outlined ' + (fill ? 'mso-fill ' : '') + className}
      style={{ fontSize: size ? size + 'px' : undefined, ...style }}
    >{name}</span>
  );
}

const STATUS_BADGE = { '진행중': 'badge-blue', '완료': 'badge-green', '위험': 'badge-red' };
function statusBadgeClass(status) { return 'badge ' + (STATUS_BADGE[status] || 'badge-gray'); }

function Badge({ kind = 'gray', children, style }) {
  return <span className={'badge badge-' + kind} style={style}>{children}</span>;
}

function Button({ variant, size, children, onClick, disabled, icon, style, title }) {
  const cls = ['btn'];
  if (variant) cls.push('btn-' + variant);
  if (size) cls.push('btn-' + size);
  return (
    <button className={cls.join(' ')} onClick={onClick} disabled={disabled} style={style} title={title}>
      {icon && <Icon name={icon} size={size === 'xs' ? 13 : size === 'sm' ? 15 : 16} />}
      {children}
    </button>
  );
}

function AddButton({ children, onClick, icon = 'add' }) {
  return (
    <button className="btn-add-action" onClick={onClick}>
      <Icon name={icon} size={13} style={{ verticalAlign: '-2px' }} />{children}
    </button>
  );
}

function Card({ children, style, className = '', onClick }) {
  return <div className={'card ' + className} style={style} onClick={onClick}>{children}</div>;
}

function Avatar({ name, variant = 'tint', size = 32 }) {
  const cls = variant === 'grad' ? 'user-avatar' : 'member-avatar';
  return <span className={cls} style={{ width: size, height: size, fontSize: size * 0.42 }}>{(name || '?')[0]}</span>;
}

function Toggle({ on, onChange }) {
  return <div className={'toggle-track' + (on ? ' on' : '')} onClick={() => onChange && onChange(!on)} />;
}

function FilterGroup({ options, value, onChange }) {
  return (
    <div className="q-filter-group">
      {options.map(o => (
        <button key={o.value} className={'q-filter-btn' + (value === o.value ? ' active' : '')}
          onClick={() => onChange(o.value)}>{o.label}</button>
      ))}
    </div>
  );
}

function Modal({ title, onClose, children, footer, width = 560 }) {
  return (
    <div className="modal-overlay" onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="modal" style={{ maxWidth: width }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{title}</h3>
          <button className="modal-close" onClick={onClose}><Icon name="close" size={18} /></button>
        </div>
        {children}
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  );
}

function Toast({ message }) {
  if (!message) return null;
  return <div className="toast">{message}</div>;
}

/* week "2026-W21" -> "W21" (current year stripped) */
function formatWeekLabel(w) {
  const m = /^(\d{4})-W(\d+)$/.exec(w || '');
  if (!m) return w;
  return parseInt(m[1]) === 2026 ? 'W' + m[2] : `${m[1]}-W${m[2]}`;
}

Object.assign(window, {
  Icon, Badge, Button, AddButton, Card, Avatar, Toggle, FilterGroup, Modal, Toast,
  statusBadgeClass, formatWeekLabel,
});
