import { useEffect, useRef, useState } from 'react';
import { EditorState } from '@codemirror/state';
import { EditorView, keymap, lineNumbers, highlightActiveLine, drawSelection } from '@codemirror/view';
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands';
import { indentOnInput, bracketMatching, syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language';
import { python } from '@codemirror/lang-python';
import { sql } from '@codemirror/lang-sql';

interface Props {
  id: string;
  label: string;
  value: string;
  language: 'python' | 'sql';
  onChange: (v: string) => void;
}

/**
 * CodeMirror 6 editor. Accessibility (A11Y-16): Tab is NOT bound, so Tab leaves the editor;
 * a plain textarea fallback is one toggle away and is the default when the toggle is on.
 */
export function CodeEditor({ id, label, value, language, onChange }: Props) {
  const host = useRef<HTMLDivElement>(null);
  const view = useRef<EditorView | null>(null);
  const latest = useRef(onChange);
  latest.current = onChange;
  const [plain, setPlain] = useState(false);

  useEffect(() => {
    if (plain || !host.current) return;
    const v = new EditorView({
      parent: host.current,
      state: EditorState.create({
        doc: value,
        extensions: [
          lineNumbers(),
          history(),
          drawSelection(),
          highlightActiveLine(),
          indentOnInput(),
          bracketMatching(),
          syntaxHighlighting(defaultHighlightStyle),
          keymap.of([...defaultKeymap, ...historyKeymap]),
          language === 'python' ? python() : sql(),
          EditorView.contentAttributes.of({
            'aria-label': label,
            'aria-describedby': `${id}-help`,
            'aria-multiline': 'true',
          }),
          EditorView.updateListener.of((u) => {
            if (u.docChanged) latest.current(u.state.doc.toString());
          }),
        ],
      }),
    });
    view.current = v;
    return () => {
      v.destroy();
      view.current = null;
    };
    // value intentionally excluded: the editor owns its document after mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [plain, language, id, label]);

  // keep external resets (new item) in sync
  useEffect(() => {
    const v = view.current;
    if (v && v.state.doc.toString() !== value) {
      v.dispatch({ changes: { from: 0, to: v.state.doc.length, insert: value } });
    }
  }, [value]);

  return (
    <div>
      <p id={`${id}-help`} className="small muted">
        Press Escape then Tab to leave the editor. You can also switch to a plain text box.
      </p>
      {plain ? (
        <textarea
          id={id}
          className="editor-plain"
          aria-label={label}
          aria-describedby={`${id}-help`}
          value={value}
          spellCheck={false}
          onChange={(e) => onChange(e.target.value)}
        />
      ) : (
        <div className="editor" ref={host} data-testid="code-editor" />
      )}
      <label className="check-row small">
        <input type="checkbox" checked={plain} onChange={(e) => setPlain(e.target.checked)} />
        <span>Use a plain text box instead of the code editor</span>
      </label>
    </div>
  );
}
