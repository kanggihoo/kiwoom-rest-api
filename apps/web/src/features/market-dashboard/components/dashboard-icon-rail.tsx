import { Clock, Settings, Star, UserRound } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const railItems = [
  { label: "내 정보", icon: UserRound, active: true },
  { label: "관심", icon: Star, active: false },
  { label: "최근", icon: Clock, active: false },
  { label: "설정", icon: Settings, active: false },
];

export function DashboardIconRail() {
  return (
    <TooltipProvider>
      <aside className="hidden h-full min-h-[680px] flex-col items-center gap-5 rounded-md border border-border bg-card py-4 xl:flex">
        {railItems.map((item) => {
          const Icon = item.icon;

          return (
            <Tooltip key={item.label}>
              <TooltipTrigger asChild>
                <Button
                  variant={item.active ? "default" : "ghost"}
                  size="icon"
                  className="rounded-[10px]"
                  aria-label={item.label}
                >
                  <Icon data-icon="icon" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>{item.label}</TooltipContent>
            </Tooltip>
          );
        })}
      </aside>
    </TooltipProvider>
  );
}
