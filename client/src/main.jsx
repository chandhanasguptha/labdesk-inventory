import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, ArrowDownToLine, ArrowRight, Bell, Box, CalendarDays, Check, ChevronDown, CircleHelp, ClipboardList, FlaskConical, LayoutDashboard, LogOut, Menu, Package, Plus, Search, Settings, ShieldCheck, SlidersHorizontal, Sparkles, Wrench, X } from 'lucide-react';
import './styles.css';

const fallbackEquipment = [
  { _id: 'eq-1', name: 'Digital Oscilloscope', category: 'Electronics', tag: 'EL-204', status: 'Available', location: 'Bench 04' },
  { _id: 'eq-2', name: 'Arduino Starter Kit', category: 'Prototyping', tag: 'PR-118', status: 'On loan', location: 'Cabinet B' },
  { _id: 'eq-3', name: 'Digital Multimeter', category: 'Electronics', tag: 'EL-087', status: 'Available', location: 'Bench 02' },
  { _id: 'eq-4', name: 'Soldering Station', category: 'Prototyping', tag: 'PR-032', status: 'Maintenance', location: 'Service desk' },
  { _id: 'eq-5', name: 'Bench Power Supply', category: 'Electronics', tag: 'EL-143', status: 'Available', location: 'Bench 07' },
  { _id: 'eq-6', name: 'Raspberry Pi 5 Kit', category: 'Computing', tag: 'CO-061', status: 'Available', location: 'Cabinet A' }
];
const fallbackRequests = [
  { _id: 'rq-1', student: 'Ananya Menon', equipment: 'Arduino Starter Kit', purpose: 'Sensor calibration lab', dueDate: '2026-10-29', status: 'Pending' },
  { _id: 'rq-2', student: 'Rohan Das', equipment: 'Digital Multimeter', purpose: 'Circuit analysis assignment', dueDate: '2026-10-28', status: 'Approved' },
  { _id: 'rq-3', student: 'Meera Nair', equipment: 'Digital Oscilloscope', purpose: 'Signal measurement practical', dueDate: '2026-10-26', status: 'Returned' }
];
const navItems = [
  { label: 'Overview', icon: LayoutDashboard },
  { label: 'Equipment', icon: Package },
  { label: 'Requests', icon: ClipboardList, count: 3 },
  { label: 'Returns', icon: ArrowDownToLine }
];
const api = async (path, options) => {
  const response = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!response.ok) throw new Error((await response.json()).message || 'Request failed');
  return response.json();
};
const Status = ({ children }) => <span className={`status status-${children.toLowerCase().replaceAll(' ', '-')}`}><i />{children}</span>;
const Avatar = ({ initials = 'AM', tone = '' }) => <span className={`avatar ${tone}`}>{initials}</span>;
const initials = name => name.split(' ').map(part => part[0]).slice(0, 2).join('').toUpperCase();

