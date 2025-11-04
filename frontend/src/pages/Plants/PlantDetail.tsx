/**
 * Plant Detail Page
 * Consolidated from Kronos EAM
 */

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Edit, Building2, Shield, Activity, TrendingUp, FileText, Network, Settings, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/services/api/apiClient';
import { assetService } from '@/services/api/asset.service';
import {
  GSETab,
  TernaTab,
  DSOTab,
  DoganeTab,
  ComplianceTab,
  WorkflowsTab,
} from './PlantDetailTabs';
import { VisualDesignerTab } from '@/components/PlantVisualDesigner/VisualDesignerTab';
import { StringConfigDialog } from '@/components/StringConfiguration/StringConfigDialog';
import { BulkImportDialog } from '@/components/BulkImport/BulkImportDialog';
import { getPlantStatusLabel, getPlantTypeLabel, getPlantStatusVariant } from '@/utils/plantUtils';

export default function PlantDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [stringConfigOpen, setStringConfigOpen] = useState(false);
  const [bulkImportOpen, setBulkImportOpen] = useState(false);
  const [selectedArrayId, setSelectedArrayId] = useState<number | null>(null);

  const { data: plant, isLoading } = useQuery({
    queryKey: ['plant', id],
    queryFn: async () => {
      const response = await apiClient.get(`/plants/${id}`);
      return response.data;
    },
  });

  const { data: assets } = useQuery({
    queryKey: ['plant-assets', id],
    queryFn: async () => {
      if (!id) return [];
      return assetService.getPlantAssets(parseInt(id));
    },
    enabled: !!id,
  });

  const { data: stats } = useQuery({
    queryKey: ['plant-stats', id],
    queryFn: async () => {
      const response = await apiClient.get(`/plants/${id}/stats`);
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

  if (!plant) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground">Plant not found</p>
          <Button onClick={() => navigate('/plants')} className="mt-4">
            Back to Plants
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/plants')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{plant.name}</h1>
            <p className="text-muted-foreground">{plant.code}</p>
          </div>
        </div>
        <Button onClick={() => navigate(`/plants/${id}/edit`)}>
          <Edit className="mr-2 h-4 w-4" />
          Edit
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Plant Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status:</span>
              <Badge variant={getPlantStatusVariant(plant.status)}>
                {getPlantStatusLabel(plant.status)}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Type:</span>
              <span className="font-medium">{getPlantTypeLabel(plant.type)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Power:</span>
              <span className="font-medium">{plant.power}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Location:</span>
              <span className="font-medium">{plant.location}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Region:</span>
              <span className="font-medium">{plant.region}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Statistics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {stats && (
              <>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Assets:</span>
                  <span className="font-medium">{stats.total_assets || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Operational Assets:</span>
                  <span className="font-medium">{stats.operational_assets || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">CER Linked:</span>
                  <Badge variant={stats.cer_linked ? 'default' : 'outline'}>
                    {stats.cer_linked ? 'Yes' : 'No'}
                  </Badge>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {assets && assets.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Assets ({assets.length})</CardTitle>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setBulkImportOpen(true)}
                >
                  <Upload className="mr-2 h-4 w-4" />
                  Bulk Import
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {assets.map((asset: any) => (
                <div 
                  key={asset.id} 
                  className="flex justify-between items-center p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{asset.name}</p>
                      {asset.manufacturer && (
                        <span className="text-xs text-muted-foreground">
                          {asset.manufacturer}
                          {asset.model && ` ${asset.model}`}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 mt-1">
                      <Badge variant="outline" className="text-xs capitalize">
                        {asset.component_type || 'Unknown'}
                      </Badge>
                      {asset.location && (
                        <span className="text-xs text-muted-foreground">{asset.location}</span>
                      )}
                      {asset.rated_power && (
                        <span className="text-xs text-muted-foreground">
                          {asset.rated_power} kW
                        </span>
                      )}
                      {asset.efficiency && (
                        <span className="text-xs text-muted-foreground">
                          {asset.efficiency}% efficiency
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {(asset.component_type === 'solar_array' || asset.component_type === 'panel') && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedArrayId(asset.id);
                          setStringConfigOpen(true);
                        }}
                        title="Configure Strings"
                      >
                        <Settings className="h-4 w-4" />
                      </Button>
                    )}
                    <Badge variant={asset.status === 'operational' ? 'default' : 'secondary'}>
                      {asset.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <div className="border-b">
        <div className="flex gap-2">
          {[
            { id: 'overview', name: 'Overview', icon: Building2 },
            { id: 'visual-designer', name: 'Visual Designer', icon: Network },
            { id: 'compliance', name: 'Compliance', icon: Shield },
            { id: 'workflows', name: 'Workflows', icon: Activity },
            { id: 'dso', name: 'DSO', icon: Activity },
            { id: 'terna', name: 'Terna', icon: Shield },
            { id: 'gse', name: 'GSE', icon: TrendingUp },
            { id: 'dogane', name: 'Customs', icon: FileText },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 border-b-2 transition-colors flex items-center gap-2 ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              >
                <Icon className="h-4 w-4" />
                {tab.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'visual-designer' && id && <VisualDesignerTab plantId={parseInt(id)} />}
        {activeTab === 'compliance' && <ComplianceTab plant={plant} />}
        {activeTab === 'workflows' && id && <WorkflowsTab plantId={parseInt(id)} />}
        {activeTab === 'dso' && <DSOTab plant={plant} />}
        {activeTab === 'terna' && <TernaTab plant={plant} />}
        {activeTab === 'gse' && <GSETab plant={plant} />}
        {activeTab === 'dogane' && <DoganeTab plant={plant} />}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Plant Metadata */}
            <Card>
              <CardHeader>
                <CardTitle>Plant Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  {plant.address && (
                    <div>
                      <span className="text-sm text-muted-foreground">Address:</span>
                      <p className="font-medium">{plant.address}</p>
                    </div>
                  )}
                  {plant.municipality && (
                    <div>
                      <span className="text-sm text-muted-foreground">Municipality:</span>
                      <p className="font-medium">{plant.municipality}</p>
                      {plant.province && <span className="text-sm text-muted-foreground"> ({plant.province})</span>}
                    </div>
                  )}
                  {plant.latitude && plant.longitude && (
                    <div>
                      <span className="text-sm text-muted-foreground">Coordinates:</span>
                      <p className="font-medium">
                        {plant.latitude.toFixed(6)}, {plant.longitude.toFixed(6)}
                      </p>
                    </div>
                  )}
                  {plant.tags && plant.tags.length > 0 && (
                    <div>
                      <span className="text-sm text-muted-foreground">Tags:</span>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {plant.tags.map((tag: string, idx: number) => (
                          <Badge key={idx} variant="outline">{tag}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Assets Summary */}
            {assets && assets.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Assets Overview</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-3">
                    <div className="text-center p-4 border rounded-lg">
                      <p className="text-2xl font-bold">{assets.length}</p>
                      <p className="text-sm text-muted-foreground">Total Assets</p>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <p className="text-2xl font-bold text-green-600">
                        {assets.filter((a: any) => a.status === 'operational').length}
                      </p>
                      <p className="text-sm text-muted-foreground">Operational</p>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <p className="text-2xl font-bold">
                        {assets.reduce((sum: number, a: any) => sum + (a.rated_power || 0), 0).toFixed(1)} kW
                      </p>
                      <p className="text-sm text-muted-foreground">Total Rated Power</p>
                    </div>
                  </div>
                  
                  {/* Asset Types Breakdown */}
                  <div className="mt-6">
                    <h4 className="text-sm font-semibold mb-3">By Component Type</h4>
                    <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
                      {Array.from(new Set(assets.map((a: any) => a.component_type))).map((type: string) => {
                        const count = assets.filter((a: any) => a.component_type === type).length;
                        return (
                          <div key={type} className="flex justify-between items-center p-2 border rounded">
                            <span className="text-sm capitalize">{type || 'Unknown'}</span>
                            <Badge variant="outline">{count}</Badge>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  <Button variant="outline" onClick={() => setBulkImportOpen(true)}>
                    <Upload className="mr-2 h-4 w-4" />
                    Bulk Import Assets
                  </Button>
                  <Button variant="outline" onClick={() => navigate(`/plants/${id}/edit`)}>
                    <Edit className="mr-2 h-4 w-4" />
                    Edit Plant
                  </Button>
                  {plant.cer_id && (
                    <Button variant="outline" onClick={() => navigate(`/cer/${plant.cer_id}`)}>
                      <Building2 className="mr-2 h-4 w-4" />
                      View CER
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* String Configuration Dialog */}
      {selectedArrayId && id && (
        <StringConfigDialog
          open={stringConfigOpen}
          onClose={() => {
            setStringConfigOpen(false);
            setSelectedArrayId(null);
          }}
          arrayId={selectedArrayId}
          plantId={parseInt(id)}
        />
      )}

      {/* Bulk Import Dialog */}
      {id && (
        <BulkImportDialog
          open={bulkImportOpen}
          onClose={() => setBulkImportOpen(false)}
          plantId={parseInt(id)}
          arrayId={selectedArrayId || undefined}
        />
      )}
    </div>
  );
}

