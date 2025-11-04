/**
 * Documents Page - Enhanced Document Library
 * Comprehensive document management with upload, filtering, and organization
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Upload,
  Download,
  Search,
  Filter,
  Trash2,
  Eye,
  Edit2,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Grid3x3,
  List,
  Plus,
  Factory,
  Building2,
  FileCheck,
  Loader2,
  MoreVertical,
  Tag,
  RefreshCw,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiClient } from '@/services/api/apiClient';
import { toast } from 'sonner';
import { format, differenceInDays, isAfter, isBefore } from 'date-fns';

interface Document {
  id: number;
  name: string;
  description?: string;
  type: string;
  status: string;
  file_name: string;
  file_size: number;
  mime_type?: string;
  plant_id?: number;
  plant_name?: string;
  cer_id?: number;
  cer_name?: string;
  compliance_record_id?: number;
  issue_date?: string;
  expiry_date?: string;
  upload_date: string;
  tags?: string[];
  version?: number;
  is_expired?: boolean;
  days_until_expiry?: number;
}

export default function Documents() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('table');
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [showViewDialog, setShowViewDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);

  // Filters
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterPlant, setFilterPlant] = useState<string>('all');
  const [filterExpiry, setFilterExpiry] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('upload_date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Upload form state
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadName, setUploadName] = useState('');
  const [uploadDescription, setUploadDescription] = useState('');
  const [uploadType, setUploadType] = useState('');
  const [uploadPlantId, setUploadPlantId] = useState<string>('');
  const [uploadCerId, setUploadCerId] = useState<string>('');
  const [uploadIssueDate, setUploadIssueDate] = useState('');
  const [uploadExpiryDate, setUploadExpiryDate] = useState('');

  // Fetch documents
  const { data: documents, isLoading, isError: documentsError, refetch } = useQuery<Document[]>({
    queryKey: ['documents', filterType, filterStatus, filterPlant, filterExpiry],
    queryFn: async () => {
      const params: any = {};
      if (filterType !== 'all') params.type = filterType;
      if (filterStatus !== 'all') params.status = filterStatus;
      if (filterPlant !== 'all') params.plant_id = parseInt(filterPlant);
      if (filterExpiry === 'expiring_soon') {
        // This would need backend support for expiring_soon filter
      }
      const response = await apiClient.get('/documents', { params });
      return response.data || [];
    },
    retry: false,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  // Fetch plants and CERs for filters
  const { data: plants, isError: plantsError } = useQuery({
    queryKey: ['plants'],
    queryFn: async () => {
      const response = await apiClient.get('/plants');
      return response.data || [];
    },
    retry: false,
  });

  const { data: cers, isError: cersError } = useQuery({
    queryKey: ['cers'],
    queryFn: async () => {
      const response = await apiClient.get('/cer/communities');
      return response.data || [];
    },
    retry: false,
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async ({ formData, params }: { formData: FormData; params: string }) => {
      const response = await apiClient.post(`/documents?${params}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success('Document uploaded successfully');
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setShowUploadDialog(false);
      resetUploadForm();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to upload document');
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (documentId: number) => {
      await apiClient.delete(`/documents/${documentId}`);
    },
    onSuccess: () => {
      toast.success('Document deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete document');
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: async (data: Partial<Document>) => {
      const response = await apiClient.put(`/documents/${selectedDocument?.id}`, data);
      return response.data;
    },
    onSuccess: () => {
      toast.success('Document updated successfully');
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setShowEditDialog(false);
      setSelectedDocument(null);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update document');
    },
  });

  const resetUploadForm = () => {
    setUploadFile(null);
    setUploadName('');
    setUploadDescription('');
    setUploadType('');
    setUploadPlantId('');
    setUploadCerId('');
    setUploadIssueDate('');
    setUploadExpiryDate('');
  };

  const handleUpload = () => {
    if (!uploadFile || !uploadName || !uploadType) {
      toast.error('Please fill in all required fields');
      return;
    }

    const formData = new FormData();
    formData.append('file', uploadFile);
    
    // Use URLSearchParams for query params since we can't send them in FormData with POST
    const params = new URLSearchParams();
    params.append('name', uploadName);
    if (uploadDescription) params.append('description', uploadDescription);
    params.append('type', uploadType);
    if (uploadPlantId) params.append('plant_id', uploadPlantId);
    if (uploadCerId) params.append('cer_id', uploadCerId);
    if (uploadIssueDate) params.append('issue_date', uploadIssueDate);
    if (uploadExpiryDate) params.append('expiry_date', uploadExpiryDate);
    
    uploadMutation.mutate({ formData, params: params.toString() });
  };

  const handleDownload = async (doc: Document) => {
    try {
      const response = await apiClient.get(`/documents/${doc.id}/download`, {
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

  const handleDelete = (doc: Document) => {
    if (confirm(`Are you sure you want to delete "${doc.name}"?`)) {
      deleteMutation.mutate(doc.id);
    }
  };

  const handleEdit = (doc: Document) => {
    setSelectedDocument(doc);
    setShowEditDialog(true);
  };

  const handleUpdate = () => {
    if (!selectedDocument) return;
    const updateData: any = {
      name: selectedDocument.name,
      description: selectedDocument.description,
      type: selectedDocument.type,
      status: selectedDocument.status,
    };
    // Only include dates if they exist
    if (selectedDocument.issue_date) updateData.issue_date = selectedDocument.issue_date;
    if (selectedDocument.expiry_date) updateData.expiry_date = selectedDocument.expiry_date;
    updateMutation.mutate(updateData);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getExpiryStatus = (doc: Document) => {
    if (!doc.expiry_date) return null;
    const daysUntilExpiry = doc.days_until_expiry ?? differenceInDays(new Date(doc.expiry_date), new Date());
    if (daysUntilExpiry < 0) return { label: 'Expired', variant: 'destructive' as const };
    if (daysUntilExpiry <= 30) return { label: `Expires in ${daysUntilExpiry} days`, variant: 'secondary' as const };
    return null;
  };

  const filteredDocuments = documents?.filter((doc) => {
    const matchesSearch =
      doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.file_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (doc.description || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || doc.type === filterType;
    const matchesStatus = filterStatus === 'all' || doc.status === filterStatus;
    const matchesPlant = filterPlant === 'all' || doc.plant_id?.toString() === filterPlant;
    const matchesExpiry =
      filterExpiry === 'all' ||
      (filterExpiry === 'expired' && doc.is_expired) ||
      (filterExpiry === 'expiring_soon' && doc.days_until_expiry !== undefined && doc.days_until_expiry <= 30 && doc.days_until_expiry >= 0);

    return matchesSearch && matchesType && matchesStatus && matchesPlant && matchesExpiry;
  }) || [];

  // Sort documents
  const sortedDocuments = [...filteredDocuments].sort((a, b) => {
    let aVal: any = a[sortBy as keyof Document];
    let bVal: any = b[sortBy as keyof Document];

    if (sortBy === 'upload_date' || sortBy === 'expiry_date' || sortBy === 'issue_date') {
      aVal = aVal ? new Date(aVal).getTime() : 0;
      bVal = bVal ? new Date(bVal).getTime() : 0;
    }

    if (sortOrder === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  // Statistics
  const stats = {
    total: documents?.length || 0,
    expiringSoon: documents?.filter((d) => d.days_until_expiry !== undefined && d.days_until_expiry <= 30 && d.days_until_expiry >= 0).length || 0,
    expired: documents?.filter((d) => d.is_expired).length || 0,
    byType: documents?.reduce((acc, doc) => {
      acc[doc.type] = (acc[doc.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>) || {},
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
          <h1 className="text-3xl font-bold">Document Library</h1>
          <p className="text-muted-foreground mt-1">
            Manage and organize all compliance and plant documentation
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button onClick={() => setShowUploadDialog(true)}>
            <Upload className="mr-2 h-4 w-4" />
            Upload Document
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Expiring Soon</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.expiringSoon}</div>
            <p className="text-xs text-muted-foreground">Next 30 days</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Expired</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.expired}</div>
            <p className="text-xs text-muted-foreground">Requires attention</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Approval</CardTitle>
            <FileCheck className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {documents?.filter((d) => d.status === 'Pending').length || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Alerts */}
      {stats.expired > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            You have {stats.expired} expired document{stats.expired > 1 ? 's' : ''} that require attention.
          </AlertDescription>
        </Alert>
      )}

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Filters</CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant={viewMode === 'table' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('table')}
              >
                <List className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid3x3 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-6">
            <div className="relative md:col-span-2">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger>
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="Certificate">Certificate</SelectItem>
                <SelectItem value="Permit">Permit</SelectItem>
                <SelectItem value="Contract">Contract</SelectItem>
                <SelectItem value="Report">Report</SelectItem>
                <SelectItem value="Invoice">Invoice</SelectItem>
                <SelectItem value="License">License</SelectItem>
                <SelectItem value="Other">Other</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="Draft">Draft</SelectItem>
                <SelectItem value="Pending">Pending</SelectItem>
                <SelectItem value="Approved">Approved</SelectItem>
                <SelectItem value="Rejected">Rejected</SelectItem>
                <SelectItem value="Expired">Expired</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filterPlant} onValueChange={setFilterPlant}>
              <SelectTrigger>
                <SelectValue placeholder="Plant" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Plants</SelectItem>
                {plants?.map((plant: any) => (
                  <SelectItem key={plant.id} value={plant.id.toString()}>
                    {plant.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filterExpiry} onValueChange={setFilterExpiry}>
              <SelectTrigger>
                <SelectValue placeholder="Expiry" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Documents</SelectItem>
                <SelectItem value="expiring_soon">Expiring Soon</SelectItem>
                <SelectItem value="expired">Expired</SelectItem>
                <SelectItem value="no_expiry">No Expiry Date</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Documents Table/Grid */}
      {viewMode === 'table' ? (
        <Card>
          <CardHeader>
            <CardTitle>Documents ({sortedDocuments.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Document</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Linked To</TableHead>
                  <TableHead>Upload Date</TableHead>
                  <TableHead>Expiry Date</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedDocuments.map((doc) => {
                  const expiryStatus = getExpiryStatus(doc);
                  return (
                    <TableRow key={doc.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-muted-foreground" />
                          <div>
                            <p className="font-medium">{doc.name}</p>
                            {doc.description && (
                              <p className="text-xs text-muted-foreground">{doc.description}</p>
                            )}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{doc.type}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            doc.status === 'Approved'
                              ? 'default'
                              : doc.status === 'Pending'
                              ? 'secondary'
                              : doc.status === 'Expired' || doc.status === 'Rejected'
                              ? 'destructive'
                              : 'outline'
                          }
                        >
                          {doc.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {doc.plant_name ? (
                          <div className="flex items-center gap-1">
                            <Factory className="h-3 w-3" />
                            <span className="text-sm">{doc.plant_name}</span>
                          </div>
                        ) : doc.cer_name ? (
                          <div className="flex items-center gap-1">
                            <Building2 className="h-3 w-3" />
                            <span className="text-sm">{doc.cer_name}</span>
                          </div>
                        ) : (
                          <span className="text-muted-foreground text-sm">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-sm">
                        {doc.upload_date ? format(new Date(doc.upload_date), 'PPP') : '-'}
                      </TableCell>
                      <TableCell>
                        {doc.expiry_date ? (
                          <div className="flex items-center gap-2">
                            <span className={expiryStatus?.variant === 'destructive' ? 'text-red-500' : ''}>
                              {format(new Date(doc.expiry_date), 'PPP')}
                            </span>
                            {expiryStatus && (
                              <Badge variant={expiryStatus.variant} className="text-xs">
                                {expiryStatus.label}
                              </Badge>
                            )}
                          </div>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-sm">{formatFileSize(doc.file_size)}</TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleDownload(doc)}>
                              <Download className="mr-2 h-4 w-4" />
                              Download
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleEdit(doc)}>
                              <Edit2 className="mr-2 h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleDelete(doc)}>
                              <Trash2 className="mr-2 h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
            {sortedDocuments.length === 0 && (
              <div className="text-center py-12">
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">No documents found</p>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {sortedDocuments.map((doc) => {
            const expiryStatus = getExpiryStatus(doc);
            return (
              <Card key={doc.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-primary/10 rounded-lg">
                        <FileText className="h-5 w-5 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-base truncate">{doc.name}</CardTitle>
                        {doc.description && (
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                            {doc.description}
                          </p>
                        )}
                      </div>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleDownload(doc)}>
                          <Download className="mr-2 h-4 w-4" />
                          Download
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleEdit(doc)}>
                          <Edit2 className="mr-2 h-4 w-4" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleDelete(doc)}>
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{doc.type}</Badge>
                    <Badge
                      variant={
                        doc.status === 'Approved'
                          ? 'default'
                          : doc.status === 'Pending'
                          ? 'secondary'
                          : doc.status === 'Expired' || doc.status === 'Rejected'
                          ? 'destructive'
                          : 'outline'
                      }
                    >
                      {doc.status}
                    </Badge>
                  </div>
                  <div className="space-y-1 text-sm">
                    {doc.plant_name && (
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Factory className="h-3 w-3" />
                        <span>{doc.plant_name}</span>
                      </div>
                    )}
                    {doc.cer_name && (
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Building2 className="h-3 w-3" />
                        <span>{doc.cer_name}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Size:</span>
                      <span>{formatFileSize(doc.file_size)}</span>
                    </div>
                    {doc.expiry_date && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Expires:</span>
                        <span className={expiryStatus?.variant === 'destructive' ? 'text-red-500' : ''}>
                          {format(new Date(doc.expiry_date), 'MMM d, yyyy')}
                        </span>
                      </div>
                    )}
                  </div>
                  {expiryStatus && (
                    <Alert variant={expiryStatus.variant === 'destructive' ? 'destructive' : 'default'}>
                      <AlertDescription className="text-xs">{expiryStatus.label}</AlertDescription>
                    </Alert>
                  )}
                  <Button variant="outline" className="w-full" onClick={() => handleDownload(doc)}>
                    <Download className="mr-2 h-4 w-4" />
                    Download
                  </Button>
                </CardContent>
              </Card>
            );
          })}
          {sortedDocuments.length === 0 && (
            <Card className="col-span-full">
              <CardContent className="py-12 text-center">
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">No documents found</p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Upload Dialog */}
      <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Upload Document</DialogTitle>
            <DialogDescription>Upload a new document to the library</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="file">File *</Label>
              <Input
                id="file"
                type="file"
                onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
              />
              {uploadFile && (
                <p className="text-sm text-muted-foreground">
                  Selected: {uploadFile.name} ({formatFileSize(uploadFile.size)})
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="name">Document Name *</Label>
              <Input
                id="name"
                value={uploadName}
                onChange={(e) => setUploadName(e.target.value)}
                placeholder="Enter document name"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={uploadDescription}
                onChange={(e) => setUploadDescription(e.target.value)}
                placeholder="Optional description"
                rows={3}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="type">Document Type *</Label>
                <Select value={uploadType} onValueChange={setUploadType}>
                  <SelectTrigger id="type">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Certificate">Certificate</SelectItem>
                    <SelectItem value="Permit">Permit</SelectItem>
                    <SelectItem value="Contract">Contract</SelectItem>
                    <SelectItem value="Report">Report</SelectItem>
                    <SelectItem value="Invoice">Invoice</SelectItem>
                    <SelectItem value="License">License</SelectItem>
                    <SelectItem value="Other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="plant">Link to Plant (Optional)</Label>
                <Select value={uploadPlantId || "none"} onValueChange={(value) => setUploadPlantId(value === "none" ? "" : value)}>
                  <SelectTrigger id="plant">
                    <SelectValue placeholder="Select plant" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None</SelectItem>
                    {plants?.map((plant: any) => (
                      <SelectItem key={plant.id} value={plant.id.toString()}>
                        {plant.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="issue_date">Issue Date (Optional)</Label>
                <Input
                  id="issue_date"
                  type="date"
                  value={uploadIssueDate}
                  onChange={(e) => setUploadIssueDate(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="expiry_date">Expiry Date (Optional)</Label>
                <Input
                  id="expiry_date"
                  type="date"
                  value={uploadExpiryDate}
                  onChange={(e) => setUploadExpiryDate(e.target.value)}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowUploadDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpload} disabled={uploadMutation.isPending}>
              {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Document</DialogTitle>
            <DialogDescription>Update document information</DialogDescription>
          </DialogHeader>
          {selectedDocument && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="edit-name">Document Name</Label>
                <Input
                  id="edit-name"
                  value={selectedDocument.name}
                  onChange={(e) =>
                    setSelectedDocument({ ...selectedDocument, name: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-description">Description</Label>
                <Textarea
                  id="edit-description"
                  value={selectedDocument.description || ''}
                  onChange={(e) =>
                    setSelectedDocument({ ...selectedDocument, description: e.target.value })
                  }
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-type">Type</Label>
                  <Select
                    value={selectedDocument.type}
                    onValueChange={(value) =>
                      setSelectedDocument({ ...selectedDocument, type: value })
                    }
                  >
                    <SelectTrigger id="edit-type">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Certificate">Certificate</SelectItem>
                      <SelectItem value="Permit">Permit</SelectItem>
                      <SelectItem value="Contract">Contract</SelectItem>
                      <SelectItem value="Report">Report</SelectItem>
                      <SelectItem value="Invoice">Invoice</SelectItem>
                      <SelectItem value="License">License</SelectItem>
                      <SelectItem value="Other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-status">Status</Label>
                  <Select
                    value={selectedDocument.status}
                    onValueChange={(value) =>
                      setSelectedDocument({ ...selectedDocument, status: value })
                    }
                  >
                    <SelectTrigger id="edit-status">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Draft">Draft</SelectItem>
                      <SelectItem value="Pending">Pending</SelectItem>
                      <SelectItem value="Approved">Approved</SelectItem>
                      <SelectItem value="Rejected">Rejected</SelectItem>
                      <SelectItem value="Expired">Expired</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdate} disabled={updateMutation.isPending}>
              {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}