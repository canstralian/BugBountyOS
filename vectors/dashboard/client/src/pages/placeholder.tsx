import { Inbox } from "lucide-react";
import { EmptyState } from "@/components/ui/empty-state";

export default function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="flex flex-col gap-4 sm:gap-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
          {title}
        </h1>
        <p className="text-sm text-muted-foreground">
          This surface isn&apos;t wired to data yet.
        </p>
      </div>
      <EmptyState
        icon={<Inbox className="h-6 w-6" />}
        title={`No ${title.toLowerCase()} yet`}
        description="As workspaces accumulate evidence, items will appear here."
      />
    </div>
  );
}
