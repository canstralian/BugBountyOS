export interface BugBountyProgram {
  id: number;
  name: string;
  scopes: string[];
}

interface UseProgramsState {
  programs: BugBountyProgram[];
  isLoading: boolean;
  error: string | null;
}

export const usePrograms = (): UseProgramsState => ({
  programs: [],
  isLoading: false,
  error: null,
});
