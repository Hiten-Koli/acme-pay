import { Moon, Sun } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'

const STORAGE_KEY = 'acme-pay-theme'

function initialDark(): boolean {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) return stored === 'dark'
  } catch {
    // Storage can be unavailable (private mode); fall back to the OS preference.
  }
  return globalThis.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
}

/** Switch between light and dark themes, remembering the choice. */
export function ThemeToggle() {
  const [dark, setDark] = useState(initialDark)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    try {
      localStorage.setItem(STORAGE_KEY, dark ? 'dark' : 'light')
    } catch {
      // Not persisting the preference is harmless.
    }
  }, [dark])

  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={dark ? 'Switch to light theme' : 'Switch to dark theme'}
      onClick={() => setDark(!dark)}
    >
      {dark ? <Sun /> : <Moon />}
    </Button>
  )
}
