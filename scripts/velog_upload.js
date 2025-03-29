const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

(async () => {
  const email = process.env.VELOG_EMAIL;
  const password = process.env.VELOG_PASSWORD;

  // 최신 마크다운 파일 선택
  const files = fs.readdirSync('./markdown')
    .filter(f => f.endsWith('.md'))
    .map(f => ({ name: f, time: fs.statSync(`./markdown/${f}`).mtime }))
    .sort((a, b) => b.time - a.time);

  if (files.length === 0) {
    console.log("[!] No markdown file found");
    process.exit(1);
  }

  const mdFile = `./markdown/${files[0].name}`;
  const content = fs.readFileSync(mdFile, 'utf-8');

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  console.log("[ℹ] Navigating to Velog homepage...");
  // 1. Velog 홈 → 로그인 확인 → 로그인 시도
  await page.goto('https://velog.io');
  const loginBtn = await page.$('a[href="/login"]');
  
  if (loginBtn) {
    console.log("[ℹ] Login button found, logging in...");
    await loginBtn.click();
    await page.waitForSelector('input[name="email"]');
    await page.type('input[name="email"]', email);
    await page.type('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForNavigation();
    console.log("[✔] Login process completed");
  } else {
    console.log("[ℹ] Already logged in or login button not present");
  }
  
  // 2. 본인 페이지 접속 → 로그인 검증
  await page.goto(`https://velog.io/@${email.split('@')[0]}`);
  await new Promise(resolve => setTimeout(resolve, 2000));
  const isLoggedIn = await page.$('a[href="/write"]');
  
  if (!isLoggedIn) {
    console.error("[❌] Login check failed — write button not found");
    await page.screenshot({ path: 'login-failed.png' });
    process.exit(1);
  }
  
  console.log("[✔] Confirmed logged in. Proceeding to write page...");
  
  // 3. 글쓰기 페이지 이동
  await page.goto('https://velog.io/write');
  await page.waitForSelector('.ToastEditor textarea', { timeout: 10000 });
  console.log("[✔] Editor loaded successfully");
  await page.click('.ToastEditor textarea');
  await page.keyboard.type(content, { delay: 5 });

  // 제목 자동 추출
  const firstLine = content.split('\n').find(line => line.trim().length > 5);
  const title = firstLine.replace(/^#*/, '').trim().slice(0, 50);
  await page.type('input[placeholder="제목을 입력하세요"]', title);

  // 발행
  await page.click('button[aria-label="출간하기"]');
  await page.waitForSelector('button:has-text("발행하기")');
  await page.click('button:has-text("발행하기")');
  await page.waitForTimeout(3000);

  console.log("[✔] Successfully uploaded to Velog");

  await browser.close();
})();
