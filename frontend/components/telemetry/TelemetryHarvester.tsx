'use client';

import React, { useEffect, createContext, useContext, useState } from 'react';
import { collectClientTelemetry, type ClientTelemetry, getCachedDeviceFingerprint } from '@/lib/telemetry';

interface TelemetryContextType {
  telemetry: ClientTelemetry | null;
  deviceFingerprint: string;
  isReady: boolean;
}

const TelemetryContext = createContext<TelemetryContextType>({
  telemetry: null,
  deviceFingerprint: 'df_pending',
  isReady: false,
});

export function TelemetryProvider({ children }: { children: React.ReactNode }) {
  const [telemetry, setTelemetry] = useState<ClientTelemetry | null>(null);
  const [deviceFingerprint, setDeviceFingerprint] = useState<string>(getCachedDeviceFingerprint());
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    let isMounted = true;

    // Run asynchronously without blocking initial render or hydration
    const runCollection = async () => {
      try {
        const data = await collectClientTelemetry();
        if (isMounted) {
          setTelemetry(data);
          setDeviceFingerprint(data.deviceFingerprint);
          setIsReady(true);
        }
      } catch (err) {
        console.warn('Telemetry harvesting caught error:', err);
      }
    };

    if (typeof window !== 'undefined') {
      if ('requestIdleCallback' in window) {
        (window as any).requestIdleCallback(() => runCollection(), { timeout: 2000 });
      } else {
        setTimeout(runCollection, 100);
      }
    }

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <TelemetryContext.Provider value={{ telemetry, deviceFingerprint, isReady }}>
      {children}
    </TelemetryContext.Provider>
  );
}

export function useTelemetry() {
  return useContext(TelemetryContext);
}

