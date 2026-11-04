/**
 * High-fidelity Printable Prediction Report Generator
 * Multi-language support (English, हिन्दी, मराठी)
 * Formats deep evaluations across all 10 life domains into a print-ready A4 dossier
 */

import { DOMAINS_LIST, type DomainMeta } from './predictionLocalization';

export type ReportLanguage = 'en' | 'hi' | 'mr';

export interface PredictionReportInput {
  name: string;
  dob: string;
  tob: string;
  city: string;
  domainsData: any;
  reportLanguage?: ReportLanguage;
}

const REPORT_TEXTS: Record<ReportLanguage, {
  siteTitle: string;
  reportSubtitle: string;
  metaDetails: string;
  printBtn: string;
  nativeName: string;
  dob: string;
  tob: string;
  pob: string;
  lagna: string;
  dasha: string;
  score: string;
  timing: string;
  remedies: string;
  gemstone: string;
  mantra: string;
  fast: string;
  donate: string;
  ritual: string;
  keyIndicators: string;
  dashaActive: string;
  dashaInactive: string;
  footer: (name: string) => string;
}> = {
  en: {
    siteTitle: '✦ AstroLogic AI ✦',
    reportSubtitle: '10 Life Domain Predictions & Classical Astrological Dossier',
    metaDetails: 'Parashari Vedic Synthesis · Swiss Ephemeris Accuracy · Vimshottari & Gochara Transits',
    printBtn: '🖨️ Print / Save as PDF',
    nativeName: 'Native Name:',
    dob: 'Date of Birth:',
    tob: 'Time of Birth:',
    pob: 'Place of Birth:',
    lagna: 'Lagna (Ascendant):',
    dasha: 'Active Dasha Period:',
    score: 'Domain Strength',
    timing: 'Timing Window',
    remedies: 'Prescribed Vedic Remedies',
    gemstone: 'Gemstone:',
    mantra: 'Beej Mantra:',
    fast: 'Fasting Day:',
    donate: 'Sacred Charity:',
    ritual: 'Remedial Ritual:',
    keyIndicators: 'Astrological Indicators',
    dashaActive: '✓ Dasha Active',
    dashaInactive: 'Baseline',
    footer: (name) => `AstroLogic Vedic Platform · Comprehensive 10 Life Domain Assessment for <strong>${name}</strong> · Lahiri Ayanamsa & Parashari Principles · For guidance & reflection`,
  },
  hi: {
    siteTitle: '✦ एस्ट्रोलॉजिक ✦',
    reportSubtitle: '१० जीवन आयाम सम्पूर्ण फलादेश एवं वैदिक मार्गदर्शन अहवाल',
    metaDetails: 'महर्षि पराशर परंपरा · स्विस एफेमेरिस सूक्ष्म गणना · विंशोत्तरी दशा एवं गोचर विश्लेषण',
    printBtn: '🖨️ प्रिंट करें / PDF सुरक्षित करें',
    nativeName: 'जातक का नाम:',
    dob: 'जन्म तिथि:',
    tob: 'जन्म समय:',
    pob: 'जन्म स्थान:',
    lagna: 'लग्न (प्रथम भाव):',
    dasha: 'सक्रिय महादशा काल:',
    score: 'क्षेत्र सामर्थ्य',
    timing: 'अनुकूल फलित काल',
    remedies: 'शास्त्रीय वैदिक उपाय',
    gemstone: 'उपयुक्त रत्न:',
    mantra: 'बीज मंत्र:',
    fast: 'व्रत दिन:',
    donate: 'दान संकल्प:',
    ritual: 'शांति विधान:',
    keyIndicators: 'ग्रहीय आधार एवं योग',
    dashaActive: '✓ सक्रिय दशा',
    dashaInactive: 'सामान्य',
    footer: (name) => `एस्ट्रोलॉजिक वैदिक मंच · जातक <strong>${name}</strong> हेतु विस्तृत १० जीवन आयाम फलादेश अहवाल · लाहिड़ी अयनांश एवं पराशर सिद्धांत · व्यक्तिगत मार्गदर्शन एवं चिंतन हेतु`,
  },
  mr: {
    siteTitle: '✦ ॲस्ट्रोलॉजिक ✦',
    reportSubtitle: '१० जीवन पैलू सखोल भविष्य आणि शास्त्रीय मार्गदर्शन अहवाल',
    metaDetails: 'महर्षी पराशर परंपरा · स्विस एफिमेरिस अचूक गणना · विंशोत्तरी दशा व गोचर फलादेश',
    printBtn: '🖨️ प्रिंट करा / PDF सेव्ह करा',
    nativeName: 'जातकाचे नाव:',
    dob: 'जन्म तारीख:',
    tob: 'जन्म वेळ:',
    pob: 'जन्म ठिकाण:',
    lagna: 'लग्न (प्रथम स्थान):',
    dasha: 'चालू महादशा काळ:',
    score: 'पैलू सामर्थ्य',
    timing: 'अनुकूल कालखंड',
    remedies: 'शास्त्रीय वैदिक उपाय',
    gemstone: 'शिफारस केलेले रत्न:',
    mantra: 'बीज मंत्र:',
    fast: 'उपवासाचा वार:',
    donate: 'दान वस्तू:',
    ritual: 'शांती विधी:',
    keyIndicators: 'ग्रहीय आधार आणि योग',
    dashaActive: '✓ दशा सक्रिय',
    dashaInactive: 'साधारण',
    footer: (name) => `ॲस्ट्रोलॉजिक वैदिक मंच · जातक <strong>${name}</strong> साठी सखोल १० जीवन पैलू भविष्य अहवाल · लहिरी अयनांश व पराशर शास्त्रीय पद्धती · वैयक्तिक मार्गदर्शन व चिंतनार्थ`,
  },
};

