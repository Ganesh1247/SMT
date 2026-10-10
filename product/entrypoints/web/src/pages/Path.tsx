import { Link } from 'react-router-dom';
import { api } from '../api/client';
import type { Level, LevelProgress } from '../api/types';
import { Empty, ErrorPanel, Loading, PageHeading, useAsync } from '../components/ui';

export const LEVEL_INFO: Record<Level, { name: string; blurb: string }> = {
  1: { name: 'Conceptual', blurb: 'Five short questions: predict output, follow a variable, define terms.' },
  2: { name: 'Debugging', blurb: 'Three broken programs. Find the error, fix it and explain what was wrong.' },
  3: { name: 'Applied', blurb: 'Two scenario tasks. Solve each one, then adapt your solution to a new constraint.' },
  4: { name: 'Live AI screening', blurb: 'A recorded video conversation about your own Level 3 solution.' },
};

function statusText(l: LevelProgress): string {
  switch (l.status) {
    case 'passed':
      return 'Passed';
    case 'in_progress':
      return 'In progress';
    case 'locked':
      return 'Locked';
    default:
      return 'Not started';
  }
}

export function PathPage() {
  const p = useAsync(() => api.progress());
  return (
    <div>
      <PageHeading>My path</PageHeading>
      <p className="muted">
        Four levels, in order. Your progress is kept. You can leave and come back to where you stopped.
      </p>
      {p.loading ? <Loading /> : null}
      {p.error ? <ErrorPanel error={p.error} onRetry={p.reload} what="your path" /> : null}
      {p.data ? (
        p.data.levels.length === 0 ? (
          <Empty>No levels are available yet.</Empty>
        ) : (
          <>
            <ol className="levels" aria-label="Levels">
              {[...p.data.levels]
                .sort((a, b) => a.level - b.level)
                .map((l) => {
                  const info = LEVEL_INFO[l.level];
                  const action =
                    l.status === 'locked' ? (
                      <span className="chip">Unlocks after Level {l.level - 1}</span>
                    ) : l.status === 'passed' ? (
                      <span className="chip success">
                        <span aria-hidden="true">{'✓'}</span> Passed
                      </span>
                    ) : (
                      <Link className="btn" to={`/lobby/${l.level}`}>
                        {l.status === 'in_progress' ? 'Resume' : l.attempts > 0 ? 'Try again' : 'Start'}
                        <span className="sr-only"> Level {l.level}</span>
                      </Link>
                    );
                  return (
                    <li key={l.level} className="level-card" data-status={l.status}>
                      <span className="level-num" aria-hidden="true">
                        {l.level}
                      </span>
                      <div>
                        <h2 style={{ margin: 0, fontSize: '1.125rem' }}>
                          Level {l.level}: {info.name}
                        </h2>
                        <p className="muted small" style={{ margin: 0 }}>
                          {info.blurb}
                        </p>
                        <p className="small" style={{ margin: 0 }}>
                          {statusText(l)}
                          {l.attempts > 0 ? `. Attempts so far: ${l.attempts}.` : ''}
                        </p>
                      </div>
                      <div>{action}</div>
                    </li>
                  );
                })}
            </ol>
            {p.data.all_passed ? (
              <p style={{ marginTop: 'var(--space-5)' }}>
                All four levels are passed. <Link to="/profile">See your profile</Link>.
              </p>
            ) : (
              <p className="muted" style={{ marginTop: 'var(--space-5)' }}>
                Your estimate updates after all four levels are passed.
              </p>
            )}
          </>
        )
      ) : null}
    </div>
  );
}
