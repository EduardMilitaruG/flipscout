import { test, expect } from '@playwright/test'

const BASE = 'http://localhost:5173'
const API  = 'http://localhost:8000'

// ── Helpers ──────────────────────────────────────────────────────────────────

async function ss(page, name) {
  await page.screenshot({ path: `qa-screenshots/${name}.png`, fullPage: true })
}

// ── API sanity checks ────────────────────────────────────────────────────────

test.describe('API endpoints', () => {
  test('health check returns ok', async ({ request }) => {
    const r = await request.get(`${API}/api/health`)
    expect(r.status()).toBe(200)
    expect((await r.json()).status).toBe('ok')
  })

  test('stats/today returns correct shape', async ({ request }) => {
    const r = await request.get(`${API}/api/stats/today`)
    expect(r.status()).toBe(200)
    const body = await r.json()
    expect(body).toHaveProperty('total_deals_today')
    expect(body).toHaveProperty('avg_margin_pct')
    expect(body.total_deals_today).toBeGreaterThan(0)
  })

  test('deals returns array with margin fields', async ({ request }) => {
    const r = await request.get(`${API}/api/deals`)
    expect(r.status()).toBe(200)
    const deals = await r.json()
    expect(deals.length).toBeGreaterThan(0)
    const d = deals[0]
    expect(d).toHaveProperty('title')
    expect(d).toHaveProperty('margin_pct')
    expect(d).toHaveProperty('gross_margin_eur')
    expect(d).toHaveProperty('jp_price_eur')
    expect(d).toHaveProperty('shipping_eur')
    expect(d).toHaveProperty('spanish_resale_eur')
    expect(d).toHaveProperty('confidence')
  })

  test('deals are sorted by margin_pct descending', async ({ request }) => {
    const r = await request.get(`${API}/api/deals`)
    const deals = await r.json()
    for (let i = 1; i < deals.length; i++) {
      expect(deals[i - 1].margin_pct).toBeGreaterThanOrEqual(deals[i].margin_pct)
    }
  })

  test('deals filter: category=tech', async ({ request }) => {
    const r = await request.get(`${API}/api/deals?category=tech`)
    const deals = await r.json()
    deals.forEach(d => expect(d.category).toBe('tech'))
  })

  test('deals filter: category=pokemon', async ({ request }) => {
    const r = await request.get(`${API}/api/deals?category=pokemon`)
    const deals = await r.json()
    deals.forEach(d => expect(d.category).toBe('pokemon'))
  })

  test('deals filter: min_margin=50 returns only high-margin deals', async ({ request }) => {
    const r = await request.get(`${API}/api/deals?min_margin=50`)
    const deals = await r.json()
    deals.forEach(d => expect(d.margin_pct).toBeGreaterThanOrEqual(50))
  })

  test('deals filter: marketplace=mercari_jp', async ({ request }) => {
    const r = await request.get(`${API}/api/deals?marketplace=mercari_jp`)
    const deals = await r.json()
    deals.forEach(d => expect(d.marketplace).toBe('mercari_jp'))
  })

  test('deals filter: high_confidence=true', async ({ request }) => {
    const r = await request.get(`${API}/api/deals?high_confidence=true`)
    const deals = await r.json()
    deals.forEach(d => expect(d.confidence).toBe('high'))
  })

  test('sniper targets returns array', async ({ request }) => {
    const r = await request.get(`${API}/api/sniper/targets`)
    expect(r.status()).toBe(200)
    const targets = await r.json()
    expect(Array.isArray(targets)).toBe(true)
    expect(targets.length).toBeGreaterThan(0)
    expect(targets[0]).toHaveProperty('id')
    expect(targets[0]).toHaveProperty('query')
  })

  test('sniper status returns correct shape', async ({ request }) => {
    const r = await request.get(`${API}/api/sniper/status`)
    expect(r.status()).toBe(200)
    const body = await r.json()
    expect(body).toHaveProperty('paused')
    expect(body).toHaveProperty('daily_spend_eur')
    expect(body).toHaveProperty('daily_limit_eur')
    expect(body.paused).toBe(false)
  })

  test('sniper events returns array with correct fields', async ({ request }) => {
    const r = await request.get(`${API}/api/sniper/events`)
    expect(r.status()).toBe(200)
    const events = await r.json()
    expect(events.length).toBeGreaterThan(0)
    expect(events[0]).toHaveProperty('action')
    expect(events[0]).toHaveProperty('listing_title')
    expect(events[0]).toHaveProperty('platform')
  })

  test('create snipe target via POST', async ({ request }) => {
    const r = await request.post(`${API}/api/sniper/targets`, {
      data: {
        id: 'qa_test_target',
        query: 'RTX 4080 Super',
        category: 'tech',
        platform: ['wallapop'],
        max_buy_price_eur: 600,
        min_margin_pct: 25,
        auto_buy: false,
        reserve_on_match: true,
        active: true,
      }
    })
    expect(r.status()).toBe(201)
    expect((await r.json()).id).toBe('qa_test_target')
  })

  test('toggle snipe target pause/resume', async ({ request }) => {
    const r = await request.patch(`${API}/api/sniper/targets/qa_test_target/toggle?active=false`)
    expect(r.status()).toBe(200)
    // Verify it's paused
    const targets = await (await request.get(`${API}/api/sniper/targets`)).json()
    const target = targets.find(t => t.id === 'qa_test_target')
    expect(target.active).toBe(0)
  })

  test('pause-all and resume-all kill switch', async ({ request }) => {
    const pause = await request.post(`${API}/api/sniper/pause-all`)
    expect(pause.status()).toBe(200)
    expect((await pause.json()).status).toBe('paused')

    const status = await (await request.get(`${API}/api/sniper/status`)).json()
    expect(status.paused).toBe(true)

    const resume = await request.post(`${API}/api/sniper/resume-all`)
    expect(resume.status()).toBe(200)
    expect((await resume.json()).status).toBe('resumed')

    const status2 = await (await request.get(`${API}/api/sniper/status`)).json()
    expect(status2.paused).toBe(false)
  })

  test('delete snipe target', async ({ request }) => {
    const r = await request.delete(`${API}/api/sniper/targets/qa_test_target`)
    expect(r.status()).toBe(204)
    const targets = await (await request.get(`${API}/api/sniper/targets`)).json()
    expect(targets.find(t => t.id === 'qa_test_target')).toBeUndefined()
  })

  test('404 for unknown deal id', async ({ request }) => {
    const r = await request.get(`${API}/api/deals/99999`)
    expect(r.status()).toBe(404)
  })
})

