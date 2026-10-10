import { Route, Routes } from 'react-router-dom'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import { Separator } from '@/components/ui/separator'
import { AppSidebar } from '@/components/AppSidebar'
import Home from '@/pages/Home'
import Catalog from '@/pages/Catalog'
import Scoreboard from '@/pages/Scoreboard'

export default function App() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-12 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger />
          <Separator orientation="vertical" className="h-6" />
          <span className="text-sm font-medium text-muted-foreground">
            Touch Grass: Play Outside
          </span>
        </header>
        <div className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/catalog" element={<Catalog />} />
            <Route path="/scoreboard" element={<Scoreboard />} />
          </Routes>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
