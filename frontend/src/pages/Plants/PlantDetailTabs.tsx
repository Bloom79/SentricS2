/**
 * Plant Detail Tabs
 * Tab components for PlantDetail page
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, TrendingUp, Shield, Activity, AlertCircle, CheckCircle } from 'lucide-react';
import { PlantComplianceView } from '@/components/compliance/PlantComplianceView';

interface Plant {
  id: number;
  name: string;
  registry?: {
    gaudi?: string;
    pod?: string;
  };
}

export function GSETab({ plant }: { plant: Plant }) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            GSE Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Convention Number:</span>
              <span className="font-medium">RID/2022/00123456</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status:</span>
              <Badge>Active</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export function TernaTab({ plant }: { plant: Plant }) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Terna/GAUDÌ Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">GAUDÌ Code:</span>
              <span className="font-medium">{plant.registry?.gaudi || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status:</span>
              <Badge>Validated</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export function DSOTab({ plant }: { plant: Plant }) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            DSO Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Distributor:</span>
              <span className="font-medium">E-Distribuzione S.p.A.</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Connection Status:</span>
              <Badge>Active</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export function DoganeTab({ plant }: { plant: Plant }) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Customs Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">License Number:</span>
              <span className="font-medium">IT12BR000123E</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status:</span>
              <Badge>Active</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export function ComplianceTab({ plant }: { plant: Plant }) {
  return <PlantComplianceView plantId={plant.id} plantName={plant.name} />;
}

export function WorkflowsTab({ plantId }: { plantId: number }) {
  // Import dynamically to avoid circular dependencies
  const WorkflowsTabComponent = React.lazy(() => 
    import('./WorkflowsTab').then(module => ({ default: module.WorkflowsTab }))
  );
  
  return (
    <React.Suspense fallback={
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
    </div>
    }>
      <WorkflowsTabComponent plantId={plantId} />
    </React.Suspense>
  );
}


