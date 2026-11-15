import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const limit = searchParams.get('limit') || '50';
    const claimedOnly = searchParams.get('claimed_only');

    const url = new URL(`${BACKEND_URL}/api/admin/ghost-sessions`);
    url.searchParams.set('limit', limit);
    if (claimedOnly !== null && claimedOnly !== undefined) {
      url.searchParams.set('claimed_only', claimedOnly);
    }

    const res = await fetch(url.toString(), {
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
      { status: 'error', detail: error?.message || 'Failed to fetch ghost sessions' },
      { status: 500 }
    );
  }
}

