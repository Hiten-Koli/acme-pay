import { useMutation, useQuery } from '@tanstack/react-query'
import { api, unwrap } from '@/lib/api'

/** Whether an AI model is configured; the assistant is hidden otherwise. */
export function useAssistantStatus() {
  return useQuery({
    queryKey: ['assistant-status'],
    queryFn: () => unwrap(api.GET('/api/assistant/status')),
    staleTime: Number.POSITIVE_INFINITY,
  })
}

/** Ask a pay question; the answer comes with the data it is based on. */
export function useAsk() {
  return useMutation({
    mutationFn: (question: string) =>
      unwrap(api.POST('/api/assistant/ask', { body: { question } })),
  })
}
