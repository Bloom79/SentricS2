/**
 * New Compliance Record Component
 * Creates a new compliance record from a requirement
 * Adapted from sentrics-repo
 */

import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { cerService } from '@/services/api/cer.service';
import { apiClient } from '@/services/api/apiClient';
import { toast } from 'sonner';
import { Calendar } from 'lucide-react';

type NewComplianceRecordProps = {
  cerId: number;
  onSuccess?: () => void;
  onCancel?: () => void;
};

export function NewComplianceRecord({ cerId, onSuccess, onCancel }: NewComplianceRecordProps) {
  const [requirementId, setRequirementId] = useState<string>('');
  const [dueDate, setDueDate] = useState<string>('');
  const [notes, setNotes] = useState('');
  const queryClient = useQueryClient();

  // Fetch available requirements for this CER
  const { data: requirements, isLoading: loadingRequirements } = useQuery({
    queryKey: ['cer-compliance-requirements', cerId],
    queryFn: () => cerService.getCERComplianceRequirements(cerId, false), // Don't include plants for creation
  });

  const { mutate: createRecord, isPending } = useMutation({
    mutationFn: async (data: { requirement_id: number; due_date: string; notes?: string }) => {
      // First, we need to create a record via the compliance service
      // Since the backend expects requirement_id and due_date, we'll call the compliance service
      const response = await apiClient.post('/compliance/records', {
        requirement_id: data.requirement_id,
        due_date: data.due_date,
        notes: data.notes,
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success('Compliance record created successfully');
      queryClient.invalidateQueries({ queryKey: ['cer-compliance-records', cerId] });
      queryClient.invalidateQueries({ queryKey: ['cer-compliance', cerId] });
      onSuccess?.();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create compliance record');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!requirementId || !dueDate) {
      toast.error('Please select a requirement and set a due date');
      return;
    }
    createRecord({
      requirement_id: parseInt(requirementId),
      due_date: dueDate,
      notes: notes || undefined,
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>New Compliance Record</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="requirement">Requirement *</Label>
            <Select
              value={requirementId}
              onValueChange={setRequirementId}
              disabled={loadingRequirements}
            >
              <SelectTrigger id="requirement">
                <SelectValue placeholder="Select a requirement" />
              </SelectTrigger>
              <SelectContent>
                {requirements && requirements.length > 0 ? (
                  requirements.map((req: any) => (
                    <SelectItem key={req.id} value={req.id.toString()}>
                      {req.name || req.title || `Requirement #${req.id}`}
                      {req.description && ` - ${req.description.substring(0, 50)}...`}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItem value="none" disabled>
                    No requirements available
                  </SelectItem>
                )}
              </SelectContent>
            </Select>
            {requirements && requirements.length === 0 && (
              <p className="text-sm text-muted-foreground">
                No compliance requirements defined for this CER. Create a requirement first.
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="dueDate">Due Date *</Label>
            <div className="relative">
              <Input
                id="dueDate"
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="pl-10"
              />
              <Calendar className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add any relevant notes..."
              rows={4}
            />
          </div>

          <div className="flex justify-end gap-2">
            {onCancel && (
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
            )}
            <Button type="submit" disabled={isPending || !requirementId || !dueDate}>
              {isPending ? 'Creating...' : 'Create Record'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
