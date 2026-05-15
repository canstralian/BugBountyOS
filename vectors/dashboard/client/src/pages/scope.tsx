import * as React from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { 
  Plus, 
  ShieldCheck, 
  ExternalLink, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle,
  RefreshCw,
  Search,
  Lock,
  Zap
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { usePrograms } from "@/hooks/use-programs";
import { useAssets } from "@/hooks/use-assets";
import { cn } from "@/lib/utils";

export default function ScopePage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const programId = searchParams.get("id");

  const { programs, isLoading: isProgramsLoading, fetchPrograms } = usePrograms();
  const { assets, isLoading: isQssetsLoading, fetchAssets, error: assetError } = useAssets(programId || undefined);

  const program = React.useMemo(() => 
    programs.find(p => p.id === programId), 
  [programs, programId]);

  React.useEffect(() => {
    if (!programs.length) fetchPrograms();
  }, [fetchPrograms, programs.length]);

  React.useEffect(() => {
    if (programId) fetchAssets();
  }, [programId]);

  if (programId && program) {
    return (
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
                {program.name}
              </h1>
              <div className={cn(
                "h-3 w-3 rounded-full animate-pulse",
                program.health === 'green' ? "bg-green-500" :
                program.health === 'yellow' ? "bg-yellow-500" : "bg-red-500"
              )} />
            </div>
            <p className="text-sm text-muted-foreground flex items-center gap-2">
              Enforcement Level: <span className="font-mono font-bold text-foreground uppercase">{program.lifecycle}</span>
              <span className="opacity-50">|</span>
              Platform: <span className="font-semibold">{program.platform}</span>
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => fetchAssets()} disabled={isAssetsLoading}>
              <RefreshCw0className={cn("h-4 w-4 mr-2", isAssetsLoading && "animate-spin")} /> Sync Kernel
            </Button>
            {program.policyUrl && (
              <Button size="sm" asChild>
                <a href={program.policyUrl} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4 mr-2" /> Policy
                </a>
              </Button>
            )}
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          <Card className="md:col-span-2">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div>
                <CardTitle className="text-lg">Authoritative Scope</CardTitle>
                <CardDescription>Verified assets registered in the Security Kernel.</CardDescription>
              </div>
              <Lock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {isAssetsLoading ? (
                <div className="flex h-40 items-center justify-center text-sm text-muted-foreground">
                  Synchronizing assets...
                </div>
              ) : assets.length === 0 ? (
                <div className="flex h-40 flex-col items-center justify-center gap-2 text-sm text-muted-foreground border-2 border-dashed rounded-lg">
                  <Search className="h-8 w-8 opacity-20" />
                  No assets identified in this vector.
                </div>
              ) : (
                <div className="rounded-md border border-border">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-muted/50 text-muted-foreground font-medium border-b">
                      <tr>
                        <th className="px-4 py-2">Identifier</th>
                        <th className="px-4 py-2 text-center">Criticality</th>
                        <th className="px-4 py-2 text-right">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {assets.map((asset) => (
                        <tr key={asset.id} className="hover:bg-accent/5 transition-colors">
                          <td className="px-4 py-3 font-mono text-[13px]">{asset.identifier}</td>
                          <td className="px-4 py-3 text-center">
                            <span className={cn(
                              "px-2 py-0.5 rounded-full text-[11px] font-bold uppercase",
                              asset.criticality === 'Critical' ? "bg-red-500/10 text-red-600" :
                              asset.criticality === 'High' ? "bg-orange-500/10 text-orange-600" :
                              "bg-blue-500/10 text-blue-600"
                            )}>
                              {asset.criticality}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right">
                             <div className="flex items-center justify-end gap-1.5 font-medium">
                               {asset.status === 'In Scope' || asset.status === 'Active' ? (
                                 <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                               ) : (
                                 <XCircle className="h-3.5 w-3.5 text-destructive" />
                               )}
                               {asset.status}
                             </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="flex flex-col gap-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-bold uppercase tracking-tight text-muted-foreground">Vector Health</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col gap-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Policy Drift</span>
                  <span className="text-xs font-bold text-green-500 flex items-center gap-1">
                    <Zap className="h-3 w-3 fill-current" /> 0%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Enforcement</span>
                  <span className={cn(
                    "text-xs font-bold",
                    program.lifecycle === 'Canonical' ? "text-blue-500" : "text-yellow-500"
                  )}>
                    {program.lifecycle === 'Canonical' ? "STRICT" : "OBSERVE"}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-accent/5">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-bold uppercase tracking-tight text-muted-foreground">Kernel Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs leading-relaxed text-muted-foreground italic">
                  {program.overview || "No kernel overview provided for this program."}
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 sm:gap-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
          New workspace
        </h1>
        <p className="text-sm text-muted-foreground">
          Define scope and initialize a new security vector.
        </p>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Define Scope</CardTitle>
          <CardDescription>
            Workspaces are currently managed via the Airtable Kernel. To add a new program, please update your Airtable base.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="rounded-lg border-2 border-dashed p-12 text-center flex flex-col items-center gap-3">
             <AlertTriangle className="h-10 w-10 text-yellow-500 opacity-50" />
             <div className="text-sm font-medium">Direct manual creation is disabled</div>
             <p className="text-xs text-muted-foreground max-w-xs">
               BugBountyOS follows the "Kernel-First" principle. All program definitions must originate from the authorizative Airtable scope rules.
             </p>
             <Button variant="outline" size="sm" className="mt-2" asChild>
               <a href="https://airtable.com/appT4zR1ybxgrujBD" target="_blank" rel="noopener noreferrer">
                 Open Airtable Kernel
               </a>
             </Button>
          </div>
        </CardContent>
        <CardFooter className="justify-center border-t py-4 bg-muted/20">
           <Button variant="ghost" size="sm" onClick={() => navigate("/")}>
             Back to Dashboard
           </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
