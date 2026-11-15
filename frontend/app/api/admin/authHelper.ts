import { NextRequest } from 'next/server';

export const ADMIN_SECRET = process.env.ADMIN_SECRET_KEY || 'AstroLogicMasterAdmin2026!';

export function verifyAdminAccess(req: NextRequest): boolean {
  const headerKey = req.headers.get('x-admin-key');
  const cookieKey = req.cookies.get('admin_key')?.value;
  return Boolean((headerKey && headerKey === ADMIN_SECRET) || (cookieKey && cookieKey === ADMIN_SECRET));
}
