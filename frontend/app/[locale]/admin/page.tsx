'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Activity,
  Users,
  Compass,
  Sparkles,
  ShieldCheck,
  RefreshCw,
  Clock,
  ArrowUpRight,
  TrendingUp,
  MessageCircle,
  Database,
  Cpu,
  Layers,
  ChevronRight,
  Search,
  CheckCircle2,
  AlertCircle,
  DollarSign,
  Radio,
  Send,
  Zap,
  BookOpen,
  Plus,
  Edit3,
  Trash2,
  ExternalLink,
  X,
  FileText,
} from 'lucide-react';

interface AdminMetrics {
  kpis: {
    total_users: number;
    new_users_24h: number;
    conversion_rate_pct: number;
    ghost_recovery_rate_pct: number;
    total_guest_sessions: number;
    claimed_guest_sessions: number;
    active_unclaimed_ghosts: number;
    whatsapp_subscribers: number;
    total_saved_charts: number;
  };
  identity_breakdown: {
    google_fedcm: number;
    whatsapp_otp: number;
    email_password: number;
  };
  monetization_overview: {
    domestic_inr_pipeline: number;
    global_usd_pipeline: number;
    currency_distribution: { INR_pct: number; USD_pct: number };
  };
  system_health: {
    ephemeris_mode: string;
    ephemeris_accuracy: string;
    cache_hits: number;
    cache_misses: number;
    cache_hit_ratio_pct: number;
  };
}

interface UserItem {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  auth_provider: string;
  preferred_language: string;
  created_at: string;
  birth_city: string | null;
  birth_date: string | null;
  whatsapp_opt_in: boolean;
  whatsapp_number: string | null;
  saved_charts_count: number;
}

interface GhostSessionItem {
  id: number;
  device_fingerprint: string;
  session_token: string;
  chart_type: string;
  person_name: string;
  birth_date: string;
  birth_time: string;
  birth_place: string;
  is_claimed: boolean;
  claimed_by_user_id: number | null;
  created_at: string;
}

interface BlogItem {
  id: number;
  title: string;
  slug: string;
  content: string;
  summary: string | null;
  language: string;
  tags: string[] | null;
  author: string | null;
  created_at: string;
}

