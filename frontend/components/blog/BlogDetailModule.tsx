'use client';

import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  Calendar,
  Clock,
  User,
  Tag,
  Share2,
  Printer,
  Sparkles,
  Compass,
} from 'lucide-react';
import { Link } from '@/i18n/routing';
import { SupportedLocale, BLOG_TRANSLATIONS } from './blogLocalization';
import { BlogPostItem } from './BlogListModule';

interface BlogDetailModuleProps {
  slug: string;
  locale: string;
}

export default function BlogDetailModule({ slug, locale }: BlogDetailModuleProps) {
  const activeLocale = (['en', 'hi', 'mr'].includes(locale) ? locale : 'en') as SupportedLocale;
  const t = BLOG_TRANSLATIONS[activeLocale];

  const [post, setPost] = useState<BlogPostItem | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    async function loadPost() {
      setLoading(true);
      setErrorMsg(null);
      try {
        const res = await fetch(`/api/blogs/${encodeURIComponent(slug)}`);
        if (!res.ok) {
          throw new Error('Article not found');
        }
        const data = await res.json();
        setPost(data);
      } catch (err: any) {
        setErrorMsg('Article could not be loaded.');
      } finally {
        setLoading(false);
      }
    }
    loadPost();
  }, [slug]);

  const handlePrint = () => {
    window.print();
  };

  const handleShare = () => {
    if (typeof navigator !== 'undefined' && navigator.share && post) {
      navigator.share({
        title: post.title,
        text: post.summary || post.title,
        url: window.location.href,
      }).catch(() => {});
    } else if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      alert('Article link copied to clipboard!');
    }
  };

  if (loading) {
    return (
      <div className="p-16 text-center rounded-3xl bg-[#FDF5E6] border border-[#F9DAB5] max-w-3xl mx-auto space-y-3">
        <Compass className="w-8 h-8 animate-spin text-[#821C17] mx-auto" />
        <p className="text-base font-serif text-[#421A10]">{t.loading}</p>
      </div>
    );
  }

  if (errorMsg || !post) {
    return (
      <div className="p-12 text-center rounded-3xl bg-[#FDF5E6] border border-[#F9DAB5] max-w-2xl mx-auto space-y-4">
        <span className="text-4xl">📜</span>
        <h2 className="font-serif text-2xl font-bold text-[#821C17]">
          {errorMsg || 'Article not found'}
        </h2>
        <Link
          href="/blogs"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#821C17] text-[#FDF5E6] font-semibold text-xs hover:brightness-110 transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{t.backToArticles}</span>
        </Link>
      </div>
    );
  }

  const readTime = Math.ceil((post.content?.length || 1000) / 900);

  // Formatter for markdown-like headers in content
  const renderFormattedContent = (content: string) => {
    const lines = content.split('\n');
    return lines.map((line, idx) => {
      const trimmed = line.trim();
      if (trimmed.startsWith('### ')) {
        return (
          <h3 key={idx} className="font-serif text-xl sm:text-2xl font-bold text-[#821C17] mt-8 mb-3">
            {trimmed.replace('### ', '')}
          </h3>
        );
      }
      if (trimmed.startsWith('## ')) {
        return (
          <h2 key={idx} className="font-serif text-2xl sm:text-3xl font-bold text-[#821C17] mt-10 mb-4 pb-2 border-b border-[#F9DAB5]">
            {trimmed.replace('## ', '')}
          </h2>
        );
      }
      if (trimmed.startsWith('- ')) {
        return (
          <li key={idx} className="ml-5 list-disc text-sm sm:text-base text-[#421A10]/90 leading-relaxed my-1">
            {trimmed.replace('- ', '')}
          </li>
        );
      }
      if (trimmed.length === 0) {
        return <div key={idx} className="h-3" />;
      }
      return (
        <p key={idx} className="font-serif text-base sm:text-lg leading-relaxed text-[#421A10]/90 my-2">
          {trimmed}
        </p>
      );
    });
  };

  return (
    <article className="max-w-3xl mx-auto space-y-8">
      {/* ── Back Navigation & Action Buttons ── */}
      <div className="flex items-center justify-between gap-4 print:hidden">
        <Link
          href="/blogs"
          className="inline-flex items-center gap-2 text-xs font-semibold text-[#821C17] hover:text-[#421A10] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{t.backToArticles}</span>
        </Link>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleShare}
            className="p-2.5 rounded-xl border border-[#F9DAB5] bg-[#FDF5E6] hover:bg-[#FCEBD2] text-[#821C17] transition-colors cursor-pointer"
            title="Share article"
          >
            <Share2 className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={handlePrint}
            className="p-2.5 rounded-xl border border-[#F9DAB5] bg-[#FDF5E6] hover:bg-[#FCEBD2] text-[#821C17] transition-colors cursor-pointer"
            title="Print article"
          >
            <Printer className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* ── Article Header ── */}
      <div className="p-8 sm:p-10 rounded-3xl bg-[#FDF5E6] border border-[#F9DAB5] shadow-xs space-y-6">
        {post.tags && post.tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {post.tags.map((tg) => (
              <span
                key={tg}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-[#821C17]/10 text-[#821C17] border border-[#821C17]/25"
              >
                <Tag className="w-3 h-3" />
                <span>{tg}</span>
              </span>
            ))}
          </div>
        )}

        <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-[#421A10] leading-tight tracking-tight">
          {post.title}
        </h1>

        {post.summary && (
          <p className="font-serif italic text-base sm:text-lg text-[#421A10]/80 leading-relaxed border-l-4 border-[#821C17] pl-4 py-1">
            {post.summary}
          </p>
        )}

        {/* Metadata Strip */}
        <div className="flex flex-wrap items-center gap-6 text-xs text-[#421A10]/70 pt-4 border-t border-[#F9DAB5]">
          {post.author && (
            <span className="flex items-center gap-2">
              <User className="w-4 h-4 text-[#C46B1E]" />
              <span>{t.writtenBy} <strong className="text-[#821C17]">{post.author}</strong></span>
            </span>
          )}
          <span className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-[#C46B1E]" />
            <span>{readTime} {t.minRead}</span>
          </span>
          <span className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#C46B1E]" />
            <span>Vedic Knowledge</span>
          </span>
        </div>
      </div>

      {/* ── Article Body Content ── */}
      <div className="p-8 sm:p-12 rounded-3xl bg-[#FDF5E6] border border-[#F9DAB5] shadow-xs space-y-4">
        {renderFormattedContent(post.content)}
      </div>

      {/* ── Article Footer / Navigation ── */}
      <div className="p-6 rounded-2xl bg-linear-to-r from-[#FDF5E6] via-[#FCEBD2] to-[#FDF5E6] border border-[#F9DAB5] flex items-center justify-between gap-4 print:hidden">
        <Link
          href="/blogs"
          className="inline-flex items-center gap-2 text-xs font-bold text-[#821C17] hover:text-[#421A10] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{t.backToArticles}</span>
        </Link>
        <button
          type="button"
          onClick={handlePrint}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-[#FDF5E6] bg-linear-to-r from-[#821C17] to-[#C46B1E] hover:brightness-110 transition-all cursor-pointer shadow-xs"
        >
          <Printer className="w-3.5 h-3.5 text-[#F3C387]" />
          <span>Print Article</span>
        </button>
      </div>
    </article>
  );
}

