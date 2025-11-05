/**
 * Asset API Service
 * Migrated from Sentrics Supabase to API client
 */

import apiClient from './apiClient';
import { handleError } from '@/utils/errorHandler';

export interface AssetType {
  id: number;
  name: string;
  description?: string;
  normalized_name: string;
  attributes: Record<string, any>;
}

export interface Asset {
  id: number;
  plant_id: number;
  type_id: number;
  name: string;
  model?: string;
  manufacturer?: string;
  serial_number?: string;
  component_type?: string;
  status: string;
  location?: string;
  installation_date?: string;
  rated_power?: number;
  efficiency?: number;
  voltage?: number;
  current?: number;
  dynamic_attributes: Record<string, any>;
  parent_id?: number;
  notes?: string;
  warranty_expiry?: string;
}

export const assetService = {
  async getAssetTypes(): Promise<AssetType[]> {
    try {
      const response = await apiClient.get('/assets/types');
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async getPlantAssets(plantId: number): Promise<Asset[]> {
    try {
      const response = await apiClient.get(`/assets/plants/${plantId}/assets`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async getAsset(assetId: number): Promise<Asset> {
    try {
      const response = await apiClient.get(`/assets/${assetId}`);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async createAsset(plantId: number, assetData: Partial<Asset>): Promise<Asset> {
    try {
      const response = await apiClient.post(`/assets/plants/${plantId}/assets`, assetData);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async updateAsset(assetId: number, assetData: Partial<Asset>): Promise<Asset> {
    try {
      const response = await apiClient.put(`/assets/${assetId}`, assetData);
      return response.data;
    } catch (error) {
      throw handleError(error);
    }
  },

  async deleteAsset(assetId: number): Promise<void> {
    try {
      await apiClient.delete(`/assets/${assetId}`);
    } catch (error) {
      throw handleError(error);
    }
  },
};
