export interface DashboardUser {
  id: number;
  username: string;
}

interface UseUserState {
  user: DashboardUser | null;
  isLoading: boolean;
  error: string | null;
}

export const useUser = (): UseUserState => ({
  user: null,
  isLoading: false,
  error: null,
});
