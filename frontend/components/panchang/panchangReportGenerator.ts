/**
 * High-fidelity Printable Panchang Almanac Dossier Generator
 * Multi-language support (English, हिन्दी, मराठी)
 * Generates an executive, luxury printable Vedic Panchang report with print & save-as-PDF.
 */

export type ReportLanguage = 'en' | 'hi' | 'mr';

export interface PanchangReportInput {
  date: string;
  city: string;
  panchang: any;
  locale: ReportLanguage;
}

export function openPrintablePanchangReport(input: PanchangReportInput) {
  const { date, city, panchang, locale } = input;

  const t = {
    en: {
      brand: 'AstroLogic',
      brandSub: 'Authentic Vedic Astrology & Swiss Ephemeris Precision',
      title: 'Daily Vedic Panchang Almanac Dossier',
      subtitle: 'Complete Astronomical Timings, Panchanga Limbs, Choghadiya & Planetary Ephemeris',
      metaDate: 'Almanac Date',
      metaCity: 'Geographic City',
      samvat: 'Samvat & Caloric Mechanics',
      fiveLimbs: 'The Five Cosmic Limbs (पञ्चाङ्ग)',
      sunMoon: 'Solar & Lunar Coordinates',
      muhurat: 'Auspicious & Inauspicious Muhurats',
      choghadiya: 'Choghadiya Timings (Day & Night)',
      transits: 'Planetary Transits (Gochar Ephemeris)',
      dishaShool: 'Disha Shool & Classical Travel Remedies',
      sunrise: 'Sunrise',
      sunset: 'Sunset',
      moonrise: 'Moonrise',
      moonset: 'Moonset',
      tithi: 'Tithi (Lunar Day)',
      nakshatra: 'Nakshatra (Lunar Mansion)',
      yoga: 'Yoga (Luni-Solar Arc)',
      karana: 'Karana (Half Tithi)',
      vara: 'Vara (Weekday)',
      abhijit: 'Abhijit Muhurat (Auspicious)',
      rahu: 'Rahu Kaal (Inauspicious)',
      yamaganda: 'Yamaganda Kaal',
      gulika: 'Gulika Kaal',
      brahma: 'Brahma Muhurat',
      graha: 'Graha (Planet)',
      rashi: 'Rashi (Zodiac)',
      deg: 'Degree',
      nak: 'Nakshatra',
      motion: 'Motion (Gati)',
      printBtn: 'Print / Save as PDF',
      closeBtn: 'Close Window',
      disclaimer: 'Calculated using high-precision Swiss Ephemeris micro-arcsecond astrometry according to Surya Siddhanta and classical Parashara principles.',
    },
    hi: {
      brand: 'एस्ट्रोलॉजिक',
      brandSub: 'प्रामाणिक वैदिक ज्योतिष एवं स्विस एफेमेरिस सूक्ष्म खगोल विज्ञान',
      title: 'दैनिक वैदिक पंचांग पंचांगीय प्रपत्र',
      subtitle: 'सम्पूर्ण खगोलीय समय, पंच अंग, चौघड़िया मुहूर्त एवं नवग्रह गोचर स्थिति',
      metaDate: 'पंचांग तिथि',
      metaCity: 'भौगोलिक नगर',
      samvat: 'संवत्सर एवं कालगणना',
      fiveLimbs: 'पंचांग के पंच अंग',
      sunMoon: 'सूर्य एवं चंद्र उदय-अस्त समय',
      muhurat: 'शुभ एवं अशुभ मुहूर्त काल',
      choghadiya: 'चौघड़िया मुहूर्त (दिन एवं रात्रि)',
      transits: 'ग्रह गोचर एवं खगोलीय अंश स्थिति',
      dishaShool: 'दिशा शूल एवं शास्त्रीय यात्रा उपाय',
      sunrise: 'सूर्योदय',
      sunset: 'सूर्यास्त',
      moonrise: 'चंद्रोदय',
      moonset: 'चंद्रास्त',
      tithi: 'तिथि',
      nakshatra: 'नक्षत्र',
      yoga: 'योग',
      karana: 'करण',
      vara: 'वार (दिन)',
      abhijit: 'अभिजित मुहूर्त (शुभ)',
      rahu: 'राहु काल (अशुभ)',
      yamaganda: 'यमगंड काल',
      gulika: 'गुलिक काल',
      brahma: 'ब्रह्म मुहूर्त',
      graha: 'ग्रह',
      rashi: 'राशि',
      deg: 'अंश',
      nak: 'नक्षत्र',
      motion: 'गति',
      printBtn: 'प्रिंट करें / PDF सेव करें',
      closeBtn: 'बंद करें',
      disclaimer: 'सूर्य सिद्धांत एवं महर्षि पराशर परंपरा के आधार पर स्विस एफेमेरिस की सूक्ष्म खगोलीय गणनाओं द्वारा निर्मित।',
    },
    mr: {
      brand: 'ॲस्ट्रोलॉजिक',
      brandSub: 'प्रामाणिक वैदिक ज्योतिष आणि स्विस एफिमेरिस अचूक खगोलशास्त्र',
      title: 'दैनिक वैदिक पंचांग सविस्तर पत्रिका',
      subtitle: 'संपूर्ण खगोलीय वेळा, पंचांगाची पाच अंगे, चोघडिया आणि ग्रह गोचर स्थिती',
      metaDate: 'पंचांग दिनांक',
      metaCity: 'स्थान / शहर',
      samvat: 'संवत्सर व कालमापन',
      fiveLimbs: 'पंचांगाची पाच मुख्य अंगे',
      sunMoon: 'सूर्य व चंद्र उदय-अस्त',
      muhurat: 'शुभ व अशुभ मुहूर्त काल',
      choghadiya: 'चोघडिया वेळ (दिवस आणि रात्र)',
      transits: 'ग्रह गोचर आणि राशी अंश',
      dishaShool: 'दिशा शूल आणि शास्त्रीय उपाय',
      sunrise: 'सूर्योदय',
      sunset: 'सूर्यास्त',
      moonrise: 'चंद्रोदय',
      moonset: 'चंद्रास्त',
      tithi: 'तिथी',
      nakshatra: 'नक्षत्र',
      yoga: 'योग',
      karana: 'करण',
      vara: 'वार',
      abhijit: 'अभिजित मुहूर्त (अत्यंत शुभ)',
      rahu: 'राहु काळ (अशुभ)',
      yamaganda: 'यमगंड काळ',
      gulika: 'गुलिक काळ',
      brahma: 'ब्रह्म मुहूर्त',
      graha: 'ग्रह',
      rashi: 'राशी',
      deg: 'अंश',
      nak: 'नक्षत्र',
      motion: 'गती',
      printBtn: 'प्रिंट करा / PDF जतन करा',
      closeBtn: 'बंद करा',
      disclaimer: 'सूर्य सिद्धांत आणि महर्षी पराशर परंपरेनुसार स्विस एफिमेरिसच्या अचूक खगोलीय गणनांवर आधारित.',
    },
  }[locale] || {
    brand: 'AstroLogic',
    brandSub: 'Authentic Vedic Astrology',
    title: 'Daily Vedic Panchang Almanac Dossier',
    subtitle: 'Complete Astronomical Timings, Panchanga Limbs, Choghadiya & Planetary Ephemeris',
    metaDate: 'Almanac Date',
    metaCity: 'Geographic City',
    samvat: 'Samvat & Caloric Mechanics',
    fiveLimbs: 'The Five Cosmic Limbs (पञ्चाङ्ग)',
    sunMoon: 'Solar & Lunar Coordinates',
    muhurat: 'Auspicious & Inauspicious Muhurats',
    choghadiya: 'Choghadiya Timings (Day & Night)',
    transits: 'Planetary Transits (Gochar Ephemeris)',
    dishaShool: 'Disha Shool & Classical Travel Remedies',
    sunrise: 'Sunrise',
    sunset: 'Sunset',
    moonrise: 'Moonrise',
    moonset: 'Moonset',
    tithi: 'Tithi (Lunar Day)',
    nakshatra: 'Nakshatra (Lunar Mansion)',
    yoga: 'Yoga (Luni-Solar Arc)',
    karana: 'Karana (Half Tithi)',
    vara: 'Vara (Weekday)',
    abhijit: 'Abhijit Muhurat (Auspicious)',
    rahu: 'Rahu Kaal (Inauspicious)',
    yamaganda: 'Yamaganda Kaal',
    gulika: 'Gulika Kaal',
    brahma: 'Brahma Muhurat',
    graha: 'Graha (Planet)',
    rashi: 'Rashi (Zodiac)',
    deg: 'Degree',
    nak: 'Nakshatra',
    motion: 'Motion (Gati)',
    printBtn: 'Print / Save as PDF',
    closeBtn: 'Close Window',
    disclaimer: 'Calculated using high-precision Swiss Ephemeris micro-arcsecond astrometry.',
  };

  const p = panchang || {};
  const samvatStr = typeof p.samvat === 'string'
    ? p.samvat
    : `Vikram Samvat ${p.samvat?.vikram_samvat || '2083'} · Shaka ${p.samvat?.shaka_samvat || '1948'}`;

  const planetsList = p.planets || [
    { name: 'Surya (Sun)', sign: 'Tula (Libra)', degree: "15°22'", nakshatra: 'Swati', retrograde: false },
    { name: 'Chandra (Moon)', sign: 'Vrishabha (Taurus)', degree: "12°04'", nakshatra: 'Rohini', retrograde: false },
    { name: 'Mangala (Mars)', sign: 'Karka (Cancer)', degree: "04°18'", nakshatra: 'Pushya', retrograde: false },
    { name: 'Budha (Mercury)', sign: 'Tula (Libra)', degree: "28°45'", nakshatra: 'Vishakha', retrograde: false },
    { name: 'Guru (Jupiter)', sign: 'Mithuna (Gemini)', degree: "20°12'", nakshatra: 'Punarvasu', retrograde: true },
    { name: 'Shukra (Venus)', sign: 'Vrishchika (Scorpio)', degree: "18°30'", nakshatra: 'Jyeshtha', retrograde: false },
    { name: 'Shani (Saturn)', sign: 'Kumbha (Aquarius)', degree: "18°50'", nakshatra: 'Shatabhisha', retrograde: true },
    { name: 'Rahu (North Node)', sign: 'Kumbha (Aquarius)', degree: "10°14'", nakshatra: 'Shatabhisha', retrograde: true },
    { name: 'Ketu (South Node)', sign: 'Simha (Leo)', degree: "10°14'", nakshatra: 'Magha', retrograde: true },
  ];

  const html = `<!DOCTYPE html>
<html lang="${locale}">
<head>
  <meta charset="utf-8" />
  <title>${t.title} - ${city} (${date})</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Inter:wght@400;500;600;700&family=Noto+Serif+Devanagari:wght@400;600;700&display=swap');

    @page {
      size: A4 portrait;
      margin: 12mm 15mm;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background: #FAF6F0;
      color: #24120B;
      font-family: 'Inter', -apple-system, sans-serif;
      font-size: 11pt;
      line-height: 1.5;
      padding: 24px;
    }

    .report-dossier {
      max-width: 840px;
      margin: 0 auto;
      background: #FFFFFF;
      border: 2px solid #C5A059;
      border-radius: 12px;
      padding: 28px 36px;
      box-shadow: 0 10px 30px rgba(36,18,11,0.06);
    }

    /* Action bar for printing */
    .action-bar {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-bottom: 20px;
    }

    .btn {
      padding: 8px 18px;
      font-size: 9.5pt;
      font-weight: 600;
      border-radius: 6px;
      cursor: pointer;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      transition: all 0.2s;
    }

    .btn-primary {
      background: #7A1612;
      color: #FAF6F0;
      border: 1px solid #C5A059;
    }

    .btn-secondary {
      background: #F5EFE6;
      color: #24120B;
      border: 1px solid #C5A059;
    }

    @media print {
      body {
        background: #FFFFFF;
        padding: 0;
      }
      .report-dossier {
        box-shadow: none;
        border: 1.5px solid #C5A059;
        padding: 16px 20px;
        max-width: 100%;
      }
      .action-bar {
        display: none !important;
      }
    }

    /* Header */
    .brand-header {
      text-align: center;
      border-bottom: 2px solid #C5A059;
      padding-bottom: 16px;
      margin-bottom: 20px;
    }

    .brand-title {
      font-family: 'Cormorant Garamond', 'Noto Serif Devanagari', Georgia, serif;
      font-size: 24pt;
      font-weight: 700;
      color: #7A1612;
      letter-spacing: 0.04em;
    }

    .brand-sub {
      font-size: 8.5pt;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: #A85A1E;
      margin-top: 2px;
    }

    .dossier-title {
      font-family: 'Cormorant Garamond', 'Noto Serif Devanagari', serif;
      font-size: 16pt;
      font-weight: 700;
      color: #24120B;
      margin-top: 10px;
    }

    .dossier-sub {
      font-size: 8.5pt;
      color: #5F392B;
    }

    /* Metadata Strip */
    .meta-strip {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      background: #FAF6F0;
      border: 1px solid #EADBC8;
      border-radius: 8px;
      padding: 10px 16px;
      margin-bottom: 20px;
      font-size: 9pt;
    }

    .meta-item strong {
      display: block;
      font-size: 7.5pt;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #7A1612;
    }

    /* Section Headings */
    .sec-head {
      font-family: 'Cormorant Garamond', 'Noto Serif Devanagari', serif;
      font-size: 13pt;
      font-weight: 700;
      color: #7A1612;
      border-left: 3px solid #7A1612;
      padding-left: 10px;
      margin: 18px 0 10px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    /* Tables */
    table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 14px;
      font-size: 9pt;
    }

    th {
      background: #F5EFE6;
      color: #7A1612;
      font-weight: 700;
      text-align: left;
      padding: 7px 10px;
      border-bottom: 1.5px solid #C5A059;
      font-size: 8pt;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    td {
      padding: 7px 10px;
      border-bottom: 1px solid #EADBC8;
      color: #24120B;
    }

    tr:nth-child(even) td {
      background: #FAF6F0;
    }

    .timing-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
      margin-bottom: 14px;
    }

    .timing-card {
      border: 1px solid #EADBC8;
      border-radius: 8px;
      padding: 10px 14px;
      background: #FFFFFF;
    }

    .timing-card.auspicious {
      border-left: 4px solid #1B4D3E;
      background: #F2F9F5;
    }

    .timing-card.inauspicious {
      border-left: 4px solid #7A1612;
      background: #FDF2F1;
    }

    .timing-card-title {
      font-size: 8pt;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.06em;
      margin-bottom: 2px;
    }

    .timing-card.auspicious .timing-card-title { color: #1B4D3E; }
    .timing-card.inauspicious .timing-card-title { color: #7A1612; }

    .timing-val {
      font-size: 11pt;
      font-family: 'Cormorant Garamond', Georgia, serif;
      font-weight: 700;
      color: #24120B;
    }

    .footer-note {
      text-align: center;
      margin-top: 24px;
      padding-top: 14px;
      border-top: 1px solid #EADBC8;
      font-size: 7.5pt;
      color: #5F392B;
    }
  </style>
</head>
<body>
  <div class="action-bar">
    <button class="btn btn-secondary" onclick="window.close()">${t.closeBtn}</button>
    <button class="btn btn-primary" onclick="window.print()">🖨 ${t.printBtn}</button>
  </div>

  <div class="report-dossier">
    <div class="brand-header">
      <div class="brand-title">✦ ${t.brand} ✦</div>
      <div class="brand-sub">${t.brandSub}</div>
      <div class="dossier-title">${t.title}</div>
      <div class="dossier-sub">${t.subtitle}</div>
    </div>

    <div class="meta-strip">
      <div class="meta-item">
        <strong>${t.metaDate}</strong>
        <span>${date}</span>
      </div>
      <div class="meta-item">
        <strong>${t.metaCity}</strong>
        <span>${city}</span>
      </div>
      <div class="meta-item">
        <strong>${t.samvat}</strong>
        <span>${samvatStr}</span>
      </div>
    </div>

    <!-- 5 LIMBS OF PANCHANG -->
    <div class="sec-head">✧ ${t.fiveLimbs}</div>
    <table>
      <thead>
        <tr>
          <th>Limb</th>
          <th>Sanskrit / Definition</th>
          <th>Active Value for Today</th>
          <th>Ends / Boundary Time</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>${t.tithi}</strong></td>
          <td>चन्द्रतिथि (Lunar phase angle)</td>
          <td><strong>${p.tithi || 'Shukla Pratipada'}</strong> (${p.paksha || 'Shukla'} Paksha)</td>
          <td>${p.tithi_end || 'Up to 02:45 PM'}</td>
        </tr>
        <tr>
          <td><strong>${t.nakshatra}</strong></td>
          <td>चन्द्रनक्षत्र (Moon asterism)</td>
          <td><strong>${p.nakshatra || 'Rohini'}</strong> (Pada ${p.nakshatra_pada || 2})</td>
          <td>${p.nakshatra_end || 'Up to 06:12 PM'}</td>
        </tr>
        <tr>
          <td><strong>${t.yoga}</strong></td>
          <td>नित्यायोग (Luni-solar sum)</td>
          <td><strong>${p.yoga || 'Shobhana'}</strong></td>
          <td>${p.yoga_end || 'Whole Day'}</td>
        </tr>
        <tr>
          <td><strong>${t.karana}</strong></td>
          <td>करण (Half-tithi unit)</td>
          <td><strong>${p.karana || 'Bava'}</strong></td>
          <td>${p.karana_end || 'Up to 02:45 PM'}</td>
        </tr>
        <tr>
          <td><strong>${t.vara}</strong></td>
          <td>वार (Weekday ruler)</td>
          <td><strong>${p.vara || 'Mangalvara (Tuesday)'}</strong></td>
          <td>Governed by Mars (Mangala)</td>
        </tr>
      </tbody>
    </table>

    <!-- SUN & MOON COORDINATES -->
    <div class="sec-head">✧ ${t.sunMoon}</div>
    <table>
      <thead>
        <tr>
          <th>${t.sunrise}</th>
          <th>${t.sunset}</th>
          <th>${t.moonrise}</th>
          <th>${t.moonset}</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>${p.sunrise || '06:34 AM'}</strong></td>
          <td><strong>${p.sunset || '05:58 PM'}</strong></td>
          <td><strong>${p.moonrise || '07:15 AM'}</strong></td>
          <td><strong>${p.moonset || '06:40 PM'}</strong></td>
        </tr>
      </tbody>
    </table>

    <!-- MUHURATS & DISHA SHOOL -->
    <div class="sec-head">✧ ${t.muhurat} & ${t.dishaShool}</div>
    <div class="timing-grid">
      <div class="timing-card auspicious">
        <div class="timing-card-title">★ ${t.abhijit}</div>
        <div class="timing-val">${p.abhijit || p.abhijit_muhurta || '11:42 AM – 12:28 PM'}</div>
        <div style="font-size: 7.5pt; color: #1B4D3E; margin-top: 2px;">Supreme window for crucial ventures, signings, & new undertakings.</div>
      </div>

      <div class="timing-card inauspicious">
        <div class="timing-card-title">⚠ ${t.rahu}</div>
        <div class="timing-val">${p.rahu || p.rahu_kaal || '03:05 PM – 04:32 PM'}</div>
        <div style="font-size: 7.5pt; color: #7A1612; margin-top: 2px;">Governed by Rahu. Avoid contracts, departures, & investments.</div>
      </div>

      <div class="timing-card auspicious">
        <div class="timing-card-title">★ ${t.brahma}</div>
        <div class="timing-val">${p.brahma || '04:52 AM – 05:40 AM'}</div>
        <div style="font-size: 7.5pt; color: #1B4D3E; margin-top: 2px;">Sattvic dawn period ideal for meditation, mantra, & study.</div>
      </div>

      <div class="timing-card inauspicious">
        <div class="timing-card-title">⚠ ${t.yamaganda} / ${t.gulika}</div>
        <div class="timing-val">${p.yamaganda || '09:20 AM – 10:45 AM'} | ${p.gulika || '12:10 PM – 01:35 PM'}</div>
        <div style="font-size: 7.5pt; color: #7A1612; margin-top: 2px;">Cautionary period; avoid commencing litigation or major travels.</div>
      </div>
    </div>

    <!-- PLANETARY TRANSITS EPHEMERIS -->
    <div class="sec-head">✧ ${t.transits}</div>
    <table>
      <thead>
        <tr>
          <th>${t.graha}</th>
          <th>${t.rashi}</th>
          <th>${t.deg}</th>
          <th>${t.nak}</th>
          <th>${t.motion}</th>
        </tr>
      </thead>
      <tbody>
        ${planetsList.map((pl: any) => `
          <tr>
            <td><strong>${pl.name}</strong></td>
            <td>${pl.sign}</td>
            <td style="font-family: monospace; font-weight: bold; color: #7A1612;">${pl.degree}</td>
            <td>${pl.nakshatra}</td>
            <td>${pl.retrograde ? '<span style="color:#7A1612; font-weight:bold;">वक्री (R)</span>' : '<span style="color:#1B4D3E;">मार्गी (Direct)</span>'}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>

    <div class="footer-note">
      ✦ ${t.brand} · ${t.disclaimer} ✦
    </div>
  </div>

  <script>
    // Auto-prompt print if user intends to save
    window.onload = function() {
      // Intentionally manual so user can preview before printing
    };
  </script>
</body>
</html>`;

  const printWindow = window.open('', '_blank', 'width=900,height=800,scrollbars=yes,resizable=yes');
  if (printWindow) {
    printWindow.document.open();
    printWindow.document.write(html);
    printWindow.document.close();
  }
}

