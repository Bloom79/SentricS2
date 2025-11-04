/**
 * Edge Configuration Dialog
 * Configure connection properties between nodes
 */

import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { Edge } from '@xyflow/react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

interface EdgeConfigDialogProps {
  open: boolean;
  onClose: () => void;
  edge: Edge | null;
  onUpdate: (edgeId: string, data: any) => void;
  onDelete: (edgeId: string) => void;
}

export function EdgeConfigDialog({
  open,
  onClose,
  edge,
  onUpdate,
  onDelete,
}: EdgeConfigDialogProps) {
  const [energyFlow, setEnergyFlow] = useState('');
  const [efficiency, setEfficiency] = useState('');
  const [label, setLabel] = useState('');
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    if (edge) {
      setEnergyFlow(edge.data?.energyFlow?.toString() || '');
      setEfficiency(edge.data?.efficiency?.toString() || '');
      setLabel(edge.label?.toString() || '');
      setAnimated(edge.animated || false);
    }
  }, [edge]);

  const handleSave = () => {
    if (!edge) return;

    const updatedData = {
      energyFlow: energyFlow ? parseFloat(energyFlow) : undefined,
      efficiency: efficiency ? parseFloat(efficiency) : undefined,
    };

    onUpdate(edge.id, {
      ...edge,
      label: label || undefined,
      animated,
      data: updatedData,
    });
  };

  const handleDelete = () => {
    if (!edge) return;
    if (window.confirm('Delete this connection?')) {
      onDelete(edge.id);
      onClose();
    }
  };

  if (!edge) return null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Connection Properties</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="edge-label">Label</Label>
            <Input
              id="edge-label"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="Connection label"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edge-energy-flow">Energy Flow (kW)</Label>
            <Input
              id="edge-energy-flow"
              type="number"
              value={energyFlow}
              onChange={(e) => setEnergyFlow(e.target.value)}
              placeholder="0"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edge-efficiency">Efficiency (%)</Label>
            <Input
              id="edge-efficiency"
              type="number"
              value={efficiency}
              onChange={(e) => setEfficiency(e.target.value)}
              placeholder="100"
              min="0"
              max="100"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="edge-animated"
              checked={animated}
              onChange={(e) => setAnimated(e.target.checked)}
              className="rounded"
            />
            <Label htmlFor="edge-animated">Animated (show energy flow)</Label>
          </div>

          <div className="flex gap-2 pt-4">
            <Button onClick={handleSave} className="flex-1">
              Save
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Delete
            </Button>
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

