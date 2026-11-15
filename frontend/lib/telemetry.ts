/**
 * AstroLogic Client Telemetry & Device Fingerprinting Engine
 * Gathers 42 hardware, display, software, and internationalization parameters
 * to compute a deterministic device fingerprint (df_<hash>) for ghost session recovery,
 * zero-friction location auto-calibration, and fraud prevention.
 */

export interface ClientTelemetry {
  // Screen & Display (1-7)
  screenWidth: number;
  screenHeight: number;
  screenAvailWidth: number;
  screenAvailHeight: number;
  screenColorDepth: number;
  screenPixelDepth: number;
  devicePixelRatio: number;

  // Hardware & Concurrency (8-12)
  hardwareConcurrency: number;
  deviceMemory: number | null;
  maxTouchPoints: number;
  touchSupport: boolean;
  platform: string;

  // Environment & Internationalization (13-17)
  timezone: string;
  timezoneOffsetMinutes: number;
  languages: string[];
  primaryLanguage: string;
  calendar: string;

  // Network & Power (18-21)
  connectionType: string | null;
  effectiveType: string | null;
  downlink: number | null;
  saveData: boolean | null;

  // Graphic & Canvas 2D (22-26)
  canvas2dHash: string;
  canvasWindingSupported: boolean;
  webglVendor: string;
  webglRenderer: string;
  webglVersion: string;

  // Audio DAC (27-29)
  audioSampleRate: number;
  audioFingerprint: string;
  audioMaxChannels: number;

  // Storage & Features (30-35)
  localStorageSupported: boolean;
  sessionStorageSupported: boolean;
  indexedDbSupported: boolean;
  cookiesEnabled: boolean;
  doNotTrack: string | null;
  pdfViewerEnabled: boolean;

  // Derived Business Flags (36-42)
  isHighNetWorthDevice: boolean;
  isMobileDevice: boolean;
  isVedicIndiaCandidate: boolean;
  colorGamut: string;
  prefersDarkMode: boolean;
  prefersReducedMotion: boolean;
  deviceFingerprint: string;
}

// 32-bit MurmurHash3 implementation for fast client-side non-cryptographic hashing
export function murmurhash3_32_gc(key: string, seed: number = 0x5bd1e995): string {
  let remainder = key.length & 3; // key.length % 4
  let bytes = key.length - remainder;
  let h1 = seed;
  let c1 = 0xcc9e2d51;
  let c2 = 0x1b873593;
  let i = 0;

  while (i < bytes) {
    let k1 =
      (key.charCodeAt(i) & 0xff) |
      ((key.charCodeAt(++i) & 0xff) << 8) |
      ((key.charCodeAt(++i) & 0xff) << 16) |
      ((key.charCodeAt(++i) & 0xff) << 24);
    ++i;

    k1 = Math.imul(k1, c1);
    k1 = (k1 << 15) | (k1 >>> 17);
    k1 = Math.imul(k1, c2);

    h1 ^= k1;
    h1 = (h1 << 13) | (h1 >>> 19);
    h1 = Math.imul(h1, 5) + 0xe6546b64;
  }

  let k1 = 0;
  switch (remainder) {
    case 3:
      k1 ^= (key.charCodeAt(i + 2) & 0xff) << 16;
    // fall through
    case 2:
      k1 ^= (key.charCodeAt(i + 1) & 0xff) << 8;
    // fall through
    case 1:
      k1 ^= key.charCodeAt(i) & 0xff;
      k1 = Math.imul(k1, c1);
      k1 = (k1 << 15) | (k1 >>> 17);
      k1 = Math.imul(k1, c2);
      h1 ^= k1;
  }

  h1 ^= key.length;
  h1 ^= h1 >>> 16;
  h1 = Math.imul(h1, 0x85ebca6b);
  h1 ^= h1 >>> 13;
  h1 = Math.imul(h1, 0xc2b2ae35);
  h1 ^= h1 >>> 16;

  return (h1 >>> 0).toString(16).padStart(8, '0');
}

/**
 * Extract 2D Canvas rendering fingerprint using sub-pixel anti-aliasing variations
 */
