import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api, type Schemas, unwrap } from '@/lib/api'

const byId = (employeeId: string) => ({ params: { path: { employee_id: employeeId } } })

/** One employee's record. */
export function useEmployee(employeeId: string) {
  return useQuery({
    queryKey: ['employee', employeeId],
    queryFn: () => unwrap(api.GET('/api/employees/{employee_id}', byId(employeeId))),
  })
}

/** Where the employee's salary sits among their peers. */
export function usePayPosition(employeeId: string) {
  return useQuery({
    queryKey: ['employee', employeeId, 'pay-position'],
    queryFn: () => unwrap(api.GET('/api/employees/{employee_id}/pay-position', byId(employeeId))),
  })
}

/** The employee's salary history, newest first. */
export function useSalaryHistory(employeeId: string) {
  return useQuery({
    queryKey: ['employee', employeeId, 'compensation'],
    queryFn: () => unwrap(api.GET('/api/employees/{employee_id}/compensation', byId(employeeId))),
  })
}

/** The effect of a proposed salary, computed by the API without saving it. */
export function useSalaryPreview(employeeId: string, newSalary: string | undefined) {
  return useQuery({
    queryKey: ['employee', employeeId, 'preview', newSalary],
    queryFn: () =>
      unwrap(
        api.POST('/api/employees/{employee_id}/compensation/preview', {
          ...byId(employeeId),
          body: { new_salary: newSalary ?? '' },
        }),
      ),
    enabled: newSalary !== undefined,
    retry: false,
  })
}

/** Give the employee a new salary; refreshes everything that depends on pay. */
export function useChangeSalary(employeeId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: Schemas['SalaryChangeRequest']) =>
      unwrap(api.POST('/api/employees/{employee_id}/compensation', { ...byId(employeeId), body })),
    onSuccess: () => queryClient.invalidateQueries(),
  })
}

/** Update profile fields. */
export function useUpdateEmployee(employeeId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: Schemas['EmployeeUpdate']) =>
      unwrap(api.PATCH('/api/employees/{employee_id}', { ...byId(employeeId), body })),
    onSuccess: () => queryClient.invalidateQueries(),
  })
}

/** Record that the employee has left. */
export function useTerminateEmployee(employeeId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: Schemas['TerminationRequest']) =>
      unwrap(api.POST('/api/employees/{employee_id}/terminate', { ...byId(employeeId), body })),
    onSuccess: () => queryClient.invalidateQueries(),
  })
}
