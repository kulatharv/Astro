'use client';

import React, { useState, useEffect } from 'react';
import {
  X,
  Sparkles,
  Phone,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  MessageSquare,
  Lock,
  Mail,
  Eye,
  EyeOff,
} from 'lucide-react';
import { useAuth } from './AuthContext';

export default function AuthModal() {
  const {
    isModalOpen,
    modalOptions,
    closeAuthModal,
    loginWithGoogle,
    loginWithEmail,
    sendWhatsAppOtp,
    verifyWhatsAppOtp,
  } = useAuth();

  const [activeTab, setActiveTab] = useState<'standard' | 'whatsapp'>('standard');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);

  const [phone, setPhone] = useState('+91');
  const [otpCode, setOtpCode] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [devOtpHint, setDevOtpHint] = useState<string | null>(null);
  const [successCelebration, setSuccessCelebration] = useState(false);

  // Timer countdown
  useEffect(() => {
    if (countdown <= 0) return;
    const interval = setInterval(() => {
      setCountdown((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, [countdown]);

  // Reset state on open
  useEffect(() => {
    if (isModalOpen) {
      setErrorMsg(null);
      setSuccessCelebration(false);
      setLoading(false);
      setEmailLoading(false);
      setEmail('');
      setPassword('');
      setShowPassword(false);
      setOtpSent(false);
      setOtpCode('');
      setDevOtpHint(null);
    }
  }, [isModalOpen]);

  // Dynamic Contextual Headers
  const getHeaderInfo = () => {
    switch (modalOptions.reason) {
      case 'save_chart':
        return {
          title: 'Preserve Your Sacred Kundali',
          subtitle: 'Save this chart to your Cosmic Family Vault to access it anytime without re-entering birth coordinates.',
          badge: 'FAMILY VAULT',
        };
      case 'whatsapp_daily':
        return {
          title: 'Activate Daily 7:00 AM WhatsApp Forecast',
          subtitle: 'Receive your daily Nakshatra transit, auspicious Abhijit Muhurat, and Rahu Kaal alerts directly on your phone.',
          badge: 'WHATSAPP ALMANAC',
        };
      case 'predictions_unlock':
        return {
          title: 'Unlock All 10 Life Domains Free',
          subtitle: 'Reveal your complete Marriage, Wealth, Career, and Health Dasha milestones and Vedic remedies.',
          badge: '10-DOMAIN DOSSIER',
        };
      case 'pdf_download':
        return {
          title: 'Download Your 15-Page Kundali PDF',
          subtitle: 'Sign in free to generate your complete printable Vedic astrological treatise.',
          badge: 'PDF EXPORT',
        };
      default:
        return {
          title: 'Claim Your Sacred Vedic Identity',
          subtitle: 'Access your Janma Kundali, Dasha timelines, and Family Vault across all your devices.',
          badge: 'VEDIC COSMIC VAULT',
        };
    }
  };

  const headerInfo = getHeaderInfo();

  // Initialize Google Identity Services if available
  useEffect(() => {
    if (!isModalOpen || typeof window === 'undefined') return;
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
    if (!clientId || !(window as any).google?.accounts?.id) return;

    try {
      (window as any).google.accounts.id.initialize({
        client_id: clientId,
        callback: async (response: any) => {
          if (response?.credential) {
            setLoading(true);
            setErrorMsg(null);
            const ok = await loginWithGoogle(response.credential);
            if (ok) {
              setSuccessCelebration(true);
              setTimeout(() => {
                if (modalOptions.onComplete) modalOptions.onComplete();
                closeAuthModal();
              }, 1200);
            } else {
              setErrorMsg('Google sign-in could not be completed. Please try again.');
            }
            setLoading(false);
          }
        },
      });

      const slot = document.getElementById('google-btn-slot');
      if (slot) {
        slot.innerHTML = '';
        (window as any).google.accounts.id.renderButton(slot, {
          theme: 'outline',
          size: 'large',
          text: 'continue_with',
          shape: 'pill',
          width: 300,
        });
      }
    } catch {
      // Ignore initial render errors
    }
  }, [isModalOpen, loginWithGoogle, modalOptions, closeAuthModal]);

  // Handle Google 1-Tap Click
  const handleGoogleAuth = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
      if (typeof window !== 'undefined' && (window as any).google?.accounts?.id && clientId) {
        (window as any).google.accounts.id.initialize({
          client_id: clientId,
          callback: async (response: any) => {
            if (response?.credential) {
              const ok = await loginWithGoogle(response.credential);
              if (ok) {
                setSuccessCelebration(true);
                setTimeout(() => {
                  if (modalOptions.onComplete) modalOptions.onComplete();
                  closeAuthModal();
                }, 1200);
              } else {
                setErrorMsg('Google sign-in could not be completed. Please try again.');
              }
            }
            setLoading(false);
          },
        });
        (window as any).google.accounts.id.prompt();
        return;
      }

      // Fallback for dev / mock credential
      const mockCredential = `eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb29nbGVfdXNlcl8ke0RhdGUubm93KCl9IiwiZW1haWwiOiJzZWVrZXIuYXN0cm9sb2dpY0BnbWFpbC5jb20iLCJuYW1lIjoiQ29zbWljIFNlZWtlciIsImlhdCI6JHtNYXRoLmZsb29yKERhdGUubm93KCkvMTAwMCl9fQ.mock_sig`;
      const ok = await loginWithGoogle(mockCredential);
      if (ok) {
        setSuccessCelebration(true);
        setTimeout(() => {
          if (modalOptions.onComplete) modalOptions.onComplete();
          closeAuthModal();
        }, 1200);
      } else {
        setErrorMsg('Google sign-in could not be completed. Please try again.');
      }
    } catch (e: any) {
      setErrorMsg(e?.message || 'Authentication error');
    } finally {
      setLoading(false);
    }
  };

  // Handle Email & Password Sign In / Auto-Signup
  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanEmail = email.trim().toLowerCase();
    if (!cleanEmail || !cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      setErrorMsg('Please enter a valid email address.');
      return;
    }
    if (!password || password.length < 6) {
      setErrorMsg('Password must be at least 6 characters long.');
      return;
    }

    setEmailLoading(true);
    setErrorMsg(null);
    try {
      const res = await loginWithEmail(cleanEmail, password);
      if (res.success) {
        setSuccessCelebration(true);
        setTimeout(() => {
          if (modalOptions.onComplete) modalOptions.onComplete();
          closeAuthModal();
        }, 1200);
      } else {
        setErrorMsg(res.message || 'Authentication failed. Please check your credentials.');
      }
    } catch (e: any) {
      setErrorMsg(e?.message || 'Authentication error');
    } finally {
      setEmailLoading(false);
    }
  };

  // Handle Send WhatsApp OTP
  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone || phone.length < 10) {
      setErrorMsg('Please enter a valid international mobile number (e.g. +91 9876543210)');
      return;
    }
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await sendWhatsAppOtp(phone);
      if (res.success) {
        setOtpSent(true);
        setCountdown(60);
        if (res.devOtp) {
          setDevOtpHint(res.devOtp);
          setOtpCode(res.devOtp); // Auto-fill in dev mode for supreme convenience
        }
      } else {
        setErrorMsg(res.message);
      }
    } catch (e: any) {
      setErrorMsg(e?.message || 'Failed to send WhatsApp code');
    } finally {
      setLoading(false);
    }
  };

  // Handle Verify WhatsApp OTP
  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otpCode || otpCode.length < 4) {
      setErrorMsg('Please enter the 6-digit code sent to your WhatsApp');
      return;
    }
    setLoading(true);
    setErrorMsg(null);
    try {
      const ok = await verifyWhatsAppOtp(phone, otpCode);
      if (ok) {
        setSuccessCelebration(true);
        setTimeout(() => {
          if (modalOptions.onComplete) modalOptions.onComplete();
          closeAuthModal();
        }, 1200);
      } else {
        setErrorMsg('Invalid or expired code. Please request a new code.');
      }
    } catch (e: any) {
      setErrorMsg(e?.message || 'Verification error');
    } finally {
      setLoading(false);
    }
  };

  if (!isModalOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
    >
      {/* Click outside backdrop */}
      <div className="absolute inset-0" onClick={closeAuthModal} />

      {/* Modal Container */}
      <div className="relative w-full max-w-md bg-[#FAF6F0] rounded-2xl border border-[#C5A059]/40 shadow-2xl overflow-hidden z-10 animate-in zoom-in-95 duration-200">
        {/* Top Sacred Luxury Hairline */}
        <div className="h-1.5 w-full bg-linear-to-r from-[#7A1612] via-[#C5A059] to-[#7A1612]" />

        {/* Close Button */}
        <button
          onClick={closeAuthModal}
          className="absolute top-4 right-4 p-2 text-[#7A1612]/60 hover:text-[#7A1612] hover:bg-[#F5EFE6] rounded-full transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        {successCelebration ? (
          /* Success Screen */
          <div className="p-8 text-center space-y-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-[#1B4D3E]/10 border border-[#1B4D3E]/30 flex items-center justify-center text-[#1B4D3E]">
              <CheckCircle2 className="w-10 h-10 animate-bounce" />
            </div>
            <h3 className="font-serif text-2xl font-bold text-[#7A1612]">
              Sacred Identity Verified!
            </h3>
            <p className="text-xs text-[#24120B]/80 max-w-xs mx-auto">
              Your Janma Kundali and birth details have been successfully preserved in your Family Vault.
            </p>
          </div>
        ) : (
          /* Normal Auth Body */
          <div className="p-6 sm:p-8 space-y-6">
            {/* Contextual Header */}
            <div className="text-center space-y-2">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#C5A059]/15 border border-[#C5A059]/30 text-[10px] font-mono uppercase tracking-widest text-[#7A1612] font-semibold">
                <Sparkles className="w-3 h-3 text-[#C5A059]" />
                <span>{headerInfo.badge}</span>
              </div>
              <h2 className="font-serif text-xl sm:text-2xl font-bold text-[#7A1612] tracking-tight">
                {headerInfo.title}
              </h2>
              <p className="text-xs text-[#24120B]/75 leading-relaxed max-w-sm mx-auto">
                {headerInfo.subtitle}
              </p>
            </div>

            {/* Error Message */}
            {errorMsg && (
              <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* 1. Google 1-Tap Auth Button */}
            <div className="space-y-3">
              <div id="google-btn-slot" className="w-full flex justify-center empty:hidden" />
              <button
                type="button"
                onClick={handleGoogleAuth}
                disabled={loading || emailLoading}
                className="w-full flex items-center justify-center gap-3 px-4 py-3 text-sm font-semibold text-[#24120B] bg-white hover:bg-neutral-50 rounded-xl border border-[#C5A059]/40 shadow-xs hover:shadow-md transition-all cursor-pointer group disabled:opacity-50"
              >
                <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                  />
                </svg>
                <span>{loading ? 'Authenticating with Google...' : 'Continue with Google (1-Tap)'}</span>
              </button>
            </div>

            {/* 2. Visual Divider: ─── or with email ─── */}
            <div className="relative flex items-center justify-center my-1">
              <div className="grow border-t border-[#C5A059]/30" />
              <span className="px-3 text-[11px] font-semibold text-[#24120B]/60 uppercase tracking-wider bg-[#FAF6F0]">
                or with email
              </span>
              <div className="grow border-t border-[#C5A059]/30" />
            </div>

            {/* 3. Manual Email & Password Form */}
            <form onSubmit={handleEmailAuth} className="space-y-3.5">
              <div>
                <label htmlFor="auth-email-input" className="block text-xs font-semibold text-[#7A1612] mb-1 cursor-pointer">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3 top-3 text-[#C5A059]" />
                  <input
                    id="auth-email-input"
                    aria-label="Email Address"
                    type="email"
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    required
                    className="w-full pl-9 pr-3 py-2.5 text-sm bg-white rounded-xl border border-[#C5A059]/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612] focus-visible:border-[#7A1612] text-[#24120B] placeholder-[#24120B]/40"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label htmlFor="auth-password-input" className="text-xs font-semibold text-[#7A1612] cursor-pointer">
                    Password
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-[11px] text-[#A85A1E] hover:underline cursor-pointer"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? 'Hide' : 'Show'}
                  </button>
                </div>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-3 text-[#C5A059]" />
                  <input
                    id="auth-password-input"
                    aria-label="Password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter password (min. 6 characters)"
                    required
                    minLength={6}
                    className="w-full pl-9 pr-10 py-2.5 text-sm bg-white rounded-xl border border-[#C5A059]/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612] focus-visible:border-[#7A1612] text-[#24120B] placeholder-[#24120B]/40 font-mono"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={emailLoading || loading}
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold rounded-xl text-[#FAF6F0] bg-linear-to-r from-[#7A1612] via-[#8E1C17] to-[#7A1612] hover:brightness-105 border border-[#C5A059]/40 shadow-xs hover:shadow-md cursor-pointer transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {emailLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-[#FAF6F0] border-t-transparent rounded-full animate-spin" />
                    <span>Authenticating...</span>
                  </>
                ) : (
                  <>
                    <span>Sign In / Create Account</span>
                    <ArrowRight className="w-4 h-4 text-[#F5E1BE]" />
                  </>
                )}
              </button>

              <p className="text-[10px] text-center text-[#24120B]/55 leading-tight pt-0.5">
                🔒 Existing users sign in automatically. New accounts are created instantly.
              </p>
            </form>

            {/* Subtle WhatsApp Footnote */}
            <div className="pt-2 border-t border-[#C5A059]/20 flex items-center justify-center gap-1.5 text-[11px] text-[#24120B]/40 select-none">
              <MessageSquare className="w-3.5 h-3.5 text-neutral-400" />
              <span>WhatsApp OTP Login</span>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-neutral-200 text-neutral-600 font-semibold uppercase tracking-wider">
                Soon
              </span>
            </div>

            {/* Privacy & Trust Statement */}
            <div className="pt-2 border-t border-[#C5A059]/20 flex items-center justify-center gap-2 text-[10px] text-[#24120B]/60">
              <ShieldCheck className="w-3.5 h-3.5 text-[#1B4D3E]" />
              <span>100% Private & Encrypted · Swiss Ephemeris Precision · No Spam</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

