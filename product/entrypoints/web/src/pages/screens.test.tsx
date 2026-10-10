import { describe, it, expect } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  auditor,
  expectNoA11yViolations,
  learner,
  recruiter,
  renderApp,
  reviewer,
  status,
} from '../test/helpers';
import type { Profile, Progress, ReviewCase } from '../api/types';

const progress: Progress = {
  track: 'python',
  all_passed: false,
  levels: [
    { level: 1, status: 'passed', attempts: 1 },
    { level: 2, status: 'in_progress', attempts: 1 },
    { level: 3, status: 'locked', attempts: 0 },
    { level: 4, status: 'locked', attempts: 0 },
  ],
};

describe('role routing (deny by default)', () => {
  it('should_redirect_signed_out_visitors_to_sign_in', async () => {
    renderApp('/path', null);
    expect(await screen.findByRole('heading', { level: 1, name: 'Sign in' })).toBeInTheDocument();
  });

  it('should_send_a_recruiter_away_from_reviewer_pages_to_their_home', async () => {
    renderApp('/review', recruiter, { 'GET /hr/roles': () => ({ roles: [] }) });
    expect(await screen.findByRole('heading', { level: 1, name: 'Roles' })).toBeInTheDocument();
    expect(screen.queryByText('Review queue')).not.toBeInTheDocument();
  });

  it('should_show_not_found_for_unknown_paths', async () => {
    renderApp('/admin', learner);
    expect(await screen.findByRole('heading', { name: 'Page not found' })).toBeInTheDocument();
  });

  it('should_take_the_role_from_the_server_not_from_client_storage', async () => {
    localStorage.setItem('role', 'auditor');
    renderApp('/audit', learner, { 'GET /me/progress': () => progress });
    expect(await screen.findByRole('heading', { level: 1, name: 'My path' })).toBeInTheDocument();
    localStorage.clear();
  });
});

describe('Sign in', () => {
  it('should_announce_field_errors_linked_to_inputs_and_have_no_axe_violations', async () => {
    const { container } = renderApp('/login', null);
    await screen.findByRole('heading', { name: 'Sign in' });
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    const email = screen.getByLabelText('Email');
    expect(email).toHaveAttribute('aria-invalid', 'true');
    expect(email).toHaveAccessibleDescription(/name@example.com/);
    await expectNoA11yViolations(container);
  });

  it('should_show_a_plain_error_when_credentials_are_wrong', async () => {
    renderApp('/login', null, { 'POST /auth/login': () => status(401) });
    await screen.findByRole('heading', { name: 'Sign in' });
    await userEvent.type(screen.getByLabelText('Email'), 'a@b.co');
    await userEvent.type(screen.getByLabelText('Password'), 'whatever');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/email or password is not right/);
  });
});

describe('My path', () => {
  it('should_show_loading_then_levels_with_locked_levels_not_actionable', async () => {
    const { container } = renderApp('/path', learner, { 'GET /me/progress': () => progress });
    expect(screen.getByRole('status')).toHaveTextContent(/Checking your session/);
    await screen.findByRole('heading', { name: /Level 1: Conceptual/ });
    expect(screen.getByRole('link', { name: /Resume\s*Level 2/ })).toHaveAttribute('href', '/lobby/2');
    expect(screen.queryByRole('link', { name: /Level 3/ })).not.toBeInTheDocument();
    expect(screen.getByText('Unlocks after Level 2')).toBeInTheDocument();
    expect(screen.getByText(/estimate updates after all four levels/)).toBeInTheDocument();
    await expectNoA11yViolations(container);
  });

  it('should_never_show_timers_or_time_taken', async () => {
    renderApp('/path', learner, { 'GET /me/progress': () => progress });
    await screen.findByRole('heading', { name: /Level 1/ });
    expect(document.body.textContent).not.toMatch(/time taken|countdown|remaining|elapsed/i);
  });

  it('should_show_error_with_retry_and_recover', async () => {
    let fail = true;
    renderApp('/path', learner, { 'GET /me/progress': () => (fail ? status(500) : progress) });
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent(/Your work is saved/);
    fail = false;
    await userEvent.click(within(alert).getByRole('button', { name: 'Retry' }));
    expect(await screen.findByRole('heading', { name: /Level 1/ })).toBeInTheDocument();
  });
});

