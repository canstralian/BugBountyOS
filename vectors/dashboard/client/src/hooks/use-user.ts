import { create } from "zustand";

export interface User {
  id: string;
  username: string;
}

interface UserState {
  user: User | null;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setLoading: (isLoading: boolean) => void;
}

const store = create<UserState>((set) => ({
  user: null,
  isLoading: false,
  setUser: (user) => set({ user, isLoading: false }),
  setLoading: (isLoading) => set({ isLoading }),
}));

export function useUser() {
  const user = store((s) => s.user);
  const isLoading = store((s) => s.isLoading);
  return { user, isLoading };
}

export const userStore = store;
