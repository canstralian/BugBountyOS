import * as React from "react";
import { NavLink, Outlet } from "react-router-dom";
import { Menu, ShieldCheck, Target, FileSearch, FileText } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface NavItem {
  to: string;
  label: string;
  icon: React.ReactNode;
}

const NAV: NavItem[] = [
  { to: "/", label: "Dashboard", icon: <ShieldCheck className="h-4 w-4" /> },
  { to: "/scope", label: "Scope", icon: <Target className="h-4 w-4" /> },
  { to: "/findings", label: "Findings", icon: <FileSearch className="h-4 w-4" /> },
  { to: "/reports", label: "Reports", icon: <FileText className="h-4 w-4" /> },
];

function NavList({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav aria-label="Primary" className="flex flex-col gap-1">
      {NAV.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === "/"}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              "flex min-h-tap items-center gap-3 rounded-md px-3 text-sm font-medium",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
              isActive
                ? "bg-secondary text-secondary-foreground"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
            )
          }
        >
          {item.icon}
          <span>{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}

export function AppShell() {
  const [open, setOpen] = React.useState(false);

  return (
    <div className="flex min-h-dvh flex-col bg-background">
      <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur safe-top">
        <div className="flex h-14 items-center gap-2 px-3 sm:px-6">
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                aria-label="Open navigation"
                className="md:hidden"
              >
                <Menu className="h-5 w-5" aria-hidden="true" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-[80%] max-w-xs">
              <SheetHeader>
                <SheetTitle>BugBountyOS</SheetTitle>
                <SheetDescription>Workflow plane navigation</SheetDescription>
              </SheetHeader>
              <div className="mt-4">
                <NavList onNavigate={() => setOpen(false)} />
              </div>
            </SheetContent>
          </Sheet>

          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary" aria-hidden="true" />
            <span className="font-semibold">BugBountyOS</span>
          </div>

          <div className="ml-auto" />
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-6xl flex-1 gap-6 px-3 py-4 sm:px-6 sm:py-6">
        <aside className="hidden w-56 shrink-0 md:block">
          <div className="sticky top-20">
            <NavList />
          </div>
        </aside>
        <main className="min-w-0 flex-1" id="main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
