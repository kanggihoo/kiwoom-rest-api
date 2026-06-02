"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export type SwitchProps = React.InputHTMLAttributes<HTMLInputElement> & {
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
};

const Switch = React.forwardRef<HTMLInputElement, SwitchProps>(
  ({ className, checked, onCheckedChange, onChange, ...props }, ref) => (
    <label className={cn("relative inline-flex cursor-pointer items-center", className)}>
      <input
        ref={ref}
        type="checkbox"
        role="switch"
        aria-checked={checked}
        className="peer sr-only"
        checked={checked}
        onChange={(event) => {
          onCheckedChange?.(event.currentTarget.checked);
          onChange?.(event);
        }}
        {...props}
      />
      <span
        className={cn(
          "h-5 w-9 rounded-full border border-border bg-muted transition-colors peer-checked:bg-primary",
          checked ? "bg-primary" : "bg-muted",
        )}
      />
      <span
        className={cn(
          "absolute left-0.5 top-0.5 h-4 w-4 rounded-full bg-white transition-transform",
          checked ? "translate-x-4" : "translate-x-0",
        )}
      />
    </label>
  ),
);
Switch.displayName = "Switch";

export { Switch };