function scoreColor(s: number): string {
  if (s >= 75) return '#15803D';
  if (s >= 55) return '#C46B1E';
  if (s >= 35) return '#EA580C';
  return '#DC2626';
}

export function openPrintablePredictionReport({
  name,
  dob,
  tob,
  city,
  domainsData,
  reportLanguage = 'en',
}: PredictionReportInput) {
  if (!domainsData || !domainsData.domains) return;

  const lang: ReportLanguage = ['en', 'hi', 'mr'].includes(reportLanguage) ? reportLanguage : 'en';
  const txt = REPORT_TEXTS[lang];
  const pName = name.trim() || (lang === 'en' ? 'Native' : 'जातक');
  const dObj = domainsData.domains;

  const dateLocales: Record<ReportLanguage, string> = { en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN' };
  const formattedDate = new Date().toLocaleDateString(dateLocales[lang], { dateStyle: 'long' });

  // 10 domains executive overview grid
  const overviewCards = DOMAINS_LIST.map((dm) => {
    const d = dObj[dm.key] || {};
    const sc = d.score || 60;
    const color = scoreColor(sc);
    const domainTitle = lang === 'mr' ? dm.mrName : lang === 'hi' ? dm.hiName : dm.enName;

    return `
      <div style="background:#faf7f2;border:1px solid #edd6b8;border-radius:8px;padding:10px;text-align:center">
        <div style="font-size:11px;color:#777;margin-bottom:3px;font-weight:600">${domainTitle}</div>
        <div style="font-size:18px;font-weight:bold;color:${color}">${sc}%</div>
        <div style="background:#fcebd2;height:4px;border-radius:2px;overflow:hidden;margin-top:4px">
          <div style="background:${color};height:100%;width:${sc}%"></div>
        </div>
      </div>
    `;
  }).join('');

  // Detailed Domain Sections
  const domainSections = DOMAINS_LIST.map((dm) => {
    const d = dObj[dm.key] || {};
    const sc = d.score || 60;
    const color = scoreColor(sc);
    const domainTitle = lang === 'mr' ? dm.mrName : lang === 'hi' ? dm.hiName : dm.enName;
    const domainSub = lang === 'mr' ? dm.mrSub : lang === 'hi' ? dm.hiSub : dm.enSub;
    const timing = d.timing || {};
    const remedies = d.remedies || {};
    const prList = remedies.planet_remedies || [];

    // Extract key indicators
    const indicatorRows: string[] = [];
    if (dm.key === 'marriage') {
      if (d.marriage_type) indicatorRows.push(`<strong>Type of Union:</strong> ${d.marriage_type}`);
      if (d.partner_traits) indicatorRows.push(`<strong>Partner Traits:</strong> ${d.partner_traits}`);
      if (d.partner_sign) indicatorRows.push(`<strong>Partner Sign:</strong> ${d.partner_sign}`);
      if (d.mangal_dosh !== undefined) indicatorRows.push(`<strong>Mangal Dosh:</strong> ${d.mangal_dosh ? '⚠ Present' : '✓ Absent'}`);
      if (d.seventh_lord) indicatorRows.push(`<strong>7th House Lord:</strong> ${d.seventh_lord}`);
    } else if (dm.key === 'career') {
      if (d.sector) indicatorRows.push(`<strong>Primary Sector:</strong> ${d.sector}`);
      if (d.best_fields) indicatorRows.push(`<strong>Favorable Fields:</strong> ${d.best_fields}`);
      if (d.business_vs_job) indicatorRows.push(`<strong>Business vs Job:</strong> ${d.business_vs_job}`);
      if (d.raj_yogas?.length) indicatorRows.push(`<strong>Raj Yogas:</strong> ${d.raj_yogas.join(', ')}`);
      if (d.tenth_lord) indicatorRows.push(`<strong>10th House Lord:</strong> ${d.tenth_lord}`);
    } else if (dm.key === 'wealth') {
      if (d.income_sources) indicatorRows.push(`<strong>Income Streams:</strong> ${d.income_sources}`);
      if (d.dhana_yogas?.length) indicatorRows.push(`<strong>Dhana Yogas:</strong> ${d.dhana_yogas.join(', ')}`);
      if (d.debt_risk) indicatorRows.push(`<strong>Debt Assessment:</strong> ${d.debt_risk}`);
      if (d.second_lord) indicatorRows.push(`<strong>2nd House Lord:</strong> ${d.second_lord}`);
    } else if (dm.key === 'health') {
      if (d.ayurvedic_dosha) indicatorRows.push(`<strong>Ayurvedic Prakriti:</strong> ${d.ayurvedic_dosha}`);
      if (d.weak_organs) indicatorRows.push(`<strong>Sensitive Organs:</strong> ${d.weak_organs}`);
      if (d.mental_health_ok !== undefined) indicatorRows.push(`<strong>Mental Vitality:</strong> ${d.mental_health_ok ? 'Stable' : 'Sensitive'}`);
    } else if (dm.key === 'challenges') {
      const df = d.doshas_found || [];
      if (df.length) {
        indicatorRows.push(`<strong>Detected Afflictions:</strong> ${df.map((x: any) => `${x.name} (${x.severity})`).join(', ')}`);
      } else {
        indicatorRows.push(`<strong>Afflictions:</strong> No severe unmitigated doshas detected.`);
      }
    } else if (dm.key === 'travel') {
      if (d.foreign_settlement !== undefined) indicatorRows.push(`<strong>Foreign Settlement:</strong> ${d.foreign_settlement ? 'Prominent' : 'Short Travel'}`);
      if (d.direction) indicatorRows.push(`<strong>Auspicious Direction:</strong> ${d.direction}`);
    } else if (dm.key === 'spirituality') {
      if (d.deity) indicatorRows.push(`<strong>Ishta Devata:</strong> ${d.deity}`);
      if (d.dharma_path) indicatorRows.push(`<strong>Dharma Path:</strong> ${d.dharma_path}`);
      if (d.moksha_yoga?.length) indicatorRows.push(`<strong>Moksha Yogas:</strong> ${d.moksha_yoga.join(', ')}`);
    }

    const remediesHtml = prList.length ? prList.map((r: any) => `
      <div style="font-size:11px;margin-bottom:4px">
        <strong>${r.planet}:</strong> 💎 ${r.gem || '—'} &nbsp;|&nbsp; 📿 ${r.mantra || '—'} &nbsp;|&nbsp; 🍽 ${r.fast || '—'}
      </div>
    `).join('') : '<span style="font-size:11px;color:#777">Harmonious general Vedic contemplation recommended.</span>';

    return `
      <div style="margin-bottom:18px;border:1px solid #edd6b8;border-radius:10px;padding:14px;background:#fff;page-break-inside:avoid">
        <div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:1.5px solid #8b1a1a;padding-bottom:6px;margin-bottom:8px">
          <div>
            <span style="font-size:15px;font-weight:bold;color:#8b1a1a">${domainTitle}</span>
            <span style="font-size:11px;color:#777;margin-left:8px">(${dm.house})</span>
          </div>
          <div>
            <span style="display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:bold;background:${d.dasha_active ? '#dcfce7' : '#fcebd2'};color:${d.dasha_active ? '#15803d' : '#8b1a1a'}">
              ${d.dasha_active ? txt.dashaActive : txt.dashaInactive}
            </span>
            <span style="font-size:16px;font-weight:bold;color:${color};margin-left:8px">${sc}%</span>
          </div>
        </div>

        <div style="font-size:11.5px;color:#333;line-height:1.5;margin-bottom:8px">
          ${d.analysis || domainSub}
        </div>

        ${indicatorRows.length ? `
          <div style="background:#faf7f2;border-radius:6px;padding:6px 10px;margin-bottom:8px;font-size:11px;display:flex;flex-wrap:wrap;gap:12px">
            ${indicatorRows.map((ir) => `<div>${ir}</div>`).join('')}
          </div>
        ` : ''}

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:11px;border-top:1px dashed #edd6b8;padding-top:6px">
          <div>
            <div style="font-weight:bold;color:#8b1a1a;margin-bottom:2px">⏱ ${txt.timing}</div>
            <div>${timing.best_window || 'Parashari baseline periods'} (Confidence: ${timing.confidence || 'Moderate'})</div>
          </div>
          <div>
            <div style="font-weight:bold;color:#8b1a1a;margin-bottom:2px">🙏 ${txt.remedies}</div>
            ${remediesHtml}
          </div>
        </div>
      </div>
    `;
  }).join('');

  const win = window.open('', '_blank', 'width=1050,height=850');
  if (!win) {
    alert('Please allow popups for this site to open the printable report.');
    return;
  }

  win.document.write(`<!DOCTYPE html>
<html lang="${lang}" translate="no" class="notranslate">
<head>
  <meta charset="utf-8">
  <meta name="google" content="notranslate" />
  <meta name="robots" content="notranslate" />
  <meta name="format-detection" content="telephone=no" />
  <title>${txt.siteTitle} — ${pName} 10 Life Domains</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans Devanagari", "Noto Serif Devanagari", "Mangal", "Nirmala UI", Georgia, serif;
      background: #fff;
      color: #1a0a00;
      font-size: 12px;
      line-height: 1.45;
    }
    .page {
      max-width: 980px;
      margin: 0 auto;
      padding: 24px 30px;
    }
    .header {
      text-align: center;
      padding: 16px 0 14px;
      border-bottom: 3px double #8b1a1a;
      margin-bottom: 16px;
    }
    .header h1 {
      font-size: 26px;
      color: #8b1a1a;
      letter-spacing: 3px;
      font-weight: 700;
      margin-bottom: 4px;
    }
    .header h2 {
      font-size: 13.5px;
      color: #555;
      font-weight: 500;
    }
    .header .meta {
      font-size: 11px;
      color: #777;
      margin-top: 5px;
    }
    .birth-strip {
      background: #faf7f2;
      border: 1px solid #edd6b8;
      border-radius: 8px;
      padding: 8px 16px;
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      font-size: 11.5px;
    }
    .overview-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 8px;
      margin-bottom: 20px;
    }
    .footer {
      text-align: center;
      font-size: 10.5px;
      color: #777;
      border-top: 1px solid #edd6b8;
      padding-top: 10px;
      margin-top: 24px;
    }
    @media print {
      @page { margin: 1cm; size: A4 portrait; }
      body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      .no-print { display: none !important; }
    }
  </style>
</head>
<body translate="no" class="notranslate">
  <div class="page">
    <!-- Action Bar -->
    <div class="no-print" style="margin-bottom:14px;display:flex;justify-content:space-between;align-items:center">
      <div style="font-size:12px;font-weight:bold;color:#8b1a1a">
        🌐 ${lang === 'mr' ? 'मराठी फलादेश अहवाल' : lang === 'hi' ? 'हिन्दी फलादेश रिपोर्ट' : 'English 10-Domain Report'}
      </div>
      <button onclick="window.print()" style="background:#8b1a1a;color:#fff;border:none;padding:8px 18px;border-radius:5px;font-size:12px;font-weight:bold;cursor:pointer">
        ${txt.printBtn}
      </button>
    </div>

    <!-- Header -->
    <div class="header">
      <h1>${txt.siteTitle}</h1>
      <h2>${txt.reportSubtitle}</h2>
      <div class="meta">
        ${formattedDate} &nbsp;·&nbsp; ${txt.metaDetails}
      </div>
    </div>

    <!-- Birth Strip -->
    <div class="birth-strip">
      <div><strong>${txt.nativeName}</strong> ${pName}</div>
      <div><strong>${txt.dob}</strong> ${dob} &nbsp;(${tob} IST)</div>
      <div><strong>${txt.pob}</strong> ${city}</div>
      <div><strong>${txt.lagna}</strong> <span style="color:#8b1a1a">${domainsData.lagna || '—'}</span></div>
      <div><strong>${txt.dasha}</strong> <span style="color:#15803d">${domainsData.mahadasha || '—'} / ${domainsData.antardasha || '—'}</span></div>
    </div>

    <!-- 10 Domains Overview Grid -->
    <div class="overview-grid">
      ${overviewCards}
    </div>

    <!-- Domain Details Sections -->
    <div>
      ${domainSections}
    </div>

    <!-- Footer -->
    <div class="footer">
      ${txt.footer(pName)}
    </div>
  </div>

  <script>
    window.onload = function() {
      setTimeout(function() {
        window.print();
      }, 400);
    };
  <\/script>
</body>
</html>`);

  win.document.close();
}

