import { describe, it, expect, vi } from 'vitest';
import { ChunkUploadQueue } from './uploadQueue';

const blob = (s: string) => new Blob([s]);

describe('ChunkUploadQueue', () => {
  it('should_number_chunks_per_stream_from_zero_and_upload_in_order', async () => {
    const calls: Array<[string, number]> = [];
    const q = new ChunkUploadQueue({
      upload: async (stream, seq) => {
        calls.push([stream, seq]);
      },
      sleep: async () => undefined,
    });
    q.enqueue('camera', blob('a'));
    q.enqueue('screen', blob('b'));
    q.enqueue('camera', blob('c'));
    await q.drain();
    expect(calls.filter((c) => c[0] === 'camera').map((c) => c[1])).toEqual([0, 1]);
    expect(calls.filter((c) => c[0] === 'screen').map((c) => c[1])).toEqual([0]);
    expect(q.stats()).toMatchObject({ pending: 0, uploaded: 3, stalled: false });
  });

  it('should_retry_with_exponential_backoff_then_succeed', async () => {
    const delays: number[] = [];
    const upload = vi.fn().mockRejectedValueOnce(new Error('x')).mockRejectedValueOnce(new Error('x')).mockResolvedValue(undefined);
    const q = new ChunkUploadQueue({
      upload,
      baseDelayMs: 250,
      maxDelayMs: 4000,
      sleep: async (ms) => {
        delays.push(ms);
      },
    });
    q.enqueue('camera', blob('a'));
    await q.drain();
    expect(upload).toHaveBeenCalledTimes(3);
    expect(delays).toEqual([250, 500]);
    expect(q.stats().uploaded).toBe(1);
  });

  it('should_cap_backoff_delay', async () => {
    const delays: number[] = [];
    const upload = vi.fn().mockRejectedValue(new Error('x'));
    const q = new ChunkUploadQueue({
      upload,
      baseDelayMs: 1000,
      maxDelayMs: 3000,
      maxAttempts: 5,
      sleep: async (ms) => {
        delays.push(ms);
      },
    });
    q.enqueue('camera', blob('a'));
    await q.drain();
    expect(delays).toEqual([1000, 2000, 3000, 3000]);
  });

  it('should_stall_without_losing_the_chunk_and_resume_on_retry', async () => {
    let ok = false;
    const upload = vi.fn(async () => {
      if (!ok) throw new Error('offline');
    });
    const q = new ChunkUploadQueue({ upload, maxAttempts: 2, sleep: async () => undefined });
    q.enqueue('camera', blob('a'));
    q.enqueue('camera', blob('b'));
    await q.drain();
    expect(q.stats()).toMatchObject({ pending: 2, uploaded: 0, stalled: true });
    ok = true;
    await q.retryStalled();
    expect(q.stats()).toMatchObject({ pending: 0, uploaded: 2, stalled: false });
  });

  it('should_not_reorder_later_chunks_ahead_of_a_failing_one', async () => {
    const order: number[] = [];
    let failFirst = true;
    const q = new ChunkUploadQueue({
      upload: async (_s, seq) => {
        if (seq === 0 && failFirst) {
          failFirst = false;
          throw new Error('x');
        }
        order.push(seq);
      },
      sleep: async () => undefined,
    });
    q.enqueue('screen', blob('a'));
    q.enqueue('screen', blob('b'));
    await q.drain();
    expect(order).toEqual([0, 1]);
  });

  it('should_drop_oldest_chunk_and_count_when_memory_cap_is_hit_while_stalled', async () => {
    const q = new ChunkUploadQueue({
      upload: async () => {
        throw new Error('offline');
      },
      maxAttempts: 1,
      maxPendingPerStream: 2,
      sleep: async () => undefined,
    });
    q.enqueue('camera', blob('a'));
    await q.drain();
    q.enqueue('camera', blob('b'));
    q.enqueue('camera', blob('c'));
    expect(q.stats().pending).toBe(2);
    expect(q.stats().dropped).toBe(1);
  });
});
