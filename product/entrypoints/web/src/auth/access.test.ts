import { describe, it, expect } from 'vitest';
import { canAccess, homeFor } from './access';

describe('canAccess (deny by default)', () => {
  it('should_allow_only_public_routes_when_not_signed_in', () => {
    expect(canAccess(null, '/login')).toBe(true);
    expect(canAccess(null, '/register')).toBe(true);
    expect(canAccess(null, '/path')).toBe(false);
    expect(canAccess(null, '/review')).toBe(false);
  });

  it('should_keep_each_role_inside_its_own_area', () => {
    expect(canAccess('learner', '/path')).toBe(true);
    expect(canAccess('learner', '/lobby/2')).toBe(true);
    expect(canAccess('learner', '/exam/abc')).toBe(true);
    expect(canAccess('learner', '/review')).toBe(false);
    expect(canAccess('learner', '/hr/roles/new')).toBe(false);
    expect(canAccess('learner', '/audit')).toBe(false);

    expect(canAccess('reviewer', '/review/case-1')).toBe(true);
    expect(canAccess('reviewer', '/profile')).toBe(false);

    expect(canAccess('recruiter', '/hr')).toBe(true);
    expect(canAccess('recruiter', '/hr/evidence/cnd_1/cmp_python')).toBe(true);
    expect(canAccess('recruiter', '/review')).toBe(false);

    expect(canAccess('auditor', '/audit')).toBe(true);
    expect(canAccess('auditor', '/hr')).toBe(false);
  });

  it('should_deny_unknown_paths_for_every_role', () => {
    for (const r of ['learner', 'reviewer', 'recruiter', 'auditor'] as const) {
      expect(canAccess(r, '/admin')).toBe(false);
      expect(canAccess(r, '/unknown/thing')).toBe(false);
    }
  });

  it('should_not_be_fooled_by_prefix_lookalikes_or_traversal', () => {
    expect(canAccess('learner', '/path-evil')).toBe(false);
    expect(canAccess('learner', '/path/../review')).toBe(false);
    expect(canAccess('reviewer', '/reviewer-tools')).toBe(false);
    expect(canAccess('recruiter', '/hr%2f..%2freview')).toBe(false);
  });

  it('should_never_accept_an_unknown_role_value', () => {
    expect(canAccess('admin' as never, '/path')).toBe(false);
  });
});

describe('homeFor', () => {
  it('should_send_each_role_to_its_home', () => {
    expect(homeFor('learner')).toBe('/path');
    expect(homeFor('reviewer')).toBe('/review');
    expect(homeFor('recruiter')).toBe('/hr');
    expect(homeFor('auditor')).toBe('/audit');
    expect(homeFor(null)).toBe('/login');
  });
});
