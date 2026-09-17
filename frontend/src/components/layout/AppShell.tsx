import { Sparkles, Menu, X, Settings, Volume2, Bot, ChevronRight, Eye, FileText, LayoutDashboard, HelpCircle, MessageSquare } from 'lucide-react';
import { useState } from 'react';
import { NavLink, useLocation, Outlet } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { cn } from '@/lib/utils';
import { useSettings } from '@/hooks/useSettings';
import { useVoice } from '@/hooks/useVoice';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/see', label: 'See & Understand', icon: Eye },
  { path: '/read', label: 'Read & Explain', icon: FileText },
  { path: '/form', label: 'Form Assist', icon: LayoutDashboard },
  { path: '/ask', label: 'Ask About What You See', icon: HelpCircle },
  { path: '/voice', label: 'Voice Assistant', icon: Volume2 },
  { path: '/chat', label: 'Chat Assistant', icon: MessageSquare },
] as const;

export function AppShell() {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { settings, updateSettings } = useSettings();
  const { voiceEnabled, toggleVoice } = useVoice();

  const classes = [
    settings.highContrast ? 'high-contrast' : '',
    settings.darkMode ? 'dark-mode' : '',
    settings.reduceMotion ? 'reduce-motion' : '',
    settings.largerButtons ? 'large-buttons' : '',
  ].filter(Boolean).join(' ');

  return (
    <div className={`app ${classes}`}>
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`} aria-label="Main navigation">
        <div className="sidebar-header">
          <NavLink to="/dashboard" className="brand" aria-label="MiraGuide dashboard">
            <span className="brand-mark"><Sparkles size={19} /></span>MiraGuide
          </NavLink>
        </div>
        <nav className="nav-section" aria-label="Assistance tools">
          <span className="nav-section-title">ASSISTANCE</span>
          {navItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                cn(
                  'side-link',
                  isActive ? 'active' : ''
                )
              }
            >
              <Icon size={19} />
              {label}
            </NavLink>
          ))}
        </nav>
        <nav className="nav-section" aria-label="Preferences">
          <span className="nav-section-title">PREFERENCES</span>
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              cn('side-link', isActive ? 'active' : '')
            }
          >
            <Settings size={19} />Settings
          </NavLink>
        </nav>
      </aside>

      <div className="app-main">
        <header className="page-header">
          <button
            className="icon-button mobile-menu"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-expanded={sidebarOpen}
            aria-label={sidebarOpen ? 'Close menu' : 'Open menu'}
          >
            {sidebarOpen ? <X /> : <Menu />}
          </button>
          <NavLink to="/dashboard" className="brand" aria-label="MiraGuide dashboard">
            <span className="brand-mark"><Sparkles size={19} /></span>MiraGuide
          </NavLink>
          <div className="header-actions">
            <span className="demo-pill"><Bot size={15} />Demo Mode</span>
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleVoice}
              aria-label={voiceEnabled ? 'Disable voice output' : 'Enable voice output'}
              aria-pressed={voiceEnabled}
            >
              <Volume2 size={20} />
            </Button>
            <NavLink to="/settings" className="icon-button" aria-label="Open settings">
              <Settings size={20} />
            </NavLink>
          </div>
        </header>
        <main id="main-content" className="page" tabIndex={-1}>
          <Outlet />
        </main>
      </div>
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} aria-hidden="true" />
      )}
    </div>
  );
}