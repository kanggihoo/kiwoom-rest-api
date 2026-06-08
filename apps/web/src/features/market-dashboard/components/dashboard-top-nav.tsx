import { Bell, Moon, RefreshCw, Search, Sun } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const navItems = ["마켓", "관심", "설정"];

export function DashboardTopNav() {
  return (
    <TooltipProvider>
      <header className="sticky top-0 z-10 border-b border-border bg-card/95">
        <div className="grid h-[68px] grid-cols-[auto_minmax(280px,1fr)_auto] items-center gap-6 px-5">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-3">
              <div className="flex size-8 items-center justify-center rounded-[10px] bg-primary">
                <span className="size-4 rotate-45 rounded-[3px] border border-primary-foreground/80" />
              </div>
              <strong className="text-[22px] font-extrabold tracking-normal">마켓뷰</strong>
            </div>
            <nav className="flex h-[68px] items-center gap-6" aria-label="Primary">
              {navItems.map((item) => (
                <Button
                  key={item}
                  variant="ghost"
                  className="h-[68px] rounded-none border-b-[3px] border-transparent px-1 text-[15px] font-bold data-[active=true]:border-primary data-[active=true]:text-primary"
                  data-active={item === "마켓"}
                >
                  {item}
                </Button>
              ))}
            </nav>
          </div>

          <div className="mx-auto w-full max-w-[430px]">
            <InputGroup className="h-10 rounded-full bg-background shadow-[inset_0_0_0_1px_var(--border)]">
              <InputGroupAddon>
                <Search data-icon="inline-start" />
              </InputGroupAddon>
              <InputGroupInput placeholder="마켓명 또는 심볼 검색" aria-label="Market search" />
              <InputGroupAddon>
                <span className="rounded-md bg-muted px-2 py-0.5 text-[13px] font-bold text-muted-foreground">
                  /
                </span>
              </InputGroupAddon>
            </InputGroup>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center rounded-full border border-border bg-background p-1">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" className="size-8 rounded-full" aria-label="밝은 테마">
                    <Sun data-icon="icon" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>밝은 테마</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="secondary" size="icon" className="size-8 rounded-full" aria-label="어두운 테마">
                    <Moon data-icon="icon" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>어두운 테마</TooltipContent>
              </Tooltip>
            </div>
            <Separator orientation="vertical" className="h-5" />
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="알림">
                  <Bell data-icon="icon" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>알림</TooltipContent>
            </Tooltip>
            <Separator orientation="vertical" className="h-5" />
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="새로고침">
                  <RefreshCw data-icon="icon" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>새로고침</TooltipContent>
            </Tooltip>
            <div className="flex items-center gap-2 pl-1 text-[13px] font-bold text-foreground">
              <span className="size-2 rounded-full bg-emerald-500" />
              실시간
            </div>
          </div>
        </div>
      </header>
    </TooltipProvider>
  );
}
