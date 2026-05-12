import { useNavigate } from "react-router-dom";
import { Compass } from "lucide-react";
import { EmptyState } from "@/components/ui/empty-state";
import { Button } from "@/components/ui/button";

export default function NotFoundPage() {
  const navigate = useNavigate();
  return (
    <EmptyState
      icon={<Compass className="h-6 w-6" />}
      title="Page not found"
      description="The route you tried doesn't exist."
      action={
        <Button onClick={() => navigate("/")} block>
          Go to dashboard
        </Button>
      }
    />
  );
}
