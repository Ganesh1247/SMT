import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '../api/client';
import type { IntegrityEvent } from '../api/types';
import { capture } from '../recording/session';
import { EventBatcher } from './batcher';
import { attachDetectors } from './detectors';
import { IntegrityTracker } from './policy';

export interface Proctoring {
  notices: string[];
  flagged: boolean;
  fsLocked: boolean;
  online: boolean;
  upload: { pending: number; uploaded: number; dropped: number; stalled: boolean };
  recording: boolean;
  cameraOk: boolean;
  videoRef: React.RefObject<HTMLVideoElement>;
  returnToFullscreen: () => Promise<void>;
  finish: () => Promise<{ pending: number }>;
}

/** Wires detectors -> tracker (neutral notices) -> batcher -> /attempts/{id}/events, and recording. */
export function useProctoring(attemptId: string, getItemId: () => string | null): Proctoring {
  const [notices, setNotices] = useState<string[]>([]);
  const [flagged, setFlagged] = useState(false);
  const [fsLocked, setFsLocked] = useState(() => typeof document !== 'undefined' && !document.fullscreenElement);
  const [online, setOnline] = useState(() => (typeof navigator === 'undefined' ? true : navigator.onLine));
  const [upload, setUpload] = useState(capture.stats());
  const [cameraOk, setCameraOk] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);
  const batcherRef = useRef<EventBatcher | null>(null);
  const detachRef = useRef<(() => void) | null>(null);
  const getItem = useRef(getItemId);
  getItem.current = getItemId;

  useEffect(() => {
    const tracker = new IntegrityTracker();
    const applyResult = (r: { notice: string | null; flagged: boolean }) => {
      if (r.notice) setNotices((n) => [...n.slice(-4), r.notice as string]);
      if (r.flagged) setFlagged(true);
    };
    const batcher = new EventBatcher({
      send: async (events: IntegrityEvent[]) => {
        const res = await api.events(attemptId, events);
        if (res && res.flagged) applyResult(tracker.adoptServerFlag());
      },
    });
    batcherRef.current = batcher;
    batcher.start();

    capture.start(attemptId, () => setUpload(capture.stats()));
    const poll = setInterval(() => setUpload(capture.stats()), 2000);

    const emit = (e: IntegrityEvent) => {
      batcher.push(e);
      applyResult(tracker.record(e.type));
      if (e.type === 'fullscreen_exit') setFsLocked(true);
      if (e.type === 'camera_lost') setCameraOk(false);
    };
    detachRef.current = attachDetectors({
      emit,
      getItemId: () => getItem.current(),
      cameraStream: capture.camera,
      screenStream: capture.screen,
      faceVideo: () => videoRef.current,
    });

    const onFs = () => setFsLocked(!document.fullscreenElement);
    const onOnline = () => setOnline(true);
    const onOffline = () => setOnline(false);
    document.addEventListener('fullscreenchange', onFs);
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);

    return () => {
      clearInterval(poll);
      detachRef.current?.();
      document.removeEventListener('fullscreenchange', onFs);
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
      void batcher.stop();
    };
  }, [attemptId]);

  useEffect(() => {
    if (videoRef.current && capture.camera) videoRef.current.srcObject = capture.camera;
  });

  const returnToFullscreen = useCallback(async () => {
    try {
      await document.documentElement.requestFullscreen();
      setFsLocked(false);
    } catch {
      setFsLocked(true);
    }
  }, []);

  const finish = useCallback(async () => {
    detachRef.current?.();
    detachRef.current = null;
    await batcherRef.current?.stop();
    return capture.finish(attemptId);
  }, [attemptId]);

  return { notices, flagged, fsLocked, online, upload, recording: capture.recording, cameraOk, videoRef, returnToFullscreen, finish };
}
