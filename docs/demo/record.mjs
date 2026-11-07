// Phase 3: drive the app through the walkthrough while recording video.
// Each narration clip is split into steps (one caption + one action per step); a step starts when
// its share of the clip's speech begins, so on-screen action follows the voice.
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { chromium } from 'playwright'

const here = new URL('.', import.meta.url)
const plan = JSON.parse(readFileSync(new URL('plan.json', here), 'utf8'))
const clips = JSON.parse(readFileSync(new URL('clips.json', here), 'utf8'))
const BASE = process.env.DEMO_BASE_URL ?? plan.base
const REPO = 'https://github.com/Hiten-Koli/acme-pay'
const { person, newSalary } = plan.data

const SIZE = { width: 1440, height: 810 }
const AUDIO_DELAY = 0.4 // seconds after a beat starts, so visuals appear just before the voice
const LEAD = 0.15 // silence kept at the start of every clip (see tts.py)
const TAIL_PAUSE = 0.6 // breathing room after each clip
const GITHUB_LOAD = 4.5 // seconds to allow for the first GitHub page to load (cold cache)
const GITHUB_LOAD_WARM = 2.2 // ...and for the second (assets already cached)

mkdirSync(new URL('video', here), { recursive: true })
const browser = await chromium.launch()
const context = await browser.newContext({
  viewport: SIZE,
  recordVideo: { dir: new URL('video', here).pathname.replace(/^\/(\w:)/, '$1'), size: SIZE },
})
await context.addInitScript({ path: new URL('overlay.js', here).pathname.replace(/^\/(\w:)/, '$1') })
const page = await context.newPage()
const t0 = Date.now()
const now = () => (Date.now() - t0) / 1000

const failures = []
const marks = {} // moments the muxer uses to align the video clock with the audio clock
let captionText = ''
let pointer = { x: SIZE.width / 2, y: SIZE.height / 2 }

const firstLine = (error) => String(error).split(String.fromCharCode(10))[0]
const sleep = (ms) => page.waitForTimeout(Math.max(0, ms))
const until = async (atSeconds) => sleep((atSeconds - now()) * 1000)

async function setCaption(text) {
  captionText = text
  await page.evaluate((t) => window.__setCaption?.(t), text)
}
async function go(url, ready, { restorePointer = true } = {}) {
  await page.goto(url, { waitUntil: 'domcontentloaded' })
  if (ready) await page.waitForSelector(ready, { timeout: 45_000 })
  await setCaption(captionText)
  // On external pages, skip this: re-hovering where the pointer was can pop up tooltips.
  if (restorePointer) await page.mouse.move(pointer.x, pointer.y)
}
async function moveTo(x, y, steps = 28) {
  await page.mouse.move(x, y, { steps })
  pointer = { x, y }
}
async function hover(locator, { dy = 0 } = {}) {
  await locator.scrollIntoViewIfNeeded()
  const box = await locator.boundingBox()
  if (!box) throw new Error('no bounding box')
  await moveTo(box.x + box.width / 2, box.y + box.height / 2 + dy)
}
async function click(locator) {
  await hover(locator)
  await sleep(350)
  await locator.click({ delay: 90 })
}
async function scrollBy(pixels, ms = 1800) {
  const stepsCount = 18
  for (let i = 0; i < stepsCount; i++) {
    await page.mouse.wheel(0, pixels / stepsCount)
    await sleep(ms / stepsCount)
  }
}

const sheet = () => page.locator('[data-slot="sheet-content"]') // the open profile panel

