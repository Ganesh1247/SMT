export type SpeedPhase = 'latency' | 'download' | 'upload' | 'done';
export interface SpeedProgress {
  phase: SpeedPhase;
  mbps?: number;
  latencyMs?: number;
}
export interface NetworkMeasurement {
  downMbps: number;
  upMbps: number;
  latencyMs: number;
}
export interface SpeedDeps {
  now: () => number;
  /** fetch `size` bytes from the precheck payload route; resolves with bytes received */
  download: (size: number) => Promise<number>;
  /** post `bytes` bytes to the precheck echo route */
  upload: (bytes: number) => Promise<void>;
  downloadBytes?: number;
  uploadBytes?: number;
  latencySamples?: number;
  onProgress?: (p: SpeedProgress) => void;
}

export function mbpsFrom(bytes: number, ms: number): number {
  if (ms <= 0) return 0;
  return (bytes * 8) / 1_000_000 / (ms / 1000);
}

function median(xs: number[]): number {
  const s = [...xs].sort((a, b) => a - b);
  return s[Math.floor(s.length / 2)];
}

export async function measureNetwork(d: SpeedDeps): Promise<NetworkMeasurement> {
  const samples = d.latencySamples ?? 3;
  const lat: number[] = [];
  d.onProgress?.({ phase: 'latency' });
  for (let i = 0; i < samples; i++) {
    const s = d.now();
    await d.download(1);
    lat.push(d.now() - s);
  }
  const latencyMs = median(lat);
  d.onProgress?.({ phase: 'latency', latencyMs });

  d.onProgress?.({ phase: 'download' });
  const ds = d.now();
  const got = await d.download(d.downloadBytes ?? 2_000_000);
  const downMbps = mbpsFrom(got, d.now() - ds);
  d.onProgress?.({ phase: 'download', mbps: downMbps });

  d.onProgress?.({ phase: 'upload' });
  const upBytes = d.uploadBytes ?? 1_000_000;
  const us = d.now();
  await d.upload(upBytes);
  const upMbps = mbpsFrom(upBytes, d.now() - us);
  d.onProgress?.({ phase: 'upload', mbps: upMbps });

  d.onProgress?.({ phase: 'done' });
  return { downMbps, upMbps, latencyMs };
}
