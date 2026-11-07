import { Link } from '@tanstack/react-router'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import type { Schemas } from '@/lib/api'
import { formatCount, formatMoney } from '@/lib/format'

/** Headcount and pay per department, with a link into the directory. */
export function DepartmentTable({ departments }: { departments: Schemas['DepartmentPay'][] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>By department</CardTitle>
        <CardDescription>Sorted by payroll, USD</CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Department</TableHead>
              <TableHead className="text-right">Headcount</TableHead>
              <TableHead className="text-right">Median salary</TableHead>
              <TableHead className="text-right">Payroll</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {departments.map((row) => (
              <TableRow key={row.department}>
                <TableCell>
                  <Link
                    to="/people"
                    search={{ department: row.department }}
                    className="font-medium hover:underline"
                  >
                    {row.department}
                  </Link>
                </TableCell>
                <TableCell className="text-right tabular-nums">
                  {formatCount(row.headcount)}
                </TableCell>
                <TableCell className="text-right tabular-nums">
                  {formatMoney(row.median_salary_usd, 'USD')}
                </TableCell>
                <TableCell className="text-right tabular-nums">
                  {formatMoney(row.payroll_usd, 'USD', { compact: true })}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