// What happens on screen during each narrated sentence. `endAt` is when the step's speech ends.
const actions = {
  async title() {
    // The title card is already up (set before the first beat); just hold it.
  },
  async problem() {
    await page.evaluate(() => window.__setTitle(false))
    marks.titleOff = now()
    await sleep(800)
    await moveTo(760, 330, 40)
  },
  async figures() {
    for (const name of ['Active headcount', 'Annual payroll', 'Median salary']) {
      await hover(page.getByText(name, { exact: true }).first(), { dy: 28 })
      await sleep(1100)
    }
  },
  async band() {
    await hover(page.getByText('Outside pay band', { exact: true }).first(), { dy: 28 })
  },
  async signal({ endAt }) {
    await hover(page.getByRole('link', { name: /below band/ }).first())
    await until(endAt - 0.4)
  },
  async benchmarks() {
    await page.getByRole('link', { name: /below band/ }).first().click({ delay: 90 })
    await page.waitForSelector('text=pay by country', { timeout: 30_000 })
    await sleep(900)
    await hover(page.getByText(/^US$/).first())
    await sleep(1200)
    await hover(page.getByText(/^IN$/).first())
  },
  async outliers({ endAt }) {
    await scrollBy(430)
    const link = page.getByRole('link', { name: new RegExp(person.name) }).first()
    await hover(link)
    await until(endAt - 0.5)
    await link.click({ delay: 90 })
    await page.waitForSelector('text=Annual salary', { timeout: 30_000 })
  },
  async profile() {
    await sleep(600)
    const bar = sheet().getByRole('img', { name: /peer median/ })
    await hover(bar)
    await sleep(900)
    await moveTo(pointer.x + 220, pointer.y - 30, 20)
    await sleep(500)
    await hover(sheet().getByText('Below band', { exact: true }))
  },
  async preview() {
    const field = sheet().locator('#new-salary')
    await click(field)
    await field.pressSequentially(newSalary, { delay: 120 })
    await page.waitForSelector('output', { timeout: 20_000 })
    await sleep(500)
    await hover(sheet().locator('output'))
  },
  async save() {
    await click(sheet().getByRole('button', { name: 'Save salary change' }))
    await page.waitForSelector('text=Salary updated', { timeout: 20_000 })
    await sleep(500)
    await sheet().getByRole('heading', { name: 'Salary history' }).scrollIntoViewIfNeeded()
    await sleep(500)
    await hover(sheet().locator('ol > li').first())
  },
  async rule() {
    const field = sheet().locator('#new-salary')
    await click(field)
    await field.pressSequentially(newSalary, { delay: 90 })
    await click(sheet().getByRole('button', { name: 'Save salary change' }))
    const message = sheet().getByText('Salary is already this amount')
    await message.waitFor({ timeout: 20_000 })
    // Park the cursor just after the text (not on it) so the whole message stays readable.
    const end = await message.evaluate((el) => {
      const range = document.createRange()
      range.selectNodeContents(el)
      const box = range.getBoundingClientRect()
      return { x: box.right, y: box.top + box.height / 2 }
    })
    await moveTo(end.x + 60, end.y, 6) // a short hop: it must arrive well before the step ends
  },
  async search({ endAt }) {
    await page.keyboard.press('Escape') // close the profile
    await sleep(700)
    await page.keyboard.press('Control+k')
    const box = page.getByPlaceholder('Search people or pages…')
    await box.waitFor({ timeout: 10_000 })
    await box.pressSequentially('patel', { delay: 140 })
    await page.getByRole('option').first().waitFor({ timeout: 15_000 })
    await hover(page.getByRole('option').first())
    await until(endAt - 0.5)
    await page.keyboard.press('Escape')
  },
  async ask() {
    await sleep(500)
    await click(page.getByRole('link', { name: 'Ask ACME Pay' }))
    await page.waitForSelector('text=Where do we pay Data Scientists', { timeout: 20_000 })
    await sleep(1500)
    await click(page.getByRole('button', { name: /Where do we pay Data Scientists/ }))
  },
  async answer({ endAt }) {
    await page.waitForSelector('section[aria-label="Answer"]', { timeout: 90_000 })
    await sleep(600)
    await scrollBy(300, 1200)
    await hover(page.getByText('Role pay by country'))
    // GitHub is slow to load; start early so the next page is on screen when its sentence begins.
    await until(endAt - GITHUB_LOAD)
    await go(`${REPO}/commits/main`, 'text=Commits', { restorePointer: false })
  },
  async commits({ endAt }) {
    await sleep(500)
    await moveTo(1300, 420, 30) // an empty margin, clear of links and their hover cards
    await scrollBy(560, Math.max(1500, (endAt - GITHUB_LOAD_WARM - now()) * 1000))
    await go(`${REPO}/tree/main/docs`, 'text=architecture.md', { restorePointer: false })
  },
  async outro() {
    await sleep(900)
    await moveTo(520, 520, 40)
  },
}

// ---- run ----
await page.goto(BASE + '/', { waitUntil: 'domcontentloaded' })
await page.waitForSelector('text=Where to look', { timeout: 45_000 })
await page.evaluate(() => window.__setTitle(true))
const trimStart = now()

const timeline = []
for (const beat of plan.beats) {
  const clip = clips[beat.id]
  const beatStart = now()
  timeline.push({ id: beat.id, start: beatStart + AUDIO_DELAY, file: clip.file, seconds: clip.seconds })

  const weights = beat.steps.map((step) => step.say.replace(/\s/g, '').length)
  const total = weights.reduce((a, b) => a + b, 0)
  const speech = clip.seconds - LEAD
  const spans = []
  let before = 0
  for (const [index, step] of beat.steps.entries()) {
    const startAt = beatStart + AUDIO_DELAY + LEAD + (before / total) * speech
    before += weights[index]
    spans.push({ step, startAt, endAt: beatStart + AUDIO_DELAY + LEAD + (before / total) * speech })
  }
  // Captions follow the voice on their own timers, whatever the actions are doing.
  const timers = spans.map(({ step, startAt }) =>
    setTimeout(() => {
      captionText = step.say
      page.evaluate((t) => window.__setCaption?.(t), step.say).catch(() => {})
    }, Math.max(0, (startAt - 0.1 - now()) * 1000)),
  )
  for (const { step, startAt, endAt } of spans) {
    await until(startAt - 0.1)
    try {
      await actions[step.id]?.({ endAt })
    } catch (error) {
      const message = firstLine(error)
      failures.push({ step: step.id, at: now(), message })
      console.log(`!! step "${step.id}" failed: ${message}`)
    }
    const late = now() - endAt
    console.log(`  ${now().toFixed(1)}s  step ${step.id.padEnd(10)} (speech ends ${endAt.toFixed(1)}s${late > 0.5 ? `, action ran ${late.toFixed(1)}s long` : ''})`)
  }
  timers.forEach(clearTimeout)
  await until(beatStart + AUDIO_DELAY + clip.seconds + TAIL_PAUSE)
  console.log(`${now().toFixed(1)}s  beat ${beat.id} done`)
}

await setCaption('')
await sleep(1200)
const video = page.video()
await context.close()
const videoPath = await video.path()
writeFileSync(
  new URL('timeline.json', here),
  JSON.stringify({ videoPath, trimStart, marks, duration: now(), timeline, failures }, null, 2),
)
await browser.close()
console.log(`recorded ${now().toFixed(0)}s, ${failures.length} failed steps -> ${videoPath}`)