function getCanvas2dFingerprint(): { hash: string; winding: boolean } {
  try {
    const canvas = document.createElement('canvas');
    canvas.width = 240;
    canvas.height = 60;
    const ctx = canvas.getContext('2d');
    if (!ctx) return { hash: 'canvas_unsupported', winding: false };

    ctx.textBaseline = 'top';
    ctx.font = "14px 'Arial', 'Noto Sans Devanagari', sans-serif";
    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = '#7A1612';
    ctx.fillRect(125, 1, 62, 20);

    ctx.fillStyle = '#C5A059';
    ctx.fillText('AstroLogic Vedic 🪐 🕉️', 2, 15);
    ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
    ctx.fillText('Cosmic Vault', 4, 38);

    // Test winding rule support
    ctx.rect(0, 0, 10, 10);
    ctx.rect(2, 2, 6, 6);
    const winding = ctx.isPointInPath(5, 5, 'evenodd');

    const dataUrl = canvas.toDataURL();
    const hash = murmurhash3_32_gc(dataUrl);
    return { hash, winding };
  } catch {
    return { hash: 'canvas_blocked', winding: false };
  }
}

/**
 * Extract WebGL GPU Unmasked Vendor and Renderer strings
 */
function getWebGLFingerprint(): { vendor: string; renderer: string; version: string } {
  try {
    const canvas = document.createElement('canvas');
    const gl =
      (canvas.getContext('webgl') as WebGLRenderingContext | null) ||
      (canvas.getContext('experimental-webgl') as WebGLRenderingContext | null);

    if (!gl) return { vendor: 'no_webgl', renderer: 'no_webgl', version: 'no_webgl' };

    const version = gl.getParameter(gl.VERSION) || 'unknown';
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    if (!ext) {
      return {
        vendor: gl.getParameter(gl.VENDOR) || 'unknown',
        renderer: gl.getParameter(gl.RENDERER) || 'unknown',
        version,
      };
    }

    const vendor = gl.getParameter(ext.UNMASKED_VENDOR_WEBGL) || 'unknown';
    const renderer = gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) || 'unknown';
    return { vendor, renderer, version };
  } catch {
    return { vendor: 'webgl_err', renderer: 'webgl_err', version: 'webgl_err' };
  }
}

/**
 * Extract Web Audio DAC and Oscillator frequency response fingerprint
 */
async function getAudioFingerprint(): Promise<{ hash: string; sampleRate: number; maxChannels: number }> {
  try {
    const AudioCtx = window.OfflineAudioContext || (window as any).webkitOfflineAudioContext;
    if (!AudioCtx) {
      return { hash: 'audio_unsupported', sampleRate: 44100, maxChannels: 2 };
    }

    const context = new AudioCtx(1, 44100, 44100);
    const oscillator = context.createOscillator();
    oscillator.type = 'triangle';
    oscillator.frequency.setValueAtTime(10000, context.currentTime);

    const compressor = context.createDynamicsCompressor();
    compressor.threshold.setValueAtTime(-50, context.currentTime);
    compressor.knee.setValueAtTime(40, context.currentTime);
    compressor.ratio.setValueAtTime(12, context.currentTime);
    compressor.attack.setValueAtTime(0, context.currentTime);
    compressor.release.setValueAtTime(0.25, context.currentTime);

    oscillator.connect(compressor);
    compressor.connect(context.destination);
    oscillator.start(0);

    const audioBuffer = await context.startRendering();
    const channelData = audioBuffer.getChannelData(0);

    let sum = 0;
    for (let i = 4500; i < 5000; i++) {
      sum += Math.abs(channelData[i]);
    }

    return {
      hash: sum.toFixed(8),
      sampleRate: context.sampleRate || 44100,
      maxChannels: context.destination.maxChannelCount || 2,
    };
  } catch {
    return { hash: 'audio_blocked', sampleRate: 44100, maxChannels: 2 };
  }
}

/**
 * Collect all 42 telemetry parameters from the execution environment
 */
