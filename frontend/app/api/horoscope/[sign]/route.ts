import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ sign: string }> }
) {
  try {
    const { sign } = await params;
    const url = `${BACKEND_URL}/api/horoscope/${encodeURIComponent(sign)}`;

    const res = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      next: { revalidate: 3600 }, // 1-hour cache
    });

    if (!res.ok) {
      // Fallback to daily-horoscope route
      const fallbackUrl = `${BACKEND_URL}/api/daily-horoscope/${encodeURIComponent(sign)}`;
      const fallbackRes = await fetch(fallbackUrl, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });
      if (fallbackRes.ok) {
        const data = await fallbackRes.json();
        return NextResponse.json(data);
      }
      return NextResponse.json(
        { error: `Backend responded with HTTP ${res.status}` },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { error: 'Failed to communicate with Horoscope engine', details: error?.message },
      { status: 500 }
    );
  }
}