export default function AdminObservatoryPage() {
  const [activeTab, setActiveTab] = useState<'funnel' | 'users' | 'ghosts' | 'monetization' | 'system' | 'blogs'>('funnel');
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [users, setUsers] = useState<UserItem[]>([]);
  const [ghostSessions, setGhostSessions] = useState<GhostSessionItem[]>([]);
  const [blogs, setBlogs] = useState<BlogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [executingAction, setExecutingAction] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Blog CMS State
  const [blogLangFilter, setBlogLangFilter] = useState<'all' | 'en' | 'hi' | 'mr'>('all');
  const [isBlogModalOpen, setIsBlogModalOpen] = useState(false);
  const [editingBlogId, setEditingBlogId] = useState<number | null>(null);
  const [blogTitle, setBlogTitle] = useState('');
  const [blogSlug, setBlogSlug] = useState('');
  const [blogLanguage, setBlogLanguage] = useState<'en' | 'hi' | 'mr'>('en');
  const [blogAuthor, setBlogAuthor] = useState('Acharya Shastri');
  const [blogTags, setBlogTags] = useState('Vedic Astrology, Navagrahas, Gochar');
  const [blogSummary, setBlogSummary] = useState('');
  const [blogContent, setBlogContent] = useState('');
  const [savingBlog, setSavingBlog] = useState(false);

  const fetchBlogs = async () => {
    try {
      const res = await fetch('/api/admin/blogs?limit=100');
      if (res.ok) {
        const data = await res.json();
        setBlogs(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error('Failed to fetch blogs', err);
    }
  };

  const fetchAllData = async () => {
    try {
      const [mRes, uRes, gRes, bRes] = await Promise.all([
        fetch('/api/admin/metrics'),
        fetch('/api/admin/users?limit=50'),
        fetch('/api/admin/ghost-sessions?limit=50'),
        fetch('/api/admin/blogs?limit=100'),
      ]);

      if (mRes.ok) {
        const mData = await mRes.json();
        setMetrics(mData);
      }
      if (uRes.ok) {
        const uData = await uRes.json();
        setUsers(uData.users || []);
      }
      if (gRes.ok) {
        const gData = await gRes.json();
        setGhostSessions(gData.sessions || []);
      }
      if (bRes.ok) {
        const bData = await bRes.json();
        setBlogs(Array.isArray(bData) ? bData : []);
      }
    } catch (err) {
      console.error('Failed to load observatory data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 15000); // 15s auto-refresh
    return () => clearInterval(interval);
  }, []);

  const handleTriggerWhatsApp = async (dryRun: boolean) => {
    setExecutingAction(true);
    setActionMessage(null);
    try {
      const res = await fetch(`/api/admin/trigger-whatsapp?dry_run=${dryRun}`, { method: 'POST' });
      const data = await res.json();
      setActionMessage(data.message || 'WhatsApp pipeline executed successfully.');
      fetchAllData();
    } catch (e: any) {
      setActionMessage('Failed to trigger WhatsApp transit worker: ' + e?.message);
    } finally {
      setExecutingAction(false);
      setTimeout(() => setActionMessage(null), 6000);
    }
  };

  const handleFlushCache = async () => {
    setExecutingAction(true);
    setActionMessage(null);
    try {
      const res = await fetch('/api/admin/flush-cache', { method: 'POST' });
      const data = await res.json();
      setActionMessage(data.message || 'Cache flushed.');
      fetchAllData();
    } catch (e: any) {
      setActionMessage('Failed to flush cache: ' + e?.message);
    } finally {
      setExecutingAction(false);
      setTimeout(() => setActionMessage(null), 6000);
    }
  };

  // Blog CRUD Handlers
  const handleOpenCreateBlog = () => {
    setEditingBlogId(null);
    setBlogTitle('');
    setBlogSlug('');
    setBlogLanguage('en');
    setBlogAuthor('Acharya Shastri');
    setBlogTags('Vedic Astrology, Navagrahas, Gochar');
    setBlogSummary('');
    setBlogContent('');
    setIsBlogModalOpen(true);
  };

  const handleOpenEditBlog = (b: BlogItem) => {
    setEditingBlogId(b.id);
    setBlogTitle(b.title);
    setBlogSlug(b.slug);
    setBlogLanguage((['en', 'hi', 'mr'].includes(b.language) ? b.language : 'en') as any);
    setBlogAuthor(b.author || 'Acharya Shastri');
    setBlogTags(Array.isArray(b.tags) ? b.tags.join(', ') : '');
    setBlogSummary(b.summary || '');
    setBlogContent(b.content || '');
    setIsBlogModalOpen(true);
  };

  const handleTitleChange = (val: string) => {
    setBlogTitle(val);
    if (!editingBlogId) {
      const autoSlug = val
        .toLowerCase()
        .replace(/[^a-z0-9\u0900-\u097F]+/g, '-')
        .replace(/^-+|-+$/g, '');
      setBlogSlug(autoSlug);
    }
  };

  const handleSaveBlog = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!blogTitle.trim() || !blogContent.trim()) {
      alert('Please fill out both the title and content.');
      return;
    }

    setSavingBlog(true);
    const parsedTags = blogTags
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);

    const payload = {
      title: blogTitle.trim(),
      slug: blogSlug.trim() || undefined,
      language: blogLanguage,
      author: blogAuthor.trim() || 'Acharya Shastri',
      tags: parsedTags,
      summary: blogSummary.trim() || undefined,
      content: blogContent.trim(),
    };

    try {
      let res: Response;
      if (editingBlogId) {
        res = await fetch(`/api/admin/blogs/${editingBlogId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } else {
        res = await fetch('/api/admin/blogs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      }

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to save blog post');
      }

      setIsBlogModalOpen(false);
      setActionMessage(editingBlogId ? 'Blog post updated successfully!' : 'New blog post published successfully!');
      fetchBlogs();
      setTimeout(() => setActionMessage(null), 5000);
    } catch (err: any) {
      alert('Error saving blog: ' + err.message);
    } finally {
      setSavingBlog(false);
    }
  };

  const handleDeleteBlog = async (id: number, title: string) => {
    if (!window.confirm(`Are you sure you want to delete "${title}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const res = await fetch(`/api/admin/blogs/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Deletion failed on server');
      setActionMessage(`Blog post "${title}" deleted.`);
      fetchBlogs();
      setTimeout(() => setActionMessage(null), 4000);
    } catch (err: any) {
      alert('Failed to delete blog: ' + err.message);
    }
  };

  const filteredUsers = users.filter((u) => {
    const q = searchQuery.toLowerCase();
    return (
      (u.name && u.name.toLowerCase().includes(q)) ||
      (u.email && u.email.toLowerCase().includes(q)) ||
      (u.phone && u.phone.includes(q)) ||
      (u.auth_provider && u.auth_provider.toLowerCase().includes(q))
    );
  });

  const filteredBlogs = blogs.filter((b) => {
    if (blogLangFilter !== 'all' && b.language !== blogLangFilter) return false;
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      (b.title && b.title.toLowerCase().includes(q)) ||
      (b.slug && b.slug.toLowerCase().includes(q)) ||
      (b.author && b.author.toLowerCase().includes(q))
    );
  });

  return (
    <div className="pt-6 sm:pt-10 pb-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      {/* ── Header & Live Controls ── */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-6 border-b border-[#EADBC8]">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#7A1612]/10 border border-[#7A1612]/20 text-[#7A1612] text-xs font-semibold uppercase tracking-wider mb-2">
            <Radio className="w-3.5 h-3.5 text-[#7A1612] animate-pulse" />
            <span>Cosmic Observatory & Governance</span>
          </div>
          <h1 className="font-serif text-3xl sm:text-4xl font-bold text-[#24120B]">
            System Observatory & Administration
          </h1>
          <p className="text-xs sm:text-sm text-[#24120B]/70 mt-1">
            Real-time monitoring of 42-parameter client telemetry, 90%+ identity funnel, blog CMS, and Swiss Ephemeris engine.
          </p>
        </div>

        {/* Global Action Buttons */}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => handleTriggerWhatsApp(true)}
            disabled={executingAction}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-[#25D366]/15 hover:bg-[#25D366]/25 text-[#128C7E] border border-[#25D366]/30 transition-all cursor-pointer disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Test WhatsApp (Dry-Run)</span>
          </button>

          <button
            onClick={handleFlushCache}
            disabled={executingAction}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-[#7A1612]/10 hover:bg-[#7A1612]/20 text-[#7A1612] border border-[#7A1612]/20 transition-all cursor-pointer disabled:opacity-50"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>Flush Ephemeris Cache</span>
          </button>

          <button
            onClick={fetchAllData}
            aria-label="Refresh metrics"
            className="p-2 rounded-xl bg-white text-[#24120B] border border-[#EADBC8] hover:bg-[#FAF6F0] transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Notification Toast */}
      {actionMessage && (
        <div className="p-3.5 rounded-xl bg-[#C5A059]/20 border border-[#C5A059]/40 text-[#24120B] text-xs font-medium flex items-center justify-between animate-fadeIn">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#7A1612]" />
            <span>{actionMessage}</span>
          </div>
          <button onClick={() => setActionMessage(null)} className="text-xs font-bold text-[#7A1612] hover:underline cursor-pointer">
            Dismiss
          </button>
        </div>
      )}

      {/* ── KPI Grid (4 High-Impact Scorecards) ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {/* Card 1: Conversion Funnel Rate */}
        <div className="bg-white p-5 rounded-2xl border border-[#EADBC8] shadow-xs relative overflow-hidden">
          <div className="flex items-center justify-between text-xs text-[#24120B]/60 font-semibold uppercase tracking-wider">
            <span>Visitor Conversion Rate</span>
            <TrendingUp className="w-4 h-4 text-[#15803D]" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="font-serif text-3xl sm:text-4xl font-bold text-[#15803D]">
              {metrics ? `${metrics.kpis.conversion_rate_pct}%` : '...'}
            </span>
            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-[#15803D]/10 text-[#15803D]">
              Target: 90%+
            </span>
          </div>
          <p className="text-[11px] text-[#24120B]/60 mt-1">
            {metrics ? `${metrics.kpis.claimed_guest_sessions} charts claimed to Vault` : 'Computing funnel...'}
          </p>
          <div className="w-full bg-gray-100 h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-[#15803D] h-full rounded-full transition-all duration-700"
              style={{ width: `${metrics ? metrics.kpis.conversion_rate_pct : 0}%` }}
            />
          </div>
        </div>

        {/* Card 2: Total Registered Users */}
        <div className="bg-white p-5 rounded-2xl border border-[#EADBC8] shadow-xs">
          <div className="flex items-center justify-between text-xs text-[#24120B]/60 font-semibold uppercase tracking-wider">
            <span>Registered Users</span>
            <Users className="w-4 h-4 text-[#7A1612]" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="font-serif text-3xl sm:text-4xl font-bold text-[#7A1612]">
              {metrics ? metrics.kpis.total_users : '...'}
            </span>
            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-[#7A1612]/10 text-[#7A1612]">
              +{metrics ? metrics.kpis.new_users_24h : 0} today
            </span>
          </div>
          <p className="text-[11px] text-[#24120B]/60 mt-1">
            Google FedCM: {metrics?.identity_breakdown.google_fedcm || 0} • WhatsApp: {metrics?.identity_breakdown.whatsapp_otp || 0}
          </p>
        </div>

        {/* Card 3: Ghost Session Recovery */}
        <div className="bg-white p-5 rounded-2xl border border-[#EADBC8] shadow-xs">
          <div className="flex items-center justify-between text-xs text-[#24120B]/60 font-semibold uppercase tracking-wider">
            <span>Ghost Session Retargeting</span>
            <Clock className="w-4 h-4 text-[#C5A059]" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="font-serif text-3xl sm:text-4xl font-bold text-[#24120B]">
              {metrics ? `${metrics.kpis.ghost_recovery_rate_pct}%` : '...'}
            </span>
            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-[#C5A059]/20 text-[#7A1612]">
              Zero-Cookie
            </span>
          </div>
          <p className="text-[11px] text-[#24120B]/60 mt-1">
            {metrics ? `${metrics.kpis.active_unclaimed_ghosts} active in 30-day recovery pool` : 'Loading...'}
          </p>
        </div>

        {/* Card 4: WhatsApp Daily Transit Reach */}
        <div className="bg-white p-5 rounded-2xl border border-[#EADBC8] shadow-xs">
          <div className="flex items-center justify-between text-xs text-[#24120B]/60 font-semibold uppercase tracking-wider">
            <span>WhatsApp Transit Reach</span>
            <MessageCircle className="w-4 h-4 text-[#25D366]" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="font-serif text-3xl sm:text-4xl font-bold text-[#128C7E]">
              {metrics ? metrics.kpis.whatsapp_subscribers : '...'}
            </span>
            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-[#25D366]/15 text-[#128C7E]">
              7:00 AM Daily
            </span>
          </div>
          <p className="text-[11px] text-[#24120B]/60 mt-1">
            Opted-in with derived Tara &amp; Chandra Bala
          </p>
        </div>
      </div>

      {/* ── Interactive Tab Navigation ── */}
      <div className="flex items-center gap-2 border-b border-[#EADBC8] overflow-x-auto pb-1">
        {[
          { key: 'funnel', label: 'Conversion Funnel', icon: TrendingUp },
          { key: 'blogs', label: `Blog CMS (${blogs.length})`, icon: BookOpen },
          { key: 'users', label: `Users Directory (${users.length})`, icon: Users },
          { key: 'ghosts', label: `Ghost Recovery (${ghostSessions.length})`, icon: Clock },
          { key: 'monetization', label: 'Monetization & PPP', icon: DollarSign },
          { key: 'system', label: 'Ephemeris & Health', icon: Cpu },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-t-xl text-xs sm:text-sm font-semibold transition-all whitespace-nowrap cursor-pointer ${
                isActive
                  ? 'bg-white text-[#7A1612] border-t-2 border-t-[#7A1612] border-x border-[#EADBC8] shadow-xs'
                  : 'text-[#24120B]/70 hover:text-[#7A1612] hover:bg-[#FAF6F0]'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-[#7A1612]' : 'text-[#24120B]/50'}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* ── TAB: BLOG CMS & ARTICLE MANAGEMENT ── */}
      {activeTab === 'blogs' && (
        <div className="bg-white rounded-2xl border border-[#EADBC8] shadow-xs overflow-hidden space-y-4 p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="font-serif text-lg font-bold text-[#24120B]">
                Vedic Blog & Astrology Articles Management ({blogs.length})
              </h3>
              <p className="text-xs text-[#24120B]/60">
                Publish, edit, and translate astrological treatise, transit advisories, and remedial wisdom.
              </p>
            </div>

            <button
              onClick={handleOpenCreateBlog}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-[#7A1612] to-[#9E2A2B] text-white shadow-sm hover:shadow-md transition-all cursor-pointer self-start sm:self-auto"
            >
              <Plus className="w-4 h-4" />
              <span>Write New Article</span>
            </button>
          </div>

          {/* Language Filter Pills & Search */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1 border-t border-[#EADBC8]/60">
            <div className="flex items-center gap-1.5 overflow-x-auto py-1">
              {[
                { id: 'all', label: 'All Languages' },
                { id: 'en', label: 'English (EN)' },
                { id: 'hi', label: 'Hindi (HI)' },
                { id: 'mr', label: 'Marathi (MR)' },
              ].map((lang) => (
                <button
                  key={lang.id}
                  onClick={() => setBlogLangFilter(lang.id as any)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                    blogLangFilter === lang.id
                      ? 'bg-[#7A1612] text-white'
                      : 'bg-[#FAF6F0] text-[#24120B]/70 hover:bg-[#EADBC8]'
                  }`}
                >
                  {lang.label}
                </button>
              ))}
            </div>

            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-[#24120B]/40" />
              <input
                id="admin-search-blogs"
                aria-label="Search blog title or slug"
                type="text"
                placeholder="Search blog title or slug..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-xl border border-[#EADBC8] text-xs focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612] focus-visible:border-[#7A1612]"
              />
            </div>
          </div>

          {/* Blogs Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#FAF6F0] text-[#24120B]/60 uppercase tracking-wider font-semibold border-b border-[#EADBC8]">
                <tr>
                  <th className="py-3 px-3">Title &amp; Slug</th>
                  <th className="py-3 px-3">Language</th>
                  <th className="py-3 px-3">Author</th>
                  <th className="py-3 px-3">Tags</th>
                  <th className="py-3 px-3">Published</th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#EADBC8]/40">
                {filteredBlogs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-[#24120B]/50">
                      No blog posts found matching criteria. Click &quot;Write New Article&quot; to publish your first post!
                    </td>
                  </tr>
                ) : (
                  filteredBlogs.map((b) => (
                    <tr key={b.id} className="hover:bg-[#FAF6F0]/50 transition-colors">
                      <td className="py-3 px-3">
                        <div className="font-bold text-[#24120B] text-sm">{b.title}</div>
                        <div className="flex items-center gap-1.5 mt-0.5 text-[11px] text-[#7A1612]">
                          <span>/{b.slug}</span>
                          <Link
                            href={`/blogs/${b.slug}`}
                            target="_blank"
                            className="inline-flex items-center text-gray-400 hover:text-[#7A1612]"
                          >
                            <ExternalLink className="w-3 h-3" />
                          </Link>
                        </div>
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`inline-block px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                            b.language === 'en'
                              ? 'bg-blue-100 text-blue-800'
                              : b.language === 'hi'
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-emerald-100 text-emerald-800'
                          }`}
                        >
                          {b.language.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-medium text-[#24120B]">{b.author || 'Astro AI'}</td>
                      <td className="py-3 px-3">
                        <div className="flex flex-wrap gap-1 max-w-xs">
                          {Array.isArray(b.tags) && b.tags.length > 0 ? (
                            b.tags.slice(0, 3).map((t, idx) => (
                              <span
                                key={idx}
                                className="px-1.5 py-0.5 rounded bg-gray-100 text-gray-700 text-[10px]"
                              >
                                #{t}
                              </span>
                            ))
                          ) : (
                            <span className="text-gray-400 text-[10px]">—</span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-3 text-[11px] text-[#24120B]/60">
                        {b.created_at ? b.created_at.split('T')[0] : '—'}
                      </td>
                      <td className="py-3 px-3 text-right">
                        <div className="inline-flex items-center gap-1.5">
                          <button
                            onClick={() => handleOpenEditBlog(b)}
                            className="p-1.5 rounded-lg text-blue-600 hover:bg-blue-50 transition-colors cursor-pointer"
                            title="Edit Article"
                          >
                            <Edit3 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteBlog(b.id, b.title)}
                            className="p-1.5 rounded-lg text-red-600 hover:bg-red-50 transition-colors cursor-pointer"
                            title="Delete Article"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── BLOG EDITOR MODAL (CREATE / EDIT) ── */}
      {isBlogModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-fadeIn">
          <div className="bg-[#FAF6F0] rounded-2xl border border-[#C5A059]/40 shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6 sm:p-8 space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-[#EADBC8]">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-[#7A1612]/10 border border-[#7A1612]/20 flex items-center justify-center text-[#7A1612]">
                  <FileText className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-serif text-xl font-bold text-[#24120B]">
                    {editingBlogId ? 'Edit Astrological Article' : 'Publish New Vedic Article'}
                  </h3>
                  <p className="text-xs text-[#24120B]/60">
                    {editingBlogId ? `Updating Article ID #${editingBlogId}` : 'Compose wisdom for AstroLogic seekers'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsBlogModalOpen(false)}
                className="p-1.5 rounded-lg text-gray-500 hover:bg-gray-200 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveBlog} className="space-y-4 text-xs">
              {/* Title & Slug */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label htmlFor="blog-modal-title" className="font-semibold text-[#24120B] cursor-pointer">Article Title *</label>
                  <input
                    id="blog-modal-title"
                    type="text"
                    required
                    placeholder="e.g. Navagrahas & Career Impact"
                    value={blogTitle}
                    onChange={(e) => handleTitleChange(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-white border border-[#EADBC8] text-xs focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                </div>

                <div className="space-y-1">
                  <label htmlFor="blog-modal-slug" className="font-semibold text-[#24120B] cursor-pointer">URL Slug (Auto-generated)</label>
                  <input
                    id="blog-modal-slug"
                    type="text"
                    placeholder="e.g. navagrahas-career-impact"
                    value={blogSlug}
                    onChange={(e) => setBlogSlug(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-white border border-[#EADBC8] text-xs font-mono focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                </div>
              </div>

              {/* Language, Author, Tags */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="space-y-1">
                  <label htmlFor="blog-modal-lang" className="font-semibold text-[#24120B] cursor-pointer">Language</label>
                  <select
                    id="blog-modal-lang"
                    value={blogLanguage}
                    onChange={(e) => setBlogLanguage(e.target.value as any)}
                    className="w-full px-3 py-2 rounded-xl bg-white border border-[#EADBC8] text-xs focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  >
                    <option value="en">English (en)</option>
                    <option value="hi">Hindi (hi)</option>
                    <option value="mr">Marathi (mr)</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label htmlFor="blog-modal-author" className="font-semibold text-[#24120B] cursor-pointer">Author</label>
                  <input
                    id="blog-modal-author"
                    type="text"
                    placeholder="Author name"
                    value={blogAuthor}
                    onChange={(e) => setBlogAuthor(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-white border border-[#EADBC8] text-xs focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                </div>

                <div className="space-y-1">
                  <label htmlFor="blog-modal-tags" className="font-semibold text-[#24120B] cursor-pointer">Tags (comma separated)</label>
                  <input
                    id="blog-modal-tags"
                    type="text"
                    placeholder="Navagraha, Dasha, Remedies"
                    value={blogTags}
                    onChange={(e) => setBlogTags(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-white border border-[#EADBC8] text-xs focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                  />
                </div>
              </div>

              {/* Summary */}
              <div className="space-y-1">
                <label htmlFor="blog-modal-summary" className="font-semibold text-[#24120B] cursor-pointer">Short Summary (SEO / Social Preview)</label>
                <textarea
                  id="blog-modal-summary"
                  rows={2}
                  placeholder="A concise synopsis of the article for search results and social previews..."
                  value={blogSummary}
                  onChange={(e) => setBlogSummary(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white border border-[#EADBC8] text-xs focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                />
              </div>

              {/* Content */}
              <div className="space-y-1">
                <label htmlFor="blog-modal-content" className="font-semibold text-[#24120B] cursor-pointer">Article Content (Markdown supported) *</label>
                <textarea
                  id="blog-modal-content"
                  rows={10}
                  required
                  placeholder="Write the full astrological treatise here. Markdown headings (##), bold text (**text**), and lists are supported..."
                  value={blogContent}
                  onChange={(e) => setBlogContent(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl bg-white border border-[#EADBC8] text-xs font-mono leading-relaxed focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612]"
                />
              </div>

              {/* Actions */}
              <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#EADBC8]">
                <button
                  type="button"
                  onClick={() => setIsBlogModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingBlog}
                  className="inline-flex items-center gap-1.5 px-5 py-2 rounded-xl text-xs font-bold bg-[#7A1612] hover:bg-[#9E2A2B] text-white shadow-sm transition-all cursor-pointer disabled:opacity-50"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>{savingBlog ? 'Saving...' : editingBlogId ? 'Save Changes' : 'Publish Article'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── TAB 1: CONVERSION FUNNEL & BEHAVIORAL ARCHITECTURE ── */}
      {activeTab === 'funnel' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-[#EADBC8] shadow-xs space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h3 className="font-serif text-lg font-bold text-[#24120B]">
                  Behavioral Conversion Architecture (MAP Funnel)
                </h3>
                <p className="text-xs text-[#24120B]/70">
                  Visitor journey from 42-parameter detection to zero-data-loss permanent vault promotion.
                </p>
              </div>
              <span className="text-xs font-semibold px-3 py-1 rounded-full bg-[#15803D]/10 text-[#15803D] self-start sm:self-auto">
                Conversion: {metrics?.kpis.conversion_rate_pct}%
              </span>
            </div>

            {/* Visual Funnel Steps */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-[#FAF6F0] border border-[#EADBC8]/60 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#7A1612]">Step 1: Arrival</span>
                  <Radio className="w-4 h-4 text-[#7A1612]" />
                </div>
                <div className="font-serif text-2xl font-bold text-[#24120B]">
                  {metrics ? metrics.kpis.total_guest_sessions + metrics.kpis.total_users : '...'}
                </div>
                <p className="text-[11px] text-[#24120B]/70">
                  42 telemetry signals harvested in &lt;1ms. Birth coordinates auto-prefilled.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-[#FAF6F0] border border-[#EADBC8]/60 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#C5A059]">Step 2: Value Peak</span>
                  <Compass className="w-4 h-4 text-[#C5A059]" />
                </div>
                <div className="font-serif text-2xl font-bold text-[#24120B]">
                  {metrics ? metrics.kpis.total_guest_sessions : '...'}
                </div>
                <p className="text-[11px] text-[#24120B]/70">
                  Chart calculated for free. Zero upfront wall. 45s sunk cost investment achieved.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-[#FAF6F0] border border-[#EADBC8]/60 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#128C7E]">Step 3: 1-Tap Auth</span>
                  <Zap className="w-4 h-4 text-[#128C7E]" />
                </div>
                <div className="font-serif text-2xl font-bold text-[#24120B]">
                  {metrics ? metrics.kpis.claimed_guest_sessions : '...'}
                </div>
                <p className="text-[11px] text-[#24120B]/70">
                  Curiosity Teaser + 1-Tap Google FedCM or WhatsApp OTP triggered in-place.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-[#15803D]/5 border border-[#15803D]/20 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#15803D]">Step 4: Vault Saved</span>
                  <ShieldCheck className="w-4 h-4 text-[#15803D]" />
                </div>
                <div className="font-serif text-2xl font-bold text-[#15803D]">
                  {metrics ? metrics.kpis.total_saved_charts : '...'}
                </div>
                <p className="text-[11px] text-[#15803D]/80">
                  Zero data loss. Guest chart permanently preserved. Conversion complete!
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 2: USERS DIRECTORY ── */}
      {activeTab === 'users' && (
        <div className="bg-white rounded-2xl border border-[#EADBC8] shadow-xs overflow-hidden space-y-4 p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <h3 className="font-serif text-lg font-bold text-[#24120B]">
              Registered Cosmic Vault Users ({users.length})
            </h3>
            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-[#24120B]/40" />
              <input
                id="admin-search-users"
                aria-label="Search name, phone, or email"
                type="text"
                placeholder="Search name, phone, email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-xl border border-[#EADBC8] text-xs focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7A1612] focus-visible:border-[#7A1612]"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#FAF6F0] text-[#24120B]/60 uppercase tracking-wider font-semibold border-b border-[#EADBC8]">
                <tr>
                  <th className="py-3 px-3">User</th>
                  <th className="py-3 px-3">Auth Provider</th>
                  <th className="py-3 px-3">Birth Origin</th>
                  <th className="py-3 px-3">WhatsApp Daily</th>
                  <th className="py-3 px-3">Vault Charts</th>
                  <th className="py-3 px-3">Joined</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#EADBC8]/40">
                {filteredUsers.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-6 text-center text-[#24120B]/50">
                      No matching registered users found.
                    </td>
                  </tr>
                ) : (
                  filteredUsers.map((u) => (
                    <tr key={u.id} className="hover:bg-[#FAF6F0]/50 transition-colors">
                      <td className="py-3 px-3">
                        <div className="font-bold text-[#24120B]">{u.name}</div>
                        <div className="text-[11px] text-[#24120B]/60">{u.email || u.phone || `ID: ${u.id}`}</div>
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider ${
                            u.auth_provider === 'google'
                              ? 'bg-blue-100 text-blue-700'
                              : u.auth_provider === 'whatsapp'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-amber-100 text-amber-700'
                          }`}
                        >
                          {u.auth_provider}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <div className="font-medium text-[#24120B]">{u.birth_city || '—'}</div>
                        <div className="text-[10px] text-[#24120B]/50">{u.birth_date || '—'}</div>
                      </td>
                      <td className="py-3 px-3">
                        {u.whatsapp_opt_in ? (
                          <span className="inline-flex items-center gap-1 text-[11px] text-[#128C7E] font-medium">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Opted In ({u.whatsapp_number ? u.whatsapp_number.slice(-4) : 'Active'})</span>
                          </span>
                        ) : (
                          <span className="text-[11px] text-gray-400">Off</span>
                        )}
                      </td>
                      <td className="py-3 px-3 font-semibold text-[#7A1612]">{u.saved_charts_count}</td>
                      <td className="py-3 px-3 text-[11px] text-[#24120B]/60">
                        {u.created_at ? u.created_at.split('T')[0] : '—'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── TAB 3: GHOST RECOVERY SESSIONS ── */}
      {activeTab === 'ghosts' && (
        <div className="bg-white rounded-2xl border border-[#EADBC8] shadow-xs overflow-hidden space-y-4 p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="font-serif text-lg font-bold text-[#24120B]">
                Guest Sessions &amp; Zero-Cookie Recovery Pool ({ghostSessions.length})
              </h3>
              <p className="text-xs text-[#24120B]/60">
                Calculations preserved against 42-parameter device fingerprints with 30-day automated TTL.
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#FAF6F0] text-[#24120B]/60 uppercase tracking-wider font-semibold border-b border-[#EADBC8]">
                <tr>
                  <th className="py-3 px-3">Native Name</th>
                  <th className="py-3 px-3">Birth Coordinates</th>
                  <th className="py-3 px-3">Device Fingerprint</th>
                  <th className="py-3 px-3">Chart Type</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3">Cached On</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#EADBC8]/40">
                {ghostSessions.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-6 text-center text-[#24120B]/50">
                      No guest sessions recorded yet.
                    </td>
                  </tr>
                ) : (
                  ghostSessions.map((s) => (
                    <tr key={s.id} className="hover:bg-[#FAF6F0]/50 transition-colors">
                      <td className="py-3 px-3 font-bold text-[#24120B]">{s.person_name}</td>
                      <td className="py-3 px-3">
                        <div>{s.birth_place}</div>
                        <div className="text-[10px] text-[#24120B]/50">
                          {s.birth_date} at {s.birth_time}
                        </div>
                      </td>
                      <td className="py-3 px-3 font-mono text-[11px] text-gray-500">
                        {s.device_fingerprint ? s.device_fingerprint.slice(0, 16) + '...' : '—'}
                      </td>
                      <td className="py-3 px-3 capitalize font-medium">{s.chart_type}</td>
                      <td className="py-3 px-3">
                        {s.is_claimed ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-100 text-green-800 text-[10px] font-semibold">
                            <CheckCircle2 className="w-3 h-3" />
                            Claimed (User #{s.claimed_by_user_id})
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-[10px] font-semibold">
                            <Clock className="w-3 h-3" />
                            Ready for Recovery
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-3 text-[11px] text-[#24120B]/60">
                        {s.created_at ? s.created_at.split('T')[0] : '—'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── TAB 4: MONETIZATION & PPP ANALYTICS ── */}
      {activeTab === 'monetization' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-[#EADBC8] shadow-xs space-y-4">
            <h3 className="font-serif text-lg font-bold text-[#24120B] flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-[#C5A059]" />
              <span>Purchasing Power Parity (PPP) Breakdown</span>
            </h3>
            <p className="text-xs text-[#24120B]/70 leading-relaxed">
              Dynamically tailors currency and pricing to optimize price elasticity ($E_d$).
            </p>

            <div className="space-y-3 pt-2">
              <div className="p-4 rounded-xl bg-[#FAF6F0] border border-[#EADBC8] flex items-center justify-between">
                <div>
                  <div className="font-bold text-sm text-[#24120B]">Domestic (India ₹)</div>
                  <div className="text-xs text-[#24120B]/60">₹499 Gemstone Report • ₹1,499 VIP Pass</div>
                  <div className="text-[10px] text-[#128C7E] font-medium mt-1">Rails: UPI Intent, GPay, PhonePe</div>
                </div>
                <div className="text-right">
                  <div className="font-serif text-xl font-bold text-[#7A1612]">
                    ₹{metrics?.monetization_overview.domestic_inr_pipeline.toLocaleString() || 0}
                  </div>
                  <span className="text-[10px] font-semibold text-gray-500">82.5% Audience Share</span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-[#FAF6F0] border border-[#EADBC8] flex items-center justify-between">
                <div>
                  <div className="font-bold text-sm text-[#24120B]">Global (US/UK/EU $)</div>
                  <div className="text-xs text-[#24120B]/60">$19.99 Gemstone Report • $49.99 VIP Pass</div>
                  <div className="text-[10px] text-blue-700 font-medium mt-1">Rails: Apple Pay, Stripe, Cards</div>
                </div>
                <div className="text-right">
                  <div className="font-serif text-xl font-bold text-[#15803D]">
                    ${metrics?.monetization_overview.global_usd_pipeline.toFixed(2) || '0.00'}
                  </div>
                  <span className="text-[10px] font-semibold text-gray-500">17.5% Audience Share</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-[#EADBC8] shadow-xs space-y-4">
            <h3 className="font-serif text-lg font-bold text-[#24120B] flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-[#7A1612]" />
              <span>High-Net-Worth (HNW) Hardware Segmentation</span>
            </h3>
            <p className="text-xs text-[#24120B]/70 leading-relaxed">
              Telemetry detects Retina 3x+ screens &amp; Apple Silicon (M1–M4) or RTX GPUs to dynamically surface the ₹4,999 / $149 VIP Royal Consultation.
            </p>

            <div className="p-4 rounded-xl bg-[#7A1612]/5 border border-[#7A1612]/15 space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-[#7A1612]">
                <span>Royal Vedic Consultation Tier</span>
                <span>Active</span>
              </div>
              <p className="text-xs text-[#24120B]/80 leading-relaxed">
                Includes 1-on-1 private video consultation with senior Vedic scholar and consecrated Navagraha silver yantra dispatched to residence.
              </p>
              <div className="pt-2 flex items-center justify-between text-xs font-semibold text-[#24120B]">
                <span>Domestic Price: ₹4,999</span>
                <span>Global Price: $149.00</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 5: EPHEMERIS & SYSTEM HEALTH ── */}
      {activeTab === 'system' && (
        <div className="bg-white p-6 rounded-2xl border border-[#EADBC8] shadow-xs space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-serif text-lg font-bold text-[#24120B] flex items-center gap-2">
              <Cpu className="w-5 h-5 text-[#7A1612]" />
              <span>Swiss Ephemeris &amp; Cache Vitality</span>
            </h3>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-green-100 text-green-800">
              Operational
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-[#FAF6F0] border border-[#EADBC8]">
              <div className="text-xs font-semibold text-[#24120B]/60 uppercase">Ephemeris Engine Mode</div>
              <div className="font-serif text-xl font-bold text-[#7A1612] mt-1 capitalize">
                {metrics?.system_health.ephemeris_mode || 'Auto'}
              </div>
              <p className="text-[11px] text-[#24120B]/60 mt-0.5">Moshier/Swiss Ephemeris runtime</p>
            </div>

            <div className="p-4 rounded-xl bg-[#FAF6F0] border border-[#EADBC8]">
              <div className="text-xs font-semibold text-[#24120B]/60 uppercase">Chart Cache Hits / Misses</div>
              <div className="font-serif text-xl font-bold text-[#24120B] mt-1">
                {metrics?.system_health.cache_hits || 0} / {metrics?.system_health.cache_misses || 0}
              </div>
              <p className="text-[11px] text-[#24120B]/60 mt-0.5">LRU 30-Day TTL memory pool</p>
            </div>

            <div className="p-4 rounded-xl bg-[#FAF6F0] border border-[#EADBC8]">
              <div className="text-xs font-semibold text-[#24120B]/60 uppercase">Cache Hit Ratio</div>
              <div className="font-serif text-xl font-bold text-[#15803D] mt-1">
                {metrics ? `${metrics.system_health.cache_hit_ratio_pct}%` : '0%'}
              </div>
              <p className="text-[11px] text-[#24120B]/60 mt-0.5">High-speed sub-millisecond retrieval</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
