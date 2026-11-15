import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const res = NextResponse.json({ success: true, message: 'Admin console locked.' });
  res.cookies.delete('admin_key');
  return res;
}
