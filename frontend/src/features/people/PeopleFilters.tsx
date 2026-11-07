import { Search } from 'lucide-react'
import { useEffect, useState } from 'react'
import type { PeopleSearch } from '@/app/router'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useOptions } from '@/features/meta/useOptions'
import { useDebounced } from '@/lib/useDebounced'

const ALL = '__all__'

function FilterSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string
  value: string | undefined
  options: { value: string; label: string }[]
  onChange: (value: string | undefined) => void
}) {
  return (
    <Select
      value={value ?? ALL}
      onValueChange={(next) => onChange(next === ALL ? undefined : next)}
    >
      <SelectTrigger aria-label={label} className="w-full sm:w-44">
        <SelectValue placeholder={label} />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value={ALL}>All {label.toLowerCase()}</SelectItem>
        {options.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

/** Search box and dropdown filters; every choice is reflected in the URL. */
export function PeopleFilters({
  search,
  onChange,
}: {
  search: PeopleSearch
  onChange: (changes: Partial<PeopleSearch>) => void
}) {
  const options = useOptions()
  const [term, setTerm] = useState(search.search ?? '')
  const debounced = useDebounced(term.trim())

  useEffect(() => {
    if (debounced !== (search.search ?? '')) onChange({ search: debounced || undefined })
  }, [debounced, search.search, onChange])

  const toOptions = (values: string[] | undefined) =>
    (values ?? []).map((value) => ({ value, label: value }))

  return (
    <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
      <div className="relative flex-1 sm:min-w-64">
        <Search
          aria-hidden
          className="absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
        />
        <Input
          type="search"
          aria-label="Search by name, email or employee code"
          placeholder="Search name, email or code…"
          className="pl-8"
          value={term}
          onChange={(event) => setTerm(event.target.value)}
        />
      </div>
      <FilterSelect
        label="Countries"
        value={search.country}
        options={(options.data?.countries ?? []).map((country) => ({
          value: country.code,
          label: `$${country.name}`,
        }))}
        onChange={(country) => onChange({ country })}
      />
      <FilterSelect
        label="Departments"
        value={search.department}
        options={toOptions(options.data?.departments)}
        onChange={(department) => onChange({ department })}
      />
      <FilterSelect
        label="Job titles"
        value={search.job_title}
        options={toOptions(options.data?.job_titles)}
        onChange={(job_title) => onChange({ job_title })}
      />
      <FilterSelect
        label="Statuses"
        value={search.status}
        options={[{ value: 'terminated', label: 'Leavers only' }]}
        onChange={(status) => onChange({ status: status as PeopleSearch['status'] })}
      />
    </div>
  )
}
