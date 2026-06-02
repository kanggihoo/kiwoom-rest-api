import {
  Bell,
  ChevronDown,
  Globe,
  Moon,
  Search,
  Sun,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const navItems = ["마켓", "거래", "입출금", "투자내역", "코인동향", "서비스"];

export function DashboardTopNav() {
  return (
    <TooltipProvider>
      <header className="sticky top-0 z-10 border-b border-border bg-card">
        <div className="grid h-[60px] grid-cols-[auto_1fr_auto] items-center gap-6 px-5">
          <div className="flex items-center gap-5">
            <Button className="size-8 rounded-[10px]" size="icon" aria-label="Upbit dashboard">
              <span className="size-3 rounded-[4px] border border-primary-foreground/60" />
            </Button>
            <nav className="flex items-center gap-1" aria-label="Primary">
              {navItems.map((item) => (
                <Button
                  key={item}
                  variant="ghost"
                  className="h-[60px] rounded-none border-b-2 border-transparent px-4 text-[15px] font-semibold data-[active=true]:border-primary data-[active=true]:text-foreground"
                  data-active={item === "마켓"}
                >
                  {item}
                </Button>
              ))}
            </nav>
          </div>

          <div className="mx-auto w-full max-w-[420px]">
            <InputGroup className="h-10 rounded-full bg-muted">
              <InputGroupAddon>
                <Search data-icon="inline-start" />
              </InputGroupAddon>
              <InputGroupInput placeholder="코인명 또는 심볼 검색" aria-label="Market search" />
              <InputGroupAddon>
                <ChevronDown data-icon="inline-end" />
              </InputGroupAddon>
            </InputGroup>
          </div>

          <div className="flex items-center gap-3">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="밝은 테마">
                  <Sun data-icon="icon" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>밝은 테마</TooltipContent>
            </Tooltip>
            <Switch aria-label="테마 전환" checked />
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="어두운 테마">
                  <Moon data-icon="icon" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>어두운 테마</TooltipContent>
            </Tooltip>
            <Separator orientation="vertical" className="h-5" />
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="알림">
                  <Bell data-icon="icon" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>알림</TooltipContent>
            </Tooltip>
            <Button variant="ghost" className="gap-1 px-2">
              <Globe data-icon="inline-start" />
              KO
              <ChevronDown data-icon="inline-end" />
            </Button>
          </div>
        </div>
      </header>
    </TooltipProvider>
  );
}
