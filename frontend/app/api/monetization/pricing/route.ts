import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const country = searchParams.get('country') || '';
    const timezone = searchParams.get('timezone') || '';
    const hnw = searchParams.get('hnw') === 'true';

    const clientIpCountry = req.headers.get('cf-ipcountry') || req.headers.get('x-vercel-ip-country') || country;

    const queryParams = new URLSearchParams();
    if (clientIpCountry) queryParams.set('country_override', clientIpCountry);
    if (timezone) queryParams.set('timezone', timezone);
    if (hnw) queryParams.set('hnw', 'true');

    const res = await fetch(`${BACKEND_URL}/api/monetization/pricing?${queryParams.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'cf-ipcountry': clientIpCountry || '',
      },
      next: { revalidate: 3600 },
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error: any) {
    return NextResponse.json(
      { status: 'error', detail: error?.message || 'Pricing query failed' },
      { status: 500 }
    );
  }
}

