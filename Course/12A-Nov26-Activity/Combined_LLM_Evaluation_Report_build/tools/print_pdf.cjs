// Print the report HTML to a tagged PDF with bookmarks and page numbers.
// Usage: node tools/print_pdf.cjs build/report.html Combined_LLM_Evaluation_Report.pdf
// Needs: npm install puppeteer-core@24 (in this tools folder or globally)
// and Google Chrome at CHROME_PATH (default /usr/bin/google-chrome).
const path = require('node:path');
const puppeteer = require('puppeteer-core');

const [htmlPath, pdfPath] = process.argv.slice(2);
const chrome = process.env.CHROME_PATH || '/usr/bin/google-chrome';

const small = 'font-family: Noto Sans, sans-serif; font-size: 7.5pt; color: #6b7480;';
const header = `<div style="width:100%; padding: 0 17mm; ${small}">
  <span>Understanding LLM Evaluation: A Practical Guide to Ten Group Topics</span></div>`;
const footer = `<div style="width:100%; padding: 0 17mm; text-align:right; ${small}">
  Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>`;

(async () => {
  const browser = await puppeteer.launch({ executablePath: chrome, headless: true,
    args: ['--no-sandbox', '--font-render-hinting=none'] });
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(htmlPath), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: pdfPath, format: 'A4', printBackground: true,
    displayHeaderFooter: true, headerTemplate: header, footerTemplate: footer,
    margin: { top: '20mm', bottom: '20mm', left: '17mm', right: '17mm' },
    outline: true, tagged: true,
  });
  await browser.close();
})().catch((error) => { console.error(error); process.exit(1); });
