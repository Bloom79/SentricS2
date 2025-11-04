/**
 * CER API Service
 * Migrated from Sentrics, using API client instead of Supabase
 */

import apiClient from './apiClient';
import { handleError } from '@/utils/errorHandler';

export interface CER {
  id: number;
  name: string;
  legal_type: string;
  status: string;
  description?: string;
  address: string;
  region: string;
  primary_substation_id: string;
  total_capacity: number;
  gse_compliance_status: string;
  pnrr_funding_applied: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CERMemberAsset {
  id: number;
  member_id: number;
  cer_id: number;
  name: string;
  asset_type: string; // SOLAR, WIND, STORAGE, BIOMASS, HYDRO
  capacity: number; // kW
  installation_date: string;
  gse_registration_id?: string;
  status: string;
  asset_metadata?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface CERMember {
  id: number;
  cer_id: number;
  name: string;
  address: string;
  member_type: string; // consumer, producer, prosumer
  pod_id: string;
  status: string;
  user_type?: string; // real, simulated
  consumption_class?: string;
  load_profile_type: string;
  contracted_power?: number;
  smart_meter_id?: string;
  meter_type?: string;
  fiscal_code?: string;
  vat_number?: string;
  voltage_level?: string;
  activation_date?: string;
  verification_status?: string;
  technical_info?: Record<string, any>;
  load_profile_data?: Record<string, any>;
  plant_id?: number; // Link to plant if exists
  assets?: CERMemberAsset[]; // Member assets
  energy_produced: number;
  energy_consumed: number;
  energy_shared: number;
  created_at: string;
  updated_at?: string;
}

export const cerService = {
  async getCERs(): Promise<CER[]> {
    try {
      const response = await apiClient.get('/cer/communities');
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async getCER(id: number): Promise<CER> {
    try {
      const response = await apiClient.get(`/cer/communities/${id}`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async createCER(data: Partial<CER>): Promise<CER> {
    try {
      const response = await apiClient.post('/cer/communities', data);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async updateCER(id: number, data: Partial<CER>): Promise<CER> {
    try {
      const response = await apiClient.put(`/cer/communities/${id}`, data);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async deleteCER(id: number): Promise<void> {
    try {
      await apiClient.delete(`/cer/communities/${id}`);
    } catch (error) {
      throw handleError(error);
    }
  },

  async getMembers(cerId: number): Promise<CERMember[]> {
    try {
      const response = await apiClient.get(`/cer/communities/${cerId}/members`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async addMember(cerId: number, memberData: Partial<CERMember>): Promise<CERMember> {
    try {
      const response = await apiClient.post(`/cer/communities/${cerId}/members`, memberData);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async getMember(cerId: number, memberId: number): Promise<CERMember> {
    try {
      const response = await apiClient.get(`/cer/communities/${cerId}/members/${memberId}`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async updateMember(cerId: number, memberId: number, memberData: Partial<CERMember>): Promise<CERMember> {
    try {
      const response = await apiClient.put(`/cer/communities/${cerId}/members/${memberId}`, memberData);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async deleteMember(cerId: number, memberId: number): Promise<void> {
    try {
      await apiClient.delete(`/cer/communities/${cerId}/members/${memberId}`);
    } catch (error) {
      throw handleError(error);
    }
  },

  async getCERStats(cerId: number): Promise<any> {
    try {
      const response = await apiClient.get(`/cer/communities/${cerId}/stats`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  // Member Assets
  async getMemberAssets(cerId: number, memberId: number): Promise<CERMemberAsset[]> {
    try {
      const response = await apiClient.get(`/cer/communities/${cerId}/members/${memberId}/assets`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async createMemberAsset(
    cerId: number,
    memberId: number,
    assetData: Partial<CERMemberAsset>
  ): Promise<CERMemberAsset> {
    try {
      const response = await apiClient.post(
        `/cer/communities/${cerId}/members/${memberId}/assets`,
        assetData
      );
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async updateMemberAsset(
    cerId: number,
    memberId: number,
    assetId: number,
    assetData: Partial<CERMemberAsset>
  ): Promise<CERMemberAsset> {
    try {
      const response = await apiClient.put(
        `/cer/communities/${cerId}/members/${memberId}/assets/${assetId}`,
        assetData
      );
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async deleteMemberAsset(cerId: number, memberId: number, assetId: number): Promise<void> {
    try {
      await apiClient.delete(`/cer/communities/${cerId}/members/${memberId}/assets/${assetId}`);
    } catch (error) {
      throw handleError(error);
    }
  },

  // Plant Linking
  async getCERPlants(cerId: number): Promise<any[]> {
    try {
      const response = await apiClient.get(`/cer/communities/${cerId}/plants`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async linkPlant(cerId: number, plantId: number): Promise<void> {
    try {
      await apiClient.post(`/cer/communities/${cerId}/plants/${plantId}/link`);
    } catch (error) {
      throw handleError(error);
    }
  },

  async unlinkPlant(cerId: number, plantId: number): Promise<void> {
    try {
      await apiClient.delete(`/cer/communities/${cerId}/plants/${plantId}/link`);
    } catch (error) {
      throw handleError(error);
    }
  },

  // Participation Requests
  async createParticipationRequest(data: {
    cer_id: number;
    notes?: string;
  }): Promise<CERParticipationRequest> {
    try {
      const response = await apiClient.post('/cer/participation-requests', data);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async getParticipationRequests(params?: {
    cer_id?: number;
    status?: string;
  }): Promise<CERParticipationRequest[]> {
    try {
      const response = await apiClient.get('/cer/participation-requests', { params });
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async getParticipationRequest(requestId: number): Promise<CERParticipationRequest> {
    try {
      const response = await apiClient.get(`/cer/participation-requests/${requestId}`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async updateParticipationRequest(
    requestId: number,
    data: { status: string; notes?: string }
  ): Promise<CERParticipationRequest> {
    try {
      const response = await apiClient.put(`/cer/participation-requests/${requestId}`, data);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async deleteParticipationRequest(requestId: number): Promise<void> {
    try {
      await apiClient.delete(`/cer/participation-requests/${requestId}`);
    } catch (error) {
      throw handleError(error);
    }
  },

  async getMyParticipationRequests(): Promise<CERParticipationRequest[]> {
    try {
      const response = await apiClient.get('/cer/participation-requests/user/me');
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async getCERParticipationRequests(cerId: number): Promise<CERParticipationRequest[]> {
    try {
      const response = await apiClient.get(`/cer/communities/${cerId}/participation-requests`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  // Documents
  async getCERDocuments(cerId: number): Promise<any[]> {
    try {
      const response = await apiClient.get(`/cer/communities/${cerId}/documents`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async getCERDocumentsOverview(cerId: number): Promise<any> {
    try {
      const response = await apiClient.get(`/cer/communities/${cerId}/documents/overview`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  // Compliance
  async getCERCompliance(cerId: number): Promise<any> {
    try {
      const response = await apiClient.get(`/cer/communities/${cerId}/compliance`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async getCERComplianceRequirements(cerId: number, includePlants: boolean = true): Promise<any[]> {
    try {
      const params = includePlants ? { include_plants: true } : {};
      const response = await apiClient.get(`/cer/communities/${cerId}/compliance/requirements`, { params });
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async getCERComplianceRecords(cerId: number, status?: string, includePlants: boolean = true): Promise<any[]> {
    try {
      const params: any = { include_plants: includePlants };
      if (status) params.status = status;
      const response = await apiClient.get(`/cer/communities/${cerId}/compliance/records`, { params });
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },
};

export interface CERParticipationRequest {
  id: number;
  cer_id: number;
  user_id: number;
  status: string; // pending, approved, rejected, cancelled
  request_date: string;
  processed_date?: string;
  notes?: string;
  // Extended fields from WithDetails schema
  user_name?: string;
  user_email?: string;
  cer_name?: string;
}

