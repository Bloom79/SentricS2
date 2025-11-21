/**
 * Italian CER Regulatory Services API
 * Provides access to GSE, Terna, tax, compliance, and notification services
 */

import apiClient from './apiClient';
import { handleError } from '@/utils/errorHandler';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface GSEAuthResult {
  access_token: string;
  token_expiry: string;
  auth_level: string;
  test_mode: boolean;
}

export interface GSEApplicationResult {
  tracking_number: string;
  application_type: string;
  submission_date: string;
  estimated_response_date: string;
  status: string;
  test_mode: boolean;
}

export interface TernaRegistrationResult {
  producer_id?: string;
  censimp_code?: string;
  registration_date: string;
  status: string;
  deadline?: string;
  test_mode: boolean;
}

export interface TaxCalculationResult {
  base_amount: number;
  tax_rate: number;
  tax_amount: number;
  total_amount: number;
  tax_type: string;
}

export interface IncentiveRateResult {
  base_rate_eur_per_mwh: number;
  zonal_adjustment_eur_per_mwh: number;
  time_of_use_multiplier: number;
  final_rate_eur_per_mwh: number;
  plant_size_category: string;
  zone: string;
  time_slot: string;
}

export interface PNRREligibilityResult {
  eligible: boolean;
  total_investment_eur: number;
  funding_percentage: number;
  funding_amount_eur: number;
  comune_population: number;
  plant_power_kw: number;
  deadline: string;
  ineligibility_reasons?: string[];
}

export interface PODDetails {
  pod_code: string;
  meter_type: string;
  voltage_level: string;
  contracted_power_kw: number;
  dso: string;
  test_mode: boolean;
}

export interface HourlyEnergyData {
  hourly_data: Array<{
    timestamp: string;
    energy_kwh: number;
    quality: string;
  }>;
  total_kwh: number;
  hours_count: number;
  data_quality: {
    measured_hours: number;
    estimated_hours: number;
    profiled_hours: number;
  };
}

// ============================================================================
// ITALIAN SERVICE
// ============================================================================

