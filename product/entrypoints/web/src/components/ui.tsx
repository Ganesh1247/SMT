import { useEffect, useRef, useState, type ReactNode } from 'react';
import { ApiError } from '../api/client';
import type { Method, Understanding } from '../api/types';

export function Alert({
  kind,
  children,
  title,
}: {
  kind: 'info' | 'success' | 'warning' | 'error';
  children: ReactNode;
  title?: string;
}) {
  const icon = { info: 'i', success: '✓', warning: '!', error: '×' }[kind];
  const word = { info: 'Information', success: 'Success', warning: 'Notice', error: 'Problem' }[kind];
  return (
    <div className={`alert ${kind}`} role={kind === 'error' ? 'alert' : 'status'}>
      <span className="alert-icon" aria-hidden="true">
        {icon}
      </span>
      <div>
        <span className="sr-only">{word}: </span>
        {title ? <strong>{title} </strong> : null}
        {children}
      </div>
    </div>
  );
}

export function Loading({ label = 'Loading your results' }: { label?: string }) {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setSlow(true), 5000);
    return () => clearTimeout(t);
  }, []);
  return (
    <div role="status" aria-live="polite">
      <p>{slow ? 'Still loading. Your work is saved.' : label}</p>
      <div className="skeleton" aria-hidden="true" style={{ width: '60%' }} />
      <div className="skeleton" aria-hidden="true" style={{ width: '80%' }} />
      <div className="skeleton" aria-hidden="true" style={{ width: '40%' }} />
    </div>
  );
}

export function ErrorPanel({ error, onRetry, what = 'this' }: { error: unknown; onRetry?: () => void; what?: string }) {
  const ref = error instanceof ApiError && error.reference ? error.reference : null;
  return (
    <div className="alert error" role="alert">
      <span className="alert-icon" aria-hidden="true">
        {'×'}
      </span>
      <div>
        <p>
          We could not load {what}. Your work is saved. Try again.
          {ref ? <span className="small muted"> Reference: {ref}</span> : null}
        </p>
        {onRetry ? (
          <button type="button" className="btn secondary" onClick={onRetry}>
            Retry
          </button>
        ) : null}
      </div>
    </div>
  );
}

export function Empty({ children, action }: { children: ReactNode; action?: ReactNode }) {
  return (
    <div className="panel empty">
      <p style={{ margin: '0 auto var(--space-3)' }}>{children}</p>
      {action}
    </div>
  );
}

export function ExperimentalBanner() {
  return (
    <p className="experimental" role="note">
      Experimental. This is not a validated predictor of job performance. Some feedback is AI-assisted and can be appealed.
    </p>
  );
}

export function Field({
  id,
  label,
  hint,
  error,
  children,
}: {
  id: string;
  label: string;
  hint?: string;
  error?: string | null;
  children: (props: { id: string; 'aria-describedby'?: string; 'aria-invalid'?: boolean }) => ReactNode;
}) {
  const hintId = hint ? `${id}-hint` : undefined;
  const errId = error ? `${id}-err` : undefined;
  const described = [hintId, errId].filter(Boolean).join(' ') || undefined;
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {hint ? (
        <span className="hint" id={hintId}>
          {hint}
        </span>
      ) : null}
      {children({ id, 'aria-describedby': described, 'aria-invalid': error ? true : undefined })}
      {error ? (
        <span className="error-text" id={errId}>
          {error}
        </span>
      ) : null}
    </div>
  );
}

export const METHOD_LABEL: Record<Method, { text: string; icon: string }> = {
  deterministic_test: { text: 'Automated test', icon: '⚙' },
  probe: { text: 'Understanding probe', icon: '?' },
  ai_judged: { text: 'AI-assisted judgement', icon: '✦' },
  live_screening: { text: 'Level 4 live screening', icon: '▶' },
  human_review: { text: 'Human review', icon: '☺' },
};

export function MethodLabel({ method }: { method: Method }) {
  const m = METHOD_LABEL[method];
  return (
    <span className="chip">
      <span aria-hidden="true">{m.icon}</span> {m.text}
    </span>
  );
}

