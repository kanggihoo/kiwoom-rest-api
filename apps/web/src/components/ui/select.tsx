"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

type SelectContextValue = {
  value?: string;
  onValueChange?: (value: string) => void;
};

const SelectContext = React.createContext<SelectContextValue>({});

type SelectProps = React.HTMLAttributes<HTMLDivElement> & {
  value?: string;
  onValueChange?: (value: string) => void;
};

const Select = ({ value, onValueChange, children, className, ...props }: SelectProps) => (
  <SelectContext.Provider value={{ value, onValueChange }}>
    <div className={cn("relative inline-flex flex-col", className)} {...props}>
      {children}
    </div>
  </SelectContext.Provider>
);
Select.displayName = "Select";

const SelectTrigger = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement>>(
  ({ className, ...props }, ref) => (
    <button
      ref={ref}
      type="button"
      className={cn(
        "inline-flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm",
        className,
      )}
      {...props}
    />
  ),
);
SelectTrigger.displayName = "SelectTrigger";

const SelectValue = ({
  placeholder,
  className,
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { placeholder?: string }) => {
  const { value } = React.useContext(SelectContext);
  return (
    <span className={cn("truncate", className)} {...props}>
      {value || placeholder}
    </span>
  );
};
SelectValue.displayName = "SelectValue";

const SelectContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("mt-1 rounded-md border border-border bg-popover p-1", className)}
      {...props}
    />
  ),
);
SelectContent.displayName = "SelectContent";

const SelectItem = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement> & { value: string }>(
  ({ className, value, ...props }, ref) => {
    const { value: selectedValue } = React.useContext(SelectContext);
    const isSelected = value === selectedValue;
    return (
      <div
        ref={ref}
        data-selected={isSelected}
        className={cn(
          "rounded-sm px-2 py-1.5 text-sm hover:bg-accent",
          isSelected && "bg-accent text-accent-foreground",
          className,
        )}
        role="option"
        aria-selected={isSelected}
        {...props}
      />
    );
  },
);
SelectItem.displayName = "SelectItem";

export { Select, SelectTrigger, SelectValue, SelectContent, SelectItem };
