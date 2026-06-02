import * as React from "react";
import { cn } from "@/lib/utils";

const TooltipProvider = ({ children }: { children: React.ReactNode }) => <>{children}</>;
TooltipProvider.displayName = "TooltipProvider";

const Tooltip = ({ children, className }: { children: React.ReactNode; className?: string }) => {
  const [trigger, content] = React.Children.toArray(children);
  return (
    <span className={cn("group relative inline-flex", className)}>
      <span className="inline-flex">{trigger}</span>
      {content ? (
        <span className="pointer-events-none absolute right-0 top-full z-10 mt-2 hidden rounded-md bg-popover px-2 py-1 text-xs text-popover-foreground group-hover:block">
          {content}
        </span>
      ) : null}
    </span>
  );
};
Tooltip.displayName = "Tooltip";

const TooltipTrigger = React.forwardRef<
  HTMLSpanElement,
  React.HTMLAttributes<HTMLSpanElement> & { asChild?: boolean }
>(({ className, ...props }, ref) => {
  return <span ref={ref} className={cn("group inline-flex", className)} {...props} />;
});
TooltipTrigger.displayName = "TooltipTrigger";

const TooltipContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("rounded-md border border-border bg-popover px-2 py-1 text-xs text-popover-foreground", className)}
      {...props}
    />
  ),
);
TooltipContent.displayName = "TooltipContent";

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider };
