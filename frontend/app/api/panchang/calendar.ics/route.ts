import { NextResponse } from 'next/server';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const city = searchParams.get('city') || 'Pune';
    const limit = searchParams.get('limit') || '15';

    const backendUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';
    const res = await fetch(`${backendUrl}/api/panchang/calendar.ics?city=${encodeURIComponent(city)}&limit=${limit}`, {
      headers: {
        Accept: 'text/calendar',
      },
    });

    if (!res.ok) {
      return new NextResponse('Calendar not available', { status: 502 });
    }

    const icsData = await res.text();
    return new NextResponse(icsData, {
      status: 200,
      headers: {
        'Content-Type': 'text/calendar; charset=utf-8',
        'Content-Disposition': `attachment; filename="Panchang_${encodeURIComponent(city)}.ics"`,
      },
    });
  } catch (err: any) {
    return new NextResponse('Failed to generate calendar', { status: 500 });
  }
}

