/**
 * Workflows Tab for Plant Detail
 * Shows all workflows associated with the plant with status and documentation
 */

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Activity,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileText,
  Eye,
  Calendar,
  TrendingUp,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import apiClient from '@/services/api/apiClient';
import { Loader2 } from 'lucide-react';

interface Workflow {
  id: number;
  name: string;
  type: string;
  status: string;
  progress_percentage: number;
  due_date?: string;
  start_date?: string;
  current_phase?: string;
  plant_name?: string;
  phases?: Array<{
    id: number;
    name: string;
    status: string;
    order: number;
    phase_data?: {
      documents?: Array<{ document_id: number; name: string }>;
    };
  }>;
}

interface WorkflowsTabProps {
  plantId: number;
}

export function WorkflowsTab({ plantId }: WorkflowsTabProps) {
  const navigate = useNavigate();

  const { data: workflows, isLoading } = useQuery<Workflow[]>({
    queryKey: ['plant-workflows', plantId],
    queryFn: async () => {
      const response = await apiClient.get('/workflows', {
        params: { plant_id: plantId },
      });
      return response.data || [];
    },
  });

  const getStatusColor = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower === 'completed') return 'bg-green-100 text-green-800 border-green-300';
    if (statusLower === 'in_progress' || statusLower === 'in progress') return 'bg-blue-100 text-blue-800 border-blue-300';
    if (statusLower === 'on_hold' || statusLower === 'on hold') return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    if (statusLower === 'draft') return 'bg-gray-100 text-gray-800 border-gray-300';
    return 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getStatusIcon = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower === 'completed') return <CheckCircle2 className="h-4 w-4 text-green-600" />;
    if (statusLower === 'in_progress' || statusLower === 'in progress') return <Activity className="h-4 w-4 text-blue-600 animate-pulse" />;
    if (statusLower === 'on_hold' || statusLower === 'on hold') return <Clock className="h-4 w-4 text-yellow-600" />;
    return <AlertCircle className="h-4 w-4 text-gray-400" />;
  };

  const getDocumentCount = (workflow: Workflow) => {
    if (!workflow.phases) return 0;
    return workflow.phases.reduce((total, phase) => {
      return total + (phase.phase_data?.documents?.length || 0);
    }, 0);
  };

  const getCompletedPhases = (workflow: Workflow) => {
    if (!workflow.phases) return 0;
    return workflow.phases.filter((p) => p.status?.toLowerCase() === 'completed').length;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!workflows || workflows.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <Activity className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
          <p className="text-muted-foreground mb-4">No workflows found for this plant</p>
          <Button onClick={() => navigate('/workflows')}>View All Workflows</Button>
        </CardContent>
      </Card>
    );
  }

  // Calculate summary statistics
  const activeWorkflows = workflows.filter((w) => w.status?.toLowerCase() !== 'completed');
  const completedWorkflows = workflows.filter((w) => w.status?.toLowerCase() === 'completed');
  const totalDocuments = workflows.reduce((sum, w) => sum + getDocumentCount(w), 0);
  const overdueWorkflows = workflows.filter(
    (w) => w.due_date && new Date(w.due_date) < new Date() && w.status?.toLowerCase() !== 'completed'
  );

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Workflows</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{workflows.length}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {activeWorkflows.length} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{completedWorkflows.length}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {workflows.length > 0 ? Math.round((completedWorkflows.length / workflows.length) * 100) : 0}% completion rate
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Documents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalDocuments}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Total uploaded
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Overdue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${overdueWorkflows.length > 0 ? 'text-red-600' : ''}`}>
              {overdueWorkflows.length}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Requiring attention
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Workflows Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Workflows ({workflows.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Workflow</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Progress</TableHead>
                <TableHead>Phases</TableHead>
                <TableHead>Documents</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {workflows.map((workflow) => {
                const isOverdue = workflow.due_date && new Date(workflow.due_date) < new Date() && workflow.status?.toLowerCase() !== 'completed';
                const documentCount = getDocumentCount(workflow);
                const completedPhases = getCompletedPhases(workflow);
                const totalPhases = workflow.phases?.length || 0;

                return (
                  <TableRow key={workflow.id} className="hover:bg-muted/50">
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(workflow.status)}
                        <span>{workflow.name}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{workflow.type}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(workflow.status)}>
                        {workflow.status.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Progress value={workflow.progress_percentage || 0} className="w-20 h-2" />
                        <span className="text-xs w-12">{workflow.progress_percentage || 0}%</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">
                        {completedPhases}/{totalPhases} completed
                      </span>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">{documentCount}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      {workflow.due_date ? (
                        <div className={`flex items-center gap-1 text-sm ${isOverdue ? 'text-red-600 font-medium' : ''}`}>
                          <Calendar className="h-3.5 w-3.5" />
                          {new Date(workflow.due_date).toLocaleDateString()}
                          {isOverdue && ' (Overdue)'}
                        </div>
                      ) : (
                        <span className="text-muted-foreground text-sm">Not set</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate(`/workflows/${workflow.id}`)}
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate('/workflows')}>
              View All Workflows
            </Button>
            <Button variant="outline" onClick={() => navigate('/workflow-templates')}>
              Create New Workflow
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

