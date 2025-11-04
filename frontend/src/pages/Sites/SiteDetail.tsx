/**
 * Site Detail Page
 * Shows site information with tabs for Plants, Consumers, Storage, Energy Flow
 */

import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Edit, MapPin, Battery, Users, Zap, Building2, Activity } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/services/api/apiClient';
import {
  PlantsTab,
  ConsumersTab,
  StorageTab,
  EnergyFlowTab,
} from './SiteDetailTabs';

export default function SiteDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');

  const { data: site, isLoading } = useQuery({
    queryKey: ['site', id],
    queryFn: async () => {
      const response = await apiClient.get(`/sites/${id}`);
      return response.data;
    },
  });

  const { data: stats } = useQuery({
    queryKey: ['site-stats', id],
    queryFn: async () => {
      const response = await apiClient.get(`/sites/${id}/stats`);
      return response.data;
    },
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (!site) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Site not found</p>
        <Button onClick={() => navigate('/sites')} className="mt-4">
          Back to Sites
        </Button>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'plants', label: 'Plants' },
    { id: 'consumers', label: 'Consumers' },
    { id: 'storage', label: 'Storage' },
    { id: 'energy-flow', label: 'Energy Flow' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/sites')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{site.name}</h1>
            {site.code && (
              <p className="text-muted-foreground">Code: {site.code}</p>
            )}
          </div>
        </div>
        <Button variant="outline">
          <Edit className="mr-2 h-4 w-4" />
          Edit Site
        </Button>
      </div>

      {/* Status Badge */}
      <div className="flex items-center gap-2">
        <Badge variant={site.status === 'active' ? 'default' : 'secondary'}>
          {site.status}
        </Badge>
        {site.site_type && (
          <Badge variant="outline">{site.site_type}</Badge>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Capacity</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.total_capacity_kw 
                ? `${(stats.total_capacity_kw / 1000).toFixed(2)} MW`
                : site.capacity 
                  ? `${(site.capacity / 1000).toFixed(2)} MW`
                  : 'N/A'}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Plants</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.plants_count || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Storage Units</CardTitle>
            <Battery className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.storage_units_count || 0}</div>
            {stats?.total_storage_capacity_kwh && (
              <p className="text-xs text-muted-foreground">
                {stats.total_storage_capacity_kwh.toFixed(2)} kWh
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Consumers</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.consumers_count || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Location Info */}
      {site.location && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              Location
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {site.address && <p>{site.address}</p>}
              {site.city && (
                <p className="text-sm text-muted-foreground">
                  {site.city}
                  {site.province && `, ${site.province}`}
                  {site.region && `, ${site.region}`}
                </p>
              )}
              {site.latitude && site.longitude && (
                <p className="text-xs text-muted-foreground">
                  Coordinates: {site.latitude}, {site.longitude}
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Card>
        <CardHeader>
          <div className="flex border-b">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </CardHeader>
        <CardContent>
          {activeTab === 'overview' && (
            <div className="space-y-4">
              {site.description && (
                <div>
                  <h3 className="font-semibold mb-2">Description</h3>
                  <p className="text-muted-foreground">{site.description}</p>
                </div>
              )}
              
              <div className="grid gap-4 md:grid-cols-2">
                {site.capacity && (
                  <div>
                    <h3 className="font-semibold mb-2">Capacity</h3>
                    <p className="text-muted-foreground">
                      {(site.capacity / 1000).toFixed(2)} MW
                    </p>
                  </div>
                )}
                {site.efficiency && (
                  <div>
                    <h3 className="font-semibold mb-2">Efficiency</h3>
                    <p className="text-muted-foreground">{site.efficiency}%</p>
                  </div>
                )}
                {site.owner && (
                  <div>
                    <h3 className="font-semibold mb-2">Owner</h3>
                    <p className="text-muted-foreground">{site.owner}</p>
                  </div>
                )}
                {site.operator && (
                  <div>
                    <h3 className="font-semibold mb-2">Operator</h3>
                    <p className="text-muted-foreground">{site.operator}</p>
                  </div>
                )}
              </div>

              {site.notes && (
                <div>
                  <h3 className="font-semibold mb-2">Notes</h3>
                  <p className="text-muted-foreground">{site.notes}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'plants' && <PlantsTab siteId={parseInt(id!)} />}
          {activeTab === 'consumers' && <ConsumersTab siteId={parseInt(id!)} />}
          {activeTab === 'storage' && <StorageTab siteId={parseInt(id!)} />}
          {activeTab === 'energy-flow' && <EnergyFlowTab siteId={parseInt(id!)} />}
        </CardContent>
      </Card>
    </div>
  );
}

