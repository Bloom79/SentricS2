/**
 * Workflow Detail Page
 * Detailed workflow view and management
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeft,
  Clock,
  AlertCircle,
  FileText,
  Factory,
  Calendar,
  Target,
  CheckCircle2,
  Circle,
  PlayCircle,
  PauseCircle,
  XCircle,
  Upload,
  MessageSquare,
  Loader2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import apiClient from '@/services/api/apiClient';

interface WorkflowPhase {
  id: number;
  name: string;
  description?: string;
  order: number;
  status: string;
  due_date?: string;
  completed_date?: string;
  phase_data?: {
    notes?: string;
    comments?: Array<{
      id: number;
      text: string;
      author: string;
      author_name?: string;
      timestamp: string;
      type: string;
    }>;
    documents?: Array<{
      document_id: number;
      name: string;
      type: string;
      uploaded_at: string;
    }>;
    assigned_to?: number;
    estimated_days?: number;
  };
}

interface Workflow {
  id: number;
  name: string;
  description?: string;
  type: string;
  status: string;
  plant_id?: number;
  plant_name?: string;
  start_date?: string;
  due_date?: string;
  completed_date?: string;
  progress_percentage: number;
  current_phase?: string;
  notes?: string;
  workflow_data?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
  phases: WorkflowPhase[];
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'Completed':
      return <CheckCircle2 className="h-5 w-5 text-green-600" />;
    case 'In Progress':
      return <PlayCircle className="h-5 w-5 text-blue-600" />;
    case 'On Hold':
      return <PauseCircle className="h-5 w-5 text-yellow-600" />;
    case 'Cancelled':
      return <XCircle className="h-5 w-5 text-gray-600" />;
    case 'Draft':
      return <Circle className="h-5 w-5 text-slate-600" />;
    default:
      return <AlertCircle className="h-5 w-5 text-gray-600" />;
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

const getPhaseStatusIcon = (status: string) => {
  switch (status?.toLowerCase()) {
    case 'completed':
      return <CheckCircle2 className="h-5 w-5 text-green-600" />;
    case 'in_progress':
    case 'in progress':
      return <PlayCircle className="h-5 w-5 text-blue-600" />;
    case 'pending':
      return <Clock className="h-5 w-5 text-gray-400" />;
    default:
      return <Circle className="h-5 w-5 text-gray-400" />;
  }
};

export default function WorkflowDetail() {
  const params = useParams<{ id?: string; workflowId?: string }>();
  const id = params.id || params.workflowId;
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPhase, setSelectedPhase] = useState<WorkflowPhase | null>(null);
  const [showPhaseDialog, setShowPhaseDialog] = useState(false);
  const [showCommentDialog, setShowCommentDialog] = useState(false);
  const [commentText, setCommentText] = useState('');
  const loadingRef = React.useRef(false);

  const loadWorkflow = React.useCallback(
    async (workflowId: number) => {
      if (!workflowId || isNaN(workflowId)) {
        console.error('Invalid workflow ID:', workflowId);
        setLoading(false);
        loadingRef.current = false;
        return;
      }

      // Prevent multiple simultaneous loads using ref
      if (loadingRef.current) {
        console.log('Already loading, skipping...');
        return;
      }

      try {
        loadingRef.current = true;
        setLoading(true);
        console.log('Loading workflow:', workflowId);
        console.log('Current user data:', localStorage.getItem('user_data'));

        const response = await apiClient.get(`/workflows/${workflowId}`);
        console.log('Workflow response received:', response);
        console.log('Response status:', response.status);
        console.log('Response data:', response.data);

        if (response && response.data) {
          console.log('Setting workflow data:', response.data);
          setWorkflow(response.data);
        } else {
          console.error('No data in response:', response);
          toast.error('Workflow data is empty');
          setWorkflow(null);
        }
      } catch (error: any) {
        console.error('Error loading workflow:', error);
        console.error('Error details:', {
          message: error.message,
          response: error.response,
          status: error.response?.status,
          data: error.response?.data,
        });

        const errorMessage =
          error.response?.data?.detail || error.message || 'Failed to load workflow';
        toast.error(errorMessage);
        setWorkflow(null);

        // If 404 or 403, navigate back to workflows list
        if (error.response?.status === 404 || error.response?.status === 403) {
          setTimeout(() => navigate('/workflows'), 2000);
        }
      } finally {
        console.log('Setting loading to false');
        loadingRef.current = false;
        setLoading(false);
      }
    },
    [navigate]
  );

  useEffect(() => {
    if (id) {
      const workflowId = Number(id);
      if (!isNaN(workflowId) && workflowId > 0) {
        loadWorkflow(workflowId);
      } else {
        console.error('Invalid workflow ID from params:', id);
        setLoading(false);
        toast.error('Invalid workflow ID');
        navigate('/workflows');
      }
    } else {
      setLoading(false);
    }
  }, [id, loadWorkflow, navigate]);

  const updatePhaseStatusMutation = useMutation({
    mutationFn: async ({
      phaseId,
      status,
      notes,
    }: {
      phaseId: number;
      status: string;
      notes?: string;
    }) => {
      const workflowId = id || params.workflowId;
      const response = await apiClient.put(`/workflows/${workflowId}/phases/${phaseId}/status`, {
        status,
        notes,
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success('Phase status updated');
      if (id) loadWorkflow(Number(id));
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update phase status');
    },
  });

  const addCommentMutation = useMutation({
    mutationFn: async ({ phaseId, text }: { phaseId: number; text: string }) => {
      const workflowId = id || params.workflowId;
      const response = await apiClient.post(`/workflows/${workflowId}/phases/${phaseId}/comments`, {
        text,
        type: 'comment',
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success('Comment added');
      setShowCommentDialog(false);
      setCommentText('');
      if (id) loadWorkflow(Number(id));
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to add comment');
    },
  });

  const handlePhaseStatusChange = (phase: WorkflowPhase, newStatus: string) => {
    if (newStatus === 'completed' && !phase.completed_date) {
      updatePhaseStatusMutation.mutate({
        phaseId: phase.id,
        status: 'completed',
      });
    } else if (newStatus === 'in_progress') {
      updatePhaseStatusMutation.mutate({
        phaseId: phase.id,
        status: 'in_progress',
      });
    } else {
      updatePhaseStatusMutation.mutate({
        phaseId: phase.id,
        status: 'pending',
      });
    }
  };

  const handleAddComment = (phase: WorkflowPhase) => {
    setSelectedPhase(phase);
    setShowCommentDialog(true);
  };

  const submitComment = () => {
    if (!selectedPhase || !commentText.trim()) return;
    addCommentMutation.mutate({
      phaseId: selectedPhase.id,
      text: commentText,
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (!workflow) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Workflow not found</p>
        <Button onClick={() => navigate('/workflows')} className="mt-4">
          Back to Workflows
        </Button>
      </div>
    );
  }

  const isOverdue =
    workflow.due_date &&
    new Date(workflow.due_date) < new Date() &&
    workflow.status !== 'Completed';
  const daysRemaining = workflow.due_date
    ? Math.ceil(
        (new Date(workflow.due_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
      )
    : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4 flex-1">
          <Button variant="ghost" onClick={() => navigate('/workflows')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold">{workflow.name}</h1>
              <Badge className={getStatusColor(workflow.status)}>
                <span className="flex items-center gap-1.5">
                  {getStatusIcon(workflow.status)}
                  {workflow.status}
                </span>
              </Badge>
              <Badge variant="outline" className={getTypeColor(workflow.type)}>
                {workflow.type}
              </Badge>
            </div>
            {workflow.description && (
              <p className="text-muted-foreground mt-1">{workflow.description}</p>
            )}
          </div>
        </div>
      </div>

      {/* Plant Association - Prominent */}
      {workflow.plant_name && (
        <Card className="border-blue-200 bg-blue-50 dark:bg-blue-950/20">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Factory className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              <div>
                <p className="text-sm text-muted-foreground">Associated Plant</p>
                <p className="text-lg font-semibold">{workflow.plant_name}</p>
              </div>
              {workflow.plant_id && (
                <Button
                  variant="outline"
                  size="sm"
                  className="ml-auto"
                  onClick={() => navigate(`/plants/${workflow.plant_id}`)}
                >
                  View Plant
                  <ArrowLeft className="ml-2 h-4 w-4 rotate-180" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Target className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Progress</p>
                <p className="text-2xl font-bold">{workflow.progress_percentage}%</p>
              </div>
            </div>
            <Progress value={workflow.progress_percentage} className="mt-3" />
          </CardContent>
        </Card>

        {workflow.due_date && (
          <Card className={isOverdue ? 'border-red-200 bg-red-50 dark:bg-red-950/20' : ''}>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Calendar
                  className={`h-5 w-5 ${isOverdue ? 'text-red-600' : 'text-muted-foreground'}`}
                />
                <div>
                  <p className="text-sm text-muted-foreground">Due Date</p>
                  <p className={`text-2xl font-bold ${isOverdue ? 'text-red-600' : ''}`}>
                    {new Date(workflow.due_date).toLocaleDateString()}
                  </p>
                  {daysRemaining !== null && (
                    <p
                      className={`text-xs mt-1 ${isOverdue ? 'text-red-600 font-medium' : 'text-muted-foreground'}`}
                    >
                      {isOverdue
                        ? `Overdue by ${Math.abs(daysRemaining)} days`
                        : `${daysRemaining} days remaining`}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {workflow.start_date && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Clock className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Started</p>
                  <p className="text-2xl font-bold">
                    {new Date(workflow.start_date).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {workflow.current_phase && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Circle className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Current Phase</p>
                  <p className="text-lg font-semibold truncate">{workflow.current_phase}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Phases / Steps */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Workflow Steps ({workflow.phases?.length || 0})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {workflow.phases && workflow.phases.length > 0 ? (
              <>
                {/* Progress Overview */}
                <div className="bg-muted/50 rounded-lg p-4 mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Overall Progress</span>
                    <span className="text-sm font-semibold">
                      {
                        workflow.phases.filter((p) => p.status?.toLowerCase() === 'completed')
                          .length
                      }{' '}
                      / {workflow.phases.length} completed
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full transition-all"
                      style={{
                        width: `${(workflow.phases.filter((p) => p.status?.toLowerCase() === 'completed').length / workflow.phases.length) * 100}%`,
                      }}
                    />
                  </div>
                </div>

                {/* Phases List */}
                <div className="space-y-3">
                  {workflow.phases.map((phase, index) => {
                    const isCompleted = phase.status?.toLowerCase() === 'completed';
                    const isInProgress =
                      phase.status?.toLowerCase() === 'in_progress' ||
                      phase.status?.toLowerCase() === 'in progress';
                    const isPending = phase.status?.toLowerCase() === 'pending' || !phase.status;
                    const isOverdue =
                      phase.due_date && new Date(phase.due_date) < new Date() && !isCompleted;

                    return (
                      <div
                        key={phase.id}
                        className={`relative flex items-start gap-4 p-5 border-2 rounded-lg transition-all cursor-pointer hover:shadow-md ${
                          isCompleted
                            ? 'bg-green-50 dark:bg-green-950/20 border-green-300'
                            : isInProgress
                              ? 'bg-blue-50 dark:bg-blue-950/20 border-blue-300'
                              : isOverdue
                                ? 'bg-red-50 dark:bg-red-950/20 border-red-300'
                                : 'bg-gray-50 dark:bg-gray-900/50 border-gray-200'
                        }`}
                        onClick={() => navigate(`/workflows/${workflow.id}/phases/${phase.id}`)}
                      >
                        {/* Step Number Badge */}
                        <div
                          className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${
                            isCompleted
                              ? 'bg-green-500 text-white'
                              : isInProgress
                                ? 'bg-blue-500 text-white'
                                : 'bg-gray-300 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                          }`}
                        >
                          {phase.order}
                        </div>

                        {/* Connecting Line */}
                        {index < workflow.phases.length - 1 && (
                          <div
                            className={`absolute left-[33px] top-[50px] w-0.5 h-6 ${
                              isCompleted ? 'bg-green-300' : 'bg-gray-300'
                            }`}
                          />
                        )}

                        {/* Phase Content */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between mb-2 gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-semibold text-lg">{phase.name}</h3>
                                {getPhaseStatusIcon(phase.status)}
                              </div>
                              {phase.description && (
                                <p className="text-sm text-muted-foreground">{phase.description}</p>
                              )}
                            </div>
                            <div className="flex items-center gap-2 flex-shrink-0">
                              <Badge
                                variant="outline"
                                className={`text-xs ${
                                  isCompleted
                                    ? 'border-green-300 text-green-700'
                                    : isInProgress
                                      ? 'border-blue-300 text-blue-700'
                                      : 'border-gray-300'
                                }`}
                              >
                                {phase.status
                                  ? phase.status
                                      .replace('_', ' ')
                                      .replace(/\b\w/g, (l) => l.toUpperCase())
                                  : 'Pending'}
                              </Badge>
                            </div>
                          </div>

                          {/* Phase Details */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                            {phase.due_date && (
                              <div className="flex items-center gap-2 text-xs">
                                <Calendar
                                  className={`h-4 w-4 ${
                                    isOverdue ? 'text-red-600' : 'text-muted-foreground'
                                  }`}
                                />
                                <span
                                  className={
                                    isOverdue ? 'text-red-600 font-medium' : 'text-muted-foreground'
                                  }
                                >
                                  Due: {new Date(phase.due_date).toLocaleDateString()}
                                  {isOverdue && ' (Overdue)'}
                                </span>
                              </div>
                            )}
                            {phase.completed_date && (
                              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                <CheckCircle2 className="h-4 w-4 text-green-600" />
                                <span>
                                  Completed: {new Date(phase.completed_date).toLocaleDateString()}
                                </span>
                              </div>
                            )}
                            {phase.phase_data?.estimated_days && (
                              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                <Clock className="h-4 w-4" />
                                <span>Estimated: {phase.phase_data.estimated_days} days</span>
                              </div>
                            )}
                          </div>

                          {/* Phase Actions */}
                          {!isCompleted && (
                            <div className="flex items-center gap-2 mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                              {phase.status?.toLowerCase() === 'pending' && (
                                <Button
                                  size="sm"
                                  variant="default"
                                  onClick={() => handlePhaseStatusChange(phase, 'in_progress')}
                                  disabled={updatePhaseStatusMutation.isPending}
                                >
                                  <PlayCircle className="h-4 w-4 mr-1" />
                                  Start Phase
                                </Button>
                              )}
                              {isInProgress && (
                                <Button
                                  size="sm"
                                  variant="default"
                                  onClick={() => handlePhaseStatusChange(phase, 'completed')}
                                  disabled={updatePhaseStatusMutation.isPending}
                                >
                                  <CheckCircle2 className="h-4 w-4 mr-1" />
                                  Mark Complete
                                </Button>
                              )}
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setSelectedPhase(phase);
                                  setShowPhaseDialog(true);
                                }}
                              >
                                <Upload className="h-4 w-4 mr-1" />
                                Upload Document
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleAddComment(phase)}
                              >
                                <MessageSquare className="h-4 w-4 mr-1" />
                                Add Comment
                              </Button>
                            </div>
                          )}

                          {/* Phase Comments */}
                          {phase.phase_data?.comments && phase.phase_data.comments.length > 0 && (
                            <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                              <p className="text-xs font-medium text-muted-foreground mb-2">
                                Comments ({phase.phase_data.comments.length})
                              </p>
                              <div className="space-y-2">
                                {phase.phase_data.comments.map((comment: any) => (
                                  <div key={comment.id} className="text-xs bg-muted/50 rounded p-2">
                                    <div className="flex items-center gap-2 mb-1">
                                      <span className="font-medium">
                                        {comment.author_name || comment.author}
                                      </span>
                                      <span className="text-muted-foreground">
                                        {new Date(comment.timestamp).toLocaleString()}
                                      </span>
                                    </div>
                                    <p className="text-muted-foreground">{comment.text}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Phase Documents */}
                          {phase.phase_data?.documents && phase.phase_data.documents.length > 0 && (
                            <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                              <p className="text-xs font-medium text-muted-foreground mb-2">
                                Documents ({phase.phase_data.documents.length})
                              </p>
                              <div className="space-y-1">
                                {phase.phase_data.documents.map((doc: any, idx: number) => (
                                  <div key={idx} className="flex items-center gap-2 text-xs">
                                    <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                                    <span className="text-muted-foreground">{doc.name}</span>
                                    <Badge variant="outline" className="text-xs ml-auto">
                                      {doc.type}
                                    </Badge>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No phases defined for this workflow</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Notes */}
      {workflow.notes && (
        <Card>
          <CardHeader>
            <CardTitle>Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm whitespace-pre-wrap">{workflow.notes}</p>
          </CardContent>
        </Card>
      )}

      {/* Metadata */}
      <Card>
        <CardHeader>
          <CardTitle>Metadata</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {workflow.created_at && (
              <div>
                <p className="text-muted-foreground">Created</p>
                <p className="font-medium">{new Date(workflow.created_at).toLocaleString()}</p>
              </div>
            )}
            {workflow.updated_at && (
              <div>
                <p className="text-muted-foreground">Last Updated</p>
                <p className="font-medium">{new Date(workflow.updated_at).toLocaleString()}</p>
              </div>
            )}
            {workflow.completed_date && (
              <div>
                <p className="text-muted-foreground">Completed</p>
                <p className="font-medium">{new Date(workflow.completed_date).toLocaleString()}</p>
              </div>
            )}
            {workflow.id && (
              <div>
                <p className="text-muted-foreground">Workflow ID</p>
                <p className="font-medium">#{workflow.id}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Phase Comment Dialog */}
      <Dialog open={showCommentDialog} onOpenChange={setShowCommentDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Comment to Phase</DialogTitle>
            <DialogDescription>Add a note or comment for {selectedPhase?.name}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="comment">Comment</Label>
              <Textarea
                id="comment"
                placeholder="Enter your comment..."
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCommentDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={submitComment}
              disabled={!commentText.trim() || addCommentMutation.isPending}
            >
              {addCommentMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Adding...
                </>
              ) : (
                'Add Comment'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Phase Document Upload Dialog */}
      <Dialog open={showPhaseDialog} onOpenChange={setShowPhaseDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload Document</DialogTitle>
            <DialogDescription>Upload a document for {selectedPhase?.name}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="file">Document File</Label>
              <input
                id="file"
                type="file"
                className="w-full"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="doc-type">Document Type</Label>
              <select id="doc-type" className="w-full rounded-md border p-2">
                <option value="">Select type...</option>
                <option value="APPLICATION_FORM">Application Form</option>
                <option value="TECHNICAL_SPECS">Technical Specifications</option>
                <option value="CERTIFICATE">Certificate</option>
                <option value="DECLARATION">Declaration</option>
                <option value="REPORT">Report</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPhaseDialog(false)}>
              Cancel
            </Button>
            <Button onClick={() => toast.info('Document upload coming soon')}>Upload</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
