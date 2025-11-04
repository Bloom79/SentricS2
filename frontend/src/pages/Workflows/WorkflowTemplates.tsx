/**
 * Workflow Templates Page
 * Comprehensive template management for compliance and plant bureaucracy processes
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, FileText, Edit2, Eye, Trash2, Copy, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { apiClient } from '@/services/api/apiClient';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';

interface WorkflowTemplatePhase {
  id?: number;
  name: string;
  description?: string;
  order: number;
  required_documents: string[];
  estimated_days?: number;
  auto_advance?: boolean;
}

interface WorkflowTemplate {
  id: number;
  name: string;
  description?: string;
  category: string;
  recurrence: string;
  workflow_purpose?: string;
  workflow_type?: string;
  is_active: boolean;
  is_system_template: boolean;
  estimated_duration_days?: number;
  phases: WorkflowTemplatePhase[];
}

export default function WorkflowTemplates() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [selectedTemplate, setSelectedTemplate] = useState<WorkflowTemplate | null>(null);
  const [showViewDialog, setShowViewDialog] = useState(false);

  const { data: templates, isLoading } = useQuery<WorkflowTemplate[]>({
    queryKey: ['workflow-templates', categoryFilter],
    queryFn: async () => {
      const params: any = { active_only: false };
      if (categoryFilter !== 'all') {
        params.category = categoryFilter;
      }
      const response = await apiClient.get('/workflows/templates', { params });
      return response.data || [];
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (templateId: number) => {
      await apiClient.delete(`/workflows/templates/${templateId}`);
    },
    onSuccess: () => {
      toast.success('Template deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['workflow-templates'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete template');
    },
  });

  const createWorkflowMutation = useMutation({
    mutationFn: async ({ templateId, plantId }: { templateId: number; plantId?: number }) => {
      const response = await apiClient.post(`/workflows/templates/${templateId}/create-workflow`, {
        plant_id: plantId,
      });
      return response.data;
    },
    onSuccess: (data) => {
      toast.success('Workflow created successfully');
      navigate(`/workflows/${data.id}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create workflow');
    },
  });

  const filteredTemplates = templates?.filter(
    (template) =>
      template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (template.description || '').toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const handleViewTemplate = (template: WorkflowTemplate) => {
    setSelectedTemplate(template);
    setShowViewDialog(true);
  };

  const handleCreateWorkflow = (templateId: number) => {
    // For now, create workflow without plant selection
    // In future, could add a dialog to select plant
    createWorkflowMutation.mutate({ templateId });
  };

  const handleDeleteTemplate = (templateId: number) => {
    if (confirm('Are you sure you want to delete this template?')) {
      deleteMutation.mutate(templateId);
    }
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
          <h1 className="text-3xl font-bold">Workflow Templates</h1>
          <p className="text-muted-foreground mt-1">
            Manage reusable workflow templates for plant bureaucracy and compliance processes
          </p>
        </div>
        <Button onClick={() => navigate('/workflow-templates/new')}>
          <Plus className="mr-2 h-4 w-4" />
          New Template
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search templates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Filter by category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            <SelectItem value="Compliance">Compliance</SelectItem>
            <SelectItem value="Registration">Registration</SelectItem>
            <SelectItem value="Activation">Activation</SelectItem>
            <SelectItem value="Maintenance">Maintenance</SelectItem>
            <SelectItem value="Fiscal">Fiscal</SelectItem>
            <SelectItem value="Document Submission">Document Submission</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Templates Table */}
      <Card>
        <CardHeader>
          <CardTitle>Workflow Templates ({filteredTemplates.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredTemplates.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Recurrence</TableHead>
                  <TableHead>Phases</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTemplates.map((template) => (
                  <TableRow key={template.id}>
                    <TableCell className="font-medium">
                      <div>
                        <div className="flex items-center gap-2">
                          {template.name}
                          {template.is_system_template && (
                            <Badge variant="outline" className="text-xs">System</Badge>
                          )}
                        </div>
                        {template.description && (
                          <p className="text-sm text-muted-foreground mt-1">
                            {template.description.substring(0, 80)}
                            {template.description.length > 80 ? '...' : ''}
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{template.category}</Badge>
                    </TableCell>
                    <TableCell className="capitalize">{template.recurrence}</TableCell>
                    <TableCell>{template.phases?.length || 0} phases</TableCell>
                    <TableCell>
                      {template.estimated_duration_days
                        ? `${template.estimated_duration_days} days`
                        : '-'}
                    </TableCell>
                    <TableCell>
                      <Badge variant={template.is_active ? 'default' : 'secondary'}>
                        {template.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleViewTemplate(template)}
                          title="View Details"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleCreateWorkflow(template.id)}
                          title="Create Workflow"
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        {!template.is_system_template && (
                          <>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => navigate(`/workflow-templates/${template.id}/edit`)}
                              title="Edit"
                            >
                              <Edit2 className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDeleteTemplate(template.id)}
                              title="Delete"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">No templates found</p>
              <Button onClick={() => navigate('/workflow-templates/new')} className="mt-4">
                <Plus className="mr-2 h-4 w-4" />
                Create First Template
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* View Template Dialog */}
      <Dialog open={showViewDialog} onOpenChange={setShowViewDialog}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{selectedTemplate?.name}</DialogTitle>
            <DialogDescription>{selectedTemplate?.description}</DialogDescription>
          </DialogHeader>
          {selectedTemplate && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Category</Label>
                  <Badge variant="outline">{selectedTemplate.category}</Badge>
                </div>
                <div>
                  <Label>Recurrence</Label>
                  <p className="capitalize">{selectedTemplate.recurrence}</p>
                </div>
                <div>
                  <Label>Workflow Purpose</Label>
                  <p>{selectedTemplate.workflow_purpose || '-'}</p>
                </div>
                <div>
                  <Label>Estimated Duration</Label>
                  <p>
                    {selectedTemplate.estimated_duration_days
                      ? `${selectedTemplate.estimated_duration_days} days`
                      : '-'}
                  </p>
                </div>
              </div>

              <div>
                <Label className="mb-2 block">Phases ({selectedTemplate.phases?.length || 0})</Label>
                <div className="space-y-2">
                  {selectedTemplate.phases?.map((phase, index) => (
                    <Card key={phase.id || index} className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold">
                              Phase {phase.order}: {phase.name}
                            </span>
                          </div>
                          {phase.description && (
                            <p className="text-sm text-muted-foreground mt-1">{phase.description}</p>
                          )}
                          {phase.required_documents && phase.required_documents.length > 0 && (
                            <div className="mt-2">
                              <p className="text-xs font-medium text-muted-foreground mb-1">
                                Required Documents:
                              </p>
                              <div className="flex flex-wrap gap-1">
                                {phase.required_documents.map((doc, idx) => (
                                  <Badge key={idx} variant="outline" className="text-xs">
                                    {doc.replace(/_/g, ' ')}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                          {phase.estimated_days && (
                            <p className="text-xs text-muted-foreground mt-1">
                              Estimated: {phase.estimated_days} days
                            </p>
                          )}
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowViewDialog(false)}>
              Close
            </Button>
            {selectedTemplate && (
              <Button onClick={() => handleCreateWorkflow(selectedTemplate.id)}>
                <Copy className="mr-2 h-4 w-4" />
                Create Workflow from Template
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
