import { useNavigate } from "react-router-dom";
import { Plus, ShieldCheck } from "lucide-react";
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

export default function DashboardPage() {
  const navigate = useNavigate();
  const { programs, isLoading } = usePrograms();

  return (
    <div className="flex flex-col gap-4 sm:gap-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
          Dashboard
        </h1>
        <p className="text-sm text-muted-foreground">
          Scope first. Evidence by default. Report-ready by design.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Workspaces</CardTitle>
          <CardDescription>
            Each workspace enforces scope, captures evidence, and produces report
            artifacts.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div
              role="status"
              aria-live="polite"
              className="flex h-32 items-center justify-center text-sm text-muted-foreground"
            >
              Loading workspaces…
            </div>
          ) : programs.length === 0 ? (
            <EmptyState
              icon={<ShieldCheck className="h-6 w-6" />}
              title="No workspaces yet"
              description="Create your first workspace to define scope and begin a research session."
              action={
                <Button onClick={() => navigate("/scope")} block>
                  <Plus aria-hidden="true" />
                  Create workspace
                </Button>
              }
            />
          ) : (
            <ul className="grid gap-3 sm:grid-cols-2">
              {programs.map((p) => (
                <li
                  key={p.id}
                  className="rounded-md border border-border p-3 text-sm"
                >
                  {p.name}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
