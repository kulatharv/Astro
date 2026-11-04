import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const lang = searchParams.get('lang') || 'en';
    const limit = searchParams.get('limit') || '30';

    const url = `${BACKEND_URL}/api/blogs?lang=${encodeURIComponent(lang)}&limit=${encodeURIComponent(limit)}`;

    const res = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      next: { revalidate: 300 }, // 5-minute cache
    });

    if (!res.ok) {
      return NextResponse.json(
        { error: `Backend responded with HTTP ${res.status}` },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { error: 'Failed to retrieve blog posts', details: error?.message },
      { status: 500 }
    );
  }
}

