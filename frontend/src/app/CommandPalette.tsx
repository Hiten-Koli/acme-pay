import { useQuery } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { BarChart3, Gauge, Search, Users } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import { api, unwrap } from '@/lib/api'
import { useDebounced } from '@/lib/useDebounced'

const PAGES = [
  { label: 'Pay Pulse', to: '/', icon: Gauge },
  { label: 'People', to: '/people', icon: Users },
  { label: 'Benchmarks', to: '/benchmarks', icon: BarChart3 },
] as const
const RESULT_LIMIT = 6

/** ⌘K / Ctrl+K: jump to a page or straight to an employee's profile. */
export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const [term, setTerm] = useState('')
  const search = useDebounced(term.trim())
  const navigate = useNavigate()

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key.toLowerCase() === 'k' && (event.metaKey || event.ctrlKey)) {
        event.preventDefault()
        setOpen((current) => !current)
      }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [])

  const people = useQuery({
    queryKey: ['palette', search],
    queryFn: () =>
      unwrap(api.GET('/api/employees', { params: { query: { search, page_size: RESULT_LIMIT } } })),
    enabled: open && search.length > 1,
  })

  const close = () => {
    setOpen(false)
    setTerm('')
  }
  const pages = PAGES.filter((page) => page.label.toLowerCase().includes(term.toLowerCase()))

  return (
    <>
      <Button
        variant="outline"
        className="w-full justify-start text-muted-foreground"
        onClick={() => setOpen(true)}
      >
        <Search />
        Search…
        <kbd className="ml-auto rounded border px-1.5 text-[10px]">Ctrl K</kbd>
      </Button>
      <CommandDialog open={open} onOpenChange={(next) => (next ? setOpen(true) : close())}>
        <CommandInput placeholder="Search people or pages…" value={term} onValueChange={setTerm} />
        <CommandList>
          <CommandEmpty>{people.isFetching ? 'Searching…' : 'No results.'}</CommandEmpty>
          {pages.length > 0 && (
            <CommandGroup heading="Pages">
              {pages.map(({ label, to, icon: Icon }) => (
                <CommandItem
                  key={to}
                  value={`page-${label}`}
                  onSelect={() => {
                    close()
                    void navigate({ to })
                  }}
                >
                  <Icon />
                  {label}
                </CommandItem>
              ))}
            </CommandGroup>
          )}
          {people.data && people.data.items.length > 0 && (
            <CommandGroup heading="People">
              {people.data.items.map((person) => (
                <CommandItem
                  key={person.id}
                  value={`person-${person.id}`}
                  onSelect={() => {
                    close()
                    void navigate({ to: '/people', search: { employee: person.id } })
                  }}
                >
                  <Users />
                  {person.first_name} {person.last_name}
                  <span className="ml-auto text-xs text-muted-foreground">
                    {person.job_title} · {person.country_code}
                  </span>
                </CommandItem>
              ))}
            </CommandGroup>
          )}
        </CommandList>
      </CommandDialog>
    </>
  )
}
