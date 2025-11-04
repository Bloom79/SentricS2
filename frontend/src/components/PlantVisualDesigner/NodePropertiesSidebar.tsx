/**
 * Node Properties Sidebar
 * Edit properties of selected nodes
 */

import React, { useState, useEffect } from 'react';
import { X, Save } from 'lucide-react';
import { Node } from '@xyflow/react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FlowNodeData } from './FlowNodeTypes';

interface NodePropertiesSidebarProps {
  node: Node | null;
  onClose: () => void;
  onUpdate: (nodeId: string, data: Partial<FlowNodeData>) => void;
  onDelete: (nodeId: string) => void;
}

export function NodePropertiesSidebar({
  node,
  onClose,
  onUpdate,
  onDelete,
}: NodePropertiesSidebarProps) {
  const [label, setLabel] = useState('');
  const [power, setPower] = useState('');
  const [efficiency, setEfficiency] = useState('');
  const [voltage, setVoltage] = useState('');
  const [current, setCurrent] = useState('');
  const [capacity, setCapacity] = useState('');
  const [status, setStatus] = useState<'active' | 'inactive' | 'error'>('active');

  useEffect(() => {
    if (node) {
      const nodeData = node.data as FlowNodeData;
      setLabel(nodeData.label || '');
      setPower(nodeData.specs?.power?.toString() || '');
      setEfficiency(nodeData.specs?.efficiency?.toString() || '');
      setVoltage(nodeData.specs?.voltage?.toString() || '');
      setCurrent(nodeData.specs?.current?.toString() || '');
      setCapacity(nodeData.specs?.capacity?.toString() || '');
      setStatus(nodeData.status || 'active');
    }
  }, [node]);

  const handleSave = () => {
    if (!node) return;
    const nodeData = node.data as FlowNodeData;

    const updatedData: Partial<FlowNodeData> = {
      label,
      status,
      specs: {
        ...nodeData.specs,
        power: power ? parseFloat(power) : undefined,
        efficiency: efficiency ? parseFloat(efficiency) : undefined,
        voltage: voltage ? parseFloat(voltage) : undefined,
        current: current ? parseFloat(current) : undefined,
        capacity: capacity ? parseFloat(capacity) : undefined,
      },
    };

    onUpdate(node.id, updatedData);
  };

  const handleDelete = () => {
    if (!node) return;
    const nodeData = node.data as FlowNodeData;
    if (window.confirm(`Delete ${nodeData.label}?`)) {
      onDelete(node.id);
      onClose();
    }
  };

  if (!node) return null;

  return (
    <Card className="w-80 h-full shadow-lg">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Node Properties</CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Basic Info */}
        <div className="space-y-2">
          <Label htmlFor="node-label">Label</Label>
          <Input
            id="node-label"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder="Node label"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="node-status">Status</Label>
          <select
            id="node-status"
            value={status}
            onChange={(e) => setStatus(e.target.value as 'active' | 'inactive' | 'error')}
            className="w-full px-3 py-2 border rounded-md"
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="error">Error</option>
          </select>
        </div>

        {/* Specs */}
        <div className="space-y-4 pt-4 border-t">
          <h4 className="font-semibold text-sm">Specifications</h4>

          {(node.type === 'solar-panel' || node.type === 'solar-array' || node.type === 'wind-turbine' || node.type === 'inverter') && (
            <div className="space-y-2">
              <Label htmlFor="node-power">Power (kW)</Label>
              <Input
                id="node-power"
                type="number"
                value={power}
                onChange={(e) => setPower(e.target.value)}
                placeholder="0"
              />
            </div>
          )}

          {(node.type === 'solar-panel' || node.type === 'solar-array' || node.type === 'inverter') && (
            <div className="space-y-2">
              <Label htmlFor="node-efficiency">Efficiency (%)</Label>
              <Input
                id="node-efficiency"
                type="number"
                value={efficiency}
                onChange={(e) => setEfficiency(e.target.value)}
                placeholder="0"
                min="0"
                max="100"
              />
            </div>
          )}

          {(node.type === 'solar-panel' || node.type === 'transformer') && (
            <>
              <div className="space-y-2">
                <Label htmlFor="node-voltage">Voltage (V)</Label>
                <Input
                  id="node-voltage"
                  type="number"
                  value={voltage}
                  onChange={(e) => setVoltage(e.target.value)}
                  placeholder="0"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="node-current">Current (A)</Label>
                <Input
                  id="node-current"
                  type="number"
                  value={current}
                  onChange={(e) => setCurrent(e.target.value)}
                  placeholder="0"
                />
              </div>
            </>
          )}

          {node.type === 'bess' || node.type === 'battery' ? (
            <div className="space-y-2">
              <Label htmlFor="node-capacity">Capacity (kWh)</Label>
              <Input
                id="node-capacity"
                type="number"
                value={capacity}
                onChange={(e) => setCapacity(e.target.value)}
                placeholder="0"
              />
            </div>
          ) : null}
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-4 border-t">
          <Button onClick={handleSave} className="flex-1">
            <Save className="mr-2 h-4 w-4" />
            Save
          </Button>
          <Button variant="destructive" onClick={handleDelete}>
            Delete
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