// ── UI tests ─────────────────────────────────────────────────────────────────

test.describe('Dashboard page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE)
    await page.waitForLoadState('networkidle')
  })

  test('page title and sidebar render', async ({ page }) => {
    await expect(page.locator('text=FlipScout').first()).toBeVisible()
    await expect(page.locator('a', { hasText: 'Deals' }).first()).toBeVisible()
    await expect(page.locator('a', { hasText: 'Sniper' })).toBeVisible()
    await ss(page, '01-dashboard-loaded')
  })

  test('stats bar shows data', async ({ page }) => {
    await expect(page.locator('text=DEALS_TODAY')).toBeVisible()
    await expect(page.locator('text=AVG_MARGIN')).toBeVisible()
    await expect(page.locator('text=BEST_DEAL')).toBeVisible()
    // Values should not all be dashes
    const statValues = await page.locator('.stat-num').allTextContents()
    expect(statValues.some(v => v !== '—')).toBe(true)
    await ss(page, '02-stats-bar')
  })

  test('deals table renders rows', async ({ page }) => {
    const rows = page.locator('tbody tr')
    await expect(rows.first()).toBeVisible()
    const count = await rows.count()
    expect(count).toBeGreaterThan(0)
    await ss(page, '03-deals-table')
  })

  test('deals table shows correct columns', async ({ page }) => {
    await expect(page.locator('th', { hasText: 'ITEM' })).toBeVisible()
    await expect(page.locator('th', { hasText: 'JP PRICE' })).toBeVisible()
    await expect(page.locator('th', { hasText: 'RESALE' })).toBeVisible()
    await expect(page.locator('th', { hasText: 'MARGIN' })).toBeVisible()
  })

  test('deal row expands to show breakdown', async ({ page }) => {
    await page.locator('tbody tr').first().click()
    await expect(page.locator('text=JP BUY').first()).toBeVisible()
    await expect(page.locator('text=SHIPPING').first()).toBeVisible()
    await expect(page.locator('text=PLATFORM FEE')).toBeVisible()
    await expect(page.locator('text=ES RESALE').first()).toBeVisible()
    await expect(page.locator('text=NET PROFIT')).toBeVisible()
    await ss(page, '04-deal-expanded')
  })

  test('deal row collapses on second click', async ({ page }) => {
    const row = page.locator('tbody tr').first()
    await row.click()
    await expect(page.locator('text=NET PROFIT')).toBeVisible()
    await row.click()
    await expect(page.locator('text=NET PROFIT')).not.toBeVisible()
  })

  test('category filter: Tech', async ({ page }) => {
    await page.selectOption('select', 'tech')
    await page.waitForTimeout(600)
    // Category label format: "TECH · ZENMARKET" — filter all divs containing " · "
    const allDivs = await page.locator('tbody td div').allTextContents()
    const labels = allDivs.filter(c => c.includes(' · '))
    expect(labels.length).toBeGreaterThan(0)
    labels.forEach(c => expect(c.toLowerCase()).toContain('tech'))
    await ss(page, '05-filter-tech')
  })

  test('category filter: Pokemon', async ({ page }) => {
    await page.selectOption('select', 'pokemon')
    await page.waitForTimeout(600)
    const allDivs = await page.locator('tbody td div').allTextContents()
    const labels = allDivs.filter(c => c.includes(' · '))
    expect(labels.length).toBeGreaterThan(0)
    labels.forEach(c => expect(c.toLowerCase()).toContain('pokemon'))
    await ss(page, '06-filter-pokemon')
  })

  test('min margin slider filters deals', async ({ page }) => {
    const slider = page.locator('input[type="range"]')
    // Set slider to 50% (around 40 on 0-80 scale)
    await slider.fill('40')
    await page.waitForTimeout(600)
    await ss(page, '07-filter-margin-40')
    // All shown rows should have margin >= 40%
    const marginCells = await page.locator('tbody td .text-2xl').allTextContents()
    const margins = marginCells.map(m => parseFloat(m)).filter(m => !isNaN(m))
    margins.forEach(m => expect(m).toBeGreaterThanOrEqual(40))
  })

  test('high confidence toggle filters results', async ({ page }) => {
    const checkbox = page.locator('label', { hasText: 'HIGH CONF' }).locator('input[type="checkbox"]')
    await checkbox.check()
    await page.waitForTimeout(600)
    // After high-confidence filter, no cell should show "LOW" as confidence
    const lowCells = page.locator('tbody td div').filter({ hasText: /^LOW$/ })
    await expect(lowCells).toHaveCount(0)
    await ss(page, '08-filter-high-confidence')
  })

  test('filter reset shows all deals', async ({ page }) => {
    await page.selectOption('select:near(:text("Category"))', 'tech')
    await page.waitForTimeout(400)
    await page.selectOption('select:near(:text("Category"))', '')
    await page.waitForTimeout(600)
    const count = await page.locator('tbody tr').count()
    expect(count).toBeGreaterThan(2)
  })

  test('external link opens in new tab', async ({ page, context }) => {
    const [newPage] = await Promise.all([
      context.waitForEvent('page'),
      page.locator('tbody a').first().click(),
    ])
    expect(newPage.url()).toContain('http')
    await newPage.close()
  })

  test('refresh button re-fetches data', async ({ page }) => {
    const refreshBtn = page.locator('button', { hasText: 'REFRESH' })
    await expect(refreshBtn).toBeVisible()
    await refreshBtn.click()
    await page.waitForTimeout(500)
    // Page should still show data after refresh
    const count = await page.locator('tbody tr').count()
    expect(count).toBeGreaterThan(0)
  })
})

