import { Outlet, NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Sun, 
  GitMerge, 
  Target, 
  Users, 
  Brain, 
  ShieldCheck, 
  UserCircle,
  Terminal
} from 'lucide-react';

export default function Layout() {
  const navItems = [
    { path: '/', label: 'COMMAND CENTER', icon: Terminal },
    { path: '/overview', label: 'Home Dashboard', icon: LayoutDashboard },
    { path: '/briefings', label: 'Daily Briefing', icon: Sun },
    { path: '/decisions', label: 'Decision Center', icon: GitMerge },
    { path: '/intent', label: 'Intent Center', icon: Target },
    { path: '/relationships', label: 'Relationships', icon: Users },
    { path: '/memory', label: 'Memory Vault', icon: Brain },
    { path: '/trust', label: 'Trust Center', icon: ShieldCheck },
    { path: '/founder', label: 'Founder Profile', icon: UserCircle },
  ];

  return (
    <div className="layout-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          JAY MISSION CONTROL
        </div>
        <nav>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink 
                key={item.path} 
                to={item.path} 
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              >
                <Icon size={20} />
                {item.label}
              </NavLink>
            );
          })}
        </nav>
      </aside>
      
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
