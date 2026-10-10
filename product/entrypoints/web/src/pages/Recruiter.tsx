import { useState, type FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api/client';
import type { CoverageState, Method, ReceiptResult, RoleCompetencyReq, RoleDraft } from '../api/types';
import {
  Alert,
  Empty,
  ErrorPanel,
  EstimateBand,
  ExperimentalBanner,
  Field,
  Loading,
  METHOD_LABEL,
  MethodLabel,
  PageHeading,
  StatCards,
  UnderstandingChip,
  competencyName,
  fmtDate,
  useAsync,
} from '../components/ui';

const COVER: Record<CoverageState, { text: string; icon: string; cls: string }> = {
  met: { text: 'Met', icon: '✓', cls: 'success' },
  partly_met: { text: 'Partly met', icon: '◐', cls: 'warning' },
  not_met: { text: 'Not met', icon: '×', cls: 'error' },
  no_shared_evidence: { text: 'No shared evidence', icon: '—', cls: '' },
};

export function RolesPage() {
  const r = useAsync(() => api.roles());
  return (
    <div>
      <PageHeading>Roles</PageHeading>
      <ExperimentalBanner />
      <div className="row" style={{ marginBottom: 'var(--space-4)' }}>
        <Link className="btn" to="/hr/roles/new">
          New role
        </Link>
      </div>
      {r.loading ? <Loading label="Loading roles" /> : null}
      {r.error ? <ErrorPanel error={r.error} onRetry={r.reload} what="roles" /> : null}
      {r.data ? (
        r.data.roles.length === 0 ? (
          <Empty>No roles yet. Create a role to see shared evidence against it.</Empty>
        ) : (
          <>
            <StatCards
              items={[
                { label: 'Roles tracked', value: r.data.roles.length, hint: 'REQ-016: coverage and gaps, no rank' },
                { label: 'Latest role version', value: Math.max(...r.data.roles.map((x) => x.version)) },
                { label: 'No-grant visibility', value: '0 fields', tone: 'success', hint: 'Until a learner shares (NFR-003)' },
              ]}
            />
          <div className="table-wrap">
            <table>
              <caption className="sr-only">Your roles</caption>
              <thead>
                <tr>
                  <th scope="col">Title</th>
                  <th scope="col">Version</th>
                  <th scope="col">Created</th>
                  <th scope="col">
                    <span className="sr-only">Open</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {r.data.roles.map((x) => (
                  <tr key={x.role_id}>
                    <th scope="row">{x.title}</th>
                    <td>{x.version}</td>
                    <td>{fmtDate(x.created_at)}</td>
                    <td>
                      <Link className="btn secondary" to={`/hr/roles/${encodeURIComponent(x.role_id)}`}>
                        See shared evidence<span className="sr-only"> for {x.title}</span>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          </>
        )
      ) : null}
    </div>
  );
}

const METHOD_KEYS = Object.keys(METHOD_LABEL) as Method[];

export function RoleSetupPage() {
  const nav = useNavigate();
  const [title, setTitle] = useState('');
  const [summary, setSummary] = useState('');
  const [comps, setComps] = useState<RoleCompetencyReq[]>([{ competency_id: 'cmp_python', priority: 'required' }]);
  const [errs, setErrs] = useState<string[]>([]);
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const update = (i: number, patch: Partial<RoleCompetencyReq>) =>
    setComps((s) => s.map((c, n) => (n === i ? { ...c, ...patch } : c)));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const er: string[] = [];
    if (title.trim().length < 3 || title.trim().length > 80) er.push('Title must be 3 to 80 characters.');
    if (summary.length > 500) er.push('Summary must be 500 characters or fewer.');
    if (comps.length === 0) er.push('Add at least one competency.');
    if (new Set(comps.map((c) => c.competency_id)).size !== comps.length) er.push('Each competency can be added once.');
    comps.forEach((c, i) => {
      if (c.min_estimate_lower !== undefined && (c.min_estimate_lower < 0 || c.min_estimate_lower > 1))
        er.push(`Competency ${i + 1}: lowest likely value must be between 0 and 1.`);
      if (c.max_evidence_age_days !== undefined && (c.max_evidence_age_days < 1 || c.max_evidence_age_days > 1825))
        er.push(`Competency ${i + 1}: evidence age must be 1 to 1825 days.`);
    });
    setErrs(er);
    if (er.length) return;
    const body: RoleDraft = { title: title.trim(), summary: summary.trim() || undefined, competencies: comps };
    setBusy(true);
    try {
      const saved = await api.createRole(body);
      setMsg(`Role saved as version ${saved.version}.`);
      nav(`/hr/roles/${encodeURIComponent(saved.role_id)}`);
    } catch {
      setErrs(['The role was not saved. Try again.']);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <PageHeading>New role</PageHeading>
      <ExperimentalBanner />
      {errs.length > 0 ? (
        <div className="alert error" role="alert" tabIndex={-1} ref={(el) => el?.focus()}>
          <div>
            <strong>Please fix the following:</strong>
            <ul>
              {errs.map((x) => (
                <li key={x}>{x}</li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}
      {msg ? <Alert kind="success">{msg}</Alert> : null}
      <form onSubmit={submit} noValidate className="narrow" style={{ maxWidth: 760 }}>
        <Field id="title" label="Role title" hint="3 to 80 characters.">
          {(p) => <input {...p} type="text" value={title} onChange={(e) => setTitle(e.target.value)} maxLength={120} />}
        </Field>
        <Field id="summary" label="Summary (optional)" hint="Up to 500 characters.">
          {(p) => <textarea {...p} value={summary} onChange={(e) => setSummary(e.target.value)} />}
        </Field>
        <h2>Competencies</h2>
        {comps.map((c, i) => (
          <fieldset key={i}>
            <legend>Competency {i + 1}</legend>
            <Field id={`comp-${i}`} label="Competency">
              {(p) => (
                <select {...p} value={c.competency_id} onChange={(e) => update(i, { competency_id: e.target.value })}>
                  <option value="cmp_python">Python</option>
                  <option value="cmp_sql">SQL</option>
                </select>
              )}
            </Field>
            <Field id={`prio-${i}`} label="Priority">
              {(p) => (
                <select {...p} value={c.priority} onChange={(e) => update(i, { priority: e.target.value as 'required' | 'preferred' })}>
                  <option value="required">Required</option>
                  <option value="preferred">Preferred</option>
                </select>
              )}
            </Field>
            <Field id={`lvl-${i}`} label="Minimum level passed (1 to 4, optional)">
              {(p) => (
                <input
                  {...p}
                  type="number"
                  min={1}
                  max={4}
                  value={c.min_levels_passed ?? ''}
                  onChange={(e) => update(i, { min_levels_passed: e.target.value ? Number(e.target.value) : undefined })}
                />
              )}
            </Field>
            <Field id={`low-${i}`} label="Lowest likely value of at least (0 to 1, optional)">
              {(p) => (
                <input
                  {...p}
                  type="number"
                  min={0}
                  max={1}
                  step={0.05}
                  value={c.min_estimate_lower ?? ''}
                  onChange={(e) => update(i, { min_estimate_lower: e.target.value ? Number(e.target.value) : undefined })}
                />
              )}
            </Field>
            <Field id={`age-${i}`} label="Evidence no older than (days, 1 to 1825, optional)">
              {(p) => (
                <input
                  {...p}
                  type="number"
                  min={1}
                  max={1825}
                  value={c.max_evidence_age_days ?? ''}
                  onChange={(e) => update(i, { max_evidence_age_days: e.target.value ? Number(e.target.value) : undefined })}
                />
              )}
            </Field>
            <label className="check-row">
              <input
                type="checkbox"
                checked={!!c.require_understanding_confirmed}
                onChange={(e) => update(i, { require_understanding_confirmed: e.target.checked })}
              />
              <span>Understanding must be confirmed</span>
            </label>
            <fieldset>
              <legend>Allowed evidence methods (none selected means all)</legend>
              {METHOD_KEYS.map((m) => (
                <label key={m} className="check-row">
                  <input
                    type="checkbox"
                    checked={c.allowed_methods?.includes(m) ?? false}
                    onChange={(e) => {
                      const cur = c.allowed_methods ?? [];
                      const next = e.target.checked ? [...cur, m] : cur.filter((x) => x !== m);
                      update(i, { allowed_methods: next.length ? next : undefined });
                    }}
                  />
                  <span>{METHOD_LABEL[m].text}</span>
                </label>
              ))}
            </fieldset>
            <p className="small" aria-live="polite">
              <strong>Reads as:</strong> {c.priority === 'required' ? 'Required' : 'Preferred'}: {competencyName(c.competency_id)}
              {c.min_levels_passed ? `, level ${c.min_levels_passed} or higher` : ''}
              {c.min_estimate_lower !== undefined ? `, lowest likely value of at least ${c.min_estimate_lower.toFixed(2)}` : ''}
              {c.max_evidence_age_days ? `, evidence from the last ${c.max_evidence_age_days} days` : ''}
              {c.require_understanding_confirmed ? ', understanding confirmed' : ''}.
            </p>
            {comps.length > 1 ? (
              <button type="button" className="btn quiet" onClick={() => setComps((s) => s.filter((_, n) => n !== i))}>
                Remove competency {i + 1}
              </button>
            ) : null}
          </fieldset>
        ))}
        {comps.length < 8 ? (
          <button
            type="button"
            className="btn secondary"
            onClick={() =>
              setComps((s) => [
                ...s,
                { competency_id: s.some((c) => c.competency_id === 'cmp_sql') ? 'cmp_python' : 'cmp_sql', priority: 'preferred' },
              ])
            }
          >
            Add competency
          </button>
        ) : null}
        <div className="row" style={{ marginTop: 'var(--space-5)' }}>
          <button type="submit" className="btn" disabled={busy}>
            Save role
          </button>
          <Link className="btn quiet" to="/hr">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}

export function RoleResultsPage() {
  const { roleId = '' } = useParams();
  const r = useAsync(() => api.roleResults(roleId), [roleId]);
  const [filter, setFilter] = useState<'all' | CoverageState | 'gap'>('all');
  return (
    <div>
      <PageHeading>Shared evidence for this role</PageHeading>
      <ExperimentalBanner />
      <p className="muted">
        Order is not a ranking. Candidates are listed by alias. Results show coverage and gaps only, with no totals.
      </p>
      {r.loading ? <Loading label="Loading shared evidence" /> : null}
      {r.error ? <ErrorPanel error={r.error} onRetry={r.reload} what="shared evidence" /> : null}
      {r.data ? (
        r.data.candidates.length === 0 ? (
          <Empty>No shared evidence yet for this role.</Empty>
        ) : (
          <>
            {(() => {
              const rows = r.data.candidates.flatMap((c) => c.competencies);
              const count = (s: CoverageState) => rows.filter((x) => x.state === s).length;
              const gaps = rows.filter((x) => x.gap).length;
              return (
                <StatCards
                  items={[
                    { label: 'Candidates shared', value: r.data.candidates.length, hint: 'By alias, order is not a ranking' },
                    { label: 'Required gaps', value: gaps, tone: gaps > 0 ? 'warning' : 'success' },
                    { label: 'Met', value: count('met'), tone: 'success' },
                    { label: 'No shared evidence', value: count('no_shared_evidence') },
                  ]}
                />
              );
            })()}
            <Field id="cf" label="Filter by coverage">
              {(p) => (
                <select {...p} value={filter} onChange={(e) => setFilter(e.target.value as typeof filter)}>
                  <option value="all">All</option>
                  <option value="gap">Gaps</option>
                  <option value="met">Met</option>
                  <option value="partly_met">Partly met</option>
                  <option value="not_met">Not met</option>
                  <option value="no_shared_evidence">No shared evidence</option>
                </select>
              )}
            </Field>
            {[...r.data.candidates]
              .sort((a, b) => a.alias.localeCompare(b.alias))
              .map((cand) => {
                const rows = cand.competencies.filter((c) => filter === 'all' || (filter === 'gap' ? c.gap : c.state === filter));
                if (rows.length === 0) return null;
                return (
                  <section key={cand.alias} className="panel" aria-labelledby={`cand-${cand.alias}`}>
                    <h2 id={`cand-${cand.alias}`} className="mono" style={{ fontSize: '1rem' }}>
                      {cand.alias}
                    </h2>
                    <div className="table-wrap">
                      <table>
                        <caption className="sr-only">Coverage for {cand.alias}</caption>
                        <thead>
                          <tr>
                            <th scope="col">Competency</th>
                            <th scope="col">Coverage</th>
                            <th scope="col">Reason</th>
                            <th scope="col">Latest evidence</th>
                            <th scope="col">
                              <span className="sr-only">Open</span>
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {rows.map((c) => {
                            const cv = COVER[c.state];
                            return (
                              <tr key={c.competency_id}>
                                <th scope="row">{competencyName(c.competency_id)}</th>
                                <td>
                                  <span className={`chip ${cv.cls}`}>
                                    <span aria-hidden="true">{cv.icon}</span> {cv.text}
                                  </span>
                                  {c.gap ? <span className="chip warning"> Gap</span> : null}
                                </td>
                                <td>{c.state === 'no_shared_evidence' ? 'No shared evidence for this competency' : c.reason ?? ''}</td>
                                <td>{fmtDate(c.last_evidence_at)}</td>
                                <td>
                                  {c.state !== 'no_shared_evidence' ? (
                                    <Link
                                      className="btn secondary"
                                      to={`/hr/evidence/${encodeURIComponent(cand.alias)}/${encodeURIComponent(c.competency_id)}`}
                                    >
                                      Open evidence<span className="sr-only"> for {cand.alias}, {competencyName(c.competency_id)}</span>
                                    </Link>
                                  ) : null}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </section>
                );
              })}
          </>
        )
      ) : null}
    </div>
  );
}

function ReceiptButton({ hash, label, candidateRef, competencyId }: { hash: string; label: string; candidateRef: string; competencyId: string }) {
  const [res, setRes] = useState<ReceiptResult | 'running' | 'error' | null>(null);
  const check = async () => {
    setRes('running');
    try {
      setRes(await api.verifyReceipt(hash, candidateRef, competencyId));
    } catch {
      setRes('error');
    }
  };
  return (
    <span>
      <button type="button" className="btn secondary" onClick={() => void check()} disabled={res === 'running'}>
        Verify receipt<span className="sr-only">: {label}</span>
      </button>{' '}
      <span role="status" className="small">
        {res === 'running' ? 'Checking the ledger' : null}
        {res === 'error' ? 'Could not check right now.' : null}
        {res && typeof res === 'object' && res.status === 'match' ? (
          <span style={{ color: 'var(--color-success)' }}>
            {'✓'} Matches the ledger{res.entry ? ` (entry ${res.entry})` : ''}
          </span>
        ) : null}
        {res && typeof res === 'object' && res.status === 'mismatch' ? (
          <span style={{ color: 'var(--color-error)' }}>{'×'} Does not match the ledger. Do not rely on this item.</span>
        ) : null}
        {res && typeof res === 'object' && res.status === 'unavailable' ? 'Could not check right now.' : null}
      </span>
    </span>
  );
}

export function EvidencePage() {
  const { alias = '', competency = '' } = useParams();
  const e = useAsync(() => api.sharedEvidence(alias, competency), [alias, competency]);
  return (
    <div>
      <PageHeading>{`Evidence for ${alias}`}</PageHeading>
      <ExperimentalBanner />
      <p className="muted">These results should support, not replace, your own assessment.</p>
      {e.loading ? <Loading label="Loading shared evidence" /> : null}
      {e.error ? (
        <Alert kind="info">This evidence is no longer shared, or was never shared. No further detail is available.</Alert>
      ) : null}
      {e.data ? (
        <>
          <section className="panel" aria-labelledby="prof">
            <h2 id="prof">{competencyName(e.data.competency_id)}</h2>
            <EstimateBand
              label={competencyName(e.data.competency_id)}
              estimate={e.data.proficiency.estimate}
              lower={e.data.proficiency.lower}
              upper={e.data.proficiency.upper}
              asOf={e.data.proficiency.as_of}
            />
            {e.data.proficiency.upper - e.data.proficiency.lower > 0.4 ? (
              <p>Wide range: little or older evidence.</p>
            ) : null}
            <p>
              Levels passed: {e.data.levels_passed.length ? e.data.levels_passed.join(', ') : 'none'}. Latest evidence:{' '}
              {fmtDate(e.data.last_evidence_at)}. AI-assisted items: {e.data.labels.ai_used ? 'yes' : 'no'}.
            </p>
            <p>
              <UnderstandingChip status={e.data.understanding_status} />
            </p>
          </section>
          <section className="panel" aria-labelledby="meth">
            <h2 id="meth">Evidence methods</h2>
            <table>
              <caption className="sr-only">Item counts by method</caption>
              <thead>
                <tr>
                  <th scope="col">Method</th>
                  <th scope="col">Items</th>
                </tr>
              </thead>
              <tbody>
                {METHOD_KEYS.map((m) => (
                  <tr key={m}>
                    <th scope="row">
                      <MethodLabel method={m} />
                    </th>
                    <td>{e.data!.method_counts[m]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
          <section aria-labelledby="items">
            <h2 id="items">Evidence items</h2>
            <ul className="stack" style={{ listStyle: 'none', padding: 0 }}>
              {e.data.evidence_items.map((it) => (
                <li key={it.event_id} className="panel">
                  <p className="row" style={{ margin: 0 }}>
                    <MethodLabel method={it.method} />
                    <span className="chip">{it.outcome === 'inconclusive' ? 'Inconclusive' : it.outcome}</span>
                    {it.ai_disclosure ? <span className="chip warning">AI-assisted</span> : null}
                    {it.understanding_status ? <UnderstandingChip status={it.understanding_status} /> : null}
                  </p>
                  <p className="small muted">
                    {fmtDate(it.occurred_at)}. Task {it.task_version}, rubric {it.rubric_version}.
                  </p>
                  {it.submission_excerpt ? (
                    <blockquote>
                      <p className="small muted">Shared by the learner</p>
                      <pre className="mono small" style={{ whiteSpace: 'pre-wrap' }}>
                        {it.submission_excerpt}
                      </pre>
                    </blockquote>
                  ) : null}
                  <ReceiptButton hash={it.receipt_hash} label={it.event_id} candidateRef={alias} competencyId={competency} />
                </li>
              ))}
            </ul>
          </section>
          <p className="small muted">
            Ledger head: sequence {e.data.ledger_proof.head_sequence},{' '}
            <span className="mono" style={{ wordBreak: 'break-all' }}>
              {e.data.ledger_proof.head_hash}
            </span>
            {e.data.assessor_report_ref ? <> . Assessor report: {e.data.assessor_report_ref}</> : null}
          </p>
        </>
      ) : null}
    </div>
  );
}
