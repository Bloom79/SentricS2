/**
 * Plant Compliance View Component
 * Detailed compliance management view for a specific plant
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Clock,
  AlertCircle,
  CheckCircle2,
  Upload,
  Calendar,
  Plus,
  ChevronRight,
  Download,
  Eye,
  Play,
  FileCheck,
  Loader2,
  TrendingUp
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { apiClient } from '@/services/api/apiClient';
import { toast } from 'sonner';
import { format, differenceInDays } from 'date-fns';

interface PlantComplianceViewProps {
  plantId: number;
  plantName?: string;
}

interface ComplianceRequirement {
  id: number;
  name: string;
  description?: string;
  type: string;
  authority: string;
  portal_name?: string;
  frequency_days?: number;
  next_due?: string;
  last_completed?: string;
  status: 'compliant' | 'pending' | 'overdue';
}

interface ComplianceWorkflow {
  id: number;
  name: string;
  type: string;
  status: string;
  progress_percentage: number;
  current_phase?: string;
  start_date?: string;
  due_date?: string;
}

interface ComplianceDocument {
  id: number;
  name: string;
  type: string;
  status: string;
  upload_date: string;
  expiry_date?: string;
  file_size: number;
  portal_submission?: string;
}

export function PlantComplianceView({ plantId, plantName }: PlantComplianceViewProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch plant compliance data
  const { data: complianceData, isLoading } = useQuery({
    queryKey: ['plant-compliance', plantId],
    queryFn: async () => {
      const [requirements, workflows, documents, records] = await Promise.all([
        apiClient.get('/compliance/requirements', { params: { plant_id: plantId } }),
        apiClient.get('/workflows', { params: { plant_id: plantId } }),
        apiClient.get('/documents', { params: { plant_id: plantId } }),
        apiClient.get('/compliance/records', { params: { plant_id: plantId } }),
      ]);

      // Process requirements with their status
      const processedRequirements = requirements.data?.map((req: any) => {
        const relevantRecord = records.data?.find((r: any) => r.requirement_id === req.id);
        const status = relevantRecord?.status === 'overdue' ? 'overdue' : 
                      relevantRecord?.status === 'pending' ? 'pending' : 'compliant';
        
        return {
          ...req,
          status,
          next_due: relevantRecord?.due_date,
          last_completed: relevantRecord?.completed_date,
        };
      }) || [];

      // Calculate compliance metrics
      const totalRequirements = processedRequirements.length;
      const compliantItems = processedRequirements.filter((r: any) => r.status === 'compliant').length;
      const overdueItems = processedRequirements.filter((r: any) => r.status === 'overdue').length;
      const pendingItems = processedRequirements.filter((r: any) => r.status === 'pending').length;

      const complianceScore = totalRequirements > 0 
        ? Math.round((compliantItems / totalRequirements) * 100)
        : 0;

      return {
        requirements: processedRequirements,
        workflows: workflows.data || [],
        documents: documents.data || [],
        records: records.data || [],
        metrics: {
          complianceScore,
          totalRequirements,
          compliantItems,
          overdueItems,
          pendingItems,
          activeWorkflows: workflows.data?.filter((w: any) => w.status === 'In Progress').length || 0,
          totalDocuments: documents.data?.length || 0,
          expiringDocuments: documents.data?.filter((d: any) => {
            if (!d.expiry_date) return false;
            const daysUntilExpiry = differenceInDays(new Date(d.expiry_date), new Date());
            return daysUntilExpiry >= 0 && daysUntilExpiry <= 30;
          }).length || 0,
        },
      };
    },
  });

  const createWorkflowMutation = useMutation({
    mutationFn: async (templateId: number) => {
      const response = await apiClient.post(`/workflows/templates/${templateId}/create-workflow`, {
        plant_id: plantId,
      });
      return response.data;
    },
    onSuccess: (data) => {
      toast.success('Workflow created successfully');
      queryClient.invalidateQueries({ queryKey: ['plant-compliance', plantId] });
      navigate(`/workflows/${data.id}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create workflow');
    },
  });

  const handleStartWorkflow = (type: string) => {
    // Map workflow type to template ID
    const templateMap: Record<string, number> = {
      'registration': 1,  // CER Registration
      'activation': 2,    // Plant Activation
      'monthly_report': 3, // Monthly Report
    };

    const templateId = templateMap[type];
    if (templateId) {
      createWorkflowMutation.mutate(templateId);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  const { requirements, workflows, documents, metrics } = complianceData || {};

  return (
    <div className="space-y-6">
      {/* Compliance Score Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Compliance Status</CardTitle>
            <Badge 
              variant={
                (metrics?.complianceScore ?? 0) >= 80 ? 'default' : 
                (metrics?.complianceScore ?? 0) >= 60 ? 'secondary' : 'destructive'
              }
              className="text-lg px-3 py-1"
            >
              {metrics?.complianceScore || 0}%
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <Progress value={metrics?.complianceScore || 0} className="h-3" />
          
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold">{metrics?.totalRequirements || 0}</p>
              <p className="text-xs text-muted-foreground">Total Requirements</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{metrics?.compliantItems || 0}</p>
              <p className="text-xs text-muted-foreground">Compliant</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">{metrics?.pendingItems || 0}</p>
              <p className="text-xs text-muted-foreground">Pending</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">{metrics?.overdueItems || 0}</p>
              <p className="text-xs text-muted-foreground">Overdue</p>
            </div>
          </div>

          {(metrics?.overdueItems ?? 0) > 0 && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                You have {metrics?.overdueItems ?? 0} overdue compliance items that require immediate attention.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-4 gap-4">
        <Button onClick={() => handleStartWorkflow('monthly_report')}>
          <Upload className="mr-2 h-4 w-4" />
          Submit Report
        </Button>
        <Button variant="outline" onClick={() => navigate('/documents/upload')}>
          <FileText className="mr-2 h-4 w-4" />
          Upload Document
        </Button>
        <Button variant="outline" onClick={() => handleStartWorkflow('registration')}>
          <Plus className="mr-2 h-4 w-4" />
          New Registration
        </Button>
        <Button variant="outline" onClick={() => navigate('/workflow-templates')}>
          <Play className="mr-2 h-4 w-4" />
          View Templates
        </Button>
      </div>

      {/* Tabbed Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="requirements">Requirements</TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Active Workflows</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {workflows?.filter((w: any) => w.status === 'In Progress').slice(0, 3).map((workflow: any) => (
                    <div key={workflow.id} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Play className="h-4 w-4 text-blue-500" />
                        <span className="text-sm">{workflow.name}</span>
                      </div>
                      <Badge variant="outline">{workflow.progress_percentage}%</Badge>
                    </div>
                  ))}
                  {workflows?.filter((w: any) => w.status === 'In Progress').length === 0 && (
                    <p className="text-sm text-muted-foreground">No active workflows</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Upcoming Deadlines</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {requirements?.filter((r: any) => r.next_due)
                    .sort((a: any, b: any) => new Date(a.next_due).getTime() - new Date(b.next_due).getTime())
                    .slice(0, 3)
                    .map((req: any) => (
                      <div key={req.id} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-orange-500" />
                          <span className="text-sm">{req.name}</span>
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {format(new Date(req.next_due), 'MMM d')}
                        </span>
                      </div>
                    ))}
                  {requirements?.filter((r: any) => r.next_due).length === 0 && (
                    <p className="text-sm text-muted-foreground">No upcoming deadlines</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Requirements Tab */}
        <TabsContent value="requirements">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Requirements</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Requirement</TableHead>
                    <TableHead>Authority</TableHead>
                    <TableHead>Portal</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Next Due</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {requirements?.map((req: ComplianceRequirement) => (
                    <TableRow key={req.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{req.name}</p>
                          {req.description && (
                            <p className="text-xs text-muted-foreground">{req.description}</p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{req.authority}</TableCell>
                      <TableCell>{req.portal_name || '-'}</TableCell>
                      <TableCell>
                        <Badge 
                          variant={
                            req.status === 'compliant' ? 'default' : 
                            req.status === 'overdue' ? 'destructive' : 'secondary'
                          }
                        >
                          {req.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {req.next_due ? format(new Date(req.next_due), 'PPP') : '-'}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            // Start workflow for this requirement
                            navigate(`/workflows/new?requirement=${req.id}&plant=${plantId}`);
                          }}
                        >
                          Start Workflow
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {requirements?.length === 0 && (
                <div className="text-center py-8">
                  <FileCheck className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No compliance requirements defined</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Plant Workflows</CardTitle>
                <Button onClick={() => navigate('/workflows/new')}>
                  <Plus className="mr-2 h-4 w-4" />
                  New Workflow
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Workflow</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Due Date</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {workflows?.map((workflow: ComplianceWorkflow) => (
                    <TableRow key={workflow.id}>
                      <TableCell className="font-medium">{workflow.name}</TableCell>
                      <TableCell>{workflow.type}</TableCell>
                      <TableCell>
                        <Badge variant={workflow.status === 'In Progress' ? 'default' : 'secondary'}>
                          {workflow.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Progress value={workflow.progress_percentage} className="w-20 h-2" />
                          <span className="text-xs">{workflow.progress_percentage}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {workflow.due_date ? format(new Date(workflow.due_date), 'PPP') : '-'}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => navigate(`/workflows/${workflow.id}`)}
                        >
                          <Eye className="mr-2 h-4 w-4" />
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {workflows?.length === 0 && (
                <div className="text-center py-8">
                  <Play className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No workflows for this plant</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Documents Tab */}
        <TabsContent value="documents">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Compliance Documents</CardTitle>
                <Button onClick={() => navigate('/documents/upload')}>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Document</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Upload Date</TableHead>
                    <TableHead>Expiry Date</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {documents?.map((doc: ComplianceDocument) => (
                    <TableRow key={doc.id}>
                      <TableCell className="font-medium">{doc.name}</TableCell>
                      <TableCell>{doc.type}</TableCell>
                      <TableCell>
                        <Badge variant={doc.status === 'Active' ? 'default' : 'secondary'}>
                          {doc.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{format(new Date(doc.upload_date), 'PPP')}</TableCell>
                      <TableCell>
                        {doc.expiry_date ? (
                          <span className={
                            differenceInDays(new Date(doc.expiry_date), new Date()) < 30 
                              ? 'text-orange-500' : ''
                          }>
                            {format(new Date(doc.expiry_date), 'PPP')}
                          </span>
                        ) : '-'}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button size="sm" variant="outline">
                          <Download className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {documents?.length === 0 && (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No documents uploaded</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
