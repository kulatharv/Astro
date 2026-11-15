'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

export interface CosmicBadges {
  lagna_sign?: string;
  moon_sign?: string;
  sun_sign?: string;
  nakshatra?: string;
  nakshatra_pada?: number;
  mahadasha?: string;
  antardasha?: string;
  is_calculated: boolean;
}

export interface AuthUser {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  auth_provider: string;
  preferred_language: string;
  whatsapp_opt_in: boolean;
  whatsapp_number?: string;
  cosmic_badges?: CosmicBadges;
}

interface OpenModalOptions {
  reason?: 'save_chart' | 'whatsapp_daily' | 'predictions_unlock' | 'pdf_download' | 'login' | string;
  title?: string;
  onComplete?: () => void;
}

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isModalOpen: boolean;
  modalOptions: OpenModalOptions;
  openAuthModal: (options?: OpenModalOptions) => void;
  closeAuthModal: () => void;
  loginWithGoogle: (credential: string) => Promise<boolean>;
  sendWhatsAppOtp: (phoneNumber: string) => Promise<{ success: boolean; message: string; devOtp?: string }>;
  verifyWhatsAppOtp: (phoneNumber: string, otpCode: string) => Promise<boolean>;
  logout: () => Promise<void>;
  setPendingGuestChart: (chart: any) => void;
  getPendingGuestChart: () => any | null;
  claimPendingChart: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const STORAGE_KEY_PENDING = 'al_pending_guest_chart';
const STORAGE_KEY_TOKEN = 'al_access_token';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalOptions, setModalOptions] = useState<OpenModalOptions>({});

  // 1. Initial Session Check
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY_TOKEN) : null;
        if (storedToken) {
          setToken(storedToken);
        }

        const headers: Record<string, string> = {};
        if (storedToken) {
          headers['Authorization'] = `Bearer ${storedToken}`;
        }

        const res = await fetch('/api/auth/me', { headers });
        if (res.ok) {
          const data = await res.json();
          if (data.authenticated && data.user) {
            setUser(data.user);
          }
        }
      } catch (err) {
        console.warn('Auth check skipped / offline');
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const openAuthModal = useCallback((options?: OpenModalOptions) => {
    setModalOptions(options || {});
    setIsModalOpen(true);
  }, []);

  const closeAuthModal = useCallback(() => {
    setIsModalOpen(false);
  }, []);

  const setPendingGuestChart = useCallback((chart: any) => {
    if (typeof window === 'undefined') return;
    try {
      window.sessionStorage.setItem(STORAGE_KEY_PENDING, JSON.stringify(chart));
    } catch (e) {
      console.warn('Failed to cache pending chart in sessionStorage');
    }
  }, []);

  const getPendingGuestChart = useCallback(() => {
    if (typeof window === 'undefined') return null;
    try {
      const raw = window.sessionStorage.getItem(STORAGE_KEY_PENDING);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }, []);

  // 2. Claim pending chart upon login (Zero Data Loss)
  const claimPendingChart = useCallback(async () => {
    const pending = getPendingGuestChart();
    if (!pending) return false;

    try {
      const storedToken = typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY_TOKEN) : null;
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (storedToken) {
        headers['Authorization'] = `Bearer ${storedToken}`;
      }

      const res = await fetch('/api/auth/claim-guest-chart', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          profile_name: pending.name || pending.fullName || 'Self',
          relationship: 'self',
          birth_date: pending.dob || pending.birthDate,
          birth_time: pending.tob || pending.birthTime || '12:00',
          birth_city: pending.city || pending.birthCity || 'Delhi',
          latitude: pending.lat || pending.latitude,
          longitude: pending.lon || pending.longitude,
          timezone_offset: pending.tzOffset || pending.timezone_offset || 5.5,
          tz_name: pending.tzName || 'Asia/Kolkata',
          notes: 'Auto-promoted from guest calculation session',
        }),
      });

      if (res.ok) {
        window.sessionStorage.removeItem(STORAGE_KEY_PENDING);
        // Refresh me to update cosmic badges
        const meRes = await fetch('/api/auth/me', { headers });
        if (meRes.ok) {
          const meData = await meRes.json();
          if (meData.user) setUser(meData.user);
        }
        return true;
      }
    } catch (e) {
      console.error('Failed to claim pending guest chart', e);
    }
    return false;
  }, [getPendingGuestChart]);

  // 3. Google Login
  const loginWithGoogle = useCallback(
    async (credential: string): Promise<boolean> => {
      try {
        const res = await fetch('/api/auth/google', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ credential }),
        });

        if (!res.ok) return false;

        const data = await res.json();
        if (data.status === 'success' && data.user) {
          setUser(data.user);
          setToken(data.access_token);
          if (typeof window !== 'undefined') {
            localStorage.setItem(STORAGE_KEY_TOKEN, data.access_token);
          }
          // Auto-claim pending chart if exists
          await claimPendingChart();
          return true;
        }
      } catch (err) {
        console.error('Google auth error', err);
      }
      return false;
    },
    [claimPendingChart]
  );

  // 4. WhatsApp Send OTP
  const sendWhatsAppOtp = useCallback(
    async (phoneNumber: string): Promise<{ success: boolean; message: string; devOtp?: string }> => {
      try {
        const res = await fetch('/api/auth/whatsapp/send-otp', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone_number: phoneNumber }),
        });

        const data = await res.json();
        if (res.ok && data.status === 'sent') {
          return {
            success: true,
            message: data.message || 'OTP dispatched to WhatsApp',
            devOtp: data.dev_otp,
          };
        }
        return {
          success: false,
          message: data.message || data.detail || 'Could not send verification code',
        };
      } catch (err: any) {
        return { success: false, message: err?.message || 'Network error sending OTP' };
      }
    },
    []
  );

  // 5. WhatsApp Verify OTP
  const verifyWhatsAppOtp = useCallback(
    async (phoneNumber: string, otpCode: string): Promise<boolean> => {
      try {
        const res = await fetch('/api/auth/whatsapp/verify-otp', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone_number: phoneNumber, otp_code: otpCode }),
        });

        if (!res.ok) return false;

        const data = await res.json();
        if (data.status === 'success' && data.user) {
          setUser(data.user);
          setToken(data.access_token);
          if (typeof window !== 'undefined') {
            localStorage.setItem(STORAGE_KEY_TOKEN, data.access_token);
          }
          await claimPendingChart();
          return true;
        }
      } catch (err) {
        console.error('WhatsApp OTP verify error', err);
      }
      return false;
    },
    [claimPendingChart]
  );

  // 6. Logout
  const logout = useCallback(async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
    } catch {}
    setUser(null);
    setToken(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY_TOKEN);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        isModalOpen,
        modalOptions,
        openAuthModal,
        closeAuthModal,
        loginWithGoogle,
        sendWhatsAppOtp,
        verifyWhatsAppOtp,
        logout,
        setPendingGuestChart,
        getPendingGuestChart,
        claimPendingChart,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