test.describe('Sniper page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE}/sniper`)
    await page.waitForLoadState('networkidle')
  })

  test('sniper page renders all sections', async ({ page }) => {
    await expect(page.locator('text=SNIPER').first()).toBeVisible()
    await expect(page.locator('text=ACTIVE_TARGETS')).toBeVisible()
    await expect(page.locator('text=SNIPE_EVENT_LOG')).toBeVisible()
    await ss(page, '09-sniper-page')
  })

  test('status bar shows active state and spend', async ({ page }) => {
    await expect(page.locator('text=DAILY_SPEND')).toBeVisible()
    await expect(page.locator('text=ACTIVE').first()).toBeVisible()
    await ss(page, '10-sniper-status')
  })

  test('existing snipe targets are listed', async ({ page }) => {
    // First td of each row contains the query text
    const firstCells = page.locator('table').first().locator('tbody tr td:first-child')
    const cellTexts = (await firstCells.allTextContents()).join(' ').toLowerCase()
    expect(cellTexts).toContain('ps5 slim')
    expect(cellTexts).toContain('psa 10 charizard')
  })

  test('add target form opens and closes', async ({ page }) => {
    await page.locator('button', { hasText: 'NEW TARGET' }).click()
    await expect(page.locator('text=NEW_SNIPE_TARGET')).toBeVisible()
    await expect(page.locator('input[placeholder="snipe_ps5"]')).toBeVisible()
    await page.locator('button', { hasText: 'CANCEL' }).click()
    await expect(page.locator('text=NEW_SNIPE_TARGET')).not.toBeVisible()
    await ss(page, '11-add-target-form')
  })

  test('add target form validation: empty fields do not submit', async ({ page }) => {
    await page.locator('button', { hasText: 'NEW TARGET' }).click()
    await page.locator('button', { hasText: 'DEPLOY' }).click()
    // Form should still be visible (no submit with empty required fields)
    await expect(page.locator('text=NEW_SNIPE_TARGET')).toBeVisible()
  })

  test('create a new snipe target via UI', async ({ page }) => {
    await page.locator('button', { hasText: 'NEW TARGET' }).click()
    await page.locator('input[placeholder="snipe_ps5"]').fill('qa_ui_target')
    await page.locator('input[placeholder="PS5 slim"]').fill('RTX 4090')
    await page.locator('input[placeholder="350"]').fill('800')
    await page.locator('input[placeholder="20"]').fill('25')
    await page.locator('button', { hasText: 'DEPLOY' }).click()
    await page.waitForTimeout(600)
    await expect(page.locator('text=RTX 4090')).toBeVisible()
    await ss(page, '12-target-created')
  })

  test('pause a snipe target', async ({ page }) => {
    const row = page.locator('tr', { hasText: 'RTX 4090' })
    const pauseBtn = row.locator('button').first()
    await pauseBtn.click()
    await page.waitForTimeout(600)
    await expect(row.locator('text=paused')).toBeVisible()
    await ss(page, '13-target-paused')
  })

  test('resume a paused snipe target', async ({ page }) => {
    const row = page.locator('tr', { hasText: 'RTX 4090' })
    const resumeBtn = row.locator('button').first()
    await resumeBtn.click()
    await page.waitForTimeout(600)
    await expect(row.locator('text=active')).toBeVisible()
  })

  test('delete a snipe target', async ({ page }) => {
    const row = page.locator('tr', { hasText: 'RTX 4090' })
    await row.locator('button').last().click()
    await page.waitForTimeout(600)
    await expect(page.locator('text=RTX 4090')).not.toBeVisible()
    await ss(page, '14-target-deleted')
  })

  test('global pause all toggle', async ({ page }) => {
    const pauseBtn = page.locator('button', { hasText: 'Pause all' })
    await pauseBtn.click()
    await page.waitForTimeout(600)
    await expect(page.locator('text=PAUSED').first()).toBeVisible()
    await expect(page.locator('button', { hasText: 'Resume all' })).toBeVisible()
    await ss(page, '15-sniper-paused')
    // Resume
    await page.locator('button', { hasText: 'Resume all' }).click()
    await page.waitForTimeout(600)
    await expect(page.locator('text=ACTIVE').first()).toBeVisible()
    await ss(page, '16-sniper-resumed')
  })

  test('snipe events history is populated', async ({ page }) => {
    const events = page.locator('table').last().locator('tbody tr')
    await expect(events.first()).toBeVisible()
    const count = await events.count()
    expect(count).toBeGreaterThan(0)
    await ss(page, '17-snipe-events')
  })

  test('action badges render with correct styles', async ({ page }) => {
    await expect(page.locator('text=messaged').first()).toBeVisible()
    await expect(page.locator('text=skipped').first()).toBeVisible()
  })

  test('refresh button works on sniper page', async ({ page }) => {
    await page.locator('button', { hasText: 'REFRESH' }).click()
    await page.waitForTimeout(500)
    await expect(page.locator('text=SNIPER').first()).toBeVisible()
  })
})

