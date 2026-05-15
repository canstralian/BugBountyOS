import { create } from "zustand";

export interface Asset {
  id: string;
  identifier: string;
  type: string;
  criticality: string;
  environment: string;
  status: string;
}

interface AssetsState {
  assets: Record<string, Asset[]>;
  isLoading: Record<string, boolean>;
  error: Record<string, string | null>;
  fetchAssets: (programId: string) => Promise<void>;
}

export const useAssetsStore = create<AssetsState>((set, get) => ({
  assets: {},
  isLoading: {},
  error: {},
  fetchAssets: async (programId: string) => {
    set((state) => ({
      isLoading: { ...state.isLoading, [programId]: true },
      error: { ...state.error, [programId]: null }
    }));

    try {
      const response = await fetch(`/api/assets?programId=${programId}`);
      if (!response.ok) throw new Error('Failed to fetch assets');
      
      const data = await response.json();
      const mapped = data.map((r: any) => ({
        id: r.id,
        identifier: r.fields['Asset Identifier'],
        type: r.fields['Asset Type'],
        criticality: r.fields['Criticality'],
        environment: r.fields['Environment'],
        status: r.fields['Status']
      }));

      set((state) => ({
        assets: { ...state.assets, [programId]: mapped },
        isLoading: { ...state.isLoading, [programId]: false }
      }));
    } catch (err: any) {
      set((state) => ({
        error: { ...state.error, [programId]: err.message },
        isLoading: { ...state.isLoading, [programId]: false }
      }));
    }
  }
}));

export function useAssets(programId?: string) {
  const store = useAssetsStore();
  
  const assets = programId ? store.assets[programId] || [] : [];
  const isLoading = programId ? store.isLoading[programId] || false : false;
  const error = programId ? store.error[programId] || null : null;

  return {
    assets,
    isLoading,
    error,
    fetchAssets: () => programId && store.fetchAssets(programId)
  };
}