export function UnderstandingChip({ status }: { status: Understanding }) {
  if (status === 'confirmed') {
    return (
      <span className="chip success">
        <span aria-hidden="true">{'✓'}</span> Understanding confirmed
      </span>
    );
  }
  if (status === 'unconfirmed') {
    return (
      <span className="chip">
        <span aria-hidden="true">{'○'}</span> Output verified, understanding unconfirmed
      </span>
    );
  }
  return <span className="chip">Understanding probe not attempted</span>;
}

export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return 'not available';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return 'not available';
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
}

export function fmt2(n: number): string {
  return n.toFixed(2);
}

export function EstimateBand({
  label,
  estimate,
  lower,
  upper,
  asOf,
}: {
  label: string;
  estimate: number;
  lower: number;
  upper: number;
  asOf: string;
}) {
  const text = `${fmt2(estimate)}, likely range ${fmt2(lower)} to ${fmt2(upper)}, as of ${fmtDate(asOf)}`;
  const pct = (n: number) => `${Math.max(0, Math.min(1, n)) * 100}%`;
  return (
    <figure style={{ margin: 0 }} aria-label={`${label} estimate`}>
      <div className="band" aria-hidden="true">
        <div className="band-range" style={{ left: pct(lower), width: `${Math.max(0, (upper - lower) * 100)}%` }} />
        <div className="band-point" style={{ left: pct(estimate) }} />
      </div>
      <figcaption>
        <strong>{label}:</strong> {text}
      </figcaption>
      <table className="small" style={{ marginTop: 'var(--space-2)' }}>
        <caption className="sr-only">{label} estimate as a table</caption>
        <thead>
          <tr>
            <th scope="col">Estimate</th>
            <th scope="col">Lowest likely</th>
            <th scope="col">Highest likely</th>
            <th scope="col">As of</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{fmt2(estimate)}</td>
            <td>{fmt2(lower)}</td>
            <td>{fmt2(upper)}</td>
            <td>{fmtDate(asOf)}</td>
          </tr>
        </tbody>
      </table>
    </figure>
  );
}

/** Modal confirm dialog: focus trapped, Escape closes, focus returns to the opener. */
export function ConfirmDialog({
  title,
  children,
  confirmLabel,
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
  danger,
}: {
  title: string;
  children: ReactNode;
  confirmLabel: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  danger?: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const opener = document.activeElement as HTMLElement | null;
    const first = ref.current?.querySelector<HTMLElement>('button');
    first?.focus();
    return () => opener?.focus?.();
  }, []);
  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      e.stopPropagation();
      onCancel();
    } else if (e.key === 'Tab') {
      const f = ref.current?.querySelectorAll<HTMLElement>('button, [href], input, textarea, select');
      if (!f || f.length === 0) return;
      const first = f[0];
      const last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  };
  return (
    <div className="dialog-backdrop">
      <div
        className="dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dlg-title"
        ref={ref}
        onKeyDown={onKey}
      >
        <h2 id="dlg-title">{title}</h2>
        <div>{children}</div>
        <div className="row" style={{ marginTop: 'var(--space-4)' }}>
          <button type="button" className="btn secondary" onClick={onCancel}>
            {cancelLabel}
          </button>
          <button type="button" className={`btn${danger ? ' danger' : ''}`} onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

/** Moves focus to the page heading on mount (A11Y-3) and sets the document title. */
export function PageHeading({ children, title }: { children: ReactNode; title?: string }) {
  const ref = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    ref.current?.focus();
    if (typeof children === 'string') document.title = `${title ?? children} - Crucible`;
  }, [children, title]);
  return (
    <h1 tabIndex={-1} ref={ref}>
      {children}
    </h1>
  );
}

export function useAsync<T>(fn: () => Promise<T>, deps: unknown[] = []) {
  const [state, setState] = useState<{ data: T | null; error: unknown; loading: boolean }>({
    data: null,
    error: null,
    loading: true,
  });
  const [tick, setTick] = useState(0);
  useEffect(() => {
    let live = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    fn().then(
      (data) => live && setState({ data, error: null, loading: false }),
      (error) => live && setState({ data: null, error, loading: false }),
    );
    return () => {
      live = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);
  return { ...state, reload: () => setTick((t) => t + 1) };
}

export const COMPETENCIES: Record<string, string> = {
  cmp_python: 'Python',
  cmp_sql: 'SQL',
  python: 'Python',
  sql: 'SQL',
};
export const competencyName = (id: string) => COMPETENCIES[id] ?? id;
