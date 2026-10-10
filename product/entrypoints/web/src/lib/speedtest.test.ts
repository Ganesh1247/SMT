import { describe, it, expect } from 'vitest';
import { measureNetwork, mbpsFrom } from './speedtest';

describe('mbpsFrom', () => {
  it('should_convert_bytes_and_milliseconds_to_megabits_per_second', () => {
    expect(mbpsFrom(1_000_000, 1000)).toBeCloseTo(8, 5);
  });
  it('should_return_zero_for_non_positive_duration', () => {
    expect(mbpsFrom(1000, 0)).toBe(0);
  });
});

describe('measureNetwork', () => {
  function clock(steps: number[]) {
    let i = 0;
    return () => steps[Math.min(i++, steps.length - 1)];
  }

  it('should_report_latency_median_download_and_upload', async () => {
    // now() call order: 3 latency samples (start,end each), download (start,end), upload (start,end)
    const now = clock([0, 30, 100, 150, 200, 260, 300, 1300, 2000, 3000]);
    const progress: string[] = [];
    const r = await measureNetwork({
      now,
      download: async (size) => (size <= 1 ? 1 : 1_000_000),
      upload: async () => undefined,
      downloadBytes: 1_000_000,
      uploadBytes: 500_000,
      onProgress: (p) => progress.push(p.phase),
    });
    // latencies 30, 50, 60 -> median 50
    expect(r.latencyMs).toBe(50);
    expect(r.downMbps).toBeCloseTo(8, 3); // 1 MB in 1 s
    expect(r.upMbps).toBeCloseTo(4, 3); // 0.5 MB in 1 s
    expect(progress).toContain('latency');
    expect(progress).toContain('download');
    expect(progress).toContain('upload');
    expect(progress[progress.length - 1]).toBe('done');
  });

  it('should_propagate_failure_so_the_ui_can_offer_retry', async () => {
    await expect(
      measureNetwork({
        now: () => 0,
        download: async () => {
          throw new Error('offline');
        },
        upload: async () => undefined,
      }),
    ).rejects.toThrow('offline');
  });
});
