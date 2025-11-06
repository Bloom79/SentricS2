import { create } from 'zustand';
import { BESSPerformance, BESSIssue } from '../types';

interface BESSStore {
  performance: BESSPerformance | null;
  setPerformance: (performance: BESSPerformance) => void;
}

// Mock data for demonstration
const mockPerformance: BESSPerformance = {
  id: 'bess_001',
  name: 'Milan Depot BESS',
  score: 87,
  totalLoss: 15284,
  issues: [
    {
      id: 'issue_1',
      severity: 'warning',
      title: 'Missing Negative Price Opportunities',
      description: "Your BESS isn't charging during negative prices",
      annualLoss: 8400,
      fix: 'Enable auto-trading mode',
      fixDetails: "We'll charge when prices go negative automatically",
    },
    {
      id: 'issue_2',
      severity: 'warning',
      title: 'Suboptimal Discharge Timing',
      description: "You're discharging at average prices, not peaks",
      annualLoss: 4900,
      fix: 'Shift discharge to 7-9pm peak window',
      fixDetails: "We'll predict peaks and optimize timing",
    },
    {
      id: 'issue_3',
      severity: 'warning',
      title: 'Conservative Depth of Discharge',
      description: "You're only using 75% of battery capacity",
      annualLoss: 1984,
      fix: 'Increase DOD to 90% (safe per warranty)',
      fixDetails: 'Adds 2,800 years to cycle life vs revenue gain',
    },
  ],
};

export const useBESSStore = create<BESSStore>((set) => ({
  performance: mockPerformance,
  setPerformance: (performance) => set({ performance }),
}));
