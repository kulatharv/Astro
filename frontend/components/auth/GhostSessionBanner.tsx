'use client';

import React, { useEffect, useState } from 'react';
import { Sparkles, ArrowRight, X, Clock, ShieldCheck } from 'lucide-react';
import { useAuth } from './AuthContext';
import { useTelemetry } from '../telemetry/TelemetryHarvester';

interface GhostSessionData {
  has_active_session: boolean;
  session_token?: string;
  chart_type?: string;
  person_name?: string;
  birth_date?: string;
  birth_time?: string;
  birth_place?: string;
  created_at?: string;
  chart_payload?: any;
}

interface GhostSessionBannerProps {
  onRestore?: (chartData: any, metadata: { name: string; dob: string; tob: string; city: string }) => void;
}

export default function GhostSessionBanner({ onRestore }: GhostSessionBannerProps) {
  const { isAuthenticated, openAuthModal } = useAuth();
  const { deviceFingerprint, isReady } = useTelemetry();
  const [ghostSession, setGhostSession] = useState<GhostSessionData | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (isAuthenticated || !deviceFingerprint || deviceFingerprint === 'df_pending') return;

    let isSubscribed = true;

    async function checkGhostSession() {
      try {
        const res = await fetch(`/api/auth/ghost-session?fingerprint=${encodeURIComponent(deviceFingerprint)}`);
        if (!res.ok) return;
        const data: GhostSessionData = await res.json();
        if (isSubscribed && data.has_active_session && data.person_name) {
          setGhostSession(data);
        }
      } catch (err) {
        // Non-blocking telemetry check
      }
    }

    checkGhostSession();

    return () => {
      isSubscribed = false;
    };
  }, [isAuthenticated, deviceFingerprint, isReady]);

  if (isAuthenticated || dismissed || !ghostSession || !ghostSession.has_active_session) {
    return null;
  }

  const handleClaim = () => {
    openAuthModal({
      reason: 'claim_ghost_session',
      title: `Claim & Save ${ghostSession.person_name}'s Chart`,
      onComplete: () => {
        setDismissed(true);
      },
    });
  };

  const handleRestore = () => {
    if (onRestore && ghostSession.chart_payload) {
      onRestore(ghostSession.chart_payload, {
        name: ghostSession.person_name || 'Self',
        dob: ghostSession.birth_date || '1995-08-15',
        tob: ghostSession.birth_time || '14:30',
        city: ghostSession.birth_place || 'Delhi',
      });
    }
  };

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#7A1612] via-[#8B1A14] to-[#5C100C] text-[#FAF6F0] p-4 sm:p-5 shadow-xl border border-[#C5A059]/40 mb-6 transition-all animate-fadeIn">
      {/* Decorative Glow */}
      <div className="absolute top-0 right-0 -mt-6 -mr-6 w-32 h-32 bg-[#C5A059]/15 rounded-full blur-2xl pointer-events-none" />

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 relative z-10">
        <div className="flex items-start gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-[#C5A059]/20 border border-[#C5A059]/40 flex items-center justify-center shrink-0 mt-0.5">
            <Sparkles className="w-5 h-5 text-[#C5A059] animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold tracking-wider uppercase text-[#C5A059]">
                Previous Session Preserved
              </span>
              <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-white/10 text-[#FAF6F0]/80">
                <Clock className="w-3 h-3 text-[#C5A059]" />
                Zero Data Loss
              </span>
            </div>
            <h4 className="font-serif text-base sm:text-lg font-bold text-white mt-0.5">
              Welcome back! We kept your calculated chart for{' '}
              <span className="text-[#C5A059] underline decoration-[#C5A059]/50">{ghostSession.person_name}</span> ready.
            </h4>
            <p className="text-xs text-[#FAF6F0]/75 mt-0.5">
              Born: {ghostSession.birth_date} at {ghostSession.birth_time} in {ghostSession.birth_place}. Claim it to your
              private Vault before your browser session clears.
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5 w-full sm:w-auto shrink-0 justify-end">
          {onRestore && ghostSession.chart_payload && (
            <button
              onClick={handleRestore}
              className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-white/10 hover:bg-white/20 text-[#FAF6F0] border border-white/20 transition-all cursor-pointer"
            >
              Restore Chart
            </button>
          )}

          <button
            onClick={handleClaim}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-[#C5A059] to-[#DFBA73] hover:from-[#B8924B] hover:to-[#C5A059] text-[#24120B] shadow-md hover:shadow-lg transition-all cursor-pointer"
          >
            <ShieldCheck className="w-4 h-4 text-[#24120B]" />
            <span>Save to Free Vault</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => setDismissed(true)}
            aria-label="Dismiss banner"
            className="p-1.5 rounded-lg text-white/50 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