export async function collectClientTelemetry(): Promise<ClientTelemetry> {
  if (typeof window === 'undefined') {
    // Server-side fallback
    return {
      screenWidth: 1920,
      screenHeight: 1080,
      screenAvailWidth: 1920,
      screenAvailHeight: 1040,
      screenColorDepth: 24,
      screenPixelDepth: 24,
      devicePixelRatio: 1,
      hardwareConcurrency: 8,
      deviceMemory: 8,
      maxTouchPoints: 0,
      touchSupport: false,
      platform: 'Server',
      timezone: 'Asia/Kolkata',
      timezoneOffsetMinutes: -330,
      languages: ['en'],
      primaryLanguage: 'en',
      calendar: 'gregorian',
      connectionType: null,
      effectiveType: null,
      downlink: null,
      saveData: null,
      canvas2dHash: 'ssr_stub',
      canvasWindingSupported: true,
      webglVendor: 'ssr_stub',
      webglRenderer: 'ssr_stub',
      webglVersion: 'ssr_stub',
      audioSampleRate: 44100,
      audioFingerprint: 'ssr_stub',
      audioMaxChannels: 2,
      localStorageSupported: true,
      sessionStorageSupported: true,
      indexedDbSupported: true,
      cookiesEnabled: true,
      doNotTrack: null,
      pdfViewerEnabled: true,
      isHighNetWorthDevice: false,
      isMobileDevice: false,
      isVedicIndiaCandidate: true,
      colorGamut: 'srgb',
      prefersDarkMode: false,
      prefersReducedMotion: false,
      deviceFingerprint: 'df_server_stub',
    };
  }

  // 1-7: Screen & Display
  const screenWidth = window.screen.width || 0;
  const screenHeight = window.screen.height || 0;
  const screenAvailWidth = window.screen.availWidth || 0;
  const screenAvailHeight = window.screen.availHeight || 0;
  const screenColorDepth = window.screen.colorDepth || 24;
  const screenPixelDepth = window.screen.pixelDepth || 24;
  const devicePixelRatio = window.devicePixelRatio || 1;

  // 8-12: Hardware & Concurrency
  const hardwareConcurrency = navigator.hardwareConcurrency || 4;
  const deviceMemory = (navigator as any).deviceMemory || null;
  const maxTouchPoints = navigator.maxTouchPoints || 0;
  const touchSupport = 'ontouchstart' in window || maxTouchPoints > 0;
  const platform = navigator.platform || (navigator as any).userAgentData?.platform || 'Unknown';

  // 13-17: Environment & Internationalization
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  const timezoneOffsetMinutes = new Date().getTimezoneOffset();
  const languages = Array.from(navigator.languages || [navigator.language || 'en']);
  const primaryLanguage = navigator.language || 'en';
  const calendar = Intl.DateTimeFormat().resolvedOptions().calendar || 'gregorian';

  // 18-21: Network & Connection
  const conn = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
  const connectionType = conn?.type || null;
  const effectiveType = conn?.effectiveType || null;
  const downlink = conn?.downlink || null;
  const saveData = conn?.saveData || null;

  // 22-26: Graphics & Canvas
  const canvasInfo = getCanvas2dFingerprint();
  const webglInfo = getWebGLFingerprint();

  // 27-29: Audio
  const audioInfo = await getAudioFingerprint();

  // 30-35: Storage & Permissions
  const localStorageSupported = (() => {
    try {
      localStorage.setItem('__al_test', '1');
      localStorage.removeItem('__al_test');
      return true;
    } catch {
      return false;
    }
  })();

  const sessionStorageSupported = (() => {
    try {
      sessionStorage.setItem('__al_test', '1');
      sessionStorage.removeItem('__al_test');
      return true;
    } catch {
      return false;
    }
  })();

  const indexedDbSupported = typeof indexedDB !== 'undefined';
  const cookiesEnabled = navigator.cookieEnabled;
  const doNotTrack = navigator.doNotTrack || null;
  const pdfViewerEnabled = (navigator as any).pdfViewerEnabled ?? true;

  // 36-42: Derived Business Parameters
  // High-Net-Worth device indicator: Apple Silicon / High-end GPU OR Retina 3x+ display with >= 8 cores / 8GB RAM
  const isHighEndGpu = /Apple M[1-4]|RTX|Radeon RX|GeForce GTX 1[0-9]|Titan/i.test(webglInfo.renderer);
  const isHighNetWorthDevice =
    (devicePixelRatio >= 2.5 && (hardwareConcurrency >= 8 || isHighEndGpu)) ||
    (deviceMemory && deviceMemory >= 8 && isHighEndGpu);

  const isMobileDevice = touchSupport && (screenWidth < 768 || /Android|iPhone|iPad|iPod/i.test(navigator.userAgent));

  const isVedicIndiaCandidate =
    timezone.includes('Kolkata') ||
    timezoneOffsetMinutes === -330 ||
    languages.some((l) => /hi|mr|ta|te|gu|kn|ml|pa|bn|-IN/i.test(l));

  const colorGamut = window.matchMedia('(color-gamut: p3)').matches
    ? 'p3'
    : window.matchMedia('(color-gamut: srgb)').matches
    ? 'srgb'
    : 'unknown';

  const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Composite Deterministic Fingerprint
  const compositeSeed = [
    screenWidth,
    screenHeight,
    screenColorDepth,
    devicePixelRatio.toFixed(2),
    hardwareConcurrency,
    deviceMemory || 'na',
    timezone,
    timezoneOffsetMinutes,
    languages.slice(0, 3).join(','),
    canvasInfo.hash,
    webglInfo.vendor,
    webglInfo.renderer,
    audioInfo.hash,
  ].join('|');

  const rawHash1 = murmurhash3_32_gc(compositeSeed, 0x12345678);
  const rawHash2 = murmurhash3_32_gc(compositeSeed, 0x87654321);
  const deviceFingerprint = `df_${rawHash1}${rawHash2}`;

  const telemetry: ClientTelemetry = {
    screenWidth,
    screenHeight,
    screenAvailWidth,
    screenAvailHeight,
    screenColorDepth,
    screenPixelDepth,
    devicePixelRatio,
    hardwareConcurrency,
    deviceMemory,
    maxTouchPoints,
    touchSupport,
    platform,
    timezone,
    timezoneOffsetMinutes,
    languages,
    primaryLanguage,
    calendar,
    connectionType,
    effectiveType,
    downlink,
    saveData,
    canvas2dHash: canvasInfo.hash,
    canvasWindingSupported: canvasInfo.winding,
    webglVendor: webglInfo.vendor,
    webglRenderer: webglInfo.renderer,
    webglVersion: webglInfo.version,
    audioSampleRate: audioInfo.sampleRate,
    audioFingerprint: audioInfo.hash,
    audioMaxChannels: audioInfo.maxChannels,
    localStorageSupported,
    sessionStorageSupported,
    indexedDbSupported,
    cookiesEnabled,
    doNotTrack,
    pdfViewerEnabled,
    isHighNetWorthDevice,
    isMobileDevice,
    isVedicIndiaCandidate,
    colorGamut,
    prefersDarkMode,
    prefersReducedMotion,
    deviceFingerprint,
  };

  // Cache in localStorage for synchronous fast retrieval across routes
  try {
    localStorage.setItem('al_device_fingerprint', deviceFingerprint);
    localStorage.setItem('al_telemetry_summary', JSON.stringify({
      df: deviceFingerprint,
      hnw: isHighNetWorthDevice,
      india: isVedicIndiaCandidate,
      tz: timezone,
    }));
  } catch {
    // Ignore storage quota errors
  }

  return telemetry;
}

