import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

afterEach(() => cleanup());

// jsdom lacks layout APIs that CodeMirror measures with.
const rectList = () => ({ length: 0, item: () => null, [Symbol.iterator]: function* () {} });
const zeroRect = () => ({ x: 0, y: 0, top: 0, left: 0, right: 0, bottom: 0, width: 0, height: 0, toJSON() {} });
if (typeof Range !== 'undefined') {
  Range.prototype.getClientRects = rectList as never;
  Range.prototype.getBoundingClientRect = zeroRect as never;
}
if (typeof document !== 'undefined') {
  (document as unknown as { elementFromPoint: () => null }).elementFromPoint = () => null;
}
