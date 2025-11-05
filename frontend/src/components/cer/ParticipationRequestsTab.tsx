/**
 * Participation Requests Tab Component
 * Manages participation requests for a CER
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Check, X, Clock, Mail, Loader2 } from 'lucide-react';
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
import { cerService, CERParticipationRequest } from '@/services/api/cer.service';

interface ParticipationRequestsTabProps {
  cerId: number;
}

export function ParticipationRequestsTab({ cerId }: ParticipationRequestsTabProps) {
  const queryClient = useQueryClient();
  const [selectedRequest, setSelectedRequest] = useState<CERParticipationRequest | null>(null);
  const [adminNotes, setAdminNotes] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [actionType, setActionType] = useState<'approve' | 'reject' | null>(null);

  const { data: requests, isLoading } = useQuery({
    queryKey: ['cer-participation-requests', cerId],
    queryFn: () => cerService.getCERParticipationRequests(cerId),
  });

  const { mutate: updateRequest, isPending: isUpdating } = useMutation({
    mutationFn: async ({
      requestId,
      status,
      notes,
    }: {
      requestId: number;
      status: string;
      notes?: string;
    }) => {
      return cerService.updateParticipationRequest(requestId, {
        status,
        notes: notes,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cer-participation-requests', cerId] });
      queryClient.invalidateQueries({ queryKey: ['cer-members', cerId] });
      toast.success(`Request ${actionType === 'approve' ? 'approved' : 'rejected'} successfully`);
      setIsDialogOpen(false);
      setSelectedRequest(null);
      setAdminNotes('');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update request');
    },
  });

  const { mutate: deleteRequest, isPending: isDeleting } = useMutation({
    mutationFn: async (requestId: number) => {
      return cerService.deleteParticipationRequest(requestId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cer-participation-requests', cerId] });
      toast.success('Request deleted successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete request');
    },
  });

  const handleApprove = (request: CERParticipationRequest) => {
    setSelectedRequest(request);
    setActionType('approve');
    setAdminNotes('');
    setIsDialogOpen(true);
  };

  const handleReject = (request: CERParticipationRequest) => {
    setSelectedRequest(request);
    setActionType('reject');
    setAdminNotes('');
    setIsDialogOpen(true);
  };

  const handleConfirmAction = () => {
    if (!selectedRequest) return;
    const status = actionType === 'approve' ? 'approved' : 'rejected';
    updateRequest({
      requestId: selectedRequest.id,
      status,
      notes: adminNotes || undefined,
    });
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      pending: 'secondary',
      approved: 'default',
      rejected: 'destructive',
      cancelled: 'outline',
    };
    return (
      <Badge variant={variants[status] || 'outline'} className="capitalize">
        {status}
      </Badge>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Participation Requests ({requests?.length || 0})</CardTitle>
        </CardHeader>
        <CardContent>
          {requests && requests.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>CER</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Request Date</TableHead>
                  <TableHead>Processed Date</TableHead>
                  <TableHead>Notes</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {requests.map((request) => (
                  <TableRow key={request.id}>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="font-medium">
                          {request.user_name || `User #${request.user_id}`}
                        </div>
                        {request.user_email && (
                          <div className="flex items-center gap-1 text-sm text-muted-foreground">
                            <Mail className="h-3 w-3" />
                            {request.user_email}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>{request.cer_name || `CER #${request.cer_id}`}</TableCell>
                    <TableCell>{getStatusBadge(request.status)}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(request.request_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {request.processed_date
                        ? new Date(request.processed_date).toLocaleDateString()
                        : '-'}
                    </TableCell>
                    <TableCell className="text-sm max-w-xs truncate">
                      {request.notes || '-'}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        {request.status === 'pending' && (
                          <>
                            <Button
                              size="sm"
                              variant="default"
                              onClick={() => handleApprove(request)}
                              disabled={isUpdating}
                            >
                              <Check className="h-3 w-3 mr-1" />
                              Approve
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleReject(request)}
                              disabled={isUpdating}
                            >
                              <X className="h-3 w-3 mr-1" />
                              Reject
                            </Button>
                          </>
                        )}
                        {(request.status === 'pending' || request.status === 'cancelled') && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => deleteRequest(request.id)}
                            disabled={isDeleting}
                          >
                            Delete
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No participation requests yet</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Request Details Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {actionType === 'approve' ? 'Approve' : 'Reject'} Participation Request
            </DialogTitle>
            <DialogDescription>
              {selectedRequest && (
                <>
                  Review the request from{' '}
                  <strong>{selectedRequest.user_name || `User #${selectedRequest.user_id}`}</strong>{' '}
                  to join
                  <strong> {selectedRequest.cer_name || `CER #${selectedRequest.cer_id}`}</strong>.
                </>
              )}
            </DialogDescription>
          </DialogHeader>
          {selectedRequest && (
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <Label className="text-muted-foreground">User</Label>
                    <p>{selectedRequest.user_name || `User #${selectedRequest.user_id}`}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">CER</Label>
                    <p>{selectedRequest.cer_name || `CER #${selectedRequest.cer_id}`}</p>
                  </div>
                  {selectedRequest.user_email && (
                    <div>
                      <Label className="text-muted-foreground">Email</Label>
                      <p>{selectedRequest.user_email}</p>
                    </div>
                  )}
                  <div>
                    <Label className="text-muted-foreground">Request Date</Label>
                    <p>{new Date(selectedRequest.request_date).toLocaleDateString()}</p>
                  </div>
                </div>
                {selectedRequest.notes && (
                  <div>
                    <Label className="text-muted-foreground">Original Notes</Label>
                    <p className="text-sm">{selectedRequest.notes}</p>
                  </div>
                )}
              </div>
              <div>
                <Label htmlFor="admin-notes">Notes {actionType === 'reject' && '(required)'}</Label>
                <Textarea
                  id="admin-notes"
                  placeholder={
                    actionType === 'approve'
                      ? 'Optional notes about this approval...'
                      : 'Please provide a reason for rejection...'
                  }
                  value={adminNotes}
                  onChange={(e) => setAdminNotes(e.target.value)}
                  rows={4}
                  className="mt-2"
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleConfirmAction}
              disabled={isUpdating || (actionType === 'reject' && !adminNotes.trim())}
              variant={actionType === 'reject' ? 'destructive' : 'default'}
            >
              {isUpdating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  {actionType === 'approve' ? (
                    <>
                      <Check className="h-4 w-4 mr-2" />
                      Approve Request
                    </>
                  ) : (
                    <>
                      <X className="h-4 w-4 mr-2" />
                      Reject Request
                    </>
                  )}
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
