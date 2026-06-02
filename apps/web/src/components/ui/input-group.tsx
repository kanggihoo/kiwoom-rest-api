import * as React from "react";

import { cn } from "@/lib/utils";

type InputGroupProps = React.HTMLAttributes<HTMLDivElement>;
type InputGroupAddonProps = React.HTMLAttributes<HTMLSpanElement>;

const InputGroup = React.forwardRef<HTMLDivElement, InputGroupProps>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("group relative flex items-center rounded-md border border-input", className)}
    {...props}
  />
));
InputGroup.displayName = "InputGroup";

const InputGroupAddon = React.forwardRef<HTMLSpanElement, InputGroupAddonProps>(({ className, ...props }, ref) => (
  <span
    ref={ref}
    className={cn("flex items-center justify-center px-3 text-muted-foreground", className)}
    {...props}
  />
));
InputGroupAddon.displayName = "InputGroupAddon";

const InputGroupInput = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "h-10 w-full bg-transparent px-0 py-2 text-sm outline-none placeholder:text-muted-foreground",
        className,
      )}
      {...props}
    />
  ),
);
InputGroupInput.displayName = "InputGroupInput";

export { InputGroup, InputGroupAddon, InputGroupInput };
