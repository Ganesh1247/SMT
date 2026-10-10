import { api } from '../api/client';
import { ChunkUploadQueue, type StreamName } from './uploadQueue';

/**
 * Holds the live capture streams between the lobby and the exam (they must survive
 * route changes), and records them with MediaRecorder in 5 s chunks.
 */
export const CHUNK_MS = 5000;

class CaptureSession {
  camera: MediaStream | null = null; // camera + mic
  screen: MediaStream | null = null;
  private recorders: MediaRecorder[] = [];
  private queue: ChunkUploadQueue | null = null;
  recording = false;

  setStreams(camera: MediaStream | null, screen: MediaStream | null): void {
    this.camera = camera;
    this.screen = screen;
  }

  get screenSurface(): string | null {
    const t = this.screen?.getVideoTracks()[0];
    if (!t) return null;
    const s = t.getSettings() as MediaTrackSettings & { displaySurface?: string };
    return s.displaySurface ?? null;
  }

  stats() {
    return this.queue?.stats() ?? { pending: 0, uploaded: 0, dropped: 0, stalled: false };
  }

  start(attemptId: string, onChange?: () => void): void {
    this.stopRecorders();
    this.queue = new ChunkUploadQueue({
      upload: (stream, seq, data) => api.chunk(attemptId, stream, seq, data),
    });
    const queue = this.queue;
    const attach = (stream: MediaStream | null, name: StreamName) => {
      if (!stream || typeof MediaRecorder === 'undefined') return;
      const mime = ['video/webm;codecs=vp8,opus', 'video/webm'].find((m) => MediaRecorder.isTypeSupported(m));
      const rec = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
      rec.ondataavailable = (ev) => {
        if (ev.data && ev.data.size > 0) {
          queue.enqueue(name, ev.data);
          onChange?.();
        }
      };
      rec.start(CHUNK_MS);
      this.recorders.push(rec);
    };
    attach(this.camera, 'camera');
    attach(this.screen, 'screen');
    this.recording = this.recorders.length > 0;
  }

  private stopRecorders(): void {
    for (const r of this.recorders) {
      try {
        if (r.state !== 'inactive') r.stop();
      } catch {
        /* already stopped */
      }
    }
    this.recorders = [];
  }

  /** Stops recording, drains the queue (with retries) and asks the server to finalize. */
  async finish(attemptId: string): Promise<{ pending: number }> {
    this.stopRecorders();
    // allow the final dataavailable events to be enqueued
    await new Promise((r) => setTimeout(r, 150));
    if (this.queue) {
      await this.queue.drain();
      if (this.queue.stats().stalled) await this.queue.retryStalled();
    }
    const pending = this.queue?.stats().pending ?? 0;
    if (pending === 0) {
      try {
        await api.finalizeRecording(attemptId);
      } catch {
        /* server finalises on finish too; surfaced via pending count only */
      }
    }
    this.recording = false;
    return { pending };
  }

  release(): void {
    this.stopRecorders();
    for (const s of [this.camera, this.screen]) s?.getTracks().forEach((t) => t.stop());
    this.camera = null;
    this.screen = null;
    this.recording = false;
  }
}

export const capture = new CaptureSession();
