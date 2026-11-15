import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

export async function POST(req: NextRequest) {
  try {
    const res = await fetch(`${BACKEND_URL}/api/auth/logout`, {
      method: 'POST',
      headers: {
        cookie: req.headers.get('cookie') || '',
      },
    });

    const data = await res.json();
    const nextResponse = NextResponse.json(data, { status: res.status });

    // Clear session cookies
    nextResponse.cookies.delete('session');
    nextResponse.cookies.delete('refresh_token');

    return nextResponse;
  } catch (error: any) {
    return NextResponse.json(
      { status: 'error', detail: error?.message || 'Failed to logout' },
      { status: 500 }
    );
  }
}

