import { create } from "zustand";

export interface Program {
  id: string;
  name: string;
  scopeRef?: string;
}

interface ProgramsState {
  programs: Program[];
  isLoading: boolean;
  error: string | null;
  setPrograms: (programs: Program[]) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
}

const store = create<ProgramsState>((set) => ({
  programs: [],
  isLoading: false,
  error: null,
  setPrograms: (programs) => set({ programs, isLoading: false, error: null }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error, isLoading: false }),
}));

export function usePrograms() {
  const programs = store((s) => s.programs);
  const isLoading = store((s) => s.isLoading);
  const error = store((s) => s.error);
  return { programs, isLoading, error };
}

export const programsStore = store;
