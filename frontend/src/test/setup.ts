// Adds DOM matchers such as `toBeInTheDocument()` to Vitest's `expect`.
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Unmount after every test (automatic only when Vitest globals are enabled).
afterEach(cleanup)

// jsdom has no matchMedia; components that read the color-scheme preference need one.
if (!window.matchMedia) {
  window.matchMedia = (query: string) =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addEventListener: () => {},
      removeEventListener: () => {},
      addListener: () => {},
      removeListener: () => {},
      dispatchEvent: () => false,
    }) as MediaQueryList
}

// jsdom has no ResizeObserver; charts measure their container with it.
globalThis.ResizeObserver ??= class {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// jsdom does not implement scrollIntoView; cmdk calls it to keep the active item visible.
Element.prototype.scrollIntoView ??= () => {}
