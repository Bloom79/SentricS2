/**
 * Maintenance Scheduling Module
 * Manage preventive and corrective maintenance for plants and assets
 */
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Calendar, Wrench, AlertCircle, CheckCircle2, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { apiClient } from '@/services/api/apiClient';
import { Breadcrumbs } from '@/components/ui/breadcrumbs';
import { useToast } from '@/hooks/use-toast';

interface MaintenanceTask {
  id: number;
  title: string;
  description?: string;
  plant_id?: number;
  plant_name?: string;
  asset_id?: number;
  asset_name?: string;
  type: 'preventive' | 'corrective' | 'inspection';
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  scheduled_date: string;
  completed_date?: string;
  assigned_to?: string;
  technician_name?: string;
  estimated_hours?: number;
  actual_hours?: number;
  cost_estimate?: number;
  actual_cost?: number;
  notes?: string;
  recurring?: boolean;
  recurrence_pattern?: string; // e.g., "monthly", "quarterly"
  next_occurrence?: string;
}

const PRIORITY_COLORS = {
  low: 'bg-gray-100 text-gray-700',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
};

const STATUS_COLORS = {
  scheduled: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-yellow-100 text-yellow-700',
  completed: 'bg-green-100 text-green-700',
  cancelled: 'bg-gray-100 text-gray-700',
};

