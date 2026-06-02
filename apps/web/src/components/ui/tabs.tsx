"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

type TabContextValue = {
  value?: string;
};

const TabContext = React.createContext<TabContextValue>({ value: undefined });

export type TabsProps = {
  value?: string;
  className?: string;
  children: React.ReactNode;
};

const Tabs = ({ value, className, children }: TabsProps) => (
  <TabContext.Provider value={{ value }}>
    <div className={cn("inline-flex", className)}>{children}</div>
  </TabContext.Provider>
);

const TabsList = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex items-center", className)} role="tablist" {...props} />
  ),
);
TabsList.displayName = "TabsList";

type TabsTriggerProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  value: string;
};

const TabsTrigger = React.forwardRef<HTMLButtonElement, TabsTriggerProps>(
  ({ className, value, ...props }, ref) => {
    const context = React.useContext(TabContext);
    const isActive = context.value === value;
    return (
      <button
        ref={ref}
        role="tab"
        aria-selected={isActive}
        className={cn(
          "rounded-md px-3 py-2 text-sm font-medium data-[active=true]:bg-accent data-[active=true]:text-accent-foreground",
          isActive && "bg-accent text-accent-foreground",
          className,
        )}
        data-active={isActive}
        type="button"
        {...props}
      />
    );
  },
);
TabsTrigger.displayName = "TabsTrigger";

export { Tabs, TabsList, TabsTrigger };
