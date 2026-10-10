import { vi } from 'vitest';

/** Browser media/fullscreen fakes for jsdom tests. */
export function fakeTrack(kind: 'video' | 'audio', settings: Record<string, unknown> = {}) {
  const et = new EventTarget();
  return Object.assign(et, {
    kind,
    readyState: 'live' as const,
    stop: vi.fn(),
    getSettings: () => settings,
  }) as unknown as MediaStreamTrack;
}

export function fakeStream(tracks: MediaStreamTrack[]): MediaStream {
  return {
    getTracks: () => tracks,
    getVideoTracks: () => tracks.filter((t) => t.kind === 'video'),
    getAudioTracks: () => tracks.filter((t) => t.kind === 'audio'),
  } as unknown as MediaStream;
}

export function setFullscreen(on: boolean) {
  Object.defineProperty(document, 'fullscreenElement', { value: on ? document.documentElement : null, configurable: true });
}

export function installBrowserFakes(opts: { surface?: string } = {}) {
  Object.defineProperty(navigator, 'userAgent', {
    value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    configurable: true,
  });
  const getUserMedia = vi.fn(async () => fakeStream([fakeTrack('video'), fakeTrack('audio')]));
  const getDisplayMedia = vi.fn(async () => fakeStream([fakeTrack('video', { displaySurface: opts.surface ?? 'monitor' })]));
  Object.defineProperty(navigator, 'mediaDevices', { value: { getUserMedia, getDisplayMedia }, configurable: true });
  setFullscreen(false);
  document.documentElement.requestFullscreen = vi.fn(async () => {
    setFullscreen(true);
    document.dispatchEvent(new Event('fullscreenchange'));
  });
  document.exitFullscreen = vi.fn(async () => {
    setFullscreen(false);
  });
  return { getUserMedia, getDisplayMedia };
}
