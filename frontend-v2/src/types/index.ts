// SentricS2 Insanely Great Edition - Type Definitions

export interface CERData {
  id: string;
  month: string;
  year: number;
  totalEarnings: number;
  changeAmount: number;
  changePercentage: number;
  lastUpdated: Date;
  hourlyReadings: number;
  membersProcessed: number;
}

export interface CERInsight {
  type: 'peak' | 'low' | 'opportunity';
  icon: string;
  title: string;
  description: string;
  impact?: string;
}

export interface TradingBriefing {
  date: Date;
  currentRevenue: number;
  potentialRevenue: number;
  opportunities: TradingOpportunity[];
}

export interface TradingOpportunity {
  id: string;
  action: string;
  description: string;
  impact: number;
  time: string;
  price: number;
}

export interface LivePrice {
  timestamp: Date;
  price: number;
  zone: string;
  status: 'negative' | 'low' | 'normal' | 'good' | 'peak';
}

export interface BESSPerformance {
  id: string;
  name: string;
  score: number;
  totalLoss: number;
  issues: BESSIssue[];
}

export interface BESSIssue {
  id: string;
  severity: 'warning' | 'error';
  title: string;
  description: string;
  annualLoss: number;
  fix: string;
  fixDetails: string;
}

export interface BESSStatus {
  id: string;
  name: string;
  soc: number;
  status: 'charging' | 'discharging' | 'idle';
  power: number;
  currentPrice: number;
  nextAction: string;
  nextActionTime: string;
  nextActionRevenue: number;
}

export interface UploadProgress {
  stage: 'detecting' | 'reading' | 'matching' | 'calculating' | 'complete';
  progress: number;
  message: string;
  fileName: string;
  details: string[];
}
