import { NextResponse } from 'next/server';

export async function GET(req: Request) {
  try {
    const backendUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';
    const cookie = req.headers.get('cookie') || '';

    const response = await fetch(`${backendUrl}/api/user/profile`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        cookie: cookie,
      },
      signal: AbortSignal.timeout(8000),
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json({ status: 'success', data });
    }

    const errorData = await response.json().catch(() => ({}));
    return NextResponse.json(
      {
        status: 'error',
        message: errorData.detail || `Backend responded with ${response.status}`,
      },
      { status: response.status }
    );
  } catch (err: any) {
    return NextResponse.json(
      {
        status: 'error',
        message: 'Could not connect to AstroLogic User Service.',
        error: err?.message || 'Network error',
      },
      { status: 502 }
    );
  }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const backendUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';
    const cookie = req.headers.get('cookie') || '';

    const response = await fetch(`${backendUrl}/api/user/profile`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        cookie: cookie,
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(10000),
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json({ status: 'success', data });
    }

    const errorData = await response.json().catch(() => ({}));
    return NextResponse.json(
      {
        status: 'error',
        message: errorData.detail || `Backend responded with ${response.status}`,
      },
      { status: response.status }
    );
  } catch (err: any) {
    return NextResponse.json(
      {
        status: 'error',
        message: 'Could not update user profile.',
        error: err?.message || 'Network error',
      },
      { status: 502 }
    );
  }
}

