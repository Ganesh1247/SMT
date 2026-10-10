export type StreamName = 'camera' | 'screen';

export interface UploadQueueOptions {
  upload: (stream: StreamName, seq: number, data: Blob) => Promise<void>;
  maxAttempts?: number;
  baseDelayMs?: number;
  maxDelayMs?: number;
  maxPendingPerStream?: number;
  sleep?: (ms: number) => Promise<void>;
}

interface Chunk {
  seq: number;
  data: Blob;
}

/**
 * Ordered, per-stream chunk uploader with exponential backoff.
 * A chunk that exhausts its attempts stays at the head ("stalled") so order is kept;
 * retryStalled() resumes. Memory is bounded: oldest pending chunk is dropped and counted.
 */
export class ChunkUploadQueue {
  private queues: Record<StreamName, Chunk[]> = { camera: [], screen: [] };
  private seq: Record<StreamName, number> = { camera: 0, screen: 0 };
  private pumps: Partial<Record<StreamName, Promise<void>>> = {};
  private stalledStreams = new Set<StreamName>();
  private uploaded = 0;
  private droppedCount = 0;

  private readonly maxAttempts: number;
  private readonly base: number;
  private readonly cap: number;
  private readonly maxPending: number;
  private readonly sleep: (ms: number) => Promise<void>;

  constructor(private readonly o: UploadQueueOptions) {
    this.maxAttempts = o.maxAttempts ?? 6;
    this.base = o.baseDelayMs ?? 500;
    this.cap = o.maxDelayMs ?? 15_000;
    this.maxPending = o.maxPendingPerStream ?? 120;
    this.sleep = o.sleep ?? ((ms) => new Promise((r) => setTimeout(r, ms)));
  }

  enqueue(stream: StreamName, data: Blob): void {
    const q = this.queues[stream];
    q.push({ seq: this.seq[stream]++, data });
    while (q.length > this.maxPending) {
      q.shift();
      this.droppedCount++;
    }
    this.start(stream);
  }

  private start(stream: StreamName): void {
    if (this.pumps[stream] || this.stalledStreams.has(stream)) return;
    this.pumps[stream] = this.pump(stream).finally(() => {
      delete this.pumps[stream];
    });
  }

  private async pump(stream: StreamName): Promise<void> {
    const q = this.queues[stream];
    while (q.length > 0) {
      const head = q[0];
      let ok = false;
      for (let attempt = 0; attempt < this.maxAttempts; attempt++) {
        try {
          await this.o.upload(stream, head.seq, head.data);
          ok = true;
          break;
        } catch {
          if (attempt < this.maxAttempts - 1) {
            await this.sleep(Math.min(this.cap, this.base * 2 ** attempt));
          }
        }
      }
      if (!ok) {
        this.stalledStreams.add(stream);
        return;
      }
      if (q[0] === head) q.shift();
      this.uploaded++;
    }
  }

  /** Resolves when every active pump has finished (uploaded or stalled). */
  async drain(): Promise<void> {
    await Promise.all(Object.values(this.pumps));
  }

  async retryStalled(): Promise<void> {
    const streams = [...this.stalledStreams];
    this.stalledStreams.clear();
    for (const s of streams) this.start(s);
    await this.drain();
  }

  stats(): { pending: number; uploaded: number; dropped: number; stalled: boolean } {
    return {
      pending: this.queues.camera.length + this.queues.screen.length,
      uploaded: this.uploaded,
      dropped: this.droppedCount,
      stalled: this.stalledStreams.size > 0,
    };
  }
}
