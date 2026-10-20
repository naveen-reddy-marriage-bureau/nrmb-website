// Public-page browser checks. Run against localhost or the live deployment.
// Local serve.mjs serves explicit .html files; production uses Vercel clean URLs.
import assert from 'node:assert/strict';
import puppeteer from 'puppeteer';

const base = process.argv[2] || 'http://localhost:3000';
const local = new URL(base).hostname === 'localhost';
const origin = 'https://www.reddyelitematrimony.com';
const paths = ['/', '/our-branches', '/branches/somajiguda', '/branches/kothapet', '/branches/warangal', '/branches/karimnagar'];
const browser = await puppeteer.launch({headless:true,args:['--no-sandbox']});
const summaries = [];
try {
  const page = await browser.newPage();
  await page.setJavaScriptEnabled(false);
  const titles = new Set();
  for (const path of paths) {
    const url = base + path + (local && path !== '/' ? '.html' : '');
    const response = await page.goto(url,{waitUntil:'networkidle2',timeout:45000});
    assert.equal(response.status(),200,`${path}: HTTP status`);
    const details = await page.evaluate(() => {
      const graph = [...document.querySelectorAll('script[type="application/ld+json"]')].flatMap(s=>JSON.parse(s.textContent)['@graph']);
      return {
        title:document.title,
        descriptions:[...document.querySelectorAll('meta[name="description"]')].map(e=>e.content),
        canonicals:[...document.querySelectorAll('link[rel="canonical"]')].map(e=>e.href),
        h1:[...document.querySelectorAll('h1')].filter(e=>e.getClientRects().length).map(e=>e.textContent),
        graph, text:document.body.innerText,
        links:[...document.querySelectorAll('a[href]')].map(a=>a.href),
        splash:document.querySelector('#splashScreen') ? getComputedStyle(document.querySelector('#splashScreen')).display : 'none',
        featureOpacities:[...document.querySelectorAll('.feat-outer')].map(e=>getComputedStyle(e).opacity),
        brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),
      };
    });
    assert.equal(details.descriptions.length,1,`${path}: one description`);
    assert.ok(details.descriptions[0].length>50,`${path}: descriptive snippet`);
    assert.deepEqual(details.canonicals,[origin+path],`${path}: canonical`);
    assert.equal(details.h1.length,1,`${path}: one visible H1`);
    assert.match(details.h1[0],/Reddy/i,`${path}: relevant heading`);
    assert.ok(!titles.has(details.title),`${path}: unique title`); titles.add(details.title);
    assert.deepEqual(details.brokenImages,[],`${path}: all images load`);
    for (const b of details.graph.filter(n=>n['@type']==='LocalBusiness')) {
      assert.ok(details.links.includes('tel:'+b.telephone),`${path}: visible matching branch telephone`);
      assert.ok(details.text.includes(b.address.streetAddress),`${path}: visible matching address`);
      const hours=b.openingHoursSpecification[0];
      assert.equal(hours.opens,'10:00'); assert.equal(hours.closes,'18:30');
      assert.equal(hours.dayOfWeek.length,6); assert.ok(!hours.dayOfWeek.includes('Tuesday'));
      assert.match(details.text,/Closed on Tuesdays/);
      assert.equal(b.aggregateRating,undefined,`${path}: no invented rating`);
    }
    if (path.startsWith('/branches/')) {
      const business=details.graph.find(n=>n['@type']==='LocalBusiness');
      assert.ok(details.links.includes(business.hasMap),`${path}: Maps directions link`);
    }
    if(path==='/') {
      assert.equal(details.splash,'none','no-JS homepage is not covered by splash');
      assert.ok(details.featureOpacities.every(o=>o==='1'),'homepage features visible without scrolling');
      for(const branch of paths.slice(2)) assert.ok(details.links.includes(base+branch),'homepage exposes branch link');
    }
    for(const width of [375,768,1280]) {
      await page.setViewport({width,height:900});
      const overflow = await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
      assert.equal(overflow,false,`${path}: no horizontal overflow at ${width}px`);
    }
    if(path==='/our-branches'||path==='/branches/somajiguda') {
      await page.setViewport({width:390,height:844});
      if(local) await page.screenshot({path:`temporary screenshots/seo-${path.split('/').pop()}-mobile.png`,fullPage:true});
    }
    summaries.push({path,title:details.title,withoutJavaScript:true,viewports:3});
  }
  const sitemapResponse=await fetch(base+'/sitemap.xml');
  assert.equal(sitemapResponse.status,200);
  const sitemap=await sitemapResponse.text();
  assert.match(sitemap,/<urlset xmlns="http:\/\/www.sitemaps.org\/schemas\/sitemap\/0.9">/);
  const sitemapUrls=[...sitemap.matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>m[1]);
  assert.deepEqual(sitemapUrls,paths.map(path=>origin+path));
  const robots=await (await fetch(base+'/robots.txt')).text();
  assert.ok(robots.includes('Sitemap: '+origin+'/sitemap.xml'));
  assert.ok(!robots.includes('Disallow: /\n'));
  const verification=await (await fetch(base+'/googlee1584360cfe843d2.html')).text();
  assert.equal(verification.trim(),'google-site-verification: googlee1584360cfe843d2.html');
  if(!local) {
    await page.setJavaScriptEnabled(true);
    await page.goto(base+'/',{waitUntil:'networkidle2'});
    await Promise.all([page.waitForNavigation({waitUntil:'networkidle2'}),page.click('#nlBranch')]);
    assert.equal(page.url(),base+'/our-branches','homepage branch navigation');
    await Promise.all([page.waitForNavigation({waitUntil:'networkidle2'}),page.click('h2 a[href="/branches/somajiguda"]')]);
    assert.equal(page.url(),base+'/branches/somajiguda','hub to branch navigation');
    await Promise.all([page.waitForNavigation({waitUntil:'networkidle2'}),page.click('header a[href="/#pgContact"]')]);
    assert.equal(await page.$eval('#pgContact',el=>getComputedStyle(el).display),'block','legacy contact hash works');
  }
  console.log(JSON.stringify({result:'PASS',base,pages:summaries,sitemapUrls:sitemapUrls.length,verification:'preserved'},null,2));
} finally { await browser.close(); }
