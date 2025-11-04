/**
 * Workflow Phase Detail Page
 * Dedicated page for each workflow phase with document uploads and completion forms
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeft,
  Upload,
  FileText,
  CheckCircle2,
  Clock,
  Calendar,
  AlertCircle,
  Save,
  Loader2,
  MessageSquare,
  User,
  Eye,
  Download,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
      uploaded_by?: string;
    }>;
    assigned_to?: number;
    estimated_days?: number;
    form_data?: Record<string, any>;
  };
}

export default function WorkflowPhaseDetail() {
  const { workflowId, phaseId } = useParams<{ workflowId: string; phaseId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [notes, setNotes] = useState('');
  const [uploading, setUploading] = useState(false);

  // Fetch phase detail directly
  const { data: phaseData, isLoading } = useQuery({
    queryKey: ['workflow-phase', workflowId, phaseId],
    queryFn: async () => {
      const response = await apiClient.get(`/workflows/${workflowId}/phases/${phaseId}`);
      return response.data;
    },
  });

  const phase = phaseData;
  const workflow = phaseData?.workflow;

  // Initialize form data from phase_data
  useEffect(() => {
    if (phase?.phase_data?.form_data) {
      setFormData(phase.phase_data.form_data);
    }
    if (phase?.phase_data?.notes) {
      setNotes(phase.phase_data.notes);
    }
  }, [phase]);

  // Update phase status mutation
  const updatePhaseStatusMutation = useMutation({
    mutationFn: async ({ status, notes: phaseNotes, form_data: formData }: { status: string; notes?: string; form_data?: Record<string, any> }) => {
      const response = await apiClient.put(`/workflows/${workflowId}/phases/${phaseId}/status`, {
        status,
        notes: phaseNotes || notes,
        form_data: formData,
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success('Phase status updated');
      queryClient.invalidateQueries({ queryKey: ['workflow', workflowId] });
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update phase status');
    },
  });

  // Upload document mutation
  const uploadDocumentMutation = useMutation({
    mutationFn: async ({ file, documentType, description }: { file: File; documentType: string; description?: string }) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);
      if (description) {
        formData.append('description', description);
      }
      const response = await apiClient.post(
        `/workflows/${workflowId}/phases/${phaseId}/documents`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      toast.success('Document uploaded successfully');
      queryClient.invalidateQueries({ queryKey: ['workflow-phase', workflowId, phaseId] });
      queryClient.invalidateQueries({ queryKey: ['workflow', workflowId] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to upload document');
      setUploading(false);
    },
  });

  // Add comment mutation
  const addCommentMutation = useMutation({
    mutationFn: async (text: string) => {
      const response = await apiClient.post(`/workflows/${workflowId}/phases/${phaseId}/comments`, {
        text,
        type: 'comment',
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success('Comment added');
      queryClient.invalidateQueries({ queryKey: ['workflow', workflowId] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to add comment');
    },
  });

  // Document upload handler
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleDocumentUpload(file);
    }
  };

  const handleDocumentUpload = (file: File) => {
    setUploading(true);
    const documentType = prompt('Enter document type (e.g., APPLICATION_FORM, CERTIFICATE):') || 'OTHER';
    const description = prompt('Enter document description (optional):') || undefined;
    
    uploadDocumentMutation.mutate(
      { file, documentType, description },
      {
        onSettled: () => setUploading(false),
      }
    );
  };

  const handleCompletePhase = () => {
    if (!phase) return;
    
    // Save form data and notes before completing
    updatePhaseStatusMutation.mutate({
      status: 'completed',
      notes: notes,
      form_data: formData as Record<string, any>,
    });
  };

  const handleSaveProgress = () => {
    if (!phase) return;
    
    updatePhaseStatusMutation.mutate({
      status: phase.status === 'pending' ? 'in_progress' : phase.status,
      notes: notes,
      form_data: formData as Record<string, any>,
    });
  };

  const handleAddComment = () => {
    const commentText = prompt('Enter your comment:');
    if (commentText && commentText.trim()) {
      addCommentMutation.mutate(commentText);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!workflow || !phase) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
        <p className="text-muted-foreground">Phase not found</p>
        <Button onClick={() => navigate(`/workflows/${workflowId}`)} className="mt-4">
          Back to Workflow
        </Button>
      </div>
    );
  }

  const isCompleted = phase.status?.toLowerCase() === 'completed';
  const isInProgress = phase.status?.toLowerCase() === 'in_progress' || phase.status?.toLowerCase() === 'in progress';
  const isOverdue = phase.due_date && new Date(phase.due_date) < new Date() && !isCompleted;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate(`/workflows/${workflowId}`)}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h1 className="text-2xl font-bold">{phase.name}</h1>
              <Badge
                variant="outline"
                className={
                  isCompleted
                    ? 'border-green-300 text-green-700'
                    : isInProgress
                    ? 'border-blue-300 text-blue-700'
                    : 'border-gray-300'
                }
              >
                {phase.status ? phase.status.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()) : 'Pending'}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              {workflow.name} {workflow.plant_name && `• ${workflow.plant_name}`}
            </p>
          </div>
        </div>
        {!isCompleted && (
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={handleSaveProgress} disabled={updatePhaseStatusMutation.isPending}>
              <Save className="h-4 w-4 mr-2" />
              Save Progress
            </Button>
            <Button onClick={handleCompletePhase} disabled={updatePhaseStatusMutation.isPending}>
              <CheckCircle2 className="h-4 w-4 mr-2" />
              Mark Complete
            </Button>
          </div>
        )}
      </div>

      {/* Phase Info */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Due Date</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Calendar className={`h-4 w-4 ${isOverdue ? 'text-red-600' : 'text-muted-foreground'}`} />
              <span className={isOverdue ? 'text-red-600 font-medium' : ''}>
                {phase.due_date ? new Date(phase.due_date).toLocaleDateString() : 'Not set'}
                {isOverdue && ' (Overdue)'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Estimated Duration</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span>{phase.phase_data?.estimated_days || 'N/A'} days</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Completion</CardTitle>
          </CardHeader>
          <CardContent>
            {phase.completed_date ? (
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <span>{new Date(phase.completed_date).toLocaleDateString()}</span>
              </div>
            ) : (
              <span className="text-muted-foreground">Not completed</span>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Description */}
      {phase.description && (
        <Card>
          <CardHeader>
            <CardTitle>Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{phase.description}</p>
          </CardContent>
        </Card>
      )}

      {/* Form Fields Section */}
      {!isCompleted && (
        <Card>
          <CardHeader>
            <CardTitle>Phase Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Dynamic form fields based on phase type */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="reference_number">Reference Number</Label>
                <Input
                  id="reference_number"
                  value={formData.reference_number || ''}
                  onChange={(e) => setFormData({ ...formData, reference_number: e.target.value })}
                  placeholder="Enter reference number"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="submission_date">Submission Date</Label>
                <Input
                  id="submission_date"
                  type="date"
                  value={formData.submission_date || ''}
                  onChange={(e) => setFormData({ ...formData, submission_date: e.target.value })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Enter phase notes..."
                rows={4}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Documents Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Documents ({phase.phase_data?.documents?.length || 0})</span>
            {!isCompleted && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => document.getElementById('file-upload')?.click()}
                disabled={uploading}
              >
                <Upload className="h-4 w-4 mr-2" />
                {uploading ? 'Uploading...' : 'Upload Document'}
              </Button>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Upload Area */}
          {!isCompleted && (
            <div className="border-2 border-dashed rounded-lg p-8 text-center transition-colors border-gray-300 hover:border-gray-400">
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                onChange={handleFileSelect}
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  Click to select a file or drag & drop
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  PDF, DOC, DOCX, XLS, XLSX, JPG, PNG
                </p>
              </label>
            </div>
          )}

          {/* Documents List */}
          {phase.phase_data?.documents && phase.phase_data.documents.length > 0 ? (
            <div className="mt-4 space-y-2">
              {phase.phase_data.documents.map((doc: any, idx: number) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">{doc.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {doc.type} • {new Date(doc.uploaded_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            !isCompleted && (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No documents uploaded yet</p>
              </div>
            )
          )}
        </CardContent>
      </Card>

      {/* Comments Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Comments ({phase.phase_data?.comments?.length || 0})</span>
            {!isCompleted && (
              <Button variant="outline" size="sm" onClick={handleAddComment}>
                <MessageSquare className="h-4 w-4 mr-2" />
                Add Comment
              </Button>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {phase.phase_data?.comments && phase.phase_data.comments.length > 0 ? (
            <div className="space-y-4">
              {phase.phase_data.comments.map((comment: any) => (
                <div key={comment.id} className="flex gap-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                      <User className="h-4 w-4 text-primary" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium">
                        {comment.author_name || comment.author}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(comment.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">{comment.text}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <MessageSquare className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No comments yet</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

