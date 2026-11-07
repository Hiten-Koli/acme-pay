import { useQuery } from '@tanstack/react-query'
import { fetchHealth } from './api'

/** Shows whether the API and its database are reachable. */
export function ApiStatus() {
  const { data, isPending, isError } = useQuery({ queryKey: ['health'], queryFn: fetchHealth })

  if (isPending) return <p role="status">Checking system status…</p>
  if (isError) return <p role="status">API unreachable</p>
  if (data.status === 'ok') return <p role="status">All systems operational</p>
  return <p role="status">Database unavailable</p>
}