function App() {
  const [page, setPage] = useState('Overview');
  const [equipment, setEquipment] = useState(fallbackEquipment);
  const [requests, setRequests] = useState(fallbackRequests);
  const [activeTab, setActiveTab] = useState('All items');
  const [search, setSearch] = useState('');
  const [modal, setModal] = useState(false);
  const [notice, setNotice] = useState('');
  const [mobileOpen, setMobileOpen] = useState(false);
  const [dbState, setDbState] = useState('Loading');
  useEffect(() => {
    Promise.all([api('/api/equipment'), api('/api/requests'), api('/api/health')]).then(([items, rows, health]) => {
      if (items?.length) setEquipment(items);
      if (rows?.length) setRequests(rows);
      setDbState(health.database === 'connected' ? 'Connected' : 'Demo mode');
    }).catch(() => setDbState('Offline preview'));
  }, []);
  useEffect(() => { if (!notice) return; const timer = setTimeout(() => setNotice(''), 3000); return () => clearTimeout(timer); }, [notice]);
  const filteredEquipment = useMemo(() => equipment.filter(item => {
    const matchesTab = activeTab === 'All items' || item.status === activeTab;
    return matchesTab && `${item.name} ${item.category} ${item.tag}`.toLowerCase().includes(search.toLowerCase());
  }), [equipment, activeTab, search]);
  const counts = { total: equipment.length, available: equipment.filter(item => item.status === 'Available').length, loaned: equipment.filter(item => item.status === 'On loan').length, pending: requests.filter(row => row.status === 'Pending').length };
  const updateRequest = async (id, status) => {
    try {
      const saved = await api(`/api/requests/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) });
      setRequests(current => current.map(row => row._id === id ? saved : row));
    } catch {
      setRequests(current => current.map(row => row._id === id ? { ...row, status } : row));
    }
    setNotice(`Request marked ${status.toLowerCase()}.`);
  };
  const submitRequest = async values => {
    const optimistic = { ...values, status: 'Pending', _id: `local-${Date.now()}` };
    setRequests(current => [optimistic, ...current]);
    try { const saved = await api('/api/requests', { method: 'POST', body: JSON.stringify(values) }); setRequests(current => current.map(row => row._id === optimistic._id ? saved : row)); } catch { /* local preview */ }
    setModal(false); setNotice('Your equipment request is ready for staff review.');
  };
  return <div className="app-shell">
    <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
      <div className="brand"><span className="brand-mark"><FlaskConical size={20} strokeWidth={2.1} /></span><span>lab<span>desk</span></span><button className="mobile-close" onClick={() => setMobileOpen(false)} aria-label="Close menu"><X size={18} /></button></div>
      <div className="workspace-switch"><span className="workspace-icon">N</span><span className="workspace-copy"><b>Northstar Institute</b><small>Science department</small></span><ChevronDown size={15} /></div>
      <span className="nav-caption">WORKSPACE</span>
      <nav>{navItems.map(({ label, icon: Icon, count }) => <button key={label} aria-label={label} title={label} className={`nav-link ${page === label ? 'selected' : ''}`} onClick={() => { setPage(label); setMobileOpen(false); }}><Icon size={17} /><span>{label}</span>{count && <small>{counts.pending || count}</small>}</button>)}</nav>
      <span className="nav-caption tools-caption">MANAGE</span>
      <nav><button className="nav-link" onClick={() => setNotice('Inventory tools are ready for your next session.')}><Wrench size={17} /><span>Maintenance</span></button><button className="nav-link" onClick={() => setNotice('Reports are being prepared.')}><Activity size={17} /><span>Reports</span></button></nav>
      <div className="sidebar-bottom"><div className="help-card"><div className="help-icon"><CircleHelp size={17} /></div><b>Need a hand?</b><span>Visit the lab guide for quick answers.</span><button onClick={() => setNotice('Lab guide opened in this demo.')}>Open lab guide <ArrowRight size={13} /></button></div><button className="nav-link settings-link" onClick={() => setNotice('Workspace settings are available to staff.')}><Settings size={17} /><span>Settings</span></button><div className="profile"><Avatar initials="AM" /><div><b>Alex Morgan</b><small>Lab coordinator</small></div><button aria-label="Sign out" onClick={() => setNotice('You are using a demo profile.')}><LogOut size={16} /></button></div></div>
    </aside>
    {mobileOpen && <button className="scrim" aria-label="Close navigation" onClick={() => setMobileOpen(false)} />}
    <main className="main-panel">
      <header className="topbar"><button className="menu-toggle" onClick={() => setMobileOpen(true)} aria-label="Open menu"><Menu size={20} /></button><div className="breadcrumb">Workspace <span>/</span> <b>{page}</b></div><div className="top-actions"><span className={`connection ${dbState === 'Connected' ? 'live' : ''}`}><i />{dbState}</span><button className="icon-button notification" aria-label="Notifications" onClick={() => setNotice('You’re all caught up.')}><Bell size={18} /><i /></button><div className="top-divider" /><Avatar initials="AM" /></div></header>
      <div className="content">
        <section className="welcome-row"><div><div className="eyebrow"><Sparkles size={13} /> MONDAY, OCTOBER 26, 2026</div><h1>{page === 'Overview' ? 'Good morning, Alex' : page}</h1><p>{page === 'Overview' ? 'Here’s what’s happening in your lab today.' : page === 'Equipment' ? 'Keep track of every instrument and asset in your lab.' : page === 'Requests' ? 'Review student requests and keep projects moving.' : 'Check in returned equipment and keep records up to date.'}</p></div><div className="welcome-actions"><button className="button button-quiet" onClick={() => setNotice('Report export is available in the full version.')}><ArrowDownToLine size={15} /> Export report</button><button className="button button-primary" onClick={() => setModal(true)}><Plus size={17} /> New request</button></div></section>
        {page === 'Overview' && <>
          <section className="stats-grid" aria-label="Lab summary"><Stat icon={Box} title="Total equipment" value={counts.total} trend="Across 3 categories" accent="blue" /><Stat icon={Check} title="Available now" value={counts.available} trend={`${Math.round((counts.available / Math.max(counts.total, 1)) * 100)}% of your inventory`} accent="green" /><Stat icon={ClipboardList} title="On loan" value={counts.loaned} trend="1 due back this week" accent="amber" /><Stat icon={CalendarDays} title="Pending requests" value={counts.pending} trend="Needs your attention" accent="violet" /></section>
          <section className="dashboard-grid"><div className="panel inventory-panel"><div className="panel-heading"><div><div className="section-kicker">INVENTORY</div><h2>Equipment overview</h2></div><button className="text-button" onClick={() => setPage('Equipment')}>View all <ArrowRight size={14} /></button></div><div className="inventory-toolbar"><div className="tabs">{['All items', 'Available', 'On loan', 'Maintenance'].map(tab => <button key={tab} className={activeTab === tab ? 'active' : ''} onClick={() => setActiveTab(tab)}>{tab}{tab === 'All items' && <span>{equipment.length}</span>}</button>)}</div><div className="search-box"><Search size={15} /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search equipment" aria-label="Search equipment" /></div></div><div className="equipment-table"><div className="table-head"><span>ITEM</span><span>ASSET TAG</span><span>LOCATION</span><span>STATUS</span><span /></div>{filteredEquipment.slice(0, 5).map((item, index) => <div className="equipment-row" key={item._id}><div className="equipment-name"><span className={`item-icon tint-${index % 4}`}><Package size={17} /></span><span><b>{item.name}</b><small>{item.category}</small></span></div><span className="tag">{item.tag}</span><span className="location">{item.location}</span><span><Status>{item.status}</Status></span><button className="dots-button" aria-label={`More about ${item.name}`} onClick={() => setNotice(`${item.name} · ${item.tag}`)}>···</button></div>)}{filteredEquipment.length === 0 && <div className="empty-state">No equipment matches this search.</div>}</div><button className="mobile-view-all" onClick={() => setPage('Equipment')}>View all equipment <ArrowRight size={14} /></button></div>
            <div className="panel requests-panel"><div className="panel-heading"><div><div className="section-kicker">NEEDS REVIEW</div><h2>Recent requests <span className="count-pill">{counts.pending}</span></h2></div><button className="more-button" aria-label="More request actions" onClick={() => setPage('Requests')}>···</button></div><div className="request-list">{requests.slice(0, 4).map((row, i) => <div className="request-item" key={row._id}><Avatar initials={initials(row.student)} tone={`avatar-tone-${i % 4}`} /><div className="request-detail"><b>{row.student}</b><span>{row.equipment}</span><small>Due {new Date(`${row.dueDate}T00:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</small></div><div className="request-side"><Status>{row.status}</Status>{row.status === 'Pending' && <button className="approve-button" onClick={() => updateRequest(row._id, 'Approved')}>Review <ArrowRight size={12} /></button>}</div></div>)}</div><button className="request-footer" onClick={() => setPage('Requests')}>See all requests <ArrowRight size={14} /></button></div></section>
          <section className="bottom-grid"><div className="panel activity-panel"><div className="panel-heading"><div><div className="section-kicker">AT A GLANCE</div><h2>Lab activity</h2></div><button className="period-select" onClick={() => setNotice('Showing this week')}>This week <ChevronDown size={13} /></button></div><div className="chart-wrap"><div className="chart-y"><span>16</span><span>12</span><span>8</span><span>4</span><span>0</span></div><div className="chart"><div className="gridline"/><div className="gridline"/><div className="gridline"/><div className="gridline"/><div className="bars">{[['M',8,5],['T',11,7],['W',7,10],['T',13,8],['F',9,12],['S',5,3],['S',3,4]].map(([day,a,b],i)=><div className="bar-day" key={i}><div className="bar-pair"><i style={{height:`${a*5}px`}}/><i style={{height:`${b*5}px`}}/></div><span>{day}</span></div>)}</div></div></div><div className="chart-legend"><span><i className="legend-blue"/>Equipment requests</span><span><i className="legend-mint"/>Returned items</span></div></div><div className="panel tip-panel"><div className="tip-glow"/><div className="tip-label"><span><Sparkles size={13}/></span>LAB TIP</div><h2>Ready for the next class?</h2><p>Check upcoming bookings and make sure high-demand equipment is back on the shelf.</p><button className="tip-link" onClick={() => setPage('Equipment')}>Review availability <ArrowRight size={14}/></button><div className="tip-art"><div className="art-orbit orbit-one"/><div className="art-orbit orbit-two"/><FlaskConical size={52} strokeWidth={1.05}/></div></div></section>
        </>}
        {page === 'Equipment' && <section className="panel full-page-panel"><div className="panel-heading"><div><div className="section-kicker">ASSET REGISTER</div><h2>All equipment</h2></div><button className="button button-primary" onClick={() => setNotice('Staff can add inventory from the full version.')}><Plus size={16}/> Add equipment</button></div><div className="inventory-toolbar full-toolbar"><div className="tabs">{['All items', 'Available', 'On loan', 'Maintenance'].map(tab => <button key={tab} className={activeTab === tab ? 'active' : ''} onClick={() => setActiveTab(tab)}>{tab}</button>)}</div><div className="search-box"><Search size={15}/><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search equipment" aria-label="Search equipment"/><SlidersHorizontal size={15}/></div></div><div className="equipment-table">{filteredEquipment.map((item, index) => <div className="equipment-row" key={item._id}><div className="equipment-name"><span className={`item-icon tint-${index % 4}`}><Package size={17}/></span><span><b>{item.name}</b><small>{item.category}</small></span></div><span className="tag">{item.tag}</span><span className="location">{item.location}</span><span><Status>{item.status}</Status></span><button className="dots-button" aria-label="Equipment options">···</button></div>)}</div></section>}
        {page === 'Requests' && <section className="panel full-page-panel"><div className="panel-heading"><div><div className="section-kicker">LOAN WORKFLOW</div><h2>Request queue</h2></div><button className="button button-primary" onClick={() => setModal(true)}><Plus size={16}/> New request</button></div><div className="request-table-head"><span>STUDENT</span><span>EQUIPMENT</span><span>PURPOSE</span><span>DUE DATE</span><span>STATUS</span><span>ACTION</span></div>{requests.map(row=><div className="request-table-row" key={row._id}><div className="student-cell"><Avatar initials={initials(row.student)}/><b>{row.student}</b></div><span>{row.equipment}</span><span>{row.purpose}</span><span>{new Date(`${row.dueDate}T00:00:00`).toLocaleDateString('en-US',{month:'short',day:'numeric'})}</span><Status>{row.status}</Status><span>{row.status==='Pending'?<button className="text-button" onClick={()=>updateRequest(row._id,'Approved')}>Approve <ArrowRight size={13}/></button>:<button className="dots-button" onClick={()=>setNotice(`Request ${row._id}`)}>···</button>}</span></div>)}</section>}
        {page === 'Returns' && <section className="panel full-page-panel"><div className="panel-heading"><div><div className="section-kicker">CHECK IN</div><h2>Expected returns</h2></div><button className="button button-quiet" onClick={()=>setNotice('Return report exported.') }><ArrowDownToLine size={15}/> Export list</button></div>{requests.filter(row=>row.status==='Approved').length ? requests.filter(row=>row.status==='Approved').map(row=><div className="return-row" key={row._id}><span className="item-icon tint-1"><Package size={17}/></span><div><b>{row.equipment}</b><small>Checked out to {row.student} · Due {new Date(`${row.dueDate}T00:00:00`).toLocaleDateString('en-US',{month:'short',day:'numeric'})}</small></div><button className="button button-primary" onClick={()=>updateRequest(row._id,'Returned')}><Check size={15}/> Mark returned</button></div>):<div className="empty-state roomy">Everything is checked in. You’re all caught up.</div>}</section>}
        <footer className="page-footer"><span>© 2026 LabDesk · Northstar Institute</span><span><ShieldCheck size={13}/> Learning demo · {dbState}</span></footer>
      </div>
    </main>
    {modal && <RequestModal equipment={equipment.filter(item=>item.status==='Available')} onClose={()=>setModal(false)} onSubmit={submitRequest}/>}
    {notice && <div className="toast"><span className="toast-check"><Check size={14}/></span>{notice}<button aria-label="Dismiss" onClick={()=>setNotice('')}><X size={14}/></button></div>}
  </div>;
}
function Stat({icon:Icon,title,value,trend,accent}) { return <div className="stat-card"><div className="stat-top"><span className={`stat-icon ${accent}`}><Icon size={17}/></span><span className="stat-period">THIS TERM</span></div><div className="stat-value">{value}</div><div className="stat-title">{title}</div><div className="stat-trend"><span className={`trend-dot ${accent}`}/>{trend}</div></div>; }
function RequestModal({equipment,onClose,onSubmit}) {
  const [student,setStudent]=useState('Alex Morgan'); const [item,setItem]=useState(equipment[0]?.name || ''); const [purpose,setPurpose]=useState(''); const [dueDate,setDueDate]=useState('2026-10-30'); const [error,setError]=useState('');
  const submit=e=>{e.preventDefault(); if(!student.trim()||!item||!purpose.trim()||!dueDate){setError('Please complete each field.');return;}onSubmit({student:student.trim(),equipment:item,purpose:purpose.trim(),dueDate});};
  return <div className="modal-backdrop" onMouseDown={e=>e.target===e.currentTarget&&onClose()}><form className="request-modal" onSubmit={submit}><div className="modal-heading"><div><div className="section-kicker">EQUIPMENT LOAN</div><h2>New request</h2><p>Tell the lab team what you need for your work.</p></div><button type="button" className="modal-close" onClick={onClose} aria-label="Close dialog"><X size={18}/></button></div><label>Your name<input value={student} onChange={e=>setStudent(e.target.value)} /></label><label>Equipment<select value={item} onChange={e=>setItem(e.target.value)}>{equipment.map(row=><option key={row._id}>{row.name}</option>)}</select></label><label>Purpose<input value={purpose} onChange={e=>setPurpose(e.target.value)} placeholder="e.g. sensor calibration practical" /></label><label>Return by<input type="date" value={dueDate} onChange={e=>setDueDate(e.target.value)} /></label>{error&&<div className="form-error">{error}</div>}<div className="modal-actions"><button type="button" className="button button-quiet" onClick={onClose}>Cancel</button><button type="submit" className="button button-primary">Submit request <ArrowRight size={15}/></button></div><small className="modal-note">Requests are reviewed by the lab coordinator before checkout.</small></form></div>;
}

createRoot(document.getElementById('root')).render(<React.StrictMode><App /></React.StrictMode>);