const fullProfile: Profile = {
  all_levels_passed: true,
  levels_passed: [1, 2, 3, 4],
  labels: { experimental: true, ai_used: true },
  competencies: [
    {
      competency_id: 'cmp_python',
      estimate: 0.58,
      lower: 0.45,
      upper: 0.7,
      as_of: '2026-10-10T00:00:00Z',
      levels_passed: [1, 2, 3, 4],
      method_counts: { deterministic_test: 6, probe: 1, ai_judged: 2, live_screening: 3, human_review: 0 },
      understanding_status: 'unconfirmed',
      evidence_items: [],
    },
  ],
};

describe('Profile', () => {
  it('should_show_empty_state_when_there_is_no_evidence', async () => {
    renderApp('/profile', learner, {
      'GET /me/profile': () => ({ ...fullProfile, all_levels_passed: false, levels_passed: [], competencies: [] }),
    });
    expect(await screen.findByText('No evidence yet. Complete Level 1 to start your profile.')).toBeInTheDocument();
  });

  it('should_hide_the_estimate_until_all_four_levels_are_passed', async () => {
    renderApp('/profile', learner, {
      'GET /me/profile': () => ({ ...fullProfile, all_levels_passed: false, levels_passed: [1, 2] }),
    });
    expect(await screen.findByText(/Your estimate updates after all four levels are passed/)).toBeInTheDocument();
    expect(screen.queryByText(/likely range/)).not.toBeInTheDocument();
  });

  it('should_show_estimate_band_asof_experimental_label_and_method_split', async () => {
    const { container } = renderApp('/profile', learner, { 'GET /me/profile': () => fullProfile });
    expect(await screen.findByText(/0.58, likely range 0.45 to 0.70, as of 10 Oct 2026/)).toBeInTheDocument();
    expect(screen.getByRole('note')).toHaveTextContent(/Experimental/);
    expect(screen.getByText('Output verified, understanding unconfirmed')).toBeInTheDocument();
    expect(screen.getByText(/Automated-test evidence/)).toBeInTheDocument();
    expect(screen.getByText(/Live-screening evidence/)).toBeInTheDocument();
    expect(document.body.textContent).not.toMatch(/overall score|rank|percentile/i);
    await expectNoA11yViolations(container);
  });
});

describe('Sharing', () => {
  const ev = { 'GET /me/evidence': () => ({ evidence_items: [], grants: [] }) };

  it('should_show_empty_state_and_validate_the_form_with_linked_errors', async () => {
    const { container } = renderApp('/sharing', learner, ev);
    expect(await screen.findByText(/Nobody can see your evidence/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Share' }));
    expect(screen.getByLabelText('Organisation code')).toHaveAttribute('aria-invalid', 'true');
    expect(screen.getByText('Choose at least one skill to share.')).toBeInTheDocument();
    await expectNoA11yViolations(container);
  });

  it('should_leave_raw_submission_off_by_default_and_require_confirm_to_stop_sharing', async () => {
    let stopped = false;
    const { api } = renderApp('/sharing', learner, {
      'GET /me/evidence': () => ({
        evidence_items: [],
        grants: stopped
          ? []
          : [{ grant_id: 'g1', recipient_id: 'org_acme', competencies: ['cmp_python'], include_raw_submission: false, expires_at: '2027-01-01T00:00:00Z' }],
      }),
      'DELETE /me/grants': () => {
        stopped = true;
        return undefined;
      },
    });
    expect(screen.queryByRole('checkbox', { name: /text of my submissions/ })).not.toBeInTheDocument();
    const stop = await screen.findByRole('button', { name: /Stop sharing/ });
    expect(screen.getByRole('checkbox', { name: /text of my submissions/ })).not.toBeChecked();
    await userEvent.click(stop);
    const dlg = await screen.findByRole('dialog');
    expect(dlg).toHaveAccessibleName('Stop sharing?');
    await userEvent.keyboard('{Escape}');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(api.count('DELETE /me/grants')).toBe(0);
    await userEvent.click(screen.getByRole('button', { name: /Stop sharing/ }));
    await userEvent.click(within(await screen.findByRole('dialog')).getByRole('button', { name: 'Stop sharing' }));
    expect(await screen.findByText(/Access removed/)).toBeInTheDocument();
  });
});

describe('Appeals', () => {
  it('should_show_empty_state', async () => {
    renderApp('/appeals', learner, { 'GET /me/appeals': () => ({ appeals: [] }) });
    expect(await screen.findByText('You have no appeals.')).toBeInTheDocument();
  });

  it('should_send_an_appeal_for_an_event_and_confirm_in_neutral_words', async () => {
    const { api } = renderApp('/appeals?event=ev-1', learner, {
      'GET /me/appeals': () => ({ appeals: [] }),
      'POST /me/appeals': () => ({ appeal_id: 'a1', status: 'received', text: 'x', created_at: '2026-10-10T00:00:00Z' }),
    });
    await userEvent.type(await screen.findByLabelText(/What do you think is wrong/), 'The row count looks off to me');
    await userEvent.click(screen.getByRole('button', { name: 'Send appeal' }));
    expect(await screen.findByText(/A person will review it/)).toBeInTheDocument();
    expect(api.calls.find((c) => c.key === 'POST /me/appeals')?.body).toMatchObject({ event_id: 'ev-1' });
  });
});

const baseCase: ReviewCase = {
  case_id: 'c1',
  alias: 'cnd_aaaaaaaaaaaaaaaa',
  attempt_id: 'att1',
  status: 'open',
  criterion: 'Explains the fix',
  reason: 'low_confidence',
  original_work: 'def f():\n    return 1',
  ai_rationale: 'Partial explanation',
  confidence: 'low',
  rubric_text: 'Names the root cause',
  rubric_version: '1.0.0',
  probe_status: 'unconfirmed',
  flags: [],
  integrity: { counts: { paste: 2, focus_loss: 1 }, risk: 'medium', isolation_mode: 'container' },
  streams: ['camera', 'screen'],
};

describe('Reviewer console', () => {
  it('should_show_empty_queue_message', async () => {
    renderApp('/review', reviewer, { 'GET /review/queue': () => ({ cases: [] }) });
    expect(await screen.findByText('No cases need review.')).toBeInTheDocument();
  });

  it('should_list_cases_by_alias_with_a_captioned_table', async () => {
    const { container } = renderApp('/review', reviewer, {
      'GET /review/queue': () => ({
        cases: [{ case_id: 'c1', alias: 'cnd_aaaaaaaaaaaaaaaa', criterion: 'Explains the fix', reason: 'low_confidence', confidence: 'low', created_at: '2026-10-09T00:00:00Z' }],
      }),
    });
    expect(await screen.findByRole('table', { name: 'Cases waiting for a decision' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Open case/ })).toHaveAttribute('href', '/review/c1');
    await expectNoA11yViolations(container);
  });

  it('should_show_case_context_neutral_wording_and_integrity_summary', async () => {
    const { container } = renderApp('/review/c1', reviewer, { 'GET /review/cases/c1': () => baseCase });
    expect(await screen.findByRole('heading', { level: 1, name: /Review case for cnd_aaaaaaaaaaaaaaaa/ })).toBeInTheDocument();
    expect(screen.getByText(/not a finding about the learner/)).toBeInTheDocument();
    expect(screen.getByText('Paste')).toBeInTheDocument();
    expect(screen.getByText(/never changes a result/)).toBeInTheDocument();
    expect(screen.getByLabelText('Camera and microphone recording')).toHaveAttribute('src', '/api/review/attempts/att1/recording/camera');
    expect(document.body.textContent).not.toMatch(/cheat|misconduct|suspicious|AI detected/i);
    await expectNoA11yViolations(container);
  });

  it('should_require_a_reason_then_confirm_then_show_the_ledger_entry', async () => {
    const { api } = renderApp('/review/c1', reviewer, {
      'GET /review/cases/c1': () => baseCase,
      'POST /review/cases/c1/decision': () => ({ ledger_entry: 215 }),
    });
    await screen.findByRole('heading', { level: 1 });
    await userEvent.click(screen.getByRole('button', { name: 'Record decision' }));
    expect(screen.getByText('Choose a decision.')).toBeInTheDocument();
    expect(api.count('POST /review/cases/c1/decision')).toBe(0);
    await userEvent.click(screen.getByRole('radio', { name: 'Uphold result' }));
    await userEvent.type(screen.getByLabelText('Reason'), 'Rubric criterion 2 is not met');
    await userEvent.click(screen.getByRole('button', { name: 'Record decision' }));
    await userEvent.click(within(await screen.findByRole('dialog')).getByRole('button', { name: 'Record decision' }));
    expect(await screen.findByText(/recorded in the ledger as entry 215/)).toBeInTheDocument();
  });

  it('should_keep_the_decision_in_the_form_when_recording_fails', async () => {
    renderApp('/review/c1', reviewer, {
      'GET /review/cases/c1': () => baseCase,
      'POST /review/cases/c1/decision': () => status(500),
    });
    await screen.findByRole('heading', { level: 1 });
    await userEvent.click(screen.getByRole('radio', { name: 'Needs more information' }));
    await userEvent.type(screen.getByLabelText('Reason'), 'Missing the original note');
    await userEvent.click(screen.getByRole('button', { name: 'Record decision' }));
    await userEvent.click(within(await screen.findByRole('dialog')).getByRole('button', { name: 'Record decision' }));
    expect(await screen.findByText(/Not recorded yet/)).toBeInTheDocument();
    expect(screen.getByLabelText('Reason')).toHaveValue('Missing the original note');
  });

  it('should_disable_decisions_when_original_work_is_missing', async () => {
    renderApp('/review/c1', reviewer, { 'GET /review/cases/c1': () => ({ ...baseCase, original_work: '' }) });
    expect(await screen.findByText(/Original work is unavailable/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Record decision' })).toBeDisabled();
  });
});

describe('Recruiter portal', () => {
  it('should_show_empty_roles', async () => {
    renderApp('/hr', recruiter, { 'GET /hr/roles': () => ({ roles: [] }) });
    expect(await screen.findByText(/No roles yet/)).toBeInTheDocument();
  });

  it('should_summarise_validation_errors_at_the_top_and_not_post', async () => {
    const { api, container } = renderApp('/hr/roles/new', recruiter);
    await userEvent.type(await screen.findByLabelText('Role title'), 'ab');
    await userEvent.click(screen.getByRole('button', { name: 'Save role' }));
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Title must be 3 to 80 characters.');
    expect(api.count('POST /hr/roles')).toBe(0);
    await expectNoA11yViolations(container);
  });

  it('should_show_coverage_with_icon_and_text_flag_gaps_and_state_no_ranking', async () => {
    const { container } = renderApp('/hr/roles/r1', recruiter, {
      'GET /hr/roles/r1/results': () => ({
        role_id: 'r1',
        candidates: [
          {
            alias: 'cnd_bbbbbbbbbbbbbbbb',
            competencies: [
              { competency_id: 'cmp_python', state: 'met', gap: false, reason: 'Level 4 passed', last_evidence_at: '2026-10-01T00:00:00Z' },
              { competency_id: 'cmp_sql', state: 'not_met', gap: true, reason: 'Level passed, but newest evidence is 240 days old; window is 180', last_evidence_at: '2026-02-01T00:00:00Z' },
            ],
          },
          { alias: 'cnd_aaaaaaaaaaaaaaaa', competencies: [{ competency_id: 'cmp_python', state: 'no_shared_evidence', gap: true }] },
        ],
      }),
    });
    expect(await screen.findByText(/Order is not a ranking/)).toBeInTheDocument();
    const heads = screen.getAllByRole('heading', { level: 2 }).map((h) => h.textContent);
    expect(heads).toEqual(['cnd_aaaaaaaaaaaaaaaa', 'cnd_bbbbbbbbbbbbbbbb']);
    expect(screen.getByText(/newest evidence is 240 days old/)).toBeInTheDocument();
    expect(screen.getAllByText('Gap').length).toBeGreaterThan(0);
    expect(screen.getAllByText('No shared evidence for this competency').length).toBe(1);
    expect(document.body.textContent).not.toMatch(/best match|recommended|match %|total score/i);
    await expectNoA11yViolations(container);
  });

  const sharedEv = {
    candidate_ref: 'cnd_aaaaaaaaaaaaaaaa',
    competency_id: 'cmp_python',
    proficiency: { estimate: 0.58, lower: 0.45, upper: 0.7, scale: '0-1', as_of: '2026-10-10T00:00:00Z' },
    levels_passed: [1, 2, 3, 4],
    method_counts: { deterministic_test: 5, probe: 1, ai_judged: 1, live_screening: 2, human_review: 0 },
    understanding_status: 'unconfirmed',
    last_evidence_at: '2026-10-10T00:00:00Z',
    ledger_proof: { head_hash: 'sha256:' + 'a'.repeat(64), head_sequence: 842 },
    labels: { experimental: true, ai_used: true },
    evidence_items: [
      { event_id: 'e1', method: 'deterministic_test', outcome: 'pass', occurred_at: '2026-10-09T00:00:00Z', task_version: '1.0.0', rubric_version: '1.0.0', receipt_hash: 'sha256:' + 'b'.repeat(64) },
    ],
  };

  it.each([
    ['match', { status: 'match', entry: 214 }, /Matches the ledger \(entry 214\)/],
    ['mismatch', { status: 'mismatch' }, /Does not match the ledger. Do not rely on this item./],
    ['unavailable', { status: 'unavailable' }, /Could not check right now/],
  ])('should_verify_a_receipt_and_say_%s_in_words', async (_n, reply, text) => {
    const { container } = renderApp('/hr/evidence/cnd_aaaaaaaaaaaaaaaa/cmp_python', recruiter, {
      'GET /hr/evidence/cnd_aaaaaaaaaaaaaaaa/cmp_python': () => sharedEv,
      'POST /hr/receipts/verify': () => reply,
    });
    expect(await screen.findByText(/0.58, likely range 0.45 to 0.70/)).toBeInTheDocument();
    expect(screen.getByRole('note')).toHaveTextContent(/Experimental/);
    await userEvent.click(screen.getByRole('button', { name: /Verify receipt/ }));
    expect(await screen.findByText(text)).toBeInTheDocument();
    await expectNoA11yViolations(container);
  });

  it('should_show_a_neutral_message_when_evidence_is_no_longer_shared', async () => {
    renderApp('/hr/evidence/cnd_x/cmp_python', recruiter, { 'GET /hr/evidence/cnd_x/cmp_python': () => status(404) });
    expect(await screen.findByText(/no longer shared, or was never shared/)).toBeInTheDocument();
  });
});

describe('Auditor ledger check', () => {
  it('should_announce_verified_with_the_head_hash', async () => {
    const { container } = renderApp('/audit', auditor, {
      'GET /audit/ledger/verify': () => ({ verified: true, entries: 842, head_hash: 'sha256:ab12', head_sequence: 842 }),
    });
    await userEvent.click(await screen.findByRole('button', { name: 'Verify ledger' }));
    expect(await screen.findByText(/entries 1 to 842 form an unbroken chain/)).toBeInTheDocument();
    expect(screen.getByText('sha256:ab12')).toBeInTheDocument();
    await expectNoA11yViolations(container);
  });

  it('should_distinguish_not_verified_from_could_not_run', async () => {
    const first = renderApp('/audit', auditor, {
      'GET /audit/ledger/verify': () => ({ verified: false, entries: 842, head_hash: 'sha256:ab12', head_sequence: 842, first_failing_sequence: 317 }),
    });
    await userEvent.click(await screen.findByRole('button', { name: 'Verify ledger' }));
    expect(await screen.findByText(/entry 317 does not match its expected hash/)).toBeInTheDocument();
    first.unmount();

    renderApp('/audit', auditor, { 'GET /audit/ledger/verify': () => status(500) });
    await userEvent.click(await screen.findByRole('button', { name: 'Verify ledger' }));
    await waitFor(() => expect(screen.getByText(/Verification could not run. This is not a result/)).toBeInTheDocument());
    expect(screen.queryByText(/Not verified/)).not.toBeInTheDocument();
  });
});
