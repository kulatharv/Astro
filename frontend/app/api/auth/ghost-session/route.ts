import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const fingerprint = searchParams.get('fingerprint') || '';

    const res = await fetch(`${BACKEND_URL}/api/auth/ghost-session?fingerprint=${encodeURIComponent(fingerprint)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        cookie: req.headers.get('cookie') || '',
      },
      cache: 'no-store',
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error: any) {
    return NextResponse.json(
      { has_active_session: false, detail: error?.message || 'Ghost session check failed' },
      { status: 200 }
    );
  }
}