export const MaintenanceSchedule: React.FC = () => {
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Fetch maintenance tasks
  const { data: tasks = [], isLoading } = useQuery<MaintenanceTask[]>({
    queryKey: ['maintenance', 'tasks', filterStatus, filterPriority],
    queryFn: async () => {
      const params: any = {};
      if (filterStatus !== 'all') params.status = filterStatus;
      if (filterPriority !== 'all') params.priority = filterPriority;

      const response = await apiClient.get('/maintenance/tasks', { params });
      return response.data;
    },
  });

  // Group tasks by status
  const tasksByStatus = tasks.reduce((acc, task) => {
    if (!acc[task.status]) acc[task.status] = [];
    acc[task.status].push(task);
    return acc;
  }, {} as Record<string, MaintenanceTask[]>);

  // Upcoming tasks (next 7 days)
  const upcomingTasks = tasks.filter((task) => {
    if (task.status !== 'scheduled') return false;
    const scheduledDate = new Date(task.scheduled_date);
    const today = new Date();
    const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
    return scheduledDate >= today && scheduledDate <= nextWeek;
  });

  // Overdue tasks
  const overdueTasks = tasks.filter((task) => {
    if (task.status === 'completed' || task.status === 'cancelled') return false;
    const scheduledDate = new Date(task.scheduled_date);
    return scheduledDate < new Date();
  });

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Breadcrumbs
            items={[{ label: 'Maintenance', href: '/maintenance' }, { label: 'Schedule' }]}
          />
          <h1 className="text-3xl font-bold mt-2">Maintenance Schedule</h1>
          <p className="text-muted-foreground">
            Manage preventive and corrective maintenance tasks
          </p>
        </div>
        <CreateMaintenanceDialog
          open={createDialogOpen}
          onOpenChange={setCreateDialogOpen}
        />
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Upcoming (7 days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{upcomingTasks.length}</div>
          </CardContent>
        </Card>

        <Card className="border-red-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Overdue
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{overdueTasks.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              In Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasksByStatus.in_progress?.length || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Completed (This Month)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasksByStatus.completed?.length || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="scheduled">Scheduled</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filterPriority} onValueChange={setFilterPriority}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Priorities</SelectItem>
            <SelectItem value="low">Low</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Task List */}
      <Card>
        <CardHeader>
          <CardTitle>Maintenance Tasks</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">Loading tasks...</div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No maintenance tasks found. Create your first task to get started.
            </div>
          ) : (
            <div className="space-y-3">
              {tasks.map((task) => (
                <MaintenanceTaskCard key={task.id} task={task} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Maintenance Task Card Component
const MaintenanceTaskCard: React.FC<{ task: MaintenanceTask }> = ({ task }) => {
  const isOverdue =
    task.status !== 'completed' &&
    task.status !== 'cancelled' &&
    new Date(task.scheduled_date) < new Date();

  return (
    <div className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold">{task.title}</h3>
            <Badge variant="outline" className={PRIORITY_COLORS[task.priority]}>
              {task.priority}
            </Badge>
            <Badge variant="outline" className={STATUS_COLORS[task.status]}>
              {task.status.replace('_', ' ')}
            </Badge>
            {isOverdue && (
              <Badge variant="destructive" className="text-xs">
                Overdue
              </Badge>
            )}
          </div>

          <div className="text-sm text-muted-foreground space-y-1">
            {task.plant_name && (
              <div>Plant: {task.plant_name}</div>
            )}
            {task.asset_name && (
              <div>Asset: {task.asset_name}</div>
            )}
            {task.technician_name && (
              <div>Assigned to: {task.technician_name}</div>
            )}
          </div>

          {task.description && (
            <p className="text-sm mt-2">{task.description}</p>
          )}
        </div>

        <div className="text-right space-y-1">
          <div className="text-sm font-medium">
            {new Date(task.scheduled_date).toLocaleDateString()}
          </div>
          {task.estimated_hours && (
            <div className="text-xs text-muted-foreground">
              {task.estimated_hours}h estimated
            </div>
          )}
          {task.cost_estimate && (
            <div className="text-xs text-muted-foreground">
              €{task.cost_estimate.toLocaleString()}
            </div>
          )}
          {task.recurring && (
            <Badge variant="secondary" className="text-xs">
              Recurring
            </Badge>
          )}
        </div>
      </div>
    </div>
  );
};

// Create Maintenance Dialog Component
const CreateMaintenanceDialog: React.FC<{
  open: boolean;
  onOpenChange: (open: boolean) => void;
}> = ({ open, onOpenChange }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'preventive',
    priority: 'medium',
    scheduled_date: '',
    estimated_hours: '',
    cost_estimate: '',
  });

  const queryClient = useQueryClient();
  const { toast } = useToast();

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await apiClient.post('/maintenance/tasks', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance'] });
      toast({
        title: 'Success',
        description: 'Maintenance task created successfully',
      });
      onOpenChange(false);
      setFormData({
        title: '',
        description: '',
        type: 'preventive',
        priority: 'medium',
        scheduled_date: '',
        estimated_hours: '',
        cost_estimate: '',
      });
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to create maintenance task',
        variant: 'destructive',
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Schedule Maintenance
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Schedule New Maintenance Task</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="title">Task Title *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g., Quarterly inverter inspection"
              required
            />
          </div>

          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Describe the maintenance work to be performed..."
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="type">Type *</Label>
              <Select
                value={formData.type}
                onValueChange={(value) => setFormData({ ...formData, type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="preventive">Preventive</SelectItem>
                  <SelectItem value="corrective">Corrective</SelectItem>
                  <SelectItem value="inspection">Inspection</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="priority">Priority *</Label>
              <Select
                value={formData.priority}
                onValueChange={(value) => setFormData({ ...formData, priority: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="scheduled_date">Scheduled Date *</Label>
              <Input
                id="scheduled_date"
                type="date"
                value={formData.scheduled_date}
                onChange={(e) =>
                  setFormData({ ...formData, scheduled_date: e.target.value })
                }
                required
              />
            </div>

            <div>
              <Label htmlFor="estimated_hours">Estimated Hours</Label>
              <Input
                id="estimated_hours"
                type="number"
                step="0.5"
                value={formData.estimated_hours}
                onChange={(e) =>
                  setFormData({ ...formData, estimated_hours: e.target.value })
                }
                placeholder="4.0"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="cost_estimate">Cost Estimate (€)</Label>
            <Input
              id="cost_estimate"
              type="number"
              step="0.01"
              value={formData.cost_estimate}
              onChange={(e) =>
                setFormData({ ...formData, cost_estimate: e.target.value })
              }
              placeholder="500.00"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Task'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default MaintenanceSchedule;
