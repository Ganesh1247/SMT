import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { api, ApiError } from '../api/client';
import type { Me, Role } from '../api/types';
import { canAccess, homeFor } from './access';
import { Loading } from '../components/ui';

interface AuthState {
  status: 'loading' | 'ready';
  me: Me | null;
  role: Role | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const Ctx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<'loading' | 'ready'>('loading');
  const [me, setMe] = useState<Me | null>(null);

  const refresh = useCallback(async () => {
    try {
      setMe(await api.me());
    } catch (e) {
      if (!(e instanceof ApiError)) console.error('session check failed');
      setMe(null);
    } finally {
      setStatus('ready');
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const value = useMemo<AuthState>(
    () => ({
      status,
      me,
      // role always comes from the server (GET /me); never from client storage
      role: me?.role ?? null,
      login: async (email, password) => {
        await api.login({ email, password });
        await refresh();
      },
      register: async (email, password, displayName) => {
        await api.register({ email, password, display_name: displayName || undefined });
        await refresh();
      },
      logout: async () => {
        try {
          await api.logout();
        } finally {
          setMe(null);
        }
      },
      refresh,
    }),
    [status, me, refresh],
  );
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAuth(): AuthState {
  const v = useContext(Ctx);
  if (!v) throw new Error('AuthProvider missing');
  return v;
}

/** Route guard: deny by default via canAccess(role, pathname). */
export function Guard({ children }: { children: ReactNode }) {
  const { status, role } = useAuth();
  const loc = useLocation();
  if (status === 'loading') {
    return (
      <div className="container">
        <Loading label="Checking your session" />
      </div>
    );
  }
  if (!canAccess(role, loc.pathname)) {
    if (role === null) return <Navigate to="/login" replace />;
    return <Navigate to={homeFor(role)} replace />;
  }
  return <>{children}</>;
}
