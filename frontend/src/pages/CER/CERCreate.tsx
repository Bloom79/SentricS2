/**
 * Create CER Page
 * Form for creating a new Renewable Energy Community
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { toast } from 'sonner';
import { cerService } from '@/services/api/cer.service';

const cerFormSchema = z.object({
  name: z.string().min(1, "Name is required").min(3, "Name must be at least 3 characters"),
  description: z.string().optional(),
  legal_type: z.enum(["cooperative", "association", "consortium"]),
  address: z.string().min(1, "Address is required"),
  region: z.string().min(1, "Region is required"),
  primary_substation_id: z.string().min(1, "Primary substation ID is required"),
  location: z.array(z.number()).length(2).optional(), // [longitude, latitude]
  boundary: z.array(z.array(z.number())).optional(), // List of [lon, lat] pairs
});

type CERFormData = z.infer<typeof cerFormSchema>;

export default function CERCreate() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const form = useForm<CERFormData>({
    resolver: zodResolver(cerFormSchema),
    defaultValues: {
      name: '',
      description: '',
      legal_type: 'cooperative',
      address: '',
      region: '',
      primary_substation_id: '',
      location: undefined,
      boundary: undefined,
    },
  });

  const { mutate: createCER, isPending } = useMutation({
    mutationFn: async (data: CERFormData) => {
      return cerService.createCER(data);
    },
    onSuccess: (cer) => {
      queryClient.invalidateQueries({ queryKey: ['cer', 'list'] });
      toast.success('CER community created successfully');
      navigate(`/cer/${cer.id}`);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create CER community');
    },
  });

  function onSubmit(data: CERFormData) {
    createCER(data);
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/cer')} className="w-fit">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">Create New CER</h1>
            <p className="text-sm text-muted-foreground">Create a new Renewable Energy Community</p>
          </div>
        </div>
      </div>

      {/* Form */}
      <Card>
        <CardHeader>
          <CardTitle>Community Information</CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Community Name *</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter community name" {...field} />
                    </FormControl>
                    <FormDescription>
                      The official name of the Renewable Energy Community
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Enter community description"
                        {...field}
                        rows={4}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="legal_type"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Legal Type *</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select legal type" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="cooperative">Cooperative</SelectItem>
                          <SelectItem value="association">Association</SelectItem>
                          <SelectItem value="consortium">Consortium</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="region"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Region *</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter region" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="address"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Address *</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter full address" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />


              <FormField
                control={form.control}
                name="primary_substation_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Primary Substation ID *</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter primary substation ID" {...field} />
                    </FormControl>
                    <FormDescription>
                      The identifier of the primary transformer substation
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex flex-col sm:flex-row justify-end gap-3 sm:gap-4 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/cer')}
                  className="w-full sm:w-auto"
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isPending} className="w-full sm:w-auto">
                  <Save className="mr-2 h-4 w-4" />
                  {isPending ? 'Creating...' : 'Create CER'}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}

