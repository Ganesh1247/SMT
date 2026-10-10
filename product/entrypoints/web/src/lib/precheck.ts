// Pre-exam check evaluation. The server re-validates; this drives the lobby UI only.
// Thresholds follow build-brief section 4 (defaults >= 2 Mbps down, >= 1 Mbps up, < 400 ms).

export interface Thresholds {
  minDownMbps: number;
  minUpMbps: number;
  maxLatencyMs: number;
}
export const DEFAULT_THRESHOLDS: Thresholds = { minDownMbps: 2, minUpMbps: 1, maxLatencyMs: 400 };

export interface PrecheckInputs {
  downMbps: number | null;
  upMbps: number | null;
  latencyMs: number | null;
  camera: boolean;
  mic: boolean;
  screenSurface: string | null;
  fullscreen: boolean;
  /** null when the browser cannot tell (API unavailable) */
  singleDisplay: boolean | null;
  chromium: boolean;
}

export type CheckId = 'network' | 'camera' | 'microphone' | 'screen' | 'fullscreen' | 'display' | 'browser';
export interface CheckResult {
  id: CheckId;
  label: string;
  ok: boolean;
  /** plain-language next step, present when not ok */
  reason?: string;
}

export function evaluatePrecheck(i: PrecheckInputs, t: Thresholds = DEFAULT_THRESHOLDS): {
  checks: CheckResult[];
  allPassed: boolean;
} {
  const net =
    i.downMbps !== null &&
    i.upMbps !== null &&
    i.latencyMs !== null &&
    i.downMbps >= t.minDownMbps &&
    i.upMbps >= t.minUpMbps &&
    i.latencyMs < t.maxLatencyMs;
  const checks: CheckResult[] = [
    {
      id: 'browser',
      label: 'Supported browser',
      ok: i.chromium,
      reason: 'This exam runs in Chrome or Edge. Open this page in one of them to continue.',
    },
    {
      id: 'network',
      label: 'Network connection',
      ok: net,
      reason: `Your connection needs at least ${t.minDownMbps} Mbps down, ${t.minUpMbps} Mbps up and a delay under ${t.maxLatencyMs} ms. Move closer to your router or close other apps, then test again.`,
    },
    {
      id: 'camera',
      label: 'Camera',
      ok: i.camera,
      reason: 'We could not use your camera. Allow camera access in the browser address bar, then try again.',
    },
    {
      id: 'microphone',
      label: 'Microphone',
      ok: i.mic,
      reason: 'We could not use your microphone. Allow microphone access in the browser address bar, then try again.',
    },
    {
      id: 'screen',
      label: 'Entire screen shared',
      ok: i.screenSurface === 'monitor',
      reason: 'Please share your entire screen, not a window or a tab. Choose "Entire screen" in the picker.',
    },
    {
      id: 'fullscreen',
      label: 'Full screen',
      ok: i.fullscreen,
      reason: 'The exam needs full screen mode. Select "Enter full screen" and allow it.',
    },
    {
      id: 'display',
      label: 'Single display',
      ok: i.singleDisplay !== false,
      reason: 'More than one display is connected. Disconnect the extra display, then check again.',
    },
  ];
  for (const c of checks) if (c.ok) delete c.reason;
  return { checks, allPassed: checks.every((c) => c.ok) };
}

export function isChromium(userAgent: string): boolean {
  if (/\b(Firefox|FxiOS)\//.test(userAgent)) return false;
  return /\b(Chrome|Chromium|Edg)\//.test(userAgent);
}
