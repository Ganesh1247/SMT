import type { IntegrityEvent } from '../api/types';

export interface BatcherOptions {
  send: (events: IntegrityEvent[]) => Promise<unknown>;
  maxBatch?: number;
  flushIntervalMs?: number;
  maxQueue?: number;
  backoffBaseMs?: number;
  backoffMaxMs?: number;
}

/**
 * Batches integrity events for POST /attempts/{id}/events.
 * - single flight; failed batches are put back at the head (order preserved)
 * - exponential backoff between retries; queue is bounded (oldest dropped and counted)
 */
export class EventBatcher {
  private queue: IntegrityEvent[] = [];
  private inFlight: Promise<void> | null = null;
  private timer: ReturnType<typeof setTimeout> | null = null;
  private running = false;
  private failures = 0;
  private notBefore = 0;
  dropped = 0;

  private readonly maxBatch: number;
  private readonly interval: number;
  private readonly maxQueue: number;
  private readonly base: number;
  private readonly cap: number;

  constructor(private readonly o: BatcherOptions) {
    this.maxBatch = o.maxBatch ?? 20;
    this.interval = o.flushIntervalMs ?? 3000;
    this.maxQueue = o.maxQueue ?? 500;
    this.base = o.backoffBaseMs ?? 1000;
    this.cap = o.backoffMaxMs ?? 30_000;
  }

  get pending(): number {
    return this.queue.length;
  }

  push(e: IntegrityEvent): void {
    this.queue.push(e);
    while (this.queue.length > this.maxQueue) {
      this.queue.shift();
      this.dropped++;
    }
    if (this.queue.length >= this.maxBatch && Date.now() >= this.notBefore) void this.flush();
  }

  start(): void {
    this.running = true;
    this.schedule(this.interval);
  }

  async stop(): Promise<void> {
    this.running = false;
    if (this.timer) clearTimeout(this.timer);
    this.timer = null;
    this.notBefore = 0;
    await this.flush();
  }

  private schedule(ms: number): void {
    if (!this.running) return;
    if (this.timer) clearTimeout(this.timer);
    this.timer = setTimeout(() => {
      this.timer = null;
      void this.flush().finally(() => {
        this.schedule(this.failures > 0 ? this.backoff() : this.interval);
      });
    }, ms);
  }

  private backoff(): number {
    return Math.min(this.cap, this.base * 2 ** Math.max(0, this.failures - 1));
  }

  async flush(): Promise<void> {
    if (this.inFlight) {
      await this.inFlight;
      return;
    }
    if (this.queue.length === 0) return;
    this.inFlight = this.drain().finally(() => {
      this.inFlight = null;
    });
    await this.inFlight;
  }

  private async drain(): Promise<void> {
    while (this.queue.length > 0) {
      const batch = this.queue.splice(0, this.maxBatch);
      try {
        await this.o.send(batch);
        this.failures = 0;
        this.notBefore = 0;
      } catch {
        this.queue = [...batch, ...this.queue];
        while (this.queue.length > this.maxQueue) {
          this.queue.shift();
          this.dropped++;
        }
        this.failures++;
        this.notBefore = Date.now() + this.backoff();
        return;
      }
    }
  }
}
