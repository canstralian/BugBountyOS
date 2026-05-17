import * as React from "react";
import { useNavigate } from "react-router-dom";
import { Plus, ShieldCheck, Globe, Activity, Circle } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { usePrograms } from "@/hooks/use-programs";
import { cn } from "@/lib/utils";

export default function DashboardPage() {
  const navigate = useNavigate();
  const { programs, isLoading, error, fetchPrograms } = usePrograms();

  React.useEffect(() => {
    fetchPrograms();
  }, [fetchPrograms]);

  return (
    <div className="flex flex-col gap-4 sm:gap-6">
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
            Security OS Dashboard
          </h1>
          <p className="text-sm text-muted-foreground">
            Synchronized with Airtable Security Kernel. Operational traffic-lights active.
          </p>
        </div>
        <Button onClick={() => navigate("/scope")} size="sm" className="hidden sm:flex">
          <Plus className="mr-2 h-4 w-4" /> Add Program
        </Button>
      </div>

      {error && (
        <div className="rounded-md bg-destructive/15 p-4 text-sm text-destructive border border-destructive/20 font-medium">
          Kernel Sync Error: {error}
        </div>
      )}

      <Card>
        <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Active Vectors</CardTitle>
              <CardDescription>
                Managed workspaces mapping to authoritative scope rules.
              </CardDescription>
            </div>
            <Activity className="h-5 w-5 text-muted-foreground" />
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div
              role="status"
              aria-live="polite"
              className="flex h-32 items-center justify-center text-sm text-muted-foreground animate-pulse"
            >
              Synchronizing with Kernel...
            </div>
          ) : programs.length === 0 ? (
            <EmptyState
              icon={<ShieldCheck className="h-6 w-6" />}
              title="No programs identified"
              description="Define your first program in the Airtable Kernel to initialize security vectors."
              action={
                <Button onClick={() => navigate("/scope")} block>
                  <Plus aria-hidden="true" />
                  Define Scope
                </Button>
              }
            />
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {programs.map((p) => (
                <Card 
                  key={p.id} 
                  className="cursor-pointer transition-colors hover:bg-accent/5"
                  onClick={() => navigate(`/scope?id=${p.id}`)}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between">
                      <div className="flex flex-col gap-1">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/80 flex items-center gap-1">
                          <Globe className="h-3 w-3" /> {p.platform}
                        </span>
                        <CardTitle className="text-base line-clamp-1">{p.name}</CardTitle>
                      </div>
                      <Circle 
                        className={cn(
                          "h-3 w-3 fill-current mt-1",
                          p.health === 'green' ? "text-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]" :
                          p.health === 'yellow' ? "text-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.4)]" :
                          "text-red-500 shadow-[0_0_8px_rgba(239,68,68,0.4)]"
                        )} 
                      />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-2">
                      <div className={cn(
                        "rounded-full px-2 py-0.5 text-[10px] font-medium border",
                        p.status === 'Active' ? "bg-green-500/10 text-green-600 border-green-500/20" :
                        p.status === 'Paused' ? "bg-yellow-500/10 text-yellow-600 border-yellow-500/20" :
                        "bg-muted text-muted-foreground border-border"
                      )}>
                        {p.status}
                      </div>
                      <div className={cn(
                        "rounded-full px-2 py-0.5 text-[10px] font-medium border uppercase tracking-tight",
                        p.lifecycle === 'Canonical' ? "bg-blue-500/10 text-blue-600 border-blue-500/20" :
                        "bg-slate-500/10 text-slate-600 border-slate-500/20"
                      )}>
                        {p.lifecycle}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
