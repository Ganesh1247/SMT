import { describe, it, expect } from 'vitest';
import { DEFAULT_THRESHOLDS, evaluatePrecheck, isChromium, type PrecheckInputs } from './precheck';

const good: PrecheckInputs = {
  downMbps: 25,
  upMbps: 8,
  latencyMs: 40,
  camera: true,
  mic: true,
  screenSurface: 'monitor',
  fullscreen: true,
  singleDisplay: true,
  chromium: true,
};

const failing = (r: ReturnType<typeof evaluatePrecheck>) => r.checks.filter((c) => !c.ok).map((c) => c.id);

describe('evaluatePrecheck', () => {
  it('should_pass_when_every_requirement_is_met', () => {
    const r = evaluatePrecheck(good);
    expect(r.allPassed).toBe(true);
    expect(failing(r)).toEqual([]);
  });

  it('should_use_documented_defaults_for_network_thresholds', () => {
    expect(DEFAULT_THRESHOLDS).toEqual({ minDownMbps: 2, minUpMbps: 1, maxLatencyMs: 400 });
  });

  it('should_pass_at_exact_threshold_boundaries', () => {
    const r = evaluatePrecheck({ ...good, downMbps: 2, upMbps: 1, latencyMs: 399 });
    expect(r.allPassed).toBe(true);
  });

  it('should_fail_network_when_latency_is_400_or_more', () => {
    expect(failing(evaluatePrecheck({ ...good, latencyMs: 400 }))).toEqual(['network']);
  });

  it('should_fail_network_when_download_is_below_minimum', () => {
    expect(failing(evaluatePrecheck({ ...good, downMbps: 1.9 }))).toEqual(['network']);
  });

  it('should_fail_network_when_upload_is_below_minimum', () => {
    expect(failing(evaluatePrecheck({ ...good, upMbps: 0.5 }))).toEqual(['network']);
  });

  it('should_fail_network_when_not_measured_yet', () => {
    expect(failing(evaluatePrecheck({ ...good, downMbps: null }))).toEqual(['network']);
  });

  it('should_honour_server_supplied_thresholds', () => {
    const r = evaluatePrecheck({ ...good, downMbps: 5 }, { minDownMbps: 10, minUpMbps: 1, maxLatencyMs: 400 });
    expect(failing(r)).toEqual(['network']);
  });

  it('should_fail_camera_and_microphone_independently', () => {
    expect(failing(evaluatePrecheck({ ...good, camera: false }))).toEqual(['camera']);
    expect(failing(evaluatePrecheck({ ...good, mic: false }))).toEqual(['microphone']);
  });

  it('should_require_the_entire_screen_not_a_window_or_tab', () => {
    expect(failing(evaluatePrecheck({ ...good, screenSurface: 'window' }))).toEqual(['screen']);
    expect(failing(evaluatePrecheck({ ...good, screenSurface: 'browser' }))).toEqual(['screen']);
    expect(failing(evaluatePrecheck({ ...good, screenSurface: null }))).toEqual(['screen']);
  });

  it('should_require_fullscreen', () => {
    expect(failing(evaluatePrecheck({ ...good, fullscreen: false }))).toEqual(['fullscreen']);
  });

  it('should_fail_when_an_extended_display_is_present', () => {
    expect(failing(evaluatePrecheck({ ...good, singleDisplay: false }))).toEqual(['display']);
  });

  it('should_pass_display_when_the_api_is_unavailable', () => {
    expect(evaluatePrecheck({ ...good, singleDisplay: null }).allPassed).toBe(true);
  });

  it('should_fail_unsupported_browser', () => {
    expect(failing(evaluatePrecheck({ ...good, chromium: false }))).toEqual(['browser']);
  });

  it('should_give_every_failed_check_a_plain_next_step', () => {
    const r = evaluatePrecheck({ ...good, camera: false, fullscreen: false });
    for (const c of r.checks.filter((x) => !x.ok)) expect(c.reason && c.reason.length).toBeGreaterThan(10);
  });
});

describe('isChromium', () => {
  it('should_detect_chrome_and_edge_user_agents', () => {
    expect(isChromium('Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36')).toBe(true);
    expect(isChromium('Mozilla/5.0 AppleWebKit/537.36 Chrome/126.0 Safari/537.36 Edg/126.0')).toBe(true);
  });
  it('should_reject_firefox_and_safari', () => {
    expect(isChromium('Mozilla/5.0 (X11; Linux) Gecko/20100101 Firefox/127.0')).toBe(false);
    expect(isChromium('Mozilla/5.0 (Macintosh) AppleWebKit/605.1.15 Version/17.5 Safari/605.1.15')).toBe(false);
  });
});
