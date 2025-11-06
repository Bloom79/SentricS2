import { create } from 'zustand';
import { CERData, CERInsight, UploadProgress } from '../types';

interface CERStore {
  data: CERData | null;
  insights: CERInsight[];
  isUploading: boolean;
  uploadProgress: UploadProgress | null;

  setData: (data: CERData) => void;
  setInsights: (insights: CERInsight[]) => void;
  startUpload: (fileName: string) => void;
  updateProgress: (progress: UploadProgress) => void;
  completeUpload: (data: CERData, insights: CERInsight[]) => void;
  reset: () => void;
}

// Mock data for demonstration
const mockCERData: CERData = {
  id: 'cer_001',
  month: 'January',
  year: 2025,
  totalEarnings: 12847,
  changeAmount: 1203,
  changePercentage: 10.3,
  lastUpdated: new Date('2025-01-15T10:32:00'),
  hourlyReadings: 720,
  membersProcessed: 12,
};

const mockInsights: CERInsight[] = [
  {
    type: 'peak',
    icon: '🌞',
    title: 'Peak sharing: Weekdays 10am-2pm',
    description: 'Average €94/hour during peak solar production',
  },
  {
    type: 'low',
    icon: '⚠️',
    title: 'Low sharing: Weekends',
    description: 'Average €23/hour - industrial consumers offline',
  },
  {
    type: 'opportunity',
    icon: '💡',
    title: 'Add 50kWh storage',
    description: 'Shift excess weekend solar to weekday evenings → +€347/month',
    impact: '+€347/month',
  },
];

export const useCERStore = create<CERStore>((set) => ({
  data: mockCERData,
  insights: mockInsights,
  isUploading: false,
  uploadProgress: null,

  setData: (data) => set({ data }),

  setInsights: (insights) => set({ insights }),

  startUpload: (fileName) => set({
    isUploading: true,
    uploadProgress: {
      stage: 'detecting',
      progress: 0,
      message: 'Detecting file format...',
      fileName,
      details: [],
    }
  }),

  updateProgress: (progress) => set({ uploadProgress: progress }),

  completeUpload: (data, insights) => set({
    data,
    insights,
    isUploading: false,
    uploadProgress: null,
  }),

  reset: () => set({
    data: null,
    insights: [],
    isUploading: false,
    uploadProgress: null,
  }),
}));
