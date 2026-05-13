import * as React from "react";
import {
  AlertCircle,
  CheckCircle2,
  Info,
  Loader2,
  TriangleAlert,
  X,
} from "lucide-react";
import { useToasts, toast as toastApi, type ToastVariant } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

const variantStyles: Record<
  ToastVariant,
  { container: string; icon: React.ReactNode; role: "status" | "alert" }
> = {
  info: {
    container: "border-border bg-card text-card-foreground",
    icon: <Info className="h-5 w-5 text-muted-foreground" aria-hidden="true" />,
    role: "status",
  },
  success: {
    container: "border-success/40 bg-card text-card-foreground",
    icon: (
      <CheckCircle2
        className="h-5 w-5 text-[hsl(var(--success))]"
        aria-hidden="true"
      />
    ),
    role: "status",
  },
  warning: {
    container: "border-warning/50 bg-card text-card-foreground",
    icon: (
      <TriangleAlert
        className="h-5 w-5 text-[hsl(var(--warning))]"
        aria-hidden="true"
      />
    ),
    role: "alert",
  },
  error: {
    container: "border-destructive/50 bg-card text-card-foreground",
    icon: <AlertCircle className="h-5 w-5 text-destructive" aria-hidden="true" />,
    role: "alert",
  },
  loading: {
    container: "border-border bg-card text-card-foreground",
    icon: (
      <Loader2
        className="h-5 w-5 animate-spin text-muted-foreground"
        aria-hidden="true"
      />
    ),
    role: "status",
  },
};

export function Toaster() {
  const toasts = useToasts();

  return (
    <div
      className={cn(
        "pointer-events-none fixed inset-x-0 bottom-0 z-[100] flex flex-col items-center gap-2 px-3 pb-3 safe-bottom",
        "sm:inset-x-auto sm:right-4 sm:bottom-4 sm:items-end sm:pb-0",
      )}
    >
      {toasts.map((t) => {
        const variant = variantStyles[t.variant];
        return (
          <div
            key={t.id}
            role={variant.role}
            className={cn(
              "pointer-events-auto w-full max-w-sm rounded-lg border p-3 shadow-lg",
              "flex items-start gap-3",
              "animate-slide-in-bottom",
              variant.container,
            )}
          >
            <div className="mt-0.5 flex-shrink-0">{variant.icon}</div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold leading-tight">{t.title}</p>
              {t.description ? (
                <p className="mt-0.5 text-sm text-muted-foreground">
                  {t.description}
                </p>
              ) : null}
              {t.action ? (
                <button
                  type="button"
                  onClick={() => {
                    t.action?.onClick();
                    toastApi.dismiss(t.id);
                  }}
                  className={cn(
                    "mt-2 inline-flex min-h-tap items-center rounded-md border border-input px-3 text-sm font-medium",
                    "hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  )}
                >
                  {t.action.label}
                </button>
              ) : null}
            </div>
            {t.variant !== "loading" ? (
              <button
                type="button"
                onClick={() => toastApi.dismiss(t.id)}
                aria-label="Dismiss notification"
                className={cn(
                  "-mr-1 -mt-1 inline-flex min-h-tap min-w-tap items-center justify-center rounded-md",
                  "text-muted-foreground hover:text-foreground",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                )}
              >
                <X className="h-4 w-4" aria-hidden="true" />
              </button>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
