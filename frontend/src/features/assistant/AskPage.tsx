import { Sparkles } from 'lucide-react'
import { type FormEvent, useState } from 'react'
import { PageHeader } from '@/components/PageHeader'
import { EmptyState, ErrorState, LoadingBlock } from '@/components/QueryStates'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useAsk, useAssistantStatus } from './api'
import { EvidenceCard } from './EvidenceCard'

const SUGGESTIONS = [
  'Where do we pay Data Scientists the most, and the least?',
  'How many people are paid below their pay band?',
  'How are salaries spread out in India?',
  'What is our total payroll in USD, and which country costs most?',
]

/** Ask pay questions in plain English; answers come with the data behind them. */
export function AskPage() {
  const status = useAssistantStatus()
  const ask = useAsk()
  const [question, setQuestion] = useState('')

  const submit = (text: string) => {
    const trimmed = text.trim()
    if (!trimmed) return
    setQuestion(trimmed)
    ask.mutate(trimmed)
  }

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    submit(question)
  }

  return (
    <>
      <PageHeader
        title="Ask ACME Pay"
        description="Ask about pay in plain English. Every answer shows the data it is based on."
      />
      {status.data?.enabled === false && (
        <EmptyState
          title="The AI analyst is not configured"
          hint="Set GEMINI_API_KEY on the server to enable it. Everything else works without it."
        />
      )}
      {status.data?.enabled && (
        <>
          <form onSubmit={onSubmit} className="flex gap-2">
            <Input
              aria-label="Your question"
              placeholder="e.g. What's the median salary for Data Scientists in Germany vs the UK?"
              value={question}
              maxLength={500}
              onChange={(event) => setQuestion(event.target.value)}
            />
            <Button type="submit" disabled={ask.isPending || !question.trim()}>
              <Sparkles />
              {ask.isPending ? 'Thinking…' : 'Ask'}
            </Button>
          </form>
          {!ask.data && !ask.isPending && (
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS.map((suggestion) => (
                <Button
                  key={suggestion}
                  variant="outline"
                  size="sm"
                  onClick={() => submit(suggestion)}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          )}
          {ask.isPending && <LoadingBlock className="h-32" />}
          {ask.isError && <ErrorState error={ask.error} onRetry={() => submit(question)} />}
          {ask.data && (
            <section aria-label="Answer" className="flex flex-col gap-4">
              <Card>
                <CardContent className="flex gap-3">
                  <Sparkles aria-hidden className="mt-0.5 size-4 shrink-0 text-chart-1" />
                  <p className="leading-relaxed">{ask.data.answer}</p>
                </CardContent>
              </Card>
              {ask.data.evidence.length > 0 && (
                <>
                  <h2 className="text-sm font-medium text-muted-foreground">Based on</h2>
                  {ask.data.evidence.map((evidence) => (
                    <EvidenceCard
                      key={`${evidence.tool}:${JSON.stringify(evidence.arguments)}`}
                      evidence={evidence}
                    />
                  ))}
                </>
              )}
            </section>
          )}
        </>
      )}
    </>
  )
}
