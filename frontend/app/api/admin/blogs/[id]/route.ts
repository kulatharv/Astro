import { NextRequest, NextResponse } from 'next/server';
import { verifyAdminAccess, ADMIN_SECRET } from '../../authHelper';

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

export async function PUT(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  if (!verifyAdminAccess(req)) {
    return NextResponse.json({ error: 'Unauthorized administrator access' }, { status: 401 });
  }

  try {
    const { id } = await params;
    const body = await req.json();

    const res = await fetch(`${BACKEND_URL}/api/blogs/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'x-admin-key': ADMIN_SECRET,
        cookie: req.headers.get('cookie') || '',
      },
      body: JSON.stringify(body),
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error: any) {
    return NextResponse.json(
      { status: 'error', detail: error?.message || 'Failed to update blog post' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  if (!verifyAdminAccess(req)) {
    return NextResponse.json({ error: 'Unauthorized administrator access' }, { status: 401 });
  }

  try {
    const { id } = await params;
    const res = await fetch(`${BACKEND_URL}/api/blogs/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'x-admin-key': ADMIN_SECRET,
        cookie: req.headers.get('cookie') || '',
      },
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (error: any) {
    return NextResponse.json(
      { status: 'error', detail: error?.message || 'Failed to delete blog post' },
      { status: 500 }
    );
  }
}
