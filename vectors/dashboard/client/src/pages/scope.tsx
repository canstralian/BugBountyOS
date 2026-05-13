import * as React from "react";
import { useNavigate } from "react-router-dom";
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
import { toast } from "@/hooks/use-toast";
import { programsStore } from "@/hooks/use-programs";

interface FormValues {
  name: string;
  scopeUrl: string;
}

interface FormErrors {
  name?: string;
  scopeUrl?: string;
}

function validate(values: FormValues): FormErrors {
  const errors: FormErrors = {};
  if (values.name.trim().length < 2) {
    errors.name = "Workspace name must be at least 2 characters.";
  }
  try {
    if (values.scopeUrl) new URL(values.scopeUrl);
    else errors.scopeUrl = "Scope source URL is required.";
  } catch {
    errors.scopeUrl = "Enter a valid URL (including https://).";
  }
  return errors;
}

export default function ScopePage() {
  const navigate = useNavigate();
  const [values, setValues] = React.useState<FormValues>({
    name: "",
    scopeUrl: "",
  });
  const [touched, setTouched] = React.useState<Record<keyof FormValues, boolean>>({
    name: false,
    scopeUrl: false,
  });
  const [submitting, setSubmitting] = React.useState(false);

  const errors = validate(values);
  const visibleErrors: FormErrors = {
    name: touched.name ? errors.name : undefined,
    scopeUrl: touched.scopeUrl ? errors.scopeUrl : undefined,
  };
  const hasErrors = Object.values(errors).some(Boolean);

  function onChange<K extends keyof FormValues>(key: K, value: FormValues[K]) {
    setValues((v) => ({ ...v, [key]: value }));
  }

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setTouched({ name: true, scopeUrl: true });
    if (hasErrors) {
      const firstInvalid = (event.currentTarget as HTMLFormElement).querySelector(
        "[aria-invalid='true']",
      ) as HTMLElement | null;
      firstInvalid?.focus();
      return;
    }

    setSubmitting(true);
    try {
      await toast.promise(
        new Promise<void>((resolve) => setTimeout(resolve, 600)),
        {
          loading: { title: "Creating workspace…" },
          success: {
            title: "Workspace created",
            description: `${values.name} is ready.`,
          },
          error: {
            title: "Couldn't create workspace",
            description: "Check your scope URL and try again.",
          },
        },
      );
      const name = values.name.trim();
      const scopeRef = values.scopeUrl.trim();
      programsStore.getState().setPrograms([
        ...programsStore.getState().programs,
        { id: crypto.randomUUID(), name, scopeRef },
      ]);
      navigate("/");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex flex-col gap-4 sm:gap-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
          New workspace
        </h1>
        <p className="text-sm text-muted-foreground">
          Scope is enforced as a constraint, not remembered as a note.
        </p>
      </div>

      <Card>
        <form noValidate onSubmit={onSubmit}>
          <CardHeader>
            <CardTitle>Define scope</CardTitle>
            <CardDescription>
              Record the authorization source and a human-readable workspace name.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <FormField
              id="name"
              label="Workspace name"
              required
              hint="A short identifier, e.g. acme-bb-2025."
              error={visibleErrors.name}
            >
              <Input
                value={values.name}
                onChange={(e) => onChange("name", e.target.value)}
                onBlur={() => setTouched((t) => ({ ...t, name: true }))}
                autoComplete="off"
                autoCapitalize="none"
                spellCheck={false}
                placeholder="acme-bb-2025"
              />
            </FormField>

            <FormField
              id="scopeUrl"
              label="Scope source URL"
              required
              hint="Program page, contract URL, or ticket link."
              error={visibleErrors.scopeUrl}
            >
              <Input
                type="url"
                inputMode="url"
                value={values.scopeUrl}
                onChange={(e) => onChange("scopeUrl", e.target.value)}
                onBlur={() => setTouched((t) => ({ ...t, scopeUrl: true }))}
                autoComplete="url"
                autoCapitalize="none"
                spellCheck={false}
                placeholder="https://example.com/program-scope"
              />
            </FormField>
          </CardContent>
          <CardFooter>
            <Button
              type="button"
              variant="ghost"
              onClick={() => navigate(-1)}
              disabled={submitting}
              block
            >
              Cancel
            </Button>
            <Button
              type="submit"
              loading={submitting}
              loadingText="Creating…"
              block
            >
              Create workspace
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
