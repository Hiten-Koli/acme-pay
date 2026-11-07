import { Link, Outlet } from '@tanstack/react-router'
import { BarChart3, Gauge, Users } from 'lucide-react'
import { CommandPalette } from '@/app/CommandPalette'
import { ThemeToggle } from '@/app/ThemeToggle'
import { Toaster } from '@/components/ui/sonner'
import { ApiStatus } from '@/features/health/ApiStatus'

const NAV = [
  { to: '/', label: 'Pay Pulse', icon: Gauge },
  { to: '/people', label: 'People', icon: Users },
  { to: '/benchmarks', label: 'Benchmarks', icon: BarChart3 },
] as const

/** Layout: navigation sidebar and the current page. */
export function AppShell() {
  return (
    <div className="flex min-h-svh flex-col md:flex-row">
      <aside className="flex shrink-0 flex-col gap-4 border-b bg-sidebar p-4 md:w-60 md:border-r md:border-b-0">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-semibold">
            <img src="/favicon.svg" alt="" className="size-6" />
            ACME Pay
          </Link>
          <ThemeToggle />
        </div>
        <CommandPalette />
        <nav aria-label="Main" className="flex gap-1 md:flex-col">
          {NAV.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              activeOptions={{ exact: to === '/' }}
              className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm text-muted-foreground hover:bg-sidebar-accent hover:text-foreground data-[status=active]:bg-sidebar-accent data-[status=active]:font-medium data-[status=active]:text-foreground"
            >
              <Icon aria-hidden className="size-4" />
              {label}
            </Link>
          ))}
        </nav>
        <div className="mt-auto hidden text-xs text-muted-foreground md:block">
          <ApiStatus />
          <p className="mt-1">Synthetic data · HR Manager</p>
        </div>
      </aside>
      <main className="min-w-0 flex-1 p-4 md:p-8">
        <div className="mx-auto flex max-w-6xl flex-col gap-6">
          <Outlet />
        </div>
      </main>
      <Toaster />
    </div>
  )
}
