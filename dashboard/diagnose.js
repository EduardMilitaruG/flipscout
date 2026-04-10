import { chromium } from 'playwright'

const BASE = 'http://localhost:5173'
const API  = 'http://localhost:8000'

const browser = await chromium.launch()
const page = await browser.newPage()

// Check what text is actually on the dashboard
await page.goto(BASE)
await page.waitForLoadState('networkidle')
const bodyText = await page.locator('body').innerText()
console.log('=== DASHBOARD BODY TEXT ===')
console.log(bodyText.slice(0, 800))

// Check the nav links
const navLinks = await page.locator('a').allTextContents()
console.log('\n=== NAV LINKS ===', navLinks)

// Check sidebar text
const sidebar = await page.locator('aside').innerText().catch(() => 'no aside')
console.log('\n=== SIDEBAR ===', sidebar)

// Check if FlipScout appears
const flipscout = await page.locator('text=FlipScout').count()
console.log('\n=== FlipScout count ===', flipscout)

// Screenshot
await page.screenshot({ path: 'qa-screenshots/diagnose-dashboard.png', fullPage: true })

// Check sniper page
await page.goto(`${BASE}/sniper`)
await page.waitForLoadState('networkidle')
const sniperText = await page.locator('body').innerText()
console.log('\n=== SNIPER BODY TEXT ===')
console.log(sniperText.slice(0, 800))

// Check "ACTIVE" visibility
const active = await page.locator('text=ACTIVE').count()
console.log('\n=== ACTIVE count ===', active)

// Check for PS5 target
const ps5 = await page.locator('text=PS5 slim').count()
console.log('PS5 slim count:', ps5)

// Category filter: what does the filter sidebar actually look like?
await page.goto(BASE)
await page.waitForLoadState('networkidle')
await page.selectOption('select', 'tech')
await page.waitForTimeout(800)
const afterFilter = await page.locator('tbody').innerText().catch(() => 'no tbody')
console.log('\n=== TBODY after tech filter ===')
console.log(afterFilter.slice(0, 500))

// Check what categories appear in rows
const rows = await page.locator('tbody td .text-xs').allTextContents()
console.log('\n=== Row category labels ===', rows)

await page.screenshot({ path: 'qa-screenshots/diagnose-filtered.png', fullPage: true })

await browser.close()
console.log('\nDone.')
