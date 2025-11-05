/**
 * String Configuration Dialog
 * Manage string assignments for solar arrays
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Settings, CheckCircle, AlertCircle, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { apiClient } from '@/services/api/apiClient';
import { PanelAssignmentDialog } from './PanelAssignmentDialog';

interface StringConfigDialogProps {
  open: boolean;
  onClose: () => void;
  arrayId: number;
  plantId: number;
}

interface StringInfo {
  string_number: number;
  string_code: string;
  panels_count: number;
  max_panels: number;
  status: 'full' | 'partial' | 'empty';
}

interface StringDetails {
  string_number: number;
  array_name: string;
  panels: Array<{
    id: number;
    name: string;
    model: string;
    voltage: number;
    current: number;
    power: number;
  }>;
  panels_count: number;
  max_panels: number;
  status: string;
  total_voltage: number;
  nominal_current: number;
  total_power: number;
}

export function StringConfigDialog({ open, onClose, arrayId, plantId }: StringConfigDialogProps) {
  const queryClient = useQueryClient();
  const [selectedString, setSelectedString] = useState<number | null>(null);
  const [configMode, setConfigMode] = useState<'view' | 'config'>('view');
  const [numberOfStrings, setNumberOfStrings] = useState(0);
  const [panelsPerString, setPanelsPerString] = useState(0);
  const [panelAssignmentOpen, setPanelAssignmentOpen] = useState(false);

  // Load string configuration
  const { data: config, isLoading: configLoading } = useQuery({
    queryKey: ['string-config', arrayId],
    queryFn: async () => {
      const response = await apiClient.get(`/assets/${arrayId}/strings/config`);
      return response.data;
    },
    enabled: open && arrayId > 0,
  });

  // Load all strings
  const { data: strings, isLoading: stringsLoading } = useQuery<StringInfo[]>({
    queryKey: ['array-strings', arrayId],
    queryFn: async () => {
      const response = await apiClient.get(`/assets/${arrayId}/strings`);
      return response.data;
    },
    enabled: open && arrayId > 0,
  });

  // Load string details
  const { data: stringDetails, isLoading: detailsLoading } = useQuery<StringDetails>({
    queryKey: ['string-details', arrayId, selectedString],
    queryFn: async () => {
      const response = await apiClient.get(`/assets/${arrayId}/strings/${selectedString}`);
      return response.data;
    },
    enabled: open && arrayId > 0 && selectedString !== null,
  });

  // Load available panels
  const { data: availablePanels } = useQuery({
    queryKey: ['plant-panels', plantId],
    queryFn: async () => {
      const response = await apiClient.get(`/assets/plants/${plantId}/assets?component_type=panel`);
      return response.data;
    },
    enabled: open && plantId > 0,
  });

  // Update config mutation
  const updateConfigMutation = useMutation({
    mutationFn: async (data: { number_of_strings: number; panels_per_string: number }) => {
      const response = await apiClient.put(
        `/assets/${arrayId}/strings/config?number_of_strings=${data.number_of_strings}&panels_per_string=${data.panels_per_string}`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['string-config', arrayId] });
      queryClient.invalidateQueries({ queryKey: ['array-strings', arrayId] });
      setConfigMode('view');
    },
  });

  // Assign panels mutation
  const assignPanelsMutation = useMutation({
    mutationFn: async (data: { string_number: number; panel_ids: number[] }) => {
      const response = await apiClient.post(
        `/assets/${arrayId}/strings/${data.string_number}/assign`,
        {
          panel_ids: data.panel_ids,
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['array-strings', arrayId] });
      queryClient.invalidateQueries({ queryKey: ['string-details', arrayId, selectedString] });
    },
  });

  React.useEffect(() => {
    if (config) {
      setNumberOfStrings(config.number_of_strings || 0);
      setPanelsPerString(config.panels_per_string || 0);
    }
  }, [config]);

  const handleSaveConfig = () => {
    if (numberOfStrings > 0 && panelsPerString > 0) {
      updateConfigMutation.mutate({
        number_of_strings: numberOfStrings,
        panels_per_string: panelsPerString,
      });
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'full':
        return (
          <Badge variant="default" className="bg-green-500">
            Full
          </Badge>
        );
      case 'partial':
        return (
          <Badge variant="secondary" className="bg-yellow-500">
            Partial
          </Badge>
        );
      case 'empty':
        return <Badge variant="outline">Empty</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const canAddMore =
    selectedString && stringDetails ? stringDetails.panels_count < stringDetails.max_panels : false;

  if (configLoading || stringsLoading) {
    return (
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            String Configuration - {config?.array_name || 'Solar Array'}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Configuration Settings */}
          {configMode === 'config' ? (
            <Card>
              <CardHeader>
                <CardTitle>Array Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="numberOfStrings">Number of Strings</Label>
                    <Input
                      id="numberOfStrings"
                      type="number"
                      min="1"
                      value={numberOfStrings}
                      onChange={(e) => setNumberOfStrings(parseInt(e.target.value) || 0)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="panelsPerString">Panels per String</Label>
                    <Input
                      id="panelsPerString"
                      type="number"
                      min="1"
                      value={panelsPerString}
                      onChange={(e) => setPanelsPerString(parseInt(e.target.value) || 0)}
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button onClick={handleSaveConfig} disabled={updateConfigMutation.isPending}>
                    Save Configuration
                  </Button>
                  <Button variant="outline" onClick={() => setConfigMode('view')}>
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm text-muted-foreground">
                  {config?.number_of_strings || 0} strings × {config?.panels_per_string || 0}{' '}
                  panels/string
                </p>
              </div>
              <Button variant="outline" size="sm" onClick={() => setConfigMode('config')}>
                <Settings className="mr-2 h-4 w-4" />
                Configure
              </Button>
            </div>
          )}

          {/* Strings List */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {strings?.map((string) => (
              <Card
                key={string.string_number}
                className={`cursor-pointer transition-all ${
                  selectedString === string.string_number ? 'ring-2 ring-primary' : ''
                }`}
                onClick={() => setSelectedString(string.string_number)}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{string.string_code}</CardTitle>
                    {getStatusBadge(string.status)}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Panels:</span>
                      <span className="font-medium">
                        {string.panels_count} / {string.max_panels}
                      </span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{
                          width: `${(string.panels_count / string.max_panels) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* String Details */}
          {selectedString && stringDetails && (
            <Card>
              <CardHeader>
                <CardTitle>String {(stringDetails as any).string_code || 'Details'}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Metrics */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded">
                    <div className="text-2xl font-bold">
                      {stringDetails.total_voltage.toFixed(1)}
                    </div>
                    <div className="text-sm text-muted-foreground">Voltage (V)</div>
                  </div>
                  <div className="text-center p-4 border rounded">
                    <div className="text-2xl font-bold">
                      {stringDetails.nominal_current.toFixed(2)}
                    </div>
                    <div className="text-sm text-muted-foreground">Current (A)</div>
                  </div>
                  <div className="text-center p-4 border rounded">
                    <div className="text-2xl font-bold">
                      {(stringDetails.total_power / 1000).toFixed(2)}
                    </div>
                    <div className="text-sm text-muted-foreground">Power (kW)</div>
                  </div>
                </div>

                {/* Panels List */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">
                      Assigned Panels ({stringDetails.panels.length})
                    </h4>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        if (selectedString && stringDetails) {
                          setPanelAssignmentOpen(true);
                        }
                      }}
                      disabled={stringDetails.panels_count >= stringDetails.max_panels}
                    >
                      Assign Panels
                    </Button>
                  </div>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {stringDetails.panels.length > 0 ? (
                      stringDetails.panels.map((panel) => (
                        <div
                          key={panel.id}
                          className="flex items-center justify-between p-2 border rounded"
                        >
                          <div>
                            <p className="font-medium">{panel.name}</p>
                            <p className="text-sm text-muted-foreground">{panel.model}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="text-right text-sm">
                              <p>
                                {panel.voltage}V × {panel.current}A
                              </p>
                              <p className="text-muted-foreground">{panel.power}W</p>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={async () => {
                                try {
                                  await apiClient.delete(`/assets/${arrayId}/strings/${panel.id}`);
                                  queryClient.invalidateQueries({
                                    queryKey: ['string-details', arrayId, selectedString],
                                  });
                                  queryClient.invalidateQueries({
                                    queryKey: ['array-strings', arrayId],
                                  });
                                } catch (error) {
                                  console.error('Failed to remove panel:', error);
                                }
                              }}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-center text-muted-foreground py-4">No panels assigned</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Panel Assignment Dialog */}
        {selectedString && stringDetails && (
          <PanelAssignmentDialog
            open={panelAssignmentOpen}
            onClose={() => setPanelAssignmentOpen(false)}
            arrayId={arrayId}
            stringNumber={selectedString}
            plantId={plantId}
            maxPanels={stringDetails.max_panels}
            currentPanelIds={stringDetails.panels.map((p) => p.id)}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}
