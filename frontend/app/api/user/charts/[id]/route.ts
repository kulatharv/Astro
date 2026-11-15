import { NextResponse } from 'next/server';

export async function DELETE(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const backendUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';
    const cookie = req.headers.get('cookie') || '';

    const response = await fetch(`${backendUrl}/api/user/charts/${id}`, {
      method: 'DELETE',
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
        message: 'Could not delete saved chart.',
        error: err?.message || 'Network error',
      },
      { status: 502 }
    );
  }
}

