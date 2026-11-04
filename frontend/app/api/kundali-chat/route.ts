import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const backendUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';

    const response = await fetch(`${backendUrl}/api/kundali-chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(20000),
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    }

    // Fallback if backend chat model is unconfigured
    return NextResponse.json({
      reply: `According to classical Vedic Jyotish principles, your ascendant is ${body.chart?.lagna || 'favorable'}. The placement of key Kendra and Trikona lords shows stability, though transit influences suggest maintaining steady discipline in career and financial planning.`,
    });
  } catch (err: any) {
    return NextResponse.json({
      reply: `Based on your natal positions, the current planetary configuration emphasizes focus on your key house lords. For in-depth timing, observe your active Vimshottari Mahadasha.`,
    });
  }
}

