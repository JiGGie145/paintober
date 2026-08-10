export function getLoadingAnimationProfile() {
  if (typeof window === 'undefined' || typeof navigator === 'undefined') {
    return { mode: 'simple', resolution: 0 }
  }

  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
    return { mode: 'simple', resolution: 0 }
  }

  const probe = document.createElement('canvas')
  if (!probe.getContext?.('2d')) {
    return { mode: 'simple', resolution: 0 }
  }

  const hardwareConcurrency = Number(navigator.hardwareConcurrency) || 0
  const deviceMemory = Number(navigator.deviceMemory) || 0
  const isMobile = navigator.maxTouchPoints > 0
    || window.matchMedia?.('(pointer: coarse)').matches

  if (isMobile && (hardwareConcurrency < 4 || deviceMemory < 4)) {
    return { mode: 'simple', resolution: 0 }
  }

  if (!isMobile && hardwareConcurrency > 0 && hardwareConcurrency < 2) {
    return { mode: 'simple', resolution: 0 }
  }

  if (!isMobile && deviceMemory > 0 && deviceMemory < 2) {
    return { mode: 'simple', resolution: 0 }
  }

  const strongClient = hardwareConcurrency >= 8 || deviceMemory >= 8
  return {
    mode: 'particle',
    resolution: strongClient ? 512 : 256,
  }
}
