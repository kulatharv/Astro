import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const backendUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';

    const response = await fetch(`${backendUrl}/api/kundali`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(15000),
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json({ status: 'success', data });
    }

    const errorData = await response.json().catch(() => ({}));
    return NextResponse.json(
      {
        status: 'error',
        message: errorData.detail || `Backend responded with status ${response.status}`,
      },
      { status: response.status }
    );
  } catch (err: any) {
    return NextResponse.json(
      {
        status: 'error',
        message: 'Could not connect to Vedic Ephemeris calculation backend.',
        error: err?.message || 'Network error',
      },
      { status: 502 }
    );
  }
}

