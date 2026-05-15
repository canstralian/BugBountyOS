import { create } from "zustand";

export type ToastVariant =
  | "info"
  | "success"
  | "warning"
  | "error"
  | "loading";

export interface Toast {
  id: string;
  variant: ToastVariant;
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
  durationMs: number | null;
}

export interface ToastInput {
  id?: string;
  title: string;
  description?: string;
  action?: Toast["action"];
  durationMs?: number | null;
}

interface ToastState {
  toasts: Toast[];
  push: (variant: ToastVariant, input: ToastInput) => string;
  update: (id: string, patch: Partial<Omit<Toast, "id">>) => void;
  dismiss: (id: string) => void;
  clear: () => void;
}

const DEFAULT_DURATION_MS: Record<ToastVariant, number | null> = {
  info: 4000,
  success: 3500,
  warning: 5000,
  error: 6500,
  loading: null,
};

const timers = new Map<string, ReturnType<typeof setTimeout>>();

function clearTimer(id: string) {
  const handle = timers.get(id);
  if (handle) {
    clearTimeout(handle);
    timers.delete(id);
  }
}

function makeId() {
  return `t_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`;
}

const store = create<ToastState>((set, get) => ({
  toasts: [],
  push: (variant, input) => {
    const id = input.id ?? makeId();
    const durationMs =
      input.durationMs === undefined ? DEFAULT_DURATION_MS[variant] : input.durationMs;
    const next: Toast = {
      id,
      variant,
      title: input.title,
      description: input.description,
      action: input.action,
      durationMs,
    };
    set((state) => {
      const existing = state.toasts.findIndex((t) => t.id === id);
      if (existing >= 0) {
        const copy = state.toasts.slice();
        copy[existing] = next;
        return { toasts: copy };
      }
      return { toasts: [...state.toasts, next] };
    });
    clearTimer(id);
    if (durationMs != null) {
      timers.set(
        id,
        setTimeout(() => get().dismiss(id), durationMs),
      );
    }
    return id;
  },
  update: (id, patch) =>
    set((state) => ({
      toasts: state.toasts.map((t) => (t.id === id ? { ...t, ...patch } : t)),
    })),
  dismiss: (id) => {
    clearTimer(id);
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
  },
  clear: () => {
    for (const id of Array.from(timers.keys())) clearTimer(id);
    set({ toasts: [] });
  },
}));

export function useToasts() {
  return store((s) => s.toasts);
}

export interface ToastApi {
  info: (input: ToastInput) => string;
  success: (input: ToastInput) => string;
  warning: (input: ToastInput) => string;
  error: (input: ToastInput) => string;
  loading: (input: ToastInput) => string;
  dismiss: (id: string) => void;
  update: (id: string, patch: Partial<Omit<Toast, "id">>) => void;
  promise: <T>(
    p: Promise<T>,
    opts: {
      loading: ToastInput;
      success: ToastInput | ((value: T) => ToastInput);
      error: ToastInput | ((err: unknown) => ToastInput);
    },
  ) => Promise<T>;
}

function makeApi(): ToastApi {
  const { push, dismiss, update } = store.getState();
  return {
    info: (input) => push("info", input),
    success: (input) => push("success", input),
    warning: (input) => push("warning", input),
    error: (input) => push("error", input),
    loading: (input) => push("loading", { durationMs: null, ...input }),
    dismiss,
    update,
    promise: async (p, opts) => {
      const id = push("loading", { durationMs: null, ...opts.loading });
      try {
        const value = await p;
        const next =
          typeof opts.success === "function" ? opts.success(value) : opts.success;
        push("success", { id, ...next });
        return value;
      } catch (err) {
        const next =
          typeof opts.error === "function" ? opts.error(err) : opts.error;
        push("error", { id, ...next });
        throw err;
      }
    },
  };
}

export const toast = makeApi();

export function useToast(): ToastApi {
  return toast;
}
