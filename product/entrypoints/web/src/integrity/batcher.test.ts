import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { EventBatcher } from './batcher';
import type { IntegrityEvent } from '../api/types';

const ev = (n: number): IntegrityEvent => ({ type: 'paste', t_ms: n, at: '2026-10-10T10:00:00Z', item_id: `i${n}` });

describe('EventBatcher', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('should_flush_when_batch_size_is_reached', async () => {
    const send = vi.fn().mockResolvedValue(undefined);
    const b = new EventBatcher({ send, maxBatch: 3, flushIntervalMs: 10_000 });
    b.push(ev(1));
    b.push(ev(2));
    expect(send).not.toHaveBeenCalled();
    b.push(ev(3));
    await vi.advanceTimersByTimeAsync(0);
    expect(send).toHaveBeenCalledTimes(1);
    expect(send.mock.calls[0][0].map((e: IntegrityEvent) => e.t_ms)).toEqual([1, 2, 3]);
  });

  it('should_flush_on_the_interval_when_below_batch_size', async () => {
    const send = vi.fn().mockResolvedValue(undefined);
    const b = new EventBatcher({ send, maxBatch: 20, flushIntervalMs: 3000 });
    b.start();
    b.push(ev(1));
    await vi.advanceTimersByTimeAsync(3000);
    expect(send).toHaveBeenCalledTimes(1);
    b.stop();
  });

  it('should_keep_events_and_retry_with_backoff_when_send_fails', async () => {
    const send = vi.fn().mockRejectedValueOnce(new Error('net')).mockRejectedValueOnce(new Error('net')).mockResolvedValue(undefined);
    const b = new EventBatcher({ send, maxBatch: 20, flushIntervalMs: 1000, backoffBaseMs: 500, backoffMaxMs: 8000 });
    b.start();
    b.push(ev(1));
    b.push(ev(2));
    await vi.advanceTimersByTimeAsync(1000); // first attempt fails
    expect(send).toHaveBeenCalledTimes(1);
    expect(b.pending).toBe(2);
    await vi.advanceTimersByTimeAsync(500); // backoff 500 -> second attempt fails
    expect(send).toHaveBeenCalledTimes(2);
    await vi.advanceTimersByTimeAsync(500); // not yet: backoff doubled to 1000
    expect(send).toHaveBeenCalledTimes(2);
    await vi.advanceTimersByTimeAsync(500);
    expect(send).toHaveBeenCalledTimes(3);
    expect(b.pending).toBe(0);
    expect(send.mock.calls[2][0].map((e: IntegrityEvent) => e.t_ms)).toEqual([1, 2]);
    b.stop();
  });

  it('should_preserve_order_when_new_events_arrive_during_a_failed_send', async () => {
    let fail = true;
    const sent: number[][] = [];
    const send = vi.fn(async (events: IntegrityEvent[]) => {
      if (fail) throw new Error('net');
      sent.push(events.map((e) => e.t_ms));
    });
    const b = new EventBatcher({ send, maxBatch: 20, flushIntervalMs: 1000, backoffBaseMs: 100 });
    b.push(ev(1));
    await b.flush();
    b.push(ev(2));
    fail = false;
    await b.flush();
    expect(sent.flat()).toEqual([1, 2]);
  });

  it('should_never_run_two_sends_at_once', async () => {
    let inFlight = 0;
    let maxInFlight = 0;
    const send = vi.fn(async () => {
      inFlight++;
      maxInFlight = Math.max(maxInFlight, inFlight);
      await new Promise((r) => setTimeout(r, 50));
      inFlight--;
    });
    const b = new EventBatcher({ send, maxBatch: 1, flushIntervalMs: 1000 });
    b.push(ev(1));
    b.push(ev(2));
    b.push(ev(3));
    await vi.advanceTimersByTimeAsync(500);
    expect(maxInFlight).toBe(1);
    expect(b.pending).toBe(0);
  });

  it('should_drop_oldest_and_count_when_queue_cap_is_exceeded', async () => {
    const send = vi.fn().mockRejectedValue(new Error('down'));
    const b = new EventBatcher({ send, maxBatch: 100, flushIntervalMs: 1000, maxQueue: 3 });
    for (let i = 1; i <= 5; i++) b.push(ev(i));
    expect(b.pending).toBe(3);
    expect(b.dropped).toBe(2);
  });

  it('should_flush_remaining_events_on_stop', async () => {
    const send = vi.fn().mockResolvedValue(undefined);
    const b = new EventBatcher({ send, maxBatch: 20, flushIntervalMs: 60_000 });
    b.start();
    b.push(ev(1));
    await b.stop();
    expect(send).toHaveBeenCalledTimes(1);
  });
});
