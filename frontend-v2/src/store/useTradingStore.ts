import { create } from 'zustand';
import { TradingBriefing, TradingOpportunity } from '../types';

interface TradingStore {
  briefing: TradingBriefing | null;
  setBriefing: (briefing: TradingBriefing) => void;
}

// Mock data for demonstration
const mockBriefing: TradingBriefing = {
  date: new Date('2025-02-06'),
  currentRevenue: 847,
  potentialRevenue: 1203,
  opportunities: [
    {
      id: '1',
      action: 'Curtail Plant #3 (Palermo)',
      description: 'Price: -€12/MWh (you PAY to produce)',
      impact: 84,
      time: '2:00-3:00pm',
      price: -12,
    },
    {
      id: '2',
      action: 'Discharge BESS #1',
      description: 'Price: €180/MWh (peak demand)',
      impact: 144,
      time: '7:00-8:00pm',
      price: 180,
    },
    {
      id: '3',
      action: 'Shift BESS #2 charge',
      description: 'Price: €15/MWh (solar surplus)',
      impact: 128,
      time: '1:00-2:00pm',
      price: 15,
    },
  ],
};

export const useTradingStore = create<TradingStore>((set) => ({
  briefing: mockBriefing,
  setBriefing: (briefing) => set({ briefing }),
}));
