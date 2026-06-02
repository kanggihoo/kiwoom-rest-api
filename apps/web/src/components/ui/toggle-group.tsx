"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

type ToggleGroupContextValue = {
  value?: string;
  type?: "single" | "multiple";
};

const ToggleGroupContext = React.createContext<ToggleGroupContextValue>({});

type ToggleGroupProps = {
  type?: "single" | "multiple";
  value?: string;
  className?: string;
  children: React.ReactNode;
};

const ToggleGroup = ({ type = "single", value, className, children }: ToggleGroupProps) => (
  <ToggleGroupContext.Provider value={{ type, value }}>
    <div role={type === "single" ? "radiogroup" : "group"} className={cn("inline-flex", className)}>
      {children}
    </div>
  </ToggleGroupContext.Provider>
);

type ToggleGroupItemProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  value: string;
};

const ToggleGroupItem = React.forwardRef<HTMLButtonElement, ToggleGroupItemProps>(
  ({ className, value, ...props }, ref) => {
    const context = React.useContext(ToggleGroupContext);
    const isActive = context.value === value;
    return (
      <button
        ref={ref}
        type="button"
        role={context.type === "single" ? "radio" : "button"}
        aria-checked={context.type === "single" ? isActive : undefined}
        className={cn(
          "inline-flex items-center justify-center rounded-md border border-border bg-card transition-colors",
          isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:bg-accent/80",
          className,
        )}
        data-active={isActive}
        {...props}
      />
    );
  },
);
ToggleGroupItem.displayName = "ToggleGroupItem";

export { ToggleGroup, ToggleGroupItem };
