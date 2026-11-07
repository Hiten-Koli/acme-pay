// Phase 1: read the live app and write plan.json (data for the walkthrough + narration text).
// The narration is built from real API numbers, so what is said always matches the screen.
import { writeFileSync } from 'node:fs'

const BASE = process.env.DEMO_BASE_URL ?? 'https://acme-pay-hiten.vercel.app'

const get = async (path) => {
  const response = await fetch(BASE + path)
  if (!response.ok) throw new Error(`GET ${path} -> ${response.status}`)
  return response.json()
}
const post = async (path, body) => {
  const response = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) throw new Error(`POST ${path} -> ${response.status}`)
  return response.json()
}

const CURRENCY_NAMES = {
  USD: 'US dollars',
  CAD: 'Canadian dollars',
  BRL: 'Brazilian reais',
  GBP: 'pounds',
  EUR: 'euros',
  INR: 'Indian rupees',
  SGD: 'Singapore dollars',
  JPY: 'yen',
  AUD: 'Australian dollars',
}

const withCommas = (n) => Math.round(Number(n)).toLocaleString('en-US')
const thousands = (n) => `${Math.round(Number(n) / 1000)} thousand`
/** Spoken form of a money amount: "2.5 million Indian rupees". */
function spoken(amount, currency) {
  const n = Number(amount)
  const value = n >= 1e6 ? `${(n / 1e6).toFixed(1)} million` : thousands(n)
  return `${value} ${CURRENCY_NAMES[currency] ?? currency}`
}

const pulse = await get('/api/insights/pulse')
const options = await get('/api/meta/options')
const countryName = (code) => {
  const name = options.countries.find((c) => c.code === code)?.name ?? code
  return /^United /.test(name) ? `the ${name}` : name
}

const signal = pulse.signals[0]
const benchmarks = await get(
  `/api/insights/benchmarks?job_title=${encodeURIComponent(signal.job_title)}`,
)
const ranked = [...benchmarks.countries].sort((a, b) => Number(b.median_usd) - Number(a.median_usd))
const top = ranked[0]
const bottom = ranked.at(-1)

const outliers = await get(
  `/api/insights/outliers?band=below&country=${signal.country_code}&job_title=${encodeURIComponent(signal.job_title)}`,
)
const person = outliers[0]
const position = await get(`/api/employees/${person.id}/pay-position`)
const peerMedian = Number(position.peers.median)
// A round amount, so what is typed on screen is exactly what is said aloud.
const target = peerMedian * 0.9
const newSalary = String(
  target >= 1e6 ? Math.round(target / 1e5) * 1e5 : Math.round(target / 1e3) * 1e3,
)
const preview = await post(`/api/employees/${person.id}/compensation/preview`, {
  new_salary: newSalary,
})

const outside = pulse.below_band + pulse.above_band
const job = signal.job_title
const landing =
  preview.proposed.band === 'within' ? 'lands within band' : `would be ${preview.proposed.band} band`

const say = {
  title: `This is ACME Pay: salary management for an HR team that looks after about ten thousand people in ten countries.`,
  problem: `Today that lives in spreadsheets. Even a simple question, like are we paying people fairly, takes hours of pivot tables. ACME Pay starts from the questions instead.`,
  figures: `Pay Pulse shows the whole organization at a glance: ${withCommas(pulse.headcount)} active people, ${Math.round(Number(pulse.payroll_usd) / 1e6)} million dollars a year in payroll, and a median salary of ${withCommas(pulse.median_salary_usd)} dollars.`,
  band: `${withCommas(outside)} people sit outside their pay band, meaning they are paid more than twenty percent away from the median for the same role in the same country.`,
  signal: `The where-to-look list points at the biggest gaps. For example, ${signal.below_band} of ${signal.headcount} ${job}s in ${countryName(signal.country_code)} are paid below band.`,
  benchmarks: `Following that signal opens Benchmarks. In US dollars, a ${job} earns a median of ${thousands(top.median_usd)} dollars in ${countryName(top.country_code)}, but only ${thousands(bottom.median_usd)} in ${countryName(bottom.country_code)}.`,
  outliers: `Further down are the salary distribution, and the people furthest outside the band. Let's open ${person.first_name} ${person.last_name}, who is paid ${person.compa_ratio} times the median.`,
  profile: `Here ${person.first_name} is shown against colleagues with the same role in the same country. The dot is far left of the shaded middle half of peers, and the badge says below band.`,
  preview: `Before changing anything, I can preview a raise. Entering ${spoken(newSalary, person.currency)} is a ${Number(preview.change_percent).toFixed(0)} percent increase, about ${withCommas(preview.annual_cost_change_usd)} dollars more a year, and it ${landing}. Nothing is saved yet.`,
  save: `Saving records the change in the pay history, with the reason, the date and who made it, and every pay view refreshes.`,
  rule: `The rules live in the API, not just the form. Submitting the same amount again is rejected with a clear message.`,
  search: `Anyone is a keystroke away with Control K. Search finds people by name, email or employee code, from any page.`,
  ask: `Ask ACME Pay answers questions in plain English. The model never sees individual employees and never writes SQL. It can only call four tested, aggregate-only queries.`,
  answer: `Every answer comes with the data behind it, so HR can check the numbers instead of trusting the text.`,
  commits: `Under the hood, the code is built test-first. For every rule, the failing test is committed before the implementation.`,
  outro: `Requirements, architecture decisions, measured performance and a log of where AI output was corrected are all in the repository. Thanks for watching.`,
}

// 8 clips (one TTS request each, a free-tier budget of 10/day per model). Each clip has steps:
// one caption + one on-screen action per step, timed by the step's share of the clip.
const beats = [
  { id: 'intro', steps: ['title', 'problem'] },
  { id: 'pulse', steps: ['figures', 'band'] },
  { id: 'signal', steps: ['signal', 'benchmarks'] },
  { id: 'person', steps: ['outliers', 'profile'] },
  { id: 'raise', steps: ['preview', 'save'] },
  { id: 'rules', steps: ['rule', 'search'] },
  { id: 'ask', steps: ['ask', 'answer'] },
  { id: 'close', steps: ['commits', 'outro'] },
].map((beat) => ({
  id: beat.id,
  steps: beat.steps.map((id) => ({ id, say: say[id] })),
  text: beat.steps.map((id) => say[id]).join(' '),
}))

const plan = {
  base: BASE,
  beats,
  data: {
    signal,
    person: { id: person.id, name: `${person.first_name} ${person.last_name}`, currency: person.currency },
    newSalary,
    previewBand: preview.proposed.band,
  },
}
writeFileSync(new URL('./plan.json', import.meta.url), JSON.stringify(plan, null, 2))
const words = beats.map((beat) => beat.text.split(/\s+/).length)
console.log(`plan written: ${beats.length} clips, words per clip: ${words.join(', ')} (total ${words.reduce((a, b) => a + b)})`)
console.log('person:', plan.data.person.name, '| new salary:', newSalary, '| preview band:', preview.proposed.band)