export const italianService = {
  // ==========================================================================
  // GSE OPERATIONS
  // ==========================================================================

  gse: {
    /**
     * Authenticate with GSE portal using SPID
     */
    async authenticate(fiscalCode: string, authLevel: string = 'level2'): Promise<GSEAuthResult> {
      try {
        const response = await apiClient.post('/cer/italian/gse/authenticate', null, {
          params: { fiscal_code: fiscalCode, auth_level: authLevel }
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Submit RID (Ritiro Dedicato) application
     */
    async submitRIDApplication(
      plantData: any,
      producerData: any,
      documents: string[]
    ): Promise<GSEApplicationResult> {
      try {
        const response = await apiClient.post('/cer/italian/gse/rid-application', {
          plant_data: plantData,
          producer_data: producerData,
          documents
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Submit TCEC incentive application (CRITICAL: 120-day deadline)
     */
    async submitTCECApplication(
      cerId: number,
      cerData: any,
      plants: any[],
      members: any[],
      documents: string[]
    ): Promise<GSEApplicationResult> {
      try {
        const response = await apiClient.post('/cer/italian/gse/tcec-application', {
          cer_id: cerId,
          cer_data: cerData,
          plants,
          members,
          documents
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Submit PNRR funding application (40% of investment)
     */
    async submitPNRRApplication(
      cerId: number,
      investmentData: any,
      comuneData: any,
      documents: string[]
    ): Promise<GSEApplicationResult> {
      try {
        const response = await apiClient.post('/cer/italian/gse/pnrr-application', {
          cer_id: cerId,
          investment_data: investmentData,
          comune_data: comuneData,
          documents
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Upload monthly hourly meter data to GSE
     */
    async uploadMeterData(
      trackingNumber: string,
      periodMonth: number,
      periodYear: number,
      hourlyData: any[]
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/gse/upload-meter-data', {
          tracking_number: trackingNumber,
          period_month: periodMonth,
          period_year: periodYear,
          hourly_data: hourlyData
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Get GSE application status
     */
    async getApplicationStatus(trackingNumber: string): Promise<any> {
      try {
        const response = await apiClient.get(`/cer/italian/gse/application-status/${trackingNumber}`);
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    }
  },

  // ==========================================================================
  // TERNA OPERATIONS
  // ==========================================================================

  terna: {
    /**
     * Register producer in Terna GAUDÌ
     */
    async registerProducer(producerData: any): Promise<TernaRegistrationResult> {
      try {
        const response = await apiClient.post('/cer/italian/terna/register-producer', {
          producer_data: producerData
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Register plant in Terna GAUDÌ (CRITICAL: 30-day deadline)
     */
    async registerPlant(
      producerId: string,
      plantData: any,
      gridConnectionDate: string
    ): Promise<TernaRegistrationResult> {
      try {
        const response = await apiClient.post('/cer/italian/terna/register-plant', {
          producer_id: producerId,
          plant_data: plantData,
          grid_connection_date: gridConnectionDate
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Check DSO validation status (15 working days)
     */
    async checkValidationStatus(censimpCode: string): Promise<any> {
      try {
        const response = await apiClient.get(`/cer/italian/terna/validation-status/${censimpCode}`);
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    }
  },

  // ==========================================================================
  // TAX OPERATIONS
  // ==========================================================================

  tax: {
    /**
     * Calculate Italian IVA (VAT)
     */
    async calculateIVA(
      amount: number,
      transactionCategory: string,
      cerLegalType: string
    ): Promise<TaxCalculationResult> {
      try {
        const response = await apiClient.post('/cer/italian/tax/calculate-iva', null, {
          params: {
            amount,
            transaction_category: transactionCategory,
            cer_legal_type: cerLegalType
          }
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Calculate Ritenuta d'Acconto (withholding tax)
     */
    async calculateRitenuta(
      gsePaymentAmount: number,
      cerLegalType: string
    ): Promise<TaxCalculationResult> {
      try {
        const response = await apiClient.post('/cer/italian/tax/calculate-ritenuta', null, {
          params: {
            gse_payment_amount: gsePaymentAmount,
            cer_legal_type: cerLegalType
          }
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Calculate IRES (corporate income tax)
     */
    async calculateIRES(
      grossIncome: number,
      deductibleExpenses: number,
      ritenutePaid: number,
      cerLegalType: string
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/tax/calculate-ires', null, {
          params: {
            gross_income: grossIncome,
            deductible_expenses: deductibleExpenses,
            ritenute_paid: ritenutePaid,
            cer_legal_type: cerLegalType
          }
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Generate F24 tax payment form
     */
    async generateF24(
      cerFiscalCode: string,
      taxType: string,
      amount: number,
      paymentPeriod: string,
      cerLegalType: string
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/tax/generate-f24', null, {
          params: {
            cer_fiscal_code: cerFiscalCode,
            tax_type: taxType,
            amount,
            payment_period: paymentPeriod,
            cer_legal_type: cerLegalType
          }
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Get current Italian tax rates
     */
    async getTaxRates(): Promise<any> {
      try {
        const response = await apiClient.get('/cer/italian/tax/rates');
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    }
  },

  // ==========================================================================
  // INCENTIVE OPERATIONS
  // ==========================================================================

  incentives: {
    /**
     * Calculate TCEC incentive rate
     */
    async calculateTCECRate(
      powerKw: number,
      zone: string,
      timestamp?: string
    ): Promise<IncentiveRateResult> {
      try {
        const params: any = { power_kw: powerKw, zone };
        if (timestamp) params.timestamp = timestamp;

        const response = await apiClient.get('/cer/italian/incentives/tcec-rate', { params });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Calculate hourly incentives
     */
    async calculateHourlyIncentives(
      powerKw: number,
      zone: string,
      hourlyEnergyKwh: Record<string, number>
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/incentives/calculate-hourly', {
          power_kw: powerKw,
          zone,
          hourly_energy_kwh: hourlyEnergyKwh
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Check PNRR funding eligibility
     */
    async checkPNRREligibility(
      totalInvestmentEur: number,
      comunePopulation: number,
      plantPowerKw: number
    ): Promise<PNRREligibilityResult> {
      try {
        const response = await apiClient.post('/cer/italian/incentives/pnrr-eligibility', {
          total_investment_eur: totalInvestmentEur,
          comune_population: comunePopulation,
          plant_power_kw: plantPowerKw
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * 20-year financial forecast
     */
    async forecast20Years(
      plantPowerKw: number,
      zone: string,
      annualProductionKwh: number,
      totalInvestmentEur: number,
      comunePopulation?: number
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/incentives/forecast-20-years', {
          plant_power_kw: plantPowerKw,
          zone,
          annual_production_kwh: annualProductionKwh,
          total_investment_eur: totalInvestmentEur,
          comune_population: comunePopulation
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    }
  },

  // ==========================================================================
  // SMART METER OPERATIONS
  // ==========================================================================

  smartMeter: {
    /**
     * Get POD details
     */
    async getPODDetails(podCode: string): Promise<PODDetails> {
      try {
        const response = await apiClient.get(`/cer/italian/smart-meter/pod-details/${podCode}`);
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Get hourly consumption data
     */
    async getHourlyConsumption(
      podCode: string,
      fromDate: string,
      toDate: string
    ): Promise<HourlyEnergyData> {
      try {
        const response = await apiClient.get(`/cer/italian/smart-meter/consumption/${podCode}`, {
          params: { from_date: fromDate, to_date: toDate }
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Get hourly production data
     */
    async getHourlyProduction(
      podCode: string,
      fromDate: string,
      toDate: string
    ): Promise<HourlyEnergyData> {
      try {
        const response = await apiClient.get(`/cer/italian/smart-meter/production/${podCode}`, {
          params: { from_date: fromDate, to_date: toDate }
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Validate smart meter data quality
     */
    async validateDataQuality(hourlyData: any[], expectedHours: number): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/smart-meter/validate-data', {
          hourly_data: hourlyData,
          expected_hours: expectedHours
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    }
  },

  // ==========================================================================
  // ARERA COMPLIANCE OPERATIONS
  // ==========================================================================

  arera: {
    /**
     * Apply GSE standard load profile
     */
    async applyStandardProfile(
      dailyTotalKwh: number,
      profileType: string,
      date: string
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/arera/apply-standard-profile', {
          daily_total_kwh: dailyTotalKwh,
          profile_type: profileType,
          date_str: date
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Validate energy sharing calculation (TIAD rules)
     */
    async validateEnergySharing(
      hourlyProduction: Record<string, number>,
      hourlyConsumption: Record<string, number>
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/arera/validate-energy-sharing', {
          hourly_production: hourlyProduction,
          hourly_consumption: hourlyConsumption
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Calculate grid fees
     */
    async calculateGridFees(energyKwh: number, voltageLevel: string): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/arera/calculate-grid-fees', {
          energy_kwh: energyKwh,
          voltage_level: voltageLevel
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Get all GSE standard load profiles
     */
    async getStandardProfiles(): Promise<any> {
      try {
        const response = await apiClient.get('/cer/italian/arera/standard-profiles');
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    }
  },

  // ==========================================================================
  // DOCUMENT GENERATION
  // ==========================================================================

  documents: {
    /**
     * Generate Modello Unico Part I (before work)
     */
    async generateModelloUnicoPart1(
      plantData: any,
      ownerData: any,
      connectionType: string
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/documents/modello-unico/part1', {
          plant_data: plantData,
          owner_data: ownerData,
          connection_type: connectionType
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Generate Modello Unico Part II (after completion)
     */
    async generateModelloUnicoPart2(
      part1Data: any,
      commissioningData: any,
      testResults: any
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/documents/modello-unico/part2', {
          part_1_data: part1Data,
          commissioning_data: commissioningData,
          test_results: testResults
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Generate CER statute (15 articles)
     */
    async generateStatute(
      cerName: string,
      legalType: string,
      foundingMembers: any[],
      primarySubstationId: string,
      governanceStructure: any
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/documents/statute/generate', {
          cer_name: cerName,
          legal_type: legalType,
          founding_members: foundingMembers,
          primary_substation_id: primarySubstationId,
          governance_structure: governanceStructure
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Validate statute compliance
     */
    async validateStatute(statuteData: any): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/documents/statute/validate', {
          statute_data: statuteData
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    }
  },

  // ==========================================================================
  // NOTIFICATIONS
  // ==========================================================================

  notifications: {
    /**
     * Send welcome email to new member
     */
    async sendWelcome(
      memberEmail: string,
      memberName: string,
      cerName: string,
      joinDate: string,
      portalUrl: string
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/notifications/welcome', {
          member_email: memberEmail,
          member_name: memberName,
          cer_name: cerName,
          join_date: joinDate,
          portal_url: portalUrl
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Send monthly energy report
     */
    async sendMonthlyReport(
      memberEmail: string,
      memberName: string,
      cerName: string,
      energyData: any,
      financialData: any,
      periodMonth: string
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/notifications/monthly-report', {
          member_email: memberEmail,
          member_name: memberName,
          cer_name: cerName,
          energy_data: energyData,
          financial_data: financialData,
          period_month: periodMonth
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Send deadline alert
     */
    async sendDeadlineAlert(
      recipientEmail: string,
      recipientName: string,
      deadlineType: string,
      deadlineDate: string,
      daysRemaining: number,
      actionRequired: string
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/notifications/deadline-alert', {
          recipient_email: recipientEmail,
          recipient_name: recipientName,
          deadline_type: deadlineType,
          deadline_date: deadlineDate,
          days_remaining: daysRemaining,
          action_required: actionRequired
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    },

    /**
     * Schedule all compliance reminders for new plant
     */
    async scheduleComplianceReminders(
      plantCommissioningDate: string,
      cerContactEmail: string,
      cerName: string,
      plantName: string
    ): Promise<any> {
      try {
        const response = await apiClient.post('/cer/italian/notifications/schedule-compliance-reminders', {
          plant_commissioning_date: plantCommissioningDate,
          cer_contact_email: cerContactEmail,
          cer_name: cerName,
          plant_name: plantName
        });
        return response.data;
      } catch (error) {
        throw handleError(error);
      }
    }
  }
};

export default italianService;
