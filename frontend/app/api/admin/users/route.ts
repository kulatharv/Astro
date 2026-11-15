import { NextRequest, NextResponse } from 'next/server';
import { verifyAdminAccess, ADMIN_SECRET } from '../authHelper';

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

export async function GET(req: NextRequest) {
  if (!verifyAdminAccess(req)) {
    return NextResponse.json({ error: 'Unauthorized administrator access' }, { status: 401 });
  }

  try {
    const searchParams = req.nextUrl.searchParams.toString();
    const url = `${BACKEND_URL}/api/admin/users${searchParams ? `?${searchParams}` : ''}`;

    const res = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'x-admin-key': ADMIN_SECRET,
        cookie: req.headers.get('cookie') || '',
        Authorization: req.headers.get('Authorization') || '',
      },
      cache: 'no-store',
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error: any) {
    return NextResponse.json(
      { status: 'error', detail: error?.message || 'Failed to fetch admin users' },
      { status: 500 }
    );
  }
}
