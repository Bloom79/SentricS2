/**
 * Document Manager Component
 * Manages documents for compliance records
 * Adapted from sentrics-repo
 */

import React, { useRef, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Upload, FileText, Trash2, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { apiClient } from '@/services/api/apiClient';
import { toast } from 'sonner';

export type DocumentManagerProps = {
  complianceRecordId: number;
  cerId?: number;
  plantId?: number;
  readOnly?: boolean;
};

type Document = {
  id: number;
  name: string;
  type: string;
  status: string;
  file_name: string;
  file_size?: number;
  mime_type?: string;
  created_at: string;
  compliance_record_id?: number;
};

const DOCUMENT_TYPES = [
  'REGISTRATION_FORM',
  'TECHNICAL_SPECS',
  'MEMBER_LIST',
  'ENERGY_DATA',
  'MEMBER_ACTIVITY',
  'FINANCIAL_REPORT',
  'COMPLIANCE_REPORT',
  'MEMBER_SUMMARY',
  'IMPACT_ANALYSIS',
  'MEMBER_AGREEMENTS',
  'OTHER',
];

export function DocumentManager({
  complianceRecordId,
  cerId,
  plantId,
  readOnly = false,
}: DocumentManagerProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedType, setSelectedType] = useState<string>('');
  const queryClient = useQueryClient();

  const { data: documents, isLoading, refetch } = useQuery({
    queryKey: ['compliance-documents', complianceRecordId],
    queryFn: async () => {
      const response = await apiClient.get('/documents', {
        params: {
          compliance_record_id: complianceRecordId,
        },
      });
      return response.data as Document[];
    },
  });

  const uploadMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      await apiClient.post('/documents', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        params: {
          compliance_record_id: complianceRecordId,
          cer_id: cerId,
          plant_id: plantId,
          type: selectedType,
        },
      });
    },
    onSuccess: () => {
      toast.success('Document uploaded successfully');
      refetch();
      queryClient.invalidateQueries({ queryKey: ['compliance-documents'] });
      setSelectedType('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to upload document');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (documentId: number) => {
      await apiClient.delete(`/documents/${documentId}`);
    },
    onSuccess: () => {
      toast.success('Document deleted successfully');
      refetch();
      queryClient.invalidateQueries({ queryKey: ['compliance-documents'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete document');
    },
  });

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !selectedType) {
      toast.error('Please select a document type');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', file.name);

    uploadMutation.mutate(formData);
  };

  const formatBytes = (bytes?: number) => {
    if (!bytes) return 'Unknown size';
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleDownload = async (doc: Document) => {
    try {
      const response = await apiClient.get(`/documents/${doc.id}`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', doc.file_name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to download document');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  const uploadedTypes = documents?.map((d) => d.type) || [];
  const availableTypes = DOCUMENT_TYPES.filter((type) => !uploadedTypes.includes(type));

  return (
    <div className="space-y-4">
      {!readOnly && availableTypes.length > 0 && (
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="text-sm font-medium mb-2 block">Document Type</label>
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger>
                <SelectValue placeholder="Select document type..." />
              </SelectTrigger>
              <SelectContent>
                {availableTypes.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type.replace(/_/g, ' ')}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button
            variant="outline"
            disabled={!selectedType || uploadMutation.isPending}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload className="w-4 h-4 mr-2" />
            {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
          </Button>
            <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            onChange={handleFileSelect}
            accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
          />
        </div>
      )}

      {documents && documents.length === 0 ? (
        <Alert>
          <AlertDescription>No documents uploaded yet</AlertDescription>
        </Alert>
      ) : (
        <div className="space-y-2">
          {documents?.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center justify-between p-3 rounded-lg border"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-muted-foreground" />
                <div>
                  <div className="font-medium">{doc.name || doc.file_name}</div>
                  <div className="text-sm text-muted-foreground">
                    {formatBytes(doc.file_size)} • {doc.mime_type?.toUpperCase() || 'Unknown'}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant="outline" className="capitalize">
                  {doc.type?.toLowerCase().replace(/_/g, ' ') || 'other'}
                </Badge>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDownload(doc)}
                  title="Download"
                >
                  <Download className="w-4 h-4" />
                </Button>
                {!readOnly && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => deleteMutation.mutate(doc.id)}
                    disabled={deleteMutation.isPending}
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

