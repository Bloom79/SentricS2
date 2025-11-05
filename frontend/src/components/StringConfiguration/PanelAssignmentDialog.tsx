/**
 * Panel Assignment Dialog
 * Select and assign panels to a string
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Check, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/services/api/apiClient';

interface PanelAssignmentDialogProps {
  open: boolean;
  onClose: () => void;
  arrayId: number;
  stringNumber: number;
  plantId: number;
  maxPanels: number;
  currentPanelIds: number[];
}

export function PanelAssignmentDialog({
  open,
  onClose,
  arrayId,
  stringNumber,
  plantId,
  maxPanels,
  currentPanelIds,
}: PanelAssignmentDialogProps) {
  const queryClient = useQueryClient();
  const [selectedPanelIds, setSelectedPanelIds] = useState<number[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  // Load available panels
  const { data: panels, isLoading } = useQuery({
    queryKey: ['plant-panels', plantId],
    queryFn: async () => {
      const response = await apiClient.get(`/assets/plants/${plantId}/assets?component_type=panel`);
      return response.data;
    },
    enabled: open && plantId > 0,
  });

  // Filter panels - exclude already assigned ones
  const availablePanels = panels?.filter((panel: any) => !currentPanelIds.includes(panel.id)) || [];

  const filteredPanels = availablePanels.filter(
    (panel: any) =>
      panel.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      panel.model?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      panel.serial_number?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Assign panels mutation
  const assignMutation = useMutation({
    mutationFn: async (panelIds: number[]) => {
      const response = await apiClient.post(`/assets/${arrayId}/strings/${stringNumber}/assign`, {
        panel_ids: panelIds,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['array-strings', arrayId] });
      queryClient.invalidateQueries({ queryKey: ['string-details', arrayId, stringNumber] });
      queryClient.invalidateQueries({ queryKey: ['string-config', arrayId] });
      onClose();
    },
  });

  const handleTogglePanel = (panelId: number) => {
    if (selectedPanelIds.includes(panelId)) {
      setSelectedPanelIds(selectedPanelIds.filter((id) => id !== panelId));
    } else {
      // Check max panels limit
      const totalAfterAdd = selectedPanelIds.length + currentPanelIds.length + 1;
      if (totalAfterAdd <= maxPanels) {
        setSelectedPanelIds([...selectedPanelIds, panelId]);
      }
    }
  };

  const handleAssign = () => {
    if (selectedPanelIds.length > 0) {
      assignMutation.mutate(selectedPanelIds);
    }
  };

  const canAddMore = selectedPanelIds.length + currentPanelIds.length < maxPanels;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Assign Panels to String {stringNumber}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Selection Summary */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Selected</p>
                  <p className="text-2xl font-bold">{selectedPanelIds.length}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Capacity</p>
                  <p className="text-2xl font-bold">
                    {currentPanelIds.length + selectedPanelIds.length} / {maxPanels}
                  </p>
                </div>
                {!canAddMore && <Badge variant="destructive">Maximum capacity reached</Badge>}
              </div>
            </CardContent>
          </Card>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search panels by name, model, or serial number..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8"
            />
          </div>

          {/* Panels List */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                Available Panels ({filteredPanels.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
                </div>
              ) : filteredPanels.length > 0 ? (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {filteredPanels.map((panel: any) => {
                    const isSelected = selectedPanelIds.includes(panel.id);
                    const canSelect = canAddMore || isSelected;

                    return (
                      <div
                        key={panel.id}
                        className={`flex items-center justify-between p-3 border rounded cursor-pointer transition-all ${
                          isSelected ? 'bg-primary/10 border-primary' : ''
                        } ${!canSelect ? 'opacity-50 cursor-not-allowed' : 'hover:bg-accent'}`}
                        onClick={() => canSelect && handleTogglePanel(panel.id)}
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`w-5 h-5 border-2 rounded flex items-center justify-center ${
                              isSelected ? 'border-primary bg-primary' : 'border-muted-foreground'
                            }`}
                          >
                            {isSelected && <Check className="h-3 w-3 text-primary-foreground" />}
                          </div>
                          <div>
                            <p className="font-medium">{panel.name}</p>
                            <div className="flex gap-2 text-sm text-muted-foreground">
                              {panel.model && <span>Model: {panel.model}</span>}
                              {panel.serial_number && <span>SN: {panel.serial_number}</span>}
                              {panel.dynamic_attributes?.power_rating && (
                                <span>{panel.dynamic_attributes.power_rating}W</span>
                              )}
                            </div>
                          </div>
                        </div>
                        <Badge variant={panel.status === 'operational' ? 'default' : 'secondary'}>
                          {panel.status}
                        </Badge>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">
                  {searchTerm ? 'No panels match your search' : 'No available panels'}
                </p>
              )}
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button
              onClick={handleAssign}
              disabled={selectedPanelIds.length === 0 || assignMutation.isPending}
            >
              {assignMutation.isPending
                ? 'Assigning...'
                : `Assign ${selectedPanelIds.length} Panel(s)`}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
