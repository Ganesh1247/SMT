import type { Role } from '../api/types';

/** Deny by default: a path is reachable only if it matches an entry for the caller's role. */
interface Rule {
  base: string;
  roles: ReadonlyArray<Role> | 'public';
}

const RULES: Rule[] = [
  { base: '/login', roles: 'public' },
  { base: '/register', roles: 'public' },
  { base: '/path', roles: ['learner'] },
  { base: '/lobby', roles: ['learner'] },
  { base: '/exam', roles: ['learner'] },
  { base: '/interview', roles: ['learner'] },
  { base: '/result', roles: ['learner'] },
  { base: '/profile', roles: ['learner'] },
  { base: '/sharing', roles: ['learner'] },
  { base: '/appeals', roles: ['learner'] },
  { base: '/review', roles: ['reviewer'] },
  { base: '/hr', roles: ['recruiter'] },
  { base: '/audit', roles: ['auditor'] },
];

const KNOWN_ROLES: ReadonlyArray<string> = ['learner', 'reviewer', 'auditor', 'recruiter'];

export function canAccess(role: Role | null, pathname: string): boolean {
  if (typeof pathname !== 'string' || !pathname.startsWith('/')) return false;
  if (pathname.includes('..') || pathname.includes('%') || pathname.includes('\\')) return false;
  const rule = RULES.find((r) => pathname === r.base || pathname.startsWith(r.base + '/'));
  if (!rule) return false;
  if (rule.roles === 'public') return true;
  if (role === null || !KNOWN_ROLES.includes(role)) return false;
  return rule.roles.includes(role);
}

export function homeFor(role: Role | null): string {
  switch (role) {
    case 'learner':
      return '/path';
    case 'reviewer':
      return '/review';
    case 'recruiter':
      return '/hr';
    case 'auditor':
      return '/audit';
    default:
      return '/login';
  }
}
