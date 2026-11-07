// Injected into every page of the recording: captions, a visible cursor, and a title card.
;(() => {
  if (window.__demoInstalled) return
  window.__demoInstalled = true
  const style = (el, css) => Object.assign(el.style, css)
  let caption
  let cursor
  let title

  function mount() {
    if (caption || !document.documentElement) return
    caption = document.createElement('div')
    style(caption, {
      position: 'fixed',
      left: '50%',
      bottom: '26px',
      transform: 'translateX(-50%)',
      width: 'max-content',
      maxWidth: '1100px',
      padding: '12px 24px',
      borderRadius: '12px',
      background: 'rgba(15, 15, 20, 0.84)',
      color: '#fff',
      font: '500 23px/1.38 "Segoe UI", system-ui, sans-serif',
      textAlign: 'center',
      boxShadow: '0 6px 24px rgba(0,0,0,.35)',
      zIndex: '2147483646',
      pointerEvents: 'none',
      display: 'none',
    })
    cursor = document.createElement('div')
    style(cursor, {
      position: 'fixed',
      left: '-50px',
      top: '-50px',
      width: '24px',
      height: '24px',
      marginLeft: '-12px',
      marginTop: '-12px',
      borderRadius: '50%',
      background: 'rgba(37, 99, 235, 0.28)',
      border: '2px solid #2563eb',
      boxShadow: '0 0 0 2px rgba(255,255,255,.7)',
      zIndex: '2147483647',
      pointerEvents: 'none',
      transition: 'left .07s linear, top .07s linear, transform .12s ease-out',
    })
    title = document.createElement('div')
    style(title, {
      position: 'fixed',
      inset: '0',
      display: 'none',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '18px',
      background: 'linear-gradient(135deg, #0b1220 0%, #1e2f6b 100%)',
      color: '#fff',
      fontFamily: '"Segoe UI", system-ui, sans-serif',
      zIndex: '2147483645',
    })
    title.innerHTML =
      '<div style="font-size:84px;font-weight:700;letter-spacing:-1px">ACME Pay</div>' +
      '<div style="font-size:30px;opacity:.9">Insight-first salary management for HR</div>' +
      '<div style="font-size:20px;opacity:.6;margin-top:26px">10,000 people · 10 countries · test-first</div>'
    document.documentElement.append(title, caption, cursor)
  }

  window.__setCaption = (text) => {
    mount()
    caption.textContent = text || ''
    caption.style.display = text ? 'block' : 'none'
  }
  window.__setTitle = (on) => {
    mount()
    title.style.display = on ? 'flex' : 'none'
  }

  addEventListener(
    'mousemove',
    (event) => {
      mount()
      cursor.style.left = `${event.clientX}px`
      cursor.style.top = `${event.clientY}px`
    },
    true,
  )
  addEventListener('mousedown', () => cursor && (cursor.style.transform = 'scale(.65)'), true)
  addEventListener('mouseup', () => cursor && (cursor.style.transform = 'scale(1)'), true)
  document.addEventListener('DOMContentLoaded', mount)
})()
