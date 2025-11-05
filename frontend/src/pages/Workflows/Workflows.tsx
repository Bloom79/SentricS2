/**
 * Workflows Page
 * Manage active workflows for plant bureaucracy and compliance processes
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Plus,
  Search,
  Factory,
  FileText,
  Loader2,
  ArrowRight,
  Calendar,
  Clock,
  AlertTriangle,
  Circle,
  Target,
  Tag,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { apiClient } from '@/services/api/apiClient';
import { toast } from 'sonner';

interface Workflow {
  id: number;
  name: string;
  description?: string;
  type: string;
  status: string;
  plant_id?: number;
  plant_name?: string;
  template_id?: number;
  progress_percentage: number;
  start_date?: string;
  due_date?: string;
  completed_date?: string;
  current_phase?: string;
  created_at?: string;
}

// Helper function to calculate urgency priority
const getUrgencyPriority = (
  dueDate?: string,
  status: string = ''
): { priority: 'high' | 'medium' | 'low' | 'none'; daysRemaining?: number } => {
  if (status === 'Completed' || status === 'Cancelled') {
    return { priority: 'none' };
  }

  if (!dueDate) {
    return { priority: 'low' };
  }

  const due = new Date(dueDate);
  const now = new Date();
  const diffTime = due.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return { priority: 'high', daysRemaining: diffDays }; // Overdue
  } else if (diffDays <= 7) {
    return { priority: 'high', daysRemaining: diffDays };
  } else if (diffDays <= 30) {
    return { priority: 'medium', daysRemaining: diffDays };
  } else {
    return { priority: 'low', daysRemaining: diffDays };
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'Completed':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'In Progress':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'On Hold':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'Cancelled':
      return 'bg-gray-100 text-gray-800 border-gray-200';
    case 'Draft':
      return 'bg-slate-100 text-slate-800 border-slate-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

const getTypeColor = (type: string) => {
  switch (type) {
    case 'Activation':
      return 'bg-purple-100 text-purple-700';
    case 'Compliance':
      return 'bg-orange-100 text-orange-700';
    case 'Fiscal':
      return 'bg-blue-100 text-blue-700';
    case 'Maintenance':
      return 'bg-teal-100 text-teal-700';
    case 'Document Submission':
      return 'bg-pink-100 text-pink-700';
    default:
      return 'bg-gray-100 text-gray-700';
  }
};

export default function Workflows() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>('');
  const [selectedPlantId, setSelectedPlantId] = useState<string>('');

  const { data: workflows, isLoading } = useQuery<Workflow[]>({
    queryKey: ['workflows', statusFilter],
    queryFn: async () => {
      const params: any = {};
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      const response = await apiClient.get('/workflows', { params });
      return response.data || [];
    },
  });

  const { data: templates } = useQuery({
    queryKey: ['workflow-templates'],
    queryFn: async () => {
      const response = await apiClient.get('/workflows/templates', {
        params: { active_only: true },
      });
      return response.data || [];
    },
  });

  const { data: plants } = useQuery({
    queryKey: ['plants'],
    queryFn: async () => {
      const response = await apiClient.get('/plants');
      return response.data || [];
    },
  });

  const createWorkflowMutation = useMutation({
    mutationFn: async (data: { template_id: number; plant_id?: number }) => {
      const response = await apiClient.post(
        `/workflows/templates/${data.template_id}/create-workflow`,
        {
          plant_id: data.plant_id
            ? typeof data.plant_id === 'string'
              ? parseInt(data.plant_id)
              : data.plant_id
            : undefined,
        }
      );
      return response.data;
    },
    onSuccess: (data) => {
      toast.success('Workflow created successfully');
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
      setShowCreateDialog(false);
      setSelectedTemplateId('');
      setSelectedPlantId('');
      navigate(`/workflows/${data.id}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create workflow');
    },
  });

  const filteredWorkflows =
    workflows?.filter(
      (workflow) =>
        workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (workflow.description || '').toLowerCase().includes(searchTerm.toLowerCase())
    ) || [];

  const handleCreateWorkflow = () => {
    if (!selectedTemplateId) {
      toast.error('Please select a template');
      return;
    }
    createWorkflowMutation.mutate({
      template_id: parseInt(selectedTemplateId),
      plant_id: selectedPlantId ? parseInt(selectedPlantId) : undefined,
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Workflows</h1>
          <p className="text-muted-foreground mt-1">
            Manage active workflows for plant bureaucracy and compliance processes
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Workflow
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search workflows..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="Draft">Draft</SelectItem>
            <SelectItem value="In Progress">In Progress</SelectItem>
            <SelectItem value="Completed">Completed</SelectItem>
            <SelectItem value="On Hold">On Hold</SelectItem>
            <SelectItem value="Cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Workflows Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredWorkflows.length > 0 ? (
          filteredWorkflows.map((workflow) => {
            const urgency = getUrgencyPriority(workflow.due_date, workflow.status);
            const isOverdue = urgency.daysRemaining !== undefined && urgency.daysRemaining < 0;

            return (
              <Card
                key={workflow.id}
                className={`cursor-pointer hover:shadow-xl hover:-translate-y-0.5 transition-all border-l-4 ${
                  urgency.priority === 'high' && !isOverdue
                    ? 'border-l-orange-500'
                    : isOverdue
                      ? 'border-l-red-500'
                      : urgency.priority === 'medium'
                        ? 'border-l-yellow-500'
                        : 'border-l-gray-300'
                }`}
                onClick={() => navigate(`/workflows/${workflow.id}`)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <CardTitle className="text-lg leading-tight flex-1">{workflow.name}</CardTitle>
                    <Badge className={`text-xs ${getStatusColor(workflow.status)}`}>
                      {workflow.status}
                    </Badge>
                  </div>

                  {/* Plant Association - Prominent */}
                  {workflow.plant_name ? (
                    <div className="flex items-center gap-2 text-sm font-medium text-foreground bg-blue-50 dark:bg-blue-950/20 px-2 py-1.5 rounded-md -mx-1">
                      <Factory className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                      <span className="truncate">{workflow.plant_name}</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground px-2 py-1.5">
                      <Factory className="h-4 w-4" />
                      <span>No plant assigned</span>
                    </div>
                  )}
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Type Badge */}
                  <div className="flex items-center gap-2">
                    <Tag className="h-3.5 w-3.5 text-muted-foreground" />
                    <Badge variant="outline" className={`text-xs ${getTypeColor(workflow.type)}`}>
                      {workflow.type}
                    </Badge>
                  </div>

                  {/* Urgency Indicator */}
                  {urgency.priority !== 'none' && workflow.due_date && (
                    <div
                      className={`flex items-center gap-2 text-sm px-2 py-1.5 rounded-md ${
                        isOverdue
                          ? 'bg-red-50 dark:bg-red-950/20 text-red-700 dark:text-red-400'
                          : urgency.priority === 'high'
                            ? 'bg-orange-50 dark:bg-orange-950/20 text-orange-700 dark:text-orange-400'
                            : 'bg-yellow-50 dark:bg-yellow-950/20 text-yellow-700 dark:text-yellow-400'
                      }`}
                    >
                      {isOverdue ? (
                        <>
                          <AlertTriangle className="h-4 w-4" />
                          <span className="font-medium">
                            Overdue by {Math.abs(urgency.daysRemaining!)}{' '}
                            {Math.abs(urgency.daysRemaining!) === 1 ? 'day' : 'days'}
                          </span>
                        </>
                      ) : (
                        <>
                          <Clock className="h-4 w-4" />
                          <span>
                            {urgency.daysRemaining} {urgency.daysRemaining === 1 ? 'day' : 'days'}{' '}
                            remaining
                          </span>
                        </>
                      )}
                    </div>
                  )}

                  {/* Dates */}
                  <div className="space-y-1.5 text-sm">
                    {workflow.due_date && (
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Calendar className="h-3.5 w-3.5" />
                        <span>Due: {new Date(workflow.due_date).toLocaleDateString()}</span>
                      </div>
                    )}
                    {workflow.start_date && (
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Target className="h-3.5 w-3.5" />
                        <span>Started: {new Date(workflow.start_date).toLocaleDateString()}</span>
                      </div>
                    )}
                    {workflow.current_phase && (
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Circle className="h-3.5 w-3.5" />
                        <span className="truncate">Phase: {workflow.current_phase}</span>
                      </div>
                    )}
                  </div>

                  {/* Progress Bar */}
                  {workflow.progress_percentage !== undefined && (
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Progress</span>
                        <span className="font-medium">{workflow.progress_percentage}%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-2 rounded-full transition-all ${
                            workflow.progress_percentage === 100
                              ? 'bg-green-500'
                              : workflow.progress_percentage >= 50
                                ? 'bg-blue-500'
                                : 'bg-orange-500'
                          }`}
                          style={{ width: `${workflow.progress_percentage}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Description Preview */}
                  {workflow.description && (
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {workflow.description}
                    </p>
                  )}

                  {/* Action Button */}
                  <Button
                    variant="outline"
                    className="w-full mt-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/workflows/${workflow.id}`);
                    }}
                  >
                    View Details
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            );
          })
        ) : (
          <Card className="col-span-full">
            <CardContent className="py-12 text-center">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">No workflows found</p>
              <Button onClick={() => setShowCreateDialog(true)} className="mt-4">
                <Plus className="mr-2 h-4 w-4" />
                Create First Workflow
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Create Workflow Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Workflow</DialogTitle>
            <DialogDescription>
              Create a workflow from a template for plant bureaucracy processes
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="template">Template *</Label>
              <Select value={selectedTemplateId} onValueChange={setSelectedTemplateId}>
                <SelectTrigger id="template">
                  <SelectValue placeholder="Select a template" />
                </SelectTrigger>
                <SelectContent>
                  {templates?.map((template: any) => (
                    <SelectItem key={template.id} value={template.id.toString()}>
                      {template.name} ({template.category})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="plant">Plant (Optional)</Label>
              <Select
                value={selectedPlantId || 'none'}
                onValueChange={(value) => setSelectedPlantId(value === 'none' ? '' : value)}
              >
                <SelectTrigger id="plant">
                  <SelectValue placeholder="Select a plant (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">No plant</SelectItem>
                  {plants?.map((plant: any) => (
                    <SelectItem key={plant.id} value={plant.id.toString()}>
                      {plant.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleCreateWorkflow}
              disabled={!selectedTemplateId || createWorkflowMutation.isPending}
            >
              {createWorkflowMutation.isPending ? 'Creating...' : 'Create Workflow'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
