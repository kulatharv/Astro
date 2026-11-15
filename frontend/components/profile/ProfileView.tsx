'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Sparkles, 
  User, 
  Users, 
  MessageSquare, 
  ShieldCheck, 
  Compass, 
  Calendar, 
  Clock, 
  MapPin, 
  Plus, 
  Trash2, 
  ExternalLink, 
  CheckCircle2, 
  AlertCircle,
  Moon,
  Sun,
  Flame,
  ArrowRight,
  Share2
} from 'lucide-react';
import { Link } from '@/i18n/routing';

interface CosmicBadges {
  lagna_sign?: string;
  moon_sign?: string;
  sun_sign?: string;
  nakshatra?: string;
  nakshatra_pada?: number;
  mahadasha?: string;
  antardasha?: string;
  is_calculated: boolean;
}

interface UserProfile {
  user_id: number;
  name: string;
  email: string;
  phone?: string;
  birth_date?: string;
  birth_time?: string;
  birth_city?: string;
  latitude?: number;
  longitude?: number;
  timezone_offset: number;
  tz_name?: string;
  birth_uncertainty: string;
  zodiac_sign?: string;
  notes?: string;
  preferred_language: string;
  whatsapp_number?: string;
  whatsapp_opt_in: boolean;
  whatsapp_time: string;
  whatsapp_language: string;
  cosmic_badges?: CosmicBadges;
  saved_charts_count: number;
}

interface SavedChart {
  id: number;
  title: string;
  person_name: string;
  gender?: string;
  birth_date: string;
  birth_time: string;
  birth_city: string;
  lagna_sign?: string;
  moon_sign?: string;
  nakshatra?: string;
  notes?: string;
}

