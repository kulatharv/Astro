import { NextResponse } from 'next/server';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const chartId = searchParams.get('chart_id');
    const backendUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';

    const url = chartId
      ? `${backendUrl}/api/download-kundali?chart_id=${encodeURIComponent(chartId)}`
      : `${backendUrl}/api/download-kundali`;

    const response = await fetch(url, {
      signal: AbortSignal.timeout(20000),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: `Backend returned status ${response.status}` },
        { status: response.status }
      );
    }

    const pdfBuffer = await response.arrayBuffer();
    return new NextResponse(pdfBuffer, {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="AstroLogic_Kundali_Report.pdf"',
      },
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || 'Error generating PDF' },
      { status: 500 }
    );
  }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const backendUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';

    const response = await fetch(`${backendUrl}/api/download-kundali`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(20000),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: `Backend returned status ${response.status}` },
        { status: response.status }
      );
    }

    const pdfBuffer = await response.arrayBuffer();
    return new NextResponse(pdfBuffer, {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="AstroLogic_Kundali_Report.pdf"',
      },
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || 'Error generating PDF via POST' },
      { status: 500 }
    );
  }
}
