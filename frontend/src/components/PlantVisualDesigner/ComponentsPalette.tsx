/**
 * Components Palette
 * Drag-and-drop component library for Visual Designer
 */

import React from 'react';
import { Sun, Wind, Battery, Zap, Factory, Grid3x3, Cable, Gauge, Radio } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

export interface PaletteComponent {
  id: string;
  type: string;
  label: string;
  icon: React.ReactNode;
  category: 'generation' | 'conversion' | 'storage' | 'consumption' | 'grid' | 'monitoring';
  description: string;
}

const components: PaletteComponent[] = [
  {
    id: 'solar-panel',
    type: 'solar-panel',
    label: 'Solar Panel',
    icon: <Sun className="h-5 w-5" />,
    category: 'generation',
    description: 'Individual solar panel',
  },
  {
    id: 'solar-array',
    type: 'solar-array',
    label: 'Solar Array',
    icon: <Sun className="h-6 w-6" />,
    category: 'generation',
    description: 'Large-scale solar installation',
  },
  {
    id: 'wind-turbine',
    type: 'wind-turbine',
    label: 'Wind Turbine',
    icon: <Wind className="h-5 w-5" />,
    category: 'generation',
    description: 'Wind turbine generator',
  },
  {
    id: 'inverter',
    type: 'inverter',
    label: 'Inverter',
    icon: <Zap className="h-5 w-5" />,
    category: 'conversion',
    description: 'DC to AC converter',
  },
  {
    id: 'transformer',
    type: 'transformer',
    label: 'Transformer',
    icon: <Cable className="h-5 w-5" />,
    category: 'conversion',
    description: 'Voltage transformer',
  },
  {
    id: 'bess',
    type: 'bess',
    label: 'BESS',
    icon: <Battery className="h-5 w-5" />,
    category: 'storage',
    description: 'Battery Energy Storage System',
  },
  {
    id: 'grid',
    type: 'grid',
    label: 'Grid',
    icon: <Grid3x3 className="h-5 w-5" />,
    category: 'grid',
    description: 'Power grid connection',
  },
  {
    id: 'consumer',
    type: 'consumer',
    label: 'Consumer',
    icon: <Factory className="h-5 w-5" />,
    category: 'consumption',
    description: 'Energy consumer',
  },
  {
    id: 'scada',
    type: 'scada',
    label: 'SCADA',
    icon: <Gauge className="h-5 w-5" />,
    category: 'monitoring',
    description: 'SCADA system',
  },
  {
    id: 'sensor',
    type: 'sensor',
    label: 'Sensor',
    icon: <Radio className="h-5 w-5" />,
    category: 'monitoring',
    description: 'Monitoring sensor',
  },
];

interface ComponentsPaletteProps {
  onDragStart: (component: PaletteComponent, event: React.DragEvent) => void;
  isEditMode: boolean;
}

export function ComponentsPalette({ onDragStart, isEditMode }: ComponentsPaletteProps) {
  if (!isEditMode) {
    return null;
  }

  const categories = {
    generation: components.filter((c) => c.category === 'generation'),
    conversion: components.filter((c) => c.category === 'conversion'),
    storage: components.filter((c) => c.category === 'storage'),
    consumption: components.filter((c) => c.category === 'consumption'),
    grid: components.filter((c) => c.category === 'grid'),
    monitoring: components.filter((c) => c.category === 'monitoring'),
  };

  return (
    <Card className="w-64 shadow-lg">
      <CardContent className="p-4">
        <h3 className="font-semibold mb-4">Components</h3>
        <div className="space-y-4 max-h-[600px] overflow-y-auto">
          {/* Generation */}
          {categories.generation.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground mb-2 uppercase">
                Generation
              </h4>
              <div className="space-y-2">
                {categories.generation.map((component) => (
                  <div
                    key={component.id}
                    draggable
                    onDragStart={(e) => onDragStart(component, e)}
                    className="flex items-center gap-2 p-2 border rounded cursor-move hover:bg-accent transition-colors"
                  >
                    <div className="text-muted-foreground">{component.icon}</div>
                    <div className="flex-1">
                      <div className="text-sm font-medium">{component.label}</div>
                      <div className="text-xs text-muted-foreground">{component.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Conversion */}
          {categories.conversion.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground mb-2 uppercase">
                Conversion
              </h4>
              <div className="space-y-2">
                {categories.conversion.map((component) => (
                  <div
                    key={component.id}
                    draggable
                    onDragStart={(e) => onDragStart(component, e)}
                    className="flex items-center gap-2 p-2 border rounded cursor-move hover:bg-accent transition-colors"
                  >
                    <div className="text-muted-foreground">{component.icon}</div>
                    <div className="flex-1">
                      <div className="text-sm font-medium">{component.label}</div>
                      <div className="text-xs text-muted-foreground">{component.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Storage */}
          {categories.storage.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground mb-2 uppercase">
                Storage
              </h4>
              <div className="space-y-2">
                {categories.storage.map((component) => (
                  <div
                    key={component.id}
                    draggable
                    onDragStart={(e) => onDragStart(component, e)}
                    className="flex items-center gap-2 p-2 border rounded cursor-move hover:bg-accent transition-colors"
                  >
                    <div className="text-muted-foreground">{component.icon}</div>
                    <div className="flex-1">
                      <div className="text-sm font-medium">{component.label}</div>
                      <div className="text-xs text-muted-foreground">{component.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Consumption */}
          {categories.consumption.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground mb-2 uppercase">
                Consumption
              </h4>
              <div className="space-y-2">
                {categories.consumption.map((component) => (
                  <div
                    key={component.id}
                    draggable
                    onDragStart={(e) => onDragStart(component, e)}
                    className="flex items-center gap-2 p-2 border rounded cursor-move hover:bg-accent transition-colors"
                  >
                    <div className="text-muted-foreground">{component.icon}</div>
                    <div className="flex-1">
                      <div className="text-sm font-medium">{component.label}</div>
                      <div className="text-xs text-muted-foreground">{component.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Grid */}
          {categories.grid.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground mb-2 uppercase">Grid</h4>
              <div className="space-y-2">
                {categories.grid.map((component) => (
                  <div
                    key={component.id}
                    draggable
                    onDragStart={(e) => onDragStart(component, e)}
                    className="flex items-center gap-2 p-2 border rounded cursor-move hover:bg-accent transition-colors"
                  >
                    <div className="text-muted-foreground">{component.icon}</div>
                    <div className="flex-1">
                      <div className="text-sm font-medium">{component.label}</div>
                      <div className="text-xs text-muted-foreground">{component.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Monitoring */}
          {categories.monitoring.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground mb-2 uppercase">
                Monitoring
              </h4>
              <div className="space-y-2">
                {categories.monitoring.map((component) => (
                  <div
                    key={component.id}
                    draggable
                    onDragStart={(e) => onDragStart(component, e)}
                    className="flex items-center gap-2 p-2 border rounded cursor-move hover:bg-accent transition-colors"
                  >
                    <div className="text-muted-foreground">{component.icon}</div>
                    <div className="flex-1">
                      <div className="text-sm font-medium">{component.label}</div>
                      <div className="text-xs text-muted-foreground">{component.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