/**
 * Fast synchronous device fingerprint getter from cache with fallback
 */
export function getCachedDeviceFingerprint(): string {
  if (typeof window === 'undefined') return 'df_server';
  try {
    const cached = localStorage.getItem('al_device_fingerprint');
    if (cached) return cached;
  } catch {
    // storage not available
  }
  return 'df_pending';
}

/**
 * Suggest astrological coordinates & default city based on timezone
 */
export function getDefaultVedicLocationForTimezone(tz: string): {
  city: string;
  latitude: number;
  longitude: number;
  timezoneOffset: number;
} {
  if (tz.includes('Kolkata') || tz === 'Asia/Calcutta') {
    return { city: 'Delhi', latitude: 28.6139, longitude: 77.209, timezoneOffset: 5.5 };
  }
  if (tz.includes('Dubai')) {
    return { city: 'Dubai', latitude: 25.2048, longitude: 55.2708, timezoneOffset: 4.0 };
  }
  if (tz.includes('London')) {
    return { city: 'London', latitude: 51.5074, longitude: -0.1278, timezoneOffset: 0.0 };
  }
  if (tz.includes('New_York')) {
    return { city: 'New York', latitude: 40.7128, longitude: -74.006, timezoneOffset: -5.0 };
  }
  if (tz.includes('Los_Angeles')) {
    return { city: 'Los Angeles', latitude: 34.0522, longitude: -118.2437, timezoneOffset: -8.0 };
  }
  if (tz.includes('Singapore')) {
    return { city: 'Singapore', latitude: 1.3521, longitude: 103.8198, timezoneOffset: 8.0 };
  }
  if (tz.includes('Toronto')) {
    return { city: 'Toronto', latitude: 43.6532, longitude: -79.3832, timezoneOffset: -5.0 };
  }
  if (tz.includes('Sydney')) {
    return { city: 'Sydney', latitude: -33.8688, longitude: 151.2093, timezoneOffset: 10.0 };
  }
  // Default to Vedic Center (Delhi/Ujjain)
  return { city: 'Delhi', latitude: 28.6139, longitude: 77.209, timezoneOffset: 5.5 };
}

