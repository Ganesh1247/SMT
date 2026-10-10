import { expect, vi } from 'vitest';
import axe from 'axe-core';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import type { ReactElement } from 'react';
import { setFetch } from '../api/client';
import { App } from '../App';
import type { Me } from '../api/types';

/** Fake HTTP layer for unit tests only. Keys are "METHOD /path" (no /api prefix, no query). */
export type Handler = (body: unknown, url: URL) => unknown | Response | Promise<unknown | Response>;
export function mockApi(routes: Record<string, Handler>) {
  const calls: Array<{ key: string; body: unknown }> = [];
  const fn = vi.fn(async (input: string, init?: RequestInit) => {
    const url = new URL(input, 'http://localhost');
    const method = init?.method ?? 'GET';
    const key = `${method} ${url.pathname.replace(/^\/api/, '')}`;
    let body: unknown = undefined;
    if (typeof init?.body === 'string') body = JSON.parse(init.body);
    else if (init?.body) body = init.body;
    calls.push({ key, body });
    const h = routes[key];
    if (!h) return new Response(JSON.stringify({}), { status: 404 });
    const out = await h(body, url);
    if (out instanceof Response) return out;
    if (out === undefined) return new Response(null, { status: 204 });
    return new Response(JSON.stringify(out), { status: 200, headers: { 'Content-Type': 'application/json' } });
  });
  setFetch(fn as never);
  return { calls, fn, count: (key: string) => calls.filter((c) => c.key === key).length };
}

export const status = (code: number) => new Response('{}', { status: code });

export function renderApp(path: string, me: Me | null, routes: Record<string, Handler> = {}) {
  const api = mockApi({
    'GET /me': () => (me ? me : status(401)),
    ...routes,
  });
  const utils = render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
  return { ...utils, api };
}

export function renderAt(ui: ReactElement, path = '/') {
  return render(<MemoryRouter initialEntries={[path]}>{ui}</MemoryRouter>);
}

/** axe-core in jsdom. Colour contrast needs layout, so it is covered by tokens.test.ts instead. */
export async function expectNoA11yViolations(container: HTMLElement) {
  const r = await axe.run(container, {
    rules: { 'color-contrast': { enabled: false }, region: { enabled: false } },
  });
  expect(r.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.html.slice(0, 80)).join(' | ')}`)).toEqual([]);
}

export const learner: Me = { user_id: 'u1', role: 'learner', alias: 'cnd_0123456789abcdef', display_name: 'Sam', track: 'python' };
export const reviewer: Me = { user_id: 'u2', role: 'reviewer', alias: null };
export const recruiter: Me = { user_id: 'u3', role: 'recruiter', alias: null };
export const auditor: Me = { user_id: 'u4', role: 'auditor', alias: null };
