/**
 * Flow Node Types Registry
 * Custom node types for React Flow
 */

import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { cn } from '@/lib/utils';
import { Sun, Wind, Battery, Zap, Factory, Grid3x3, Cable, Gauge, Radio } from 'lucide-react';

export interface FlowNodeData {
  label: string;
  type: string;
  specs?: {
    power?: number;
    efficiency?: number;
    voltage?: number;
    current?: number;
    capacity?: number;
    [key: string]: any;
  };
  status?: 'active' | 'inactive' | 'error';
  [key: string]: any;
}

const nodeBaseStyles = 'px-4 py-3 rounded-lg border-2 shadow-md min-w-[120px] text-center';
const nodeActiveStyles = 'border-green-500 bg-green-50';
const nodeInactiveStyles = 'border-gray-300 bg-gray-50';
const nodeErrorStyles = 'border-red-500 bg-red-50';

// Solar Panel Node
export function SolarPanelNode({ data, selected }: NodeProps) {
  const nodeData = data as FlowNodeData;
  const isActive = nodeData.status === 'active';
  const hasError = nodeData.status === 'error';

  return (
    <div
      className={cn(
        nodeBaseStyles,
        hasError ? nodeErrorStyles : isActive ? nodeActiveStyles : nodeInactiveStyles,
        selected && 'ring-2 ring-primary'
      )}
    >
      <Handle type="target" position={Position.Top} />
      <Sun className="h-6 w-6 mx-auto mb-1" />
      <div className="font-semibold text-sm">{nodeData.label}</div>
      {nodeData.specs?.power && (
        <div className="text-xs text-muted-foreground">{nodeData.specs.power}W</div>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Solar Array Node
export function SolarArrayNode({ data, selected }: NodeProps) {
  const nodeData = data as FlowNodeData;
  const isActive = nodeData.status === 'active';
  const hasError = nodeData.status === 'error';

  return (
    <div
      className={cn(
        nodeBaseStyles,
        hasError ? nodeErrorStyles : isActive ? nodeActiveStyles : nodeInactiveStyles,
        selected && 'ring-2 ring-primary',
        'min-w-[150px]'
      )}
    >
      <Handle type="target" position={Position.Top} />
      <Sun className="h-8 w-8 mx-auto mb-2" />
      <div className="font-semibold">{nodeData.label}</div>
      {nodeData.specs?.power && (
        <div className="text-xs text-muted-foreground">
          {(nodeData.specs.power / 1000).toFixed(2)} MW
        </div>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Wind Turbine Node
export function WindTurbineNode({ data, selected }: NodeProps) {
  const nodeData = data as FlowNodeData;
  const isActive = nodeData.status === 'active';
  const hasError = nodeData.status === 'error';

  return (
    <div
      className={cn(
        nodeBaseStyles,
        hasError ? nodeErrorStyles : isActive ? nodeActiveStyles : nodeInactiveStyles,
        selected && 'ring-2 ring-primary'
      )}
    >
      <Handle type="target" position={Position.Top} />
      <Wind className="h-6 w-6 mx-auto mb-1" />
      <div className="font-semibold text-sm">{nodeData.label}</div>
      {nodeData.specs?.power && (
        <div className="text-xs text-muted-foreground">{nodeData.specs.power}kW</div>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Inverter Node
export function InverterNode({ data, selected }: NodeProps) {
  const nodeData = data as FlowNodeData;
  const isActive = nodeData.status === 'active';
  const hasError = nodeData.status === 'error';

  return (
    <div
      className={cn(
        nodeBaseStyles,
        hasError ? nodeErrorStyles : isActive ? nodeActiveStyles : nodeInactiveStyles,
        selected && 'ring-2 ring-primary'
      )}
    >
      <Handle type="target" position={Position.Top} />
      <Zap className="h-6 w-6 mx-auto mb-1" />
      <div className="font-semibold text-sm">{nodeData.label}</div>
      {nodeData.specs?.power && (
        <div className="text-xs text-muted-foreground">{nodeData.specs.power}kW</div>
      )}
      {nodeData.specs?.efficiency && (
        <div className="text-xs text-muted-foreground">η {nodeData.specs.efficiency}%</div>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Battery/BESS Node
export function BESSNode({ data, selected }: NodeProps) {
  const nodeData = data as FlowNodeData;
  const isActive = nodeData.status === 'active';
  const hasError = nodeData.status === 'error';

  return (
    <div
      className={cn(
        nodeBaseStyles,
        hasError ? nodeErrorStyles : isActive ? nodeActiveStyles : nodeInactiveStyles,
        selected && 'ring-2 ring-primary'
      )}
    >
      <Handle type="target" position={Position.Top} />
      <Battery className="h-6 w-6 mx-auto mb-1" />
      <div className="font-semibold text-sm">{nodeData.label}</div>
      {nodeData.specs?.capacity && (
        <div className="text-xs text-muted-foreground">{nodeData.specs.capacity}kWh</div>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Transformer Node
export function TransformerNode({ data, selected }: NodeProps) {
  const nodeData = data as FlowNodeData;
  const isActive = nodeData.status === 'active';
  const hasError = nodeData.status === 'error';

  return (
    <div
      className={cn(
        nodeBaseStyles,
        hasError ? nodeErrorStyles : isActive ? nodeActiveStyles : nodeInactiveStyles,
        selected && 'ring-2 ring-primary'
      )}
    >
      <Handle type="target" position={Position.Top} />
      <Cable className="h-6 w-6 mx-auto mb-1" />
      <div className="font-semibold text-sm">{nodeData.label}</div>
      {nodeData.specs?.voltage && (
        <div className="text-xs text-muted-foreground">{nodeData.specs.voltage}V</div>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Grid Node
export function GridNode({ data, selected }: NodeProps) {
  const nodeData = data as FlowNodeData;
  const isActive = nodeData.status === 'active';
  const hasError = nodeData.status === 'error';

  return (
    <div
      className={cn(
        nodeBaseStyles,
        hasError ? nodeErrorStyles : isActive ? nodeActiveStyles : nodeInactiveStyles,
        selected && 'ring-2 ring-primary'
      )}
    >
      <Handle type="target" position={Position.Top} />
      <Grid3x3 className="h-6 w-6 mx-auto mb-1" />
      <div className="font-semibold text-sm">{nodeData.label}</div>
      <div className="text-xs text-muted-foreground">Grid</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Consumer Node
export function ConsumerNode({ data, selected }: NodeProps) {
  const nodeData = data as FlowNodeData;
  const isActive = nodeData.status === 'active';
  const hasError = nodeData.status === 'error';

  return (
    <div
      className={cn(
        nodeBaseStyles,
        hasError ? nodeErrorStyles : isActive ? nodeActiveStyles : nodeInactiveStyles,
        selected && 'ring-2 ring-primary'
      )}
    >
      <Handle type="target" position={Position.Top} />
      <Factory className="h-6 w-6 mx-auto mb-1" />
      <div className="font-semibold text-sm">{nodeData.label}</div>
      {nodeData.specs?.power && (
        <div className="text-xs text-muted-foreground">{nodeData.specs.power}kW</div>
      )}
    </div>
  );
}

// SCADA Node
export function SCADANode({ data, selected }: NodeProps) {
  const nodeData = data as FlowNodeData;
  const isActive = nodeData.status === 'active';
  const hasError = nodeData.status === 'error';

  return (
    <div
      className={cn(
        nodeBaseStyles,
        hasError ? nodeErrorStyles : isActive ? nodeActiveStyles : nodeInactiveStyles,
        selected && 'ring-2 ring-primary'
      )}
    >
      <Handle type="target" position={Position.Top} />
      <Gauge className="h-6 w-6 mx-auto mb-1" />
      <div className="font-semibold text-sm">{nodeData.label}</div>
      <div className="text-xs text-muted-foreground">SCADA</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Sensor Node
export function SensorNode({ data, selected }: NodeProps) {
  const nodeData = data as FlowNodeData;
  const isActive = nodeData.status === 'active';
  const hasError = nodeData.status === 'error';

  return (
    <div
      className={cn(
        nodeBaseStyles,
        hasError ? nodeErrorStyles : isActive ? nodeActiveStyles : nodeInactiveStyles,
        selected && 'ring-2 ring-primary',
        'min-w-[100px]'
      )}
    >
      <Handle type="target" position={Position.Top} />
      <Radio className="h-5 w-5 mx-auto mb-1" />
      <div className="font-semibold text-xs">{nodeData.label}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Default Node
export function DefaultNode({ data, selected }: NodeProps) {
  const nodeData = data as FlowNodeData;
  const isActive = nodeData.status === 'active';
  const hasError = nodeData.status === 'error';

  return (
    <div
      className={cn(
        nodeBaseStyles,
        hasError ? nodeErrorStyles : isActive ? nodeActiveStyles : nodeInactiveStyles,
        selected && 'ring-2 ring-primary'
      )}
    >
      <Handle type="target" position={Position.Top} />
      <div className="font-semibold text-sm">{nodeData.label}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// Node types registry
export const nodeTypes = {
  'solar-panel': SolarPanelNode,
  'solar-array': SolarArrayNode,
  'wind-turbine': WindTurbineNode,
  inverter: InverterNode,
  bess: BESSNode,
  battery: BESSNode,
  transformer: TransformerNode,
  grid: GridNode,
  consumer: ConsumerNode,
  scada: SCADANode,
  sensor: SensorNode,
  default: DefaultNode,
};
