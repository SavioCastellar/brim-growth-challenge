import { Separator } from "@/components/ui/separator"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Button } from "./button"
import { Popover, PopoverContent, PopoverTrigger } from "@radix-ui/react-popover"
import { BatchScoreUploader } from "../dashboard/BatchScoreUploader"

export function SiteHeader() {
  return (
    <header className="flex h-(--header-height) shrink-0 items-center gap-2 border-b transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-(--header-height)">
      <div className="flex w-full items-center gap-1 px-4 lg:gap-2 lg:px-6">
        <SidebarTrigger className="-ml-1" />
        <Separator
          orientation="vertical"
          className="mx-2 data-[orientation=vertical]:h-4"
        />
        <h1 className="text-base font-medium">Dashboard</h1>
      </div>
      <div className="ml-auto flex items-center gap-2 mr-6">
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="sm" className="hidden sm:flex dark:text-foreground">
              Upload Leads
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-96 bg-background border border-border shadow-lg p-8">
            <BatchScoreUploader />
          </PopoverContent>
        </Popover>
      </div>
    </header>
  )
}
