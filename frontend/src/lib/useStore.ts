import { create } from "zustand";

interface Profile {
    age: number;
    income: number;
    expenses: number;
    investments: Array<{ type: string; amount: number }>;
    goals: Array<{ type: string; target: number; years: number }>;
    risk_profile: string;
}

interface FinancialStore {
    profile: Profile | null;
    healthScore: any | null;
    setProfile: (p: Profile) => void;
    setHealthScore: (hs: any) => void;
    clear: () => void;
}

export const useFinancialStore = create<FinancialStore>((set) => ({
    profile: null,
    healthScore: null,
    setProfile: (profile) => set({ profile }),
    setHealthScore: (healthScore) => set({ healthScore }),
    clear: () => set({ profile: null, healthScore: null }),
}));
