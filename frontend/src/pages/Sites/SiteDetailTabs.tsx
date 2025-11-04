/**
 * Site Detail Tabs Components
 * Tab components for Plants, Consumers, Storage, Energy Flow
 */

// React import removed (unused) 'react';
import { useQuery } from '@tanstack/react-query';
import { Plus, Building2, Users, Battery, Zap, MapPin } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/services/api/apiClient';
import { useNavigate } from 'react-router-dom';
import { getPlantStatusLabel, getPlantTypeLabel, getPlantStatusVariant } from '@/utils/plantUtils';

interface PlantsTabProps {
  siteId: number;
}

export function PlantsTab({ siteId }: PlantsTabProps) {
  const navigate = useNavigate();

  const { data: plants, isLoading } = useQuery({
    queryKey: ['site-plants', siteId],
    queryFn: async () => {
      const response = await apiClient.get(`/plants?site_id=${siteId}`);
      return response.data;
    },
  });

  if (isLoading) {
    return <div className="text-center py-8">Loading plants...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Plants at this Site</h3>
        <Button size="sm" onClick={() => navigate(`/plants/new?site_id=${siteId}`)}>
          <Plus className="mr-2 h-4 w-4" />
          Add Plant
        </Button>
      </div>

      {plants && plants.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {plants.map((plant: any) => (
            <Card
              key={plant.id}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => navigate(`/plants/${plant.id}`)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-base">{plant.name}</CardTitle>
                    <p className="text-sm text-muted-foreground">{plant.code}</p>
                  </div>
                  <Badge variant={getPlantStatusVariant(plant.status)}>
                    {getPlantStatusLabel(plant.status)}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Type:</span>
                    <span className="font-medium">{getPlantTypeLabel(plant.type)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Power:</span>
                    <span className="font-medium">{plant.power}</span>
                  </div>
                  {plant.location && (
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <MapPin className="h-3 w-3" />
                      <span className="text-xs">{plant.location}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-muted-foreground">
          <Building2 className="h-12 w-12 mx-auto mb-2 opacity-50" />
          <p>No plants at this site</p>
        </div>
      )}
    </div>
  );
}

interface ConsumersTabProps {
  siteId: number;
}

export function ConsumersTab({ siteId }: ConsumersTabProps) {
  const { data: consumers, isLoading } = useQuery({
    queryKey: ['site-consumers', siteId],
    queryFn: async () => {
      const response = await apiClient.get(`/sites/${siteId}/consumers`);
      return response.data;
    },
  });

  if (isLoading) {
    return <div className="text-center py-8">Loading consumers...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Consumers</h3>
        <Button size="sm">
          <Plus className="mr-2 h-4 w-4" />
          Add Consumer
        </Button>
      </div>

      {consumers && consumers.length > 0 ? (
        <div className="space-y-4">
          {consumers.map((consumer: any) => (
            <Card key={consumer.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-base">{consumer.name}</CardTitle>
                    {consumer.code && (
                      <p className="text-sm text-muted-foreground">{consumer.code}</p>
                    )}
                  </div>
                  <Badge variant="outline">{consumer.consumer_type}</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid gap-2 md:grid-cols-2 text-sm">
                  {consumer.pod_id && (
                    <div>
                      <span className="text-muted-foreground">POD:</span>
                      <span className="ml-2 font-medium">{consumer.pod_id}</span>
                    </div>
                  )}
                  {consumer.average_consumption_kw && (
                    <div>
                      <span className="text-muted-foreground">Avg Consumption:</span>
                      <span className="ml-2 font-medium">
                        {consumer.average_consumption_kw.toFixed(2)} kW
                      </span>
                    </div>
                  )}
                  {consumer.peak_consumption_kw && (
                    <div>
                      <span className="text-muted-foreground">Peak Consumption:</span>
                      <span className="ml-2 font-medium">
                        {consumer.peak_consumption_kw.toFixed(2)} kW
                      </span>
                    </div>
                  )}
                  {consumer.address && (
                    <div className="flex items-center gap-1">
                      <MapPin className="h-3 w-3 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">{consumer.address}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-muted-foreground">
          <Users className="h-12 w-12 mx-auto mb-2 opacity-50" />
          <p>No consumers at this site</p>
        </div>
      )}
    </div>
  );
}

interface StorageTabProps {
  siteId: number;
}

export function StorageTab({ siteId }: StorageTabProps) {
  const { data: storageUnits, isLoading } = useQuery({
    queryKey: ['site-storage', siteId],
    queryFn: async () => {
      const response = await apiClient.get(`/sites/${siteId}/storage-units`);
      return response.data;
    },
  });

  if (isLoading) {
    return <div className="text-center py-8">Loading storage units...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Storage Units (BESS)</h3>
        <Button size="sm">
          <Plus className="mr-2 h-4 w-4" />
          Add Storage Unit
        </Button>
      </div>

      {storageUnits && storageUnits.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {storageUnits.map((unit: any) => (
            <Card key={unit.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-base">{unit.name}</CardTitle>
                    {unit.code && (
                      <p className="text-sm text-muted-foreground">{unit.code}</p>
                    )}
                  </div>
                  <Badge variant={unit.status === 'operational' ? 'default' : 'secondary'}>
                    {unit.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Capacity:</span>
                    <span className="font-medium">{unit.capacity_kwh.toFixed(2)} kWh</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Rated Power:</span>
                    <span className="font-medium">{unit.rated_power_kw.toFixed(2)} kW</span>
                  </div>
                  {unit.chemistry_type && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Chemistry:</span>
                      <span className="font-medium">{unit.chemistry_type}</span>
                    </div>
                  )}
                  {unit.state_of_charge !== null && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">State of Charge:</span>
                      <span className="font-medium">{unit.state_of_charge.toFixed(1)}%</span>
                    </div>
                  )}
                  {unit.state_of_health !== null && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">State of Health:</span>
                      <span className="font-medium">{unit.state_of_health.toFixed(1)}%</span>
                    </div>
                  )}
                  {unit.total_cycles !== null && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Total Cycles:</span>
                      <span className="font-medium">{unit.total_cycles}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-muted-foreground">
          <Battery className="h-12 w-12 mx-auto mb-2 opacity-50" />
          <p>No storage units at this site</p>
        </div>
      )}
    </div>
  );
}

interface EnergyFlowTabProps {
  siteId: number;
}

export function EnergyFlowTab({ siteId }: EnergyFlowTabProps) {
  const { data: energyFlow, isLoading } = useQuery({
    queryKey: ['site-energy-flow', siteId],
    queryFn: async () => {
      const response = await apiClient.get(`/sites/${siteId}/energy-flow`);
      return response.data;
    },
  });

  if (isLoading) {
    return <div className="text-center py-8">Loading energy flow...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Energy Flow Visualization</h3>
        <Button size="sm">
          <Zap className="mr-2 h-4 w-4" />
          Edit Layout
        </Button>
      </div>

      {energyFlow ? (
        <Card>
          <CardContent className="py-8">
            <div className="text-center text-muted-foreground">
              <Zap className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>Visual Plant Designer coming soon</p>
              <p className="text-xs mt-2">
                This will display the React Flow canvas with plant layout
              </p>
            </div>
            {/* TODO: Implement React Flow canvas here */}
          </CardContent>
        </Card>
      ) : (
        <div className="text-center py-8 text-muted-foreground">
          <Zap className="h-12 w-12 mx-auto mb-2 opacity-50" />
          <p>No energy flow layout configured</p>
          <Button className="mt-4" size="sm">
            Create Energy Flow Layout
          </Button>
        </div>
      )}
    </div>
  );
}

