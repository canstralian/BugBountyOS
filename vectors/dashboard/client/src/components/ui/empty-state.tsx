import * as React from "react";
import { cn } from "@/lib/utils";

export interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  icon?: React.ReactNode;
  title: string;
  description?: React.ReactNode;
  action?: React.ReactNode;
  secondaryAction?: React.ReactNode;
  variant?: "empty" | "filtered" | "error";
}

const variantBorder: Record<NonNullable<EmptyStateProps["variant"]>, string> = {
  empty: "border-dashed border-border",
  filtered: "border-dashed border-muted-foreground/40",
  error: "border-destructive/40 bg-destructive/5",
};

export function EmptyState({
  icon,
  title,
  description,
  action,
  secondaryAction,
  variant = "empty",
  className,
  ...props
}: EmptyStateProps) {
  return (
    <div
      role="status"
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-lg border p-6 text-center sm:p-10",
        variantBorder[variant],
        className,
      )}
      {...props}
    >
      {icon ? (
        <div
          aria-hidden="true"
          className="flex h-12 w-12 items-center justify-center rounded-full bg-muted text-muted-foreground"
        >
          {icon}
        </div>
      ) : null}
      <div className="flex flex-col gap-1">
        <h3 className="text-base font-semibold sm:text-lg">{title}</h3>
        {description ? (
          <p className="text-sm text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {(action || secondaryAction) && (
        <div className="mt-2 flex flex-col-reverse items-stretch gap-2 sm:flex-row sm:items-center">
          {secondaryAction}
          {action}
        </div>
      )}
    </div>
  );
}
