import { describe, it, expect, vi } from 'vitest';
import { attachDetectors } from './detectors';
import type { IntegrityEvent } from '../api/types';

describe('attachDetectors', () => {
  it('should_emit_paste_copy_context_menu_and_focus_loss_with_item_id_and_monotonic_time', () => {
    const emit = vi.fn<(e: IntegrityEvent) => void>();
    let t = 100;
    const off = attachDetectors({ emit, getItemId: () => 'item-7', now: () => (t += 5) });
    document.dispatchEvent(new Event('paste'));
    document.dispatchEvent(new Event('copy'));
    document.dispatchEvent(new Event('contextmenu'));
    window.dispatchEvent(new Event('blur'));
    window.dispatchEvent(new Event('offline'));
    off();
    const types = emit.mock.calls.map((c) => c[0].type);
    expect(types).toEqual(['paste', 'copy', 'context_menu', 'focus_loss', 'network_drop']);
    expect(emit.mock.calls.every((c) => c[0].item_id === 'item-7')).toBe(true);
    const ts = emit.mock.calls.map((c) => c[0].t_ms);
    expect([...ts].sort((a, b) => a - b)).toEqual(ts);
  });

  it('should_emit_tab_hidden_only_when_the_document_becomes_hidden', () => {
    const emit = vi.fn();
    const off = attachDetectors({ emit, getItemId: () => null });
    Object.defineProperty(document, 'visibilityState', { value: 'visible', configurable: true });
    document.dispatchEvent(new Event('visibilitychange'));
    expect(emit).not.toHaveBeenCalled();
    Object.defineProperty(document, 'visibilityState', { value: 'hidden', configurable: true });
    document.dispatchEvent(new Event('visibilitychange'));
    expect(emit).toHaveBeenCalledTimes(1);
    Object.defineProperty(document, 'visibilityState', { value: 'visible', configurable: true });
    off();
  });

  it('should_emit_camera_lost_and_screen_share_ended_when_tracks_end', () => {
    const emit = vi.fn<(e: IntegrityEvent) => void>();
    const camTrack = new EventTarget() as unknown as MediaStreamTrack;
    const scrTrack = new EventTarget() as unknown as MediaStreamTrack;
    const off = attachDetectors({
      emit,
      getItemId: () => null,
      cameraStream: { getTracks: () => [camTrack] } as unknown as MediaStream,
      screenStream: { getVideoTracks: () => [scrTrack] } as unknown as MediaStream,
    });
    camTrack.dispatchEvent(new Event('ended'));
    scrTrack.dispatchEvent(new Event('ended'));
    off();
    expect(emit.mock.calls.map((c) => c[0].type)).toEqual(['camera_lost', 'screen_share_ended']);
  });

  it('should_stop_emitting_after_cleanup', () => {
    const emit = vi.fn();
    const off = attachDetectors({ emit, getItemId: () => null });
    off();
    document.dispatchEvent(new Event('paste'));
    expect(emit).not.toHaveBeenCalled();
  });
});
