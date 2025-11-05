/**
 * Documents Tab Component
 * Manages documents for a CER
 */

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileText, Download, Upload, AlertCircle, Loader2, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
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
import { cerService } from '@/services/api/cer.service';

interface DocumentsTabProps {
  cerId: number;
}

export function DocumentsTab({ cerId }: DocumentsTabProps) {
  const { data: documents, isLoading: loadingDocuments } = useQuery({
    queryKey: ['cer-documents', cerId],
    queryFn: () => cerService.getCERDocuments(cerId),
  });

  const { data: overview, isLoading: loadingOverview } = useQuery({
    queryKey: ['cer-documents-overview', cerId],
    queryFn: () => cerService.getCERDocumentsOverview(cerId),
  });

  if (loadingDocuments || loadingOverview) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Overview Cards */}
      {overview && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overview.total_documents || 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Expired</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">
                {overview.expired_count || 0}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Expiring Soon</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-500">
                {overview.expiring_soon_count || 0}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">By Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1 text-sm">
                {overview.by_status &&
                  Object.entries(overview.by_status).map(([status, count]: [string, any]) => (
                    <div key={status} className="flex justify-between">
                      <span className="capitalize text-muted-foreground">{status}:</span>
                      <span className="font-medium">{count}</span>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Documents List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Documents ({documents?.length || 0})</CardTitle>
            <Button>
              <Upload className="mr-2 h-4 w-4" />
              Upload Document
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {documents && documents.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Expiry Date</TableHead>
                  <TableHead>Uploaded</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documents.map((doc: any) => (
                  <TableRow key={doc.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        {doc.name || doc.filename || `Document #${doc.id}`}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {doc.type || 'unknown'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          doc.status === 'active' || doc.status === 'approved'
                            ? 'default'
                            : doc.status === 'expired'
                              ? 'destructive'
                              : 'secondary'
                        }
                        className="capitalize"
                      >
                        {doc.status || 'unknown'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {doc.expiry_date ? (
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(doc.expiry_date).toLocaleDateString()}
                          {doc.is_expired && (
                            <AlertCircle className="h-3 w-3 text-destructive ml-1" />
                          )}
                        </div>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : '-'}
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No documents yet</p>
              <Button className="mt-4" variant="outline">
                <Upload className="mr-2 h-4 w-4" />
                Upload First Document
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
