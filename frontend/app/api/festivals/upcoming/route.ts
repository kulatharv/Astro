import { NextResponse } from 'next/server';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const limit = searchParams.get('limit') || '14';
    const backendUrl = process.env.BACKEND_API_URL || 'http://127.0.0.1:8000';

    const response = await fetch(`${backendUrl}/api/festivals/upcoming?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(6000),
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    }

    return NextResponse.json({ festivals: [] }, { status: 200 });
  } catch (err: any) {
    return NextResponse.json(
      {
        festivals: [
          {
            name: "Dev Deepawali (Kartik Purnima)",
            date: "24 Nov 2026",
            iso_date: "2026-11-24",
            desc: "Festival of lights celebrated by the Gods in Kashi (Varanasi).",
            tithi: "Shukla Purnima",
            paksha: "Shukla",
            nakshatra: "Krittika",
            tag: "major",
            icon: "🪔",
            remedies: "Light clay lamps near rivers or shrines; chant Shiva Mahimna Stotram.",
            is_today: false
          },
          {
            name: "Devutthana Ekadashi",
            date: "20 Nov 2026",
            iso_date: "2026-11-20",
            desc: "Lord Vishnu awakens from four-month cosmic slumber; auspicious ceremonies commence.",
            tithi: "Shukla Ekadashi",
            paksha: "Shukla",
            nakshatra: "Uttara Bhadrapada",
            tag: "ekadashi",
            icon: "🌿",
            remedies: "Observe nirjala or phalahar fast; worship Lord Vishnu and Tulsi Devi.",
            is_today: false
          },
          {
            name: "Shukla Pradosh Vrat",
            date: "22 Nov 2026",
            iso_date: "2026-11-22",
            desc: "Sacred twilight worship of Lord Shiva and Maa Parvati for wish-fulfillment.",
            tithi: "Shukla Trayodashi",
            paksha: "Shukla",
            nakshatra: "Ashwini",
            tag: "vrat",
            icon: "🔱",
            remedies: "Offer Bilva leaves and milk abhishek during Pradosh twilight window.",
            is_today: false
          },
          {
            name: "Sankashti Chaturthi",
            date: "27 Nov 2026",
            iso_date: "2026-11-27",
            desc: "Monthly vow dedicated to Lord Ganesha for freedom from obstructions.",
            tithi: "Krishna Chaturthi",
            paksha: "Krishna",
            nakshatra: "Ardra",
            tag: "vrat",
            icon: "🐘",
            remedies: "Fast until moonrise; offer 21 Durva grass blades with modaks.",
            is_today: false
          }
        ]
      },
      { status: 200 }
    );
  }
}
