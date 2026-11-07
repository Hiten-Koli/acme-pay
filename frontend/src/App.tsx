import { RouterProvider } from '@tanstack/react-router'
import { router } from '@/app/router'
import { TooltipProvider } from '@/components/ui/tooltip'

/** Root component: routing and shared UI providers. */
export default function App() {
  return (
    <TooltipProvider>
      <RouterProvider router={router} />
    </TooltipProvider>
  )
}