test.describe('Navigation', () => {
  test('navigate Deals → Sniper → Deals', async ({ page }) => {
    await page.goto(BASE)
    await page.waitForLoadState('networkidle')
    await expect(page.locator('tbody tr').first()).toBeVisible()

    await page.locator('a', { hasText: 'Sniper' }).click()
    await expect(page.locator('text=SNIPER').first()).toBeVisible()

    await page.locator('a', { hasText: 'Deals' }).click()
    await expect(page.locator('tbody tr').first()).toBeVisible()
    await ss(page, '18-navigation')
  })

  test('active nav link is highlighted', async ({ page }) => {
    await page.goto(BASE)
    const dealsLink = page.locator('a', { hasText: 'Deals' })
    await expect(dealsLink).toHaveClass(/text-t-orange/)

    await page.locator('a', { hasText: 'Sniper' }).click()
    const sniperLink = page.locator('a', { hasText: 'Sniper' })
    await expect(sniperLink).toHaveClass(/text-t-orange/)
  })

  test('direct URL navigation works', async ({ page }) => {
    await page.goto(`${BASE}/sniper`)
    await expect(page.locator('text=SNIPER').first()).toBeVisible()
  })
})

test.describe('Responsive layout', () => {
  test('mobile viewport renders without overflow', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await page.goto(BASE)
    await page.waitForLoadState('networkidle')
    await ss(page, '19-mobile-deals')
    await page.goto(`${BASE}/sniper`)
    await page.waitForLoadState('networkidle')
    await ss(page, '20-mobile-sniper')
  })

  test('tablet viewport renders correctly', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.goto(BASE)
    await page.waitForLoadState('networkidle')
    await ss(page, '21-tablet-deals')
  })
})
