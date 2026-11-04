import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const body = await req.json().catch(() => ({ city: 'Delhi' }));
    const backendUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';

    const response = await fetch(`${backendUrl}/api/panchang`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      // Set 8s timeout so complex astronomical calculations complete reliably
      signal: AbortSignal.timeout(8000),
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json({ status: 'live', data });
    }

    return NextResponse.json(
      { status: 'unavailable', message: 'Cosmic Ephemeris backend responded with status ' + response.status },
      { status: 502 }
    );
  } catch (err: any) {
    return NextResponse.json(
      {
        status: 'offline',
        message: 'Backend Panchang API is offline. Showing classical reference values.',
        error: err?.message || 'Network error',
      },
      { status: 200 }
    );
  }
}
