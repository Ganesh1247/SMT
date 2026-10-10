import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import type { Role } from '../api/types';

const NAV: Record<Role, Array<{ to: string; label: string }>> = {
  learner: [
    { to: '/path', label: 'My path' },
    { to: '/profile', label: 'Profile' },
    { to: '/sharing', label: 'Sharing' },
    { to: '/appeals', label: 'Appeals' },
  ],
  reviewer: [{ to: '/review', label: 'Review queue' }],
  recruiter: [{ to: '/hr', label: 'Roles' }],
  auditor: [{ to: '/audit', label: 'Ledger check' }],
};

export function Layout() {
  const { role, me, logout } = useAuth();
  const items = role ? NAV[role] : [];
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to main content
      </a>
      <header className="app-header">
        <span className="brand">Crucible</span>
        <nav aria-label="Main">
          <ul className="nav">
            {items.map((i) => (
              <li key={i.to}>
                <NavLink to={i.to} end={i.to === '/hr'}>
                  {i.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <div className="row">
          <span className="small muted">
            {me?.alias ? <span className="mono">{me.alias}</span> : me?.display_name}
          </span>
          <button type="button" className="btn quiet" onClick={() => void logout()}>
            Sign out
          </button>
        </div>
      </header>
      <main id="main" className="container">
        <Outlet />
      </main>
      <footer className="footer">
        Crucible is experimental. Results are evidence for people to review, not an automated decision.
      </footer>
    </>
  );
}
