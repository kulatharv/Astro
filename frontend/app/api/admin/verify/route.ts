import { NextRequest, NextResponse } from 'next/server';
import { ADMIN_SECRET, verifyAdminAccess } from '../authHelper';

// Check if currently authenticated
export async function GET(req: NextRequest) {
  if (verifyAdminAccess(req)) {
    return NextResponse.json({ authenticated: true });
  }
  return NextResponse.json({ authenticated: false }, { status: 401 });
}

// Authenticate with admin passkey
export async function POST(req: NextRequest) {
  try {
    const { passkey } = await req.json();
    if (passkey && passkey.trim() === ADMIN_SECRET) {
      const res = NextResponse.json({ success: true, message: 'Administrator authenticated.' });
      res.cookies.set('admin_key', ADMIN_SECRET, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 3600 * 8, // 8 hours session
        path: '/',
      });
      return res;
    }
    return NextResponse.json(
      { success: false, detail: 'Invalid administrator passkey. Access logged.' },
      { status: 401 }
    );
  } catch (err: any) {
    return NextResponse.json(
      { success: false, detail: err?.message || 'Authentication error' },
      { status: 500 }
    );
  }
}
