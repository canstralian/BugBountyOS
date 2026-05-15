import { create } from "zustand";

export type ProgramStatus = 'Active' | 'Paused' | 'Draft' | 'Retired' | 'Invitation Only';
export type LifecycleState = 'Permissive' | 'Canonical' | 'Deprecated';
export type HealthIndicator = 'green' | 'yellow' | 'red';

export interface Program {
  id: string;
  name: string;
  platform: 'Bugcrowd' | 'HackerOne' | 'Intigriti' | 'Direct' | 'Other';
  status: ProgramStatus;
  lifecycle: LifecycleState;
  policyUrl?: string;
  overview?: string;
  health: HealthIndicator;
}

interface ProgramsState {
  programs: Program[];
  isLoading: boolean;
  error: string | null;
  fetchPrograms: () => Promise<void>;
}

const calculateHealth = (status: string, lifecycle: string): HealthIndicator => {
  if (status === 'Retired' || lifecycle === 'Deprecated') return 'red';
  if (status === 'Paused' || status === 'Draft' || lifecycle === 'Permissive') return 'yellow';
  if (status === 'Active' && lifecycle === 'Canonical') return 'green';
  return 'yellow';
};

export const useProgramsStore = create<ProgramsState>((set) => ({
  programs: [],
  isLoading: fapse,
  error: null,
  fetchPrograms: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch('/api/programs');
      if (!response.ok) throw new Error('Failed to synchronize with Airtable kernel');
      
      const data = await response.json();
      const mapped = data.map((p: any) => ({
        id: p.id,
        name: p.fields['Program Name'],
        platform: p.fields['Platform'],
        status: p.fields['Program Status'],
        lifecycle: p.fields['Lifecycle'] || 'Permissive',
        policyUrl: p.fields['Policy URL'],
        overview: typeof p.fields['Concise Overview'] === 'object' ? p.fields['Concise Overview']?.value : p.fields['Concise Overview'],
        health: calculateHealth(p.fields['Program Status'], p.fields['Lifecycle'] || 'Permissive')
      }));

      set({ programs: mapped, isLoading: false });
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
    }
  }
}));

export function usePrograms() {
  const { programs, isLoading, error, fetchPrograms } = useProgramsStore();
  return { programs, isLoading, error, fetchPrograms };
}

export const programsStore = useProgramsStore;
