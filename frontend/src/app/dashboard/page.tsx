import { AppSidebar } from "@/components/ui/app-sidebar"
import { ChartAreaInteractive } from "@/components/ui/chart-area-interactive"
import { SectionCards } from "@/components/ui/section-cards"
import { SiteHeader } from "@/components/ui/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { ScoredLeadDataTable } from "@/components/dashboard/tables/ScoredLeadDataTable"

async function getTrendData() {
  const backendUrl = "http://backend:8000";
  const res = await fetch(`${backendUrl}/api/analytics/funnel-over-time?days=30`, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}

async function getTableData() {
  const backendUrl = "http://backend:8000";
  const res = await fetch(`${backendUrl}/api/analytics/scored-leads-table`, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}

export default async function Dashboard() {
  const trendData = await getTrendData();
  const tableData = await getTableData();

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": "calc(var(--spacing) * 72)",
          "--header-height": "calc(var(--spacing) * 12)",
        } as React.CSSProperties
      }
    >
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader />
        <div className="flex flex-1 flex-col">
          <div className="@container/main flex flex-1 flex-col gap-2">
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
              <SectionCards />
              <div className="px-4 lg:px-6">
                <ChartAreaInteractive data={trendData} />
              </div>
              <ScoredLeadDataTable data={tableData} />
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
