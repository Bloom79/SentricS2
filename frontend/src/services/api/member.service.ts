/**
 * Member API Service
 * Provides member-specific operations including dashboard data
 */

import apiClient from './apiClient';
import { handleError } from '@/utils/errorHandler';

export interface MemberDashboardData {
  member: {
    id: number;
    name: string;
    member_code: string;
    member_type: 'consumer' | 'producer' | 'prosumer';
    join_date: string;
    status: string;
  };

  // Energy metrics
  energy: {
    consumed_mtd: number; // kWh month-to-date
    produced_mtd: number; // kWh
    shared_mtd: number; // kWh
    self_consumed_mtd: number; // kWh
    consumed_ytd: number;
    produced_ytd: number;
    shared_ytd: number;
  };

  // Financial benefits
  financial: {
    savings_mtd: number; // EUR
    incentives_mtd: number; // EUR
    total_benefit_mtd: number; // EUR
    savings_ytd: number;
    incentives_ytd: number;
    total_benefit_ytd: number;
    pending_payments: number;
    last_payment_date: string | null;
    last_payment_amount: number;
  };

  // Monthly history
  history: Array<{
    month: string;
    consumed: number;
    produced: number;
    shared: number;
    savings: number;
    incentives: number;
  }>;

  // Invoices
  invoices: Array<{
    id: number;
    invoice_number: string;
    date: string;
    amount: number;
    status: 'pending' | 'paid' | 'overdue';
    pdf_url: string;
  }>;

  // Environmental impact
  environmental: {
    co2_avoided_ytd: number; // kg
    trees_equivalent: number;
  };

  // Community info
  community: {
    cer_name: string;
    total_members: number;
    total_capacity_kw: number;
    member_rank: number; // Ranking by shared energy
  };
}

export interface MemberBenefitsSummary {
  member_id: number;
  period_start: string;
  period_end: string;
  energy_shared: number;
  savings_amount: number;
  incentives_amount: number;
  total_benefit: number;
}

export interface MemberEnergyHistory {
  timestamp: string;
  consumed: number;
  produced: number;
  shared: number;
  self_consumed: number;
}

export const memberService = {
  /**
   * Get comprehensive dashboard data for a member
   */
  async getMemberDashboard(cerId: number, memberId: number): Promise<MemberDashboardData> {
    try {
      const response = await apiClient.get(`/cer/communities/${cerId}/members/${memberId}/dashboard`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  /**
   * Get member benefits summary for a specific period
   */
  async getMemberBenefits(
    cerId: number,
    memberId: number,
    periodStart?: string,
    periodEnd?: string
  ): Promise<MemberBenefitsSummary> {
    try {
      const params: any = {};
      if (periodStart) params.period_start = periodStart;
      if (periodEnd) params.period_end = periodEnd;

      const response = await apiClient.get(
        `/cer/communities/${cerId}/members/${memberId}/benefits`,
        { params }
      );
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  /**
   * Get member energy history
   */
  async getMemberEnergyHistory(
    cerId: number,
    memberId: number,
    months: number = 12
  ): Promise<MemberEnergyHistory[]> {
    try {
      const response = await apiClient.get(
        `/cer/communities/${cerId}/members/${memberId}/energy-history`,
        { params: { months } }
      );
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  /**
   * Get member invoices
   */
  async getMemberInvoices(
    cerId: number,
    memberId: number,
    limit: number = 20
  ): Promise<any[]> {
    try {
      const response = await apiClient.get(
        `/cer/communities/${cerId}/members/${memberId}/invoices`,
        { params: { limit } }
      );
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  /**
   * Validate POD (Point of Delivery) code
   */
  async validatePOD(podCode: string): Promise<{ valid: boolean; details?: any; error?: string }> {
    try {
      const response = await apiClient.post('/cer/italian/smart-meter/validate-pod', {
        pod_code: podCode
      });
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  /**
   * Download member invoice PDF
   */
  async downloadInvoicePDF(invoiceId: number): Promise<Blob> {
    try {
      const response = await apiClient.get(`/billing/invoices/${invoiceId}/pdf`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  /**
   * Export member dashboard report
   */
  async exportDashboardReport(
    cerId: number,
    memberId: number,
    format: 'pdf' | 'excel' = 'pdf'
  ): Promise<Blob> {
    try {
      const response = await apiClient.get(
        `/cer/communities/${cerId}/members/${memberId}/dashboard/export`,
        {
          params: { format },
          responseType: 'blob'
        }
      );
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  }
};

export default memberService;