export default function ProfileView() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [savedCharts, setSavedCharts] = useState<SavedChart[]>([]);
  const [activeTab, setActiveTab] = useState<'cosmic' | 'family' | 'whatsapp' | 'account'>('cosmic');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // New family chart form state
  const [showAddFamily, setShowAddFamily] = useState(false);
  const [familyForm, setFamilyForm] = useState({
    title: 'Spouse',
    person_name: '',
    gender: 'female',
    birth_date: '',
    birth_time: '12:00',
    birth_city: 'Pune',
    notes: '',
  });

  // Interactive 3D Holographic Card State
  const [isHoloActive, setIsHoloActive] = useState(true);
  const [cardTilt, setCardTilt] = useState({ x: 0, y: 0, sheenX: 50, sheenY: 50 });
  const cardRef = useRef<HTMLDivElement | null>(null);

  const handleCardMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!isHoloActive || !cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const xRatio = (e.clientX - rect.left) / rect.width;
    const yRatio = (e.clientY - rect.top) / rect.height;

    const rotY = (xRatio - 0.5) * 14;
    const rotX = (0.5 - yRatio) * 14;

    setCardTilt({
      x: rotX,
      y: rotY,
      sheenX: xRatio * 100,
      sheenY: yRatio * 100,
    });
  }, [isHoloActive]);

  const handleCardMouseLeave = useCallback(() => {
    setCardTilt({ x: 0, y: 0, sheenX: 50, sheenY: 50 });
  }, []);

  // Mobile Device Gyroscope Tilt
  useEffect(() => {
    if (!isHoloActive || typeof window === 'undefined') return;
    const handleOrientation = (e: DeviceOrientationEvent) => {
      if (e.beta !== null && e.gamma !== null) {
        const tiltX = Math.min(Math.max((e.beta - 45) * 0.35, -12), 12);
        const tiltY = Math.min(Math.max(e.gamma * 0.35, -12), 12);
        setCardTilt({
          x: tiltX,
          y: tiltY,
          sheenX: 50 + tiltY * 3,
          sheenY: 50 + tiltX * 3,
        });
      }
    };
    window.addEventListener('deviceorientation', handleOrientation);
    return () => window.removeEventListener('deviceorientation', handleOrientation);
  }, [isHoloActive]);

  useEffect(() => {
    fetchProfileAndCharts();
  }, []);

  async function fetchProfileAndCharts() {
    setLoading(true);
    try {
      const [profRes, chartsRes] = await Promise.all([
        fetch('/api/user/profile'),
        fetch('/api/user/charts'),
      ]);

      if (profRes.ok) {
        const json = await profRes.json();
        if (json.status === 'success') {
          setProfile(json.data);
        }
      }

      if (chartsRes.ok) {
        const json = await chartsRes.json();
        if (json.status === 'success') {
          setSavedCharts(json.data);
        }
      }
    } catch (err) {
      console.error('Error fetching profile:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleProfileSave(e: React.FormEvent) {
    e.preventDefault();
    if (!profile) return;
    setSaving(true);
    setStatusMsg(null);

    try {
      const res = await fetch('/api/user/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: profile.name,
          phone: profile.phone,
          birth_date: profile.birth_date,
          birth_time: profile.birth_time,
          birth_city: profile.birth_city,
          birth_uncertainty: profile.birth_uncertainty,
          notes: profile.notes,
          preferred_language: profile.preferred_language,
        }),
      });

      const json = await res.json();
      if (res.ok && json.status === 'success') {
        setProfile(json.data);
        setStatusMsg({ type: 'success', text: 'Cosmic profile & astrological badges updated successfully!' });
      } else {
        setStatusMsg({ type: 'error', text: json.message || 'Failed to update profile.' });
      }
    } catch (err) {
      setStatusMsg({ type: 'error', text: 'Network connection failed.' });
    } finally {
      setSaving(false);
      setTimeout(() => setStatusMsg(null), 4000);
    }
  }

  async function handleWhatsAppSave(e: React.FormEvent) {
    e.preventDefault();
    if (!profile) return;
    setSaving(true);
    setStatusMsg(null);

    try {
      const res = await fetch('/api/user/whatsapp-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          whatsapp_number: profile.whatsapp_number || '',
          whatsapp_opt_in: profile.whatsapp_opt_in,
          whatsapp_time: profile.whatsapp_time || '07:00',
          whatsapp_language: profile.whatsapp_language || 'en',
        }),
      });

      const json = await res.json();
      if (res.ok && json.status === 'success') {
        setProfile(json.data);
        setStatusMsg({ type: 'success', text: 'WhatsApp daily briefing preferences saved!' });
      } else {
        setStatusMsg({ type: 'error', text: json.message || 'Could not save WhatsApp settings.' });
      }
    } catch (err) {
      setStatusMsg({ type: 'error', text: 'Network connection failed.' });
    } finally {
      setSaving(false);
      setTimeout(() => setStatusMsg(null), 4000);
    }
  }

  async function handleAddFamilyChart(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await fetch('/api/user/charts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(familyForm),
      });

      const json = await res.json();
      if (res.ok && json.status === 'success') {
        setSavedCharts([json.data, ...savedCharts]);
        setShowAddFamily(false);
        setFamilyForm({
          title: 'Child',
          person_name: '',
          gender: 'female',
          birth_date: '',
          birth_time: '12:00',
          birth_city: 'Pune',
          notes: '',
        });
        setStatusMsg({ type: 'success', text: `Added ${json.data.person_name} to Family Vault!` });
      } else {
        setStatusMsg({ type: 'error', text: json.message || 'Failed to add chart.' });
      }
    } catch (err) {
      setStatusMsg({ type: 'error', text: 'Network connection failed.' });
    } finally {
      setSaving(false);
      setTimeout(() => setStatusMsg(null), 4000);
    }
  }

  async function handleDeleteSavedChart(id: number) {
    if (!confirm('Are you sure you want to remove this chart from your vault?')) return;
    try {
      const res = await fetch(`/api/user/charts/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setSavedCharts(savedCharts.filter(c => c.id !== id));
        setStatusMsg({ type: 'success', text: 'Chart removed from vault.' });
      }
    } catch (err) {
      setStatusMsg({ type: 'error', text: 'Could not delete chart.' });
    } finally {
      setTimeout(() => setStatusMsg(null), 3000);
    }
  }

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4">
        <div className="w-12 h-12 rounded-full border-2 border-[#C5A059] border-t-transparent animate-spin" />
        <p className="font-serif text-[#7A1612] text-sm tracking-wide">Loading your Cosmic Profile...</p>
      </div>
    );
  }

  const badges = profile?.cosmic_badges;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Status banner */}
      {statusMsg && (
        <div
          className={`p-4 rounded-xl flex items-center gap-3 text-sm font-medium transition-all ${
            statusMsg.type === 'success'
              ? 'bg-[#FAF8F5] border border-[#C5A059] text-[#7A1612]'
              : 'bg-red-50 border border-red-200 text-red-700'
          }`}
        >
          {statusMsg.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5 text-[#C5A059] shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
          )}
          <span>{statusMsg.text}</span>
        </div>
      )}

      {/* Cosmic Identity 3D Holographic Pass */}
      <div
        ref={cardRef}
        onMouseMove={handleCardMouseMove}
        onMouseLeave={handleCardMouseLeave}
        style={{
          transform: isHoloActive
            ? `perspective(1200px) rotateX(${cardTilt.x}deg) rotateY(${cardTilt.y}deg) scale3d(1.01, 1.01, 1.01)`
            : 'none',
          transition: 'transform 0.12s ease-out',
          transformStyle: 'preserve-3d',
        }}
        className="relative overflow-hidden rounded-3xl bg-linear-to-br from-[#7A1612] via-[#24120B] to-[#120703] text-[#FAF6F0] p-6 sm:p-8 border border-[#C5A059]/50 shadow-2xl transition-all select-none"
      >
        {/* Dynamic Specular Iridescent Sheen Layer */}
        {isHoloActive && (
          <div
            className="absolute inset-0 pointer-events-none rounded-3xl z-30 mix-blend-color-dodge transition-opacity duration-200"
            style={{
              background: `radial-gradient(circle at ${cardTilt.sheenX}% ${cardTilt.sheenY}%, rgba(245,225,190,0.35) 0%, rgba(197,160,89,0.12) 35%, transparent 65%)`,
            }}
          />
        )}

        <div className="absolute top-0 right-0 w-96 h-96 bg-[radial-gradient(ellipse_at_top_right,rgba(197,160,89,0.25),transparent_70%)] pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-[#C5A059]/20 border border-[#C5A059]/40 text-[#F5E1BE] text-xs font-mono uppercase tracking-widest">
                <Sparkles className="w-3.5 h-3.5 text-[#C5A059]" />
                <span>Cosmic Identity Pass</span>
              </div>
              <button
                type="button"
                onClick={() => setIsHoloActive(!isHoloActive)}
                className="text-[10px] text-[#C5A059] hover:underline px-2 py-0.5 rounded-md bg-white/5 border border-white/10"
              >
                {isHoloActive ? '3D Hologram ON' : 'Flat 2D'}
              </button>
            </div>
            <h1 className="font-serif text-3xl sm:text-4xl font-bold tracking-tight text-[#FAF6F0]">
              {profile?.name || 'Vedic Explorer'}
            </h1>
            <p className="text-sm text-[#F5E1BE]/80 max-w-xl">
              {profile?.birth_date && profile?.birth_city
                ? `Born on ${profile.birth_date} at ${profile.birth_time || '12:00'} in ${profile.birth_city}. Computed using Lahiri Ayanamsha & Swiss Ephemeris.`
                : 'Complete your birth date, time, and city below to unlock your personalized Cosmic Badges and Kundali.'}
            </p>
          </div>

          <div className="flex flex-wrap gap-2.5">
            <Link
              href="/kundali"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#C5A059] text-[#24120B] font-semibold text-xs uppercase tracking-wider hover:brightness-110 shadow-md transition-all cursor-pointer"
            >
              <Compass className="w-4 h-4" />
              <span>View Full Kundali</span>
            </Link>
            <Link
              href="/predictions"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 text-[#FAF6F0] border border-white/20 font-semibold text-xs uppercase tracking-wider transition-all cursor-pointer"
            >
              <span>10-Domain Insights</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Dynamic Cosmic Badges Row */}
        {badges?.is_calculated ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-8 pt-6 border-t border-white/10">
            <div className="p-3.5 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
              <div className="flex items-center gap-2 text-xs text-[#C5A059] font-medium uppercase tracking-wider mb-1">
                <Compass className="w-3.5 h-3.5" />
                <span>Ascendant (Lagna)</span>
              </div>
              <div className="text-xl font-serif font-bold text-[#FAF6F0]">
                {badges.lagna_sign}
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
              <div className="flex items-center gap-2 text-xs text-[#9BDCFF] font-medium uppercase tracking-wider mb-1">
                <Moon className="w-3.5 h-3.5" />
                <span>Moon Sign (Rashi)</span>
              </div>
              <div className="text-xl font-serif font-bold text-[#FAF6F0]">
                {badges.moon_sign}
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
              <div className="flex items-center gap-2 text-xs text-[#F5C16C] font-medium uppercase tracking-wider mb-1">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Janma Nakshatra</span>
              </div>
              <div className="text-lg font-serif font-bold text-[#FAF6F0] truncate">
                {badges.nakshatra} {badges.nakshatra_pada ? `(Pada ${badges.nakshatra_pada})` : ''}
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
              <div className="flex items-center gap-2 text-xs text-[#4ADE80] font-medium uppercase tracking-wider mb-1">
                <Flame className="w-3.5 h-3.5" />
                <span>Active Dasha</span>
              </div>
              <div className="text-lg font-serif font-bold text-[#FAF6F0]">
                {badges.mahadasha} {badges.antardasha ? `/ ${badges.antardasha}` : ''}
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between text-xs text-[#F5E1BE]/80">
            <span>⚠️ Save your birth details below to compute your Lagna, Moon Sign, Nakshatra, and Active Dasha.</span>
          </div>
        )}
      </div>

      {/* Navigation Tabs with mobile scroll indicator */}
      <div className="relative">
        <div className="flex border-b border-[#C5A059]/30 gap-1.5 sm:gap-4 overflow-x-auto pb-px scrollbar-none">
          {[
            { key: 'cosmic', label: 'Birth Details & Badges', icon: Compass, disabled: false },
            { key: 'family', label: `Family & Client Vault (${savedCharts.length})`, icon: Users, disabled: false },
            { key: 'whatsapp', label: 'Daily WhatsApp Forecast', icon: MessageSquare, disabled: true },
            { key: 'account', label: 'Account & Preferences', icon: ShieldCheck, disabled: false },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            if (tab.disabled) {
              return (
                <button
                  key={tab.key}
                  type="button"
                  disabled
                  className="min-h-[44px] flex items-center gap-1.5 px-3.5 sm:px-4 py-3 text-xs sm:text-sm font-semibold border-b-2 border-transparent text-[#24120B]/40 opacity-50 cursor-not-allowed whitespace-nowrap select-none"
                  title="WhatsApp Forecast is coming soon"
                >
                  <Icon className="w-4 h-4 shrink-0 text-neutral-400" />
                  <span>{tab.label}</span>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-neutral-200 text-neutral-600 font-semibold uppercase tracking-wider">Soon</span>
                </button>
              );
            }
            return (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActiveTab(tab.key as any)}
                className={`min-h-[44px] flex items-center gap-2 px-3.5 sm:px-4 py-3 text-xs sm:text-sm font-semibold border-b-2 whitespace-nowrap transition-all cursor-pointer ${
                  isActive
                    ? 'border-[#7A1612] text-[#7A1612] bg-[#FAF6F0]'
                    : 'border-transparent text-[#24120B]/70 hover:text-[#7A1612] hover:bg-[#FAF6F0]/50'
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[#7A1612]' : 'text-[#A85A1E]'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
        {/* Subtle scroll hint gradient on mobile */}
        <div className="pointer-events-none absolute right-0 top-0 bottom-0 w-8 bg-linear-to-l from-[#FAF6F0] to-transparent sm:hidden" />
      </div>

      {/* TAB 1: Birth Details & Cosmic Identity */}
      {activeTab === 'cosmic' && profile && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-[#FAF6F0] rounded-2xl p-6 sm:p-8 border border-[#C5A059]/30 shadow-sm space-y-6">
            <div>
              <h2 className="font-serif text-xl font-bold text-[#7A1612]">Personal Birth Coordinates</h2>
              <p className="text-xs text-[#24120B]/70 mt-1">
                Your birth time and city dictate your planetary ascendant and active Vimshottari dasha cycles.
              </p>
            </div>

            <form onSubmit={handleProfileSave} className="space-y-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="profile-full-name" className="block text-xs font-semibold uppercase tracking-wider text-[#7A1612] mb-1.5 cursor-pointer">
                    Full Name
                  </label>
                  <input
                    id="profile-full-name"
                    type="text"
                    value={profile.name || ''}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-[#24120B] text-base sm:text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                </div>

                <div>
                  <label htmlFor="profile-phone-number" className="block text-xs font-semibold uppercase tracking-wider text-[#7A1612] mb-1.5 cursor-pointer">
                    Phone Number
                  </label>
                  <input
                    id="profile-phone-number"
                    type="tel"
                    value={profile.phone || ''}
                    placeholder="+91 9876543210"
                    onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-[#24120B] text-base sm:text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label htmlFor="profile-birth-date" className="block text-xs font-semibold uppercase tracking-wider text-[#7A1612] mb-1.5 cursor-pointer">
                    Birth Date
                  </label>
                  <input
                    id="profile-birth-date"
                    type="date"
                    value={profile.birth_date || ''}
                    onChange={(e) => setProfile({ ...profile, birth_date: e.target.value })}
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-[#24120B] text-base sm:text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                </div>

                <div>
                  <label htmlFor="profile-birth-time" className="block text-xs font-semibold uppercase tracking-wider text-[#7A1612] mb-1.5 cursor-pointer">
                    Birth Time
                  </label>
                  <input
                    id="profile-birth-time"
                    type="time"
                    value={profile.birth_time || '12:00'}
                    onChange={(e) => setProfile({ ...profile, birth_time: e.target.value })}
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-[#24120B] text-base sm:text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                </div>

                <div>
                  <label htmlFor="profile-birth-city" className="block text-xs font-semibold uppercase tracking-wider text-[#7A1612] mb-1.5 cursor-pointer">
                    Birth City
                  </label>
                  <input
                    id="profile-birth-city"
                    type="text"
                    value={profile.birth_city || ''}
                    placeholder="e.g. Pune, Delhi, Mumbai"
                    onChange={(e) => setProfile({ ...profile, birth_city: e.target.value })}
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-[#24120B] text-base sm:text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                </div>
              </div>

              {/* Birth Time Uncertainty Preference */}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-[#7A1612] mb-1.5">
                  Birth Time Precision
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {[
                    { val: 'exact', label: 'Exact (±1 min)', desc: 'From birth certificate' },
                    { val: 'approximate', label: 'Approximate (±15 min)', desc: 'Hospital memory' },
                    { val: 'uncertain', label: 'Uncertain (±1 hour)', desc: 'Rectification advised' },
                  ].map((opt) => (
                    <label
                      key={opt.val}
                      className={`p-3 rounded-xl border cursor-pointer transition-all flex flex-col gap-1 ${
                        profile.birth_uncertainty === opt.val
                          ? 'border-[#7A1612] bg-[#F5EFE6] text-[#7A1612]'
                          : 'border-[#C5A059]/30 bg-white text-[#24120B]/80 hover:bg-[#F5EFE6]/50'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <input
                          type="radio"
                          name="birth_uncertainty"
                          value={opt.val}
                          checked={profile.birth_uncertainty === opt.val}
                          onChange={(e) => setProfile({ ...profile, birth_uncertainty: e.target.value })}
                          className="accent-[#7A1612]"
                        />
                        <span className="text-xs font-bold">{opt.label}</span>
                      </div>
                      <span className="text-[11px] text-[#24120B]/60 pl-5">{opt.desc}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label htmlFor="profile-astrology-notes" className="block text-xs font-semibold uppercase tracking-wider text-[#7A1612] mb-1.5 cursor-pointer">
                  Personal Astrology Notes / Focus Areas
                </label>
                <textarea
                  id="profile-astrology-notes"
                  rows={3}
                  value={profile.notes || ''}
                  placeholder="Record remedies, astrologer consultation notes, or key life milestones..."
                  onChange={(e) => setProfile({ ...profile, notes: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-[#24120B] text-base sm:text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                />
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="px-6 py-2.5 rounded-xl bg-linear-to-r from-[#7A1612] to-[#24120B] text-[#FAF6F0] font-semibold text-xs uppercase tracking-wider hover:brightness-110 shadow-md transition-all cursor-pointer disabled:opacity-50"
                >
                  {saving ? 'Recalculating Badges...' : 'Save & Recalculate Badges'}
                </button>
              </div>
            </form>
          </div>

          {/* Quick Actions & Ephemeris Info */}
          <div className="space-y-6">
            <div className="bg-[#FAF6F0] rounded-2xl p-6 border border-[#C5A059]/30 shadow-sm space-y-4">
              <h3 className="font-serif font-bold text-[#7A1612] text-base">Vedic Engine Parameters</h3>
              <div className="space-y-2.5 text-xs">
                <div className="flex justify-between py-1.5 border-b border-[#C5A059]/20">
                  <span className="text-[#24120B]/70">Ephemeris Mode:</span>
                  <span className="font-semibold text-[#7A1612]">Swiss / Moshier</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-[#C5A059]/20">
                  <span className="text-[#24120B]/70">Ayanamsha:</span>
                  <span className="font-semibold text-[#7A1612]">Chitra Paksha / Lahiri</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-[#C5A059]/20">
                  <span className="text-[#24120B]/70">Coordinates:</span>
                  <span className="font-semibold text-[#7A1612]">
                    {profile.latitude ? `${profile.latitude.toFixed(2)}°N, ${profile.longitude?.toFixed(2)}°E` : 'Auto-detected'}
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-[#C5A059]/20">
                  <span className="text-[#24120B]/70">Timezone:</span>
                  <span className="font-semibold text-[#7A1612]">UTC +{profile.timezone_offset || 5.5}</span>
                </div>
              </div>
            </div>

            <div className="bg-linear-to-br from-[#FAF6F0] to-[#F5EFE6] rounded-2xl p-6 border border-[#C5A059]/40 shadow-sm space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold text-[#7A1612] uppercase tracking-wider">
                <Sparkles className="w-4 h-4 text-[#C5A059]" />
                <span>Next Predictive Step</span>
              </div>
              <p className="text-xs text-[#24120B]/80 leading-relaxed">
                With your birth details loaded, explore your complete 10-domain life insight forecast across Career, Wealth, Marriage, and Health.
              </p>
              <Link
                href="/predictions"
                className="w-full inline-flex items-center justify-center gap-2 py-2.5 rounded-xl bg-[#7A1612] text-[#FAF6F0] font-semibold text-xs uppercase tracking-wider hover:brightness-110 transition-all cursor-pointer"
              >
                <span>Run 10-Domain Engine</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Family & Client Vault */}
      {activeTab === 'family' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="font-serif text-2xl font-bold text-[#7A1612]">Multi-Chart Family & Client Vault</h2>
              <p className="text-xs text-[#24120B]/70 mt-1">
                Save charts for your spouse, children, parents, or consulting clients to quickly switch charts or run compatibility matching.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setShowAddFamily(!showAddFamily)}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#7A1612] text-[#FAF6F0] font-semibold text-xs uppercase tracking-wider hover:brightness-110 shadow-sm transition-all cursor-pointer shrink-0"
            >
              <Plus className="w-4 h-4 text-[#C5A059]" />
              <span>Add Member Chart</span>
            </button>
          </div>

          {/* Add Member Form Modal / Expandable Card */}
          {showAddFamily && (
            <div className="bg-[#FAF6F0] rounded-2xl p-6 border border-[#C5A059]/40 shadow-md space-y-4">
              <h3 className="font-serif font-bold text-lg text-[#7A1612]">Add Chart to Vault</h3>
              <form onSubmit={handleAddFamilyChart} className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label htmlFor="family-relation" className="block text-xs font-semibold uppercase text-[#7A1612] mb-1 cursor-pointer">Relation / Label</label>
                  <select
                    id="family-relation"
                    value={familyForm.title}
                    onChange={(e) => setFamilyForm({ ...familyForm, title: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-base sm:text-sm text-[#24120B] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  >
                    <option value="Spouse">Spouse / Partner</option>
                    <option value="Child">Child</option>
                    <option value="Mother">Mother</option>
                    <option value="Father">Father</option>
                    <option value="Sibling">Sibling</option>
                    <option value="Client">Client</option>
                    <option value="Friend">Friend</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="family-person-name" className="block text-xs font-semibold uppercase text-[#7A1612] mb-1 cursor-pointer">Full Name</label>
                  <input
                    id="family-person-name"
                    type="text"
                    value={familyForm.person_name}
                    placeholder="e.g. Priya Sharma"
                    onChange={(e) => setFamilyForm({ ...familyForm, person_name: e.target.value })}
                    required
                    className="w-full px-3 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-base sm:text-sm text-[#24120B] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                </div>

                <div>
                  <label htmlFor="family-gender" className="block text-xs font-semibold uppercase text-[#7A1612] mb-1 cursor-pointer">Gender</label>
                  <select
                    id="family-gender"
                    value={familyForm.gender}
                    onChange={(e) => setFamilyForm({ ...familyForm, gender: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-base sm:text-sm text-[#24120B] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  >
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="family-birth-date" className="block text-xs font-semibold uppercase text-[#7A1612] mb-1 cursor-pointer">Birth Date</label>
                  <input
                    id="family-birth-date"
                    type="date"
                    value={familyForm.birth_date}
                    onChange={(e) => setFamilyForm({ ...familyForm, birth_date: e.target.value })}
                    required
                    className="w-full px-3 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-base sm:text-sm text-[#24120B] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                </div>

                <div>
                  <label htmlFor="family-birth-time" className="block text-xs font-semibold uppercase text-[#7A1612] mb-1 cursor-pointer">Birth Time</label>
                  <input
                    id="family-birth-time"
                    type="time"
                    value={familyForm.birth_time}
                    onChange={(e) => setFamilyForm({ ...familyForm, birth_time: e.target.value })}
                    required
                    className="w-full px-3 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-base sm:text-sm text-[#24120B] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                </div>

                <div>
                  <label htmlFor="family-birth-city" className="block text-xs font-semibold uppercase text-[#7A1612] mb-1 cursor-pointer">Birth City</label>
                  <input
                    id="family-birth-city"
                    type="text"
                    value={familyForm.birth_city}
                    placeholder="e.g. Mumbai"
                    onChange={(e) => setFamilyForm({ ...familyForm, birth_city: e.target.value })}
                    required
                    className="w-full px-3 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-base sm:text-sm text-[#24120B] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                </div>

                <div className="sm:col-span-3 flex justify-end gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowAddFamily(false)}
                    className="px-4 py-2 rounded-xl text-xs font-semibold text-[#24120B]/70 hover:bg-[#F5EFE6]"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={saving}
                    className="px-6 py-2 rounded-xl bg-[#7A1612] text-[#FAF6F0] font-semibold text-xs uppercase tracking-wider hover:brightness-110"
                  >
                    Save to Vault
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Cards Grid */}
          {savedCharts.length === 0 ? (
            <div className="bg-[#FAF6F0] rounded-2xl p-12 text-center border border-[#C5A059]/30 space-y-3">
              <Users className="w-12 h-12 text-[#C5A059] mx-auto opacity-70" />
              <h3 className="font-serif text-lg font-bold text-[#7A1612]">Your Vault is Empty</h3>
              <p className="text-xs text-[#24120B]/70 max-w-md mx-auto">
                Add birth charts for your spouse, children, or family members to easily view their planetary charts and check compatibility.
              </p>
              <button
                type="button"
                onClick={() => setShowAddFamily(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#7A1612] text-[#FAF6F0] text-xs font-semibold uppercase tracking-wider cursor-pointer"
              >
                <Plus className="w-4 h-4 text-[#C5A059]" />
                <span>Add First Chart</span>
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {savedCharts.map((chart) => (
                <div
                  key={chart.id}
                  className="bg-[#FAF6F0] rounded-2xl p-5 border border-[#C5A059]/30 shadow-xs hover:shadow-md transition-all space-y-4 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono uppercase tracking-wider bg-[#7A1612]/10 text-[#7A1612] border border-[#7A1612]/20 font-semibold">
                        {chart.title}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleDeleteSavedChart(chart.id)}
                        className="min-w-[40px] min-h-[40px] flex items-center justify-center text-[#24120B]/40 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors cursor-pointer"
                        title="Delete chart"
                        aria-label={`Delete ${chart.person_name} chart`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    <h4 className="font-serif text-lg font-bold text-[#24120B]">
                      {chart.person_name}
                    </h4>

                    <div className="text-xs text-[#24120B]/70 space-y-1 mt-2">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-3.5 h-3.5 text-[#C5A059]" />
                        <span>{chart.birth_date} at {chart.birth_time}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5 text-[#C5A059]" />
                        <span>{chart.birth_city}</span>
                      </div>
                    </div>

                    {/* Pre-computed badges if available */}
                    {(chart.lagna_sign || chart.moon_sign) && (
                      <div className="grid grid-cols-2 gap-2 mt-3 pt-3 border-t border-[#C5A059]/20 text-xs">
                        {chart.lagna_sign && (
                          <div className="p-2 rounded-lg bg-white/70 border border-[#C5A059]/20">
                            <span className="text-[10px] uppercase text-[#7A1612] font-semibold block">Lagna</span>
                            <span className="font-bold text-[#24120B]">{chart.lagna_sign}</span>
                          </div>
                        )}
                        {chart.moon_sign && (
                          <div className="p-2 rounded-lg bg-white/70 border border-[#C5A059]/20">
                            <span className="text-[10px] uppercase text-[#7A1612] font-semibold block">Rashi</span>
                            <span className="font-bold text-[#24120B]">{chart.moon_sign}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2 pt-2 border-t border-[#C5A059]/20">
                    <Link
                      href={`/kundali?name=${encodeURIComponent(chart.person_name)}&date=${chart.birth_date}&time=${chart.birth_time}&city=${encodeURIComponent(chart.birth_city)}`}
                      className="flex-1 text-center py-2 rounded-xl bg-[#7A1612] text-[#FAF6F0] text-xs font-semibold hover:brightness-110 transition-all cursor-pointer"
                    >
                      Open Kundali
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: Daily WhatsApp Briefing */}
      {activeTab === 'whatsapp' && profile && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-[#FAF6F0] rounded-2xl p-6 sm:p-8 border border-[#C5A059]/30 shadow-sm space-y-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-emerald-100 border border-emerald-300 text-emerald-800 text-xs font-mono font-semibold uppercase tracking-wider mb-2">
                  <MessageSquare className="w-3.5 h-3.5 text-emerald-600" />
                  <span>WhatsApp Intelligence Service</span>
                </div>
                <h2 className="font-serif text-2xl font-bold text-[#7A1612]">
                  Daily Personalized Morning Forecast
                </h2>
                <p className="text-xs text-[#24120B]/70 mt-1 max-w-lg">
                  Receive an automated briefing every morning calculated against your personal Janma Nakshatra (Tara Bala), Moon sign (Chandrabala), and city-specific Rahu Kaal.
                </p>
              </div>
            </div>

            <form onSubmit={handleWhatsAppSave} className="space-y-5">
              {/* Opt-in toggle */}
              <div className="p-4 rounded-xl border border-[#C5A059]/40 bg-white flex items-center justify-between">
                <div>
                  <span className="text-sm font-bold text-[#24120B] block">Enable Daily WhatsApp Briefing</span>
                  <span className="text-xs text-[#24120B]/60">Delivered automatically at your selected morning time.</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    aria-label="Enable Daily WhatsApp Briefing"
                    type="checkbox"
                    checked={profile.whatsapp_opt_in}
                    onChange={(e) => setProfile({ ...profile, whatsapp_opt_in: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus-visible:ring-2 peer-focus-visible:ring-[#7A1612] peer-focus-visible:ring-offset-2 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600" />
                </label>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="profile-whatsapp-phone" className="block text-xs font-semibold uppercase tracking-wider text-[#7A1612] mb-1.5 cursor-pointer">
                    WhatsApp Phone Number (with Country Code)
                  </label>
                  <input
                    id="profile-whatsapp-phone"
                    type="tel"
                    placeholder="+91 9876543210"
                    value={profile.whatsapp_number || ''}
                    onChange={(e) => setProfile({ ...profile, whatsapp_number: e.target.value })}
                    required={profile.whatsapp_opt_in}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-[#24120B] text-base sm:text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                  <span className="text-[11px] text-[#24120B]/60 mt-1 block">Include country code (e.g. +91 for India, +1 for USA)</span>
                </div>

                <div>
                  <label htmlFor="profile-whatsapp-time" className="block text-xs font-semibold uppercase tracking-wider text-[#7A1612] mb-1.5 cursor-pointer">
                    Delivery Time
                  </label>
                  <select
                    id="profile-whatsapp-time"
                    value={profile.whatsapp_time || '07:00'}
                    onChange={(e) => setProfile({ ...profile, whatsapp_time: e.target.value })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#C5A059]/40 bg-white text-[#24120B] text-base sm:text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  >
                    <option value="06:00">6:00 AM (Early Morning)</option>
                    <option value="06:30">6:30 AM</option>
                    <option value="07:00">7:00 AM (Recommended)</option>
                    <option value="07:30">7:30 AM</option>
                    <option value="08:00">8:00 AM</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-[#7A1612] mb-1.5">
                  Briefing Language
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { code: 'en', label: 'English' },
                    { code: 'hi', label: 'हिन्दी (Hindi)' },
                    { code: 'mr', label: 'मराठी (Marathi)' },
                  ].map((l) => (
                    <label
                      key={l.code}
                      className={`p-3 rounded-xl border text-center cursor-pointer transition-all ${
                        (profile.whatsapp_language || 'en') === l.code
                          ? 'border-[#7A1612] bg-[#F5EFE6] text-[#7A1612] font-bold'
                          : 'border-[#C5A059]/30 bg-white text-[#24120B]/80'
                      }`}
                    >
                      <input
                        type="radio"
                        name="whatsapp_language"
                        value={l.code}
                        checked={(profile.whatsapp_language || 'en') === l.code}
                        onChange={(e) => setProfile({ ...profile, whatsapp_language: e.target.value })}
                        className="sr-only"
                      />
                      <span className="text-xs">{l.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="px-6 py-2.5 rounded-xl bg-emerald-700 text-white font-semibold text-xs uppercase tracking-wider hover:bg-emerald-800 shadow-md transition-all cursor-pointer disabled:opacity-50"
                >
                  {saving ? 'Saving Preferences...' : 'Save WhatsApp Preferences'}
                </button>
              </div>
            </form>
          </div>

          {/* Interactive Live Preview of Morning Message */}
          <div className="space-y-4">
            <h3 className="font-serif font-bold text-sm text-[#7A1612] uppercase tracking-wider">
              Sample Morning Message Preview
            </h3>
            <div className="bg-[#E7F3E9] p-4 rounded-2xl border border-emerald-200 shadow-inner font-sans text-xs text-[#1F2937] space-y-2.5 leading-relaxed">
              <div className="font-bold text-emerald-900">
                🌟 Good morning, {profile.name}! Your Personal Astrological Forecast:
              </div>
              <div className="space-y-1">
                <p className="font-semibold text-[#7A1612]">🗓️ PANCHANGA ({profile.birth_city || 'Pune'})</p>
                <p>• Tithi: Shukla Shashthi · Auspicious</p>
                <p>• Nakshatra: Uttara Ashadha (Focused)</p>
                <p>• Rahu Kaal: 10:44 AM – 12:08 PM ⚠️</p>
                <p>• Abhijit Muhurta: 11:47 AM – 12:33 PM ✨</p>
              </div>
              <div className="space-y-1">
                <p className="font-semibold text-[#7A1612]">🌕 YOUR PERSONAL TRANSIT</p>
                <p>• Chandrabala: 11th from your {badges?.moon_sign || 'Moon'} (Favorable for gains)</p>
                <p>• Tara Bala: Sadhaka Tara (Success-yielding)</p>
              </div>
              <div className="p-2.5 rounded-xl bg-white/80 border border-emerald-200 text-emerald-950 font-medium italic">
                💡 &quot;Channel key discussions before 10:30 AM. Hold off on contract signings during Rahu Kaal.&quot;
              </div>
              <div className="flex gap-2 pt-1 text-[11px] font-semibold text-emerald-800">
                <span className="px-2 py-1 bg-white rounded-md border border-emerald-200">[ 📊 View Chart ]</span>
                <span className="px-2 py-1 bg-white rounded-md border border-emerald-200">[ ❓ Ask Copilot ]</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Account & Security */}
      {activeTab === 'account' && profile && (
        <div className="bg-[#FAF6F0] rounded-2xl p-6 sm:p-8 border border-[#C5A059]/30 shadow-sm max-w-2xl space-y-6">
          <div>
            <h2 className="font-serif text-xl font-bold text-[#7A1612]">Account & Security</h2>
            <p className="text-xs text-[#24120B]/70 mt-1">Manage your credentials, login status, and data export.</p>
          </div>

          <div className="space-y-4 text-xs">
            <div className="p-4 rounded-xl bg-white border border-[#C5A059]/20 flex justify-between items-center">
              <div>
                <span className="font-semibold text-[#24120B] block">Email Address</span>
                <span className="text-[#24120B]/60">{profile.email}</span>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 font-mono text-[10px] uppercase font-bold">
                Verified
              </span>
            </div>

            <div className="p-4 rounded-xl bg-white border border-[#C5A059]/20 flex justify-between items-center">
              <div>
                <span className="font-semibold text-[#24120B] block">Membership Tier</span>
                <span className="text-[#24120B]/60">AstroLogic Free Explorer</span>
              </div>
              <button
                type="button"
                className="px-3 py-1.5 rounded-lg bg-[#C5A059] text-[#24120B] font-bold text-xs uppercase cursor-pointer hover:brightness-105"
              >
                Upgrade to Pro
              </button>
            </div>

            <div className="p-4 rounded-xl bg-white border border-[#C5A059]/20 flex justify-between items-center">
              <div>
                <label htmlFor="profile-preferred-lang" className="font-semibold text-[#24120B] block cursor-pointer">Preferred Language</label>
                <span className="text-[#24120B]/60">Default language for calculations and narrative</span>
              </div>
              <select
                id="profile-preferred-lang"
                value={profile.preferred_language || 'en'}
                onChange={(e) => setProfile({ ...profile, preferred_language: e.target.value })}
                className="px-3 py-2 rounded-lg border border-[#C5A059]/40 bg-white text-base sm:text-xs font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
              >
                <option value="en">English</option>
                <option value="hi">हिन्दी</option>
                <option value="mr">मराठी</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

