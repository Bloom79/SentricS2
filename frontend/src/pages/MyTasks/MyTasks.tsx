/**
 * My Tasks Page
 * User task management
 */

import React, { useState, useEffect } from 'react';
import { CheckSquare, Clock, AlertCircle, CheckCircle, FileText, Building2, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import apiClient from '@/services/api/apiClient';

interface Task {
  id: number;
  title: string;
  description?: string;
  status: string;
  due_date?: string;
  priority?: string;
  workflow?: {
    id: number;
    name: string;
    plant_id: number;
    plant_name: string;
  };
}

export default function MyTasks() {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'todo' | 'overdue' | 'completed'>('todo');

  useEffect(() => {
    loadTasks();
  }, [filter]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      let endpoint = '/workflows/users/me/tasks';
      if (filter === 'todo') {
        endpoint += '?status=pending';
      } else if (filter === 'completed') {
        endpoint += '?status=completed';
      }
      const response = await apiClient.get(endpoint);
      setTasks(response.data || []);
    } catch (error) {
      console.error('Error loading tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const isOverdue = (task: Task) => {
    if (!task.due_date || task.status === 'completed') return false;
    return new Date(task.due_date) < new Date();
  };

  const stats = {
    total: tasks.length,
    todo: tasks.filter(t => t.status === 'pending').length,
    overdue: tasks.filter(t => isOverdue(t)).length,
    completed: tasks.filter(t => t.status === 'completed').length,
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'overdue') return isOverdue(task);
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">My Tasks</h1>
        <p className="text-muted-foreground mt-1">
          Manage activities assigned to you in workflows
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">To Do</p>
              <p className="text-2xl font-bold">{stats.todo}</p>
            </div>
            <Clock className="h-8 w-8 text-blue-500 opacity-20" />
          </div>
        </div>
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Overdue</p>
              <p className="text-2xl font-bold text-red-600">{stats.overdue}</p>
            </div>
            <AlertCircle className="h-8 w-8 text-red-500 opacity-20" />
          </div>
        </div>
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Completed</p>
              <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500 opacity-20" />
          </div>
        </div>
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total</p>
              <p className="text-2xl font-bold">{stats.total}</p>
            </div>
            <CheckSquare className="h-8 w-8 text-primary opacity-20" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {(['all', 'todo', 'overdue', 'completed'] as const).map((f) => (
          <Button
            key={f}
            variant={filter === f ? 'default' : 'outline'}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </Button>
        ))}
      </div>

      {/* Tasks List */}
      <div className="space-y-2">
        {filteredTasks.map((task) => (
          <div
            key={task.id}
            className="border rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  {task.status === 'completed' ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : isOverdue(task) ? (
                    <AlertCircle className="h-5 w-5 text-red-600" />
                  ) : (
                    <Clock className="h-5 w-5 text-blue-600" />
                  )}
                  <h3 className="font-semibold">{task.title}</h3>
                </div>
                {task.description && (
                  <p className="text-sm text-muted-foreground mb-2">
                    {task.description}
                  </p>
                )}
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  {task.workflow && (
                    <>
                      <div className="flex items-center gap-1">
                        <FileText className="h-4 w-4" />
                        <span>{task.workflow.name}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Building2 className="h-4 w-4" />
                        <span>{task.workflow.plant_name}</span>
                      </div>
                    </>
                  )}
                  {task.due_date && (
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      <span>{new Date(task.due_date).toLocaleDateString()}</span>
                    </div>
                  )}
                </div>
              </div>
              {task.status !== 'completed' && (
                <Button
                  onClick={() => navigate(`/workflows/${task.workflow?.id}`)}
                >
                  View Workflow
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredTasks.length === 0 && (
        <div className="text-center py-12">
          <CheckSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No tasks found</p>
        </div>
      )}
    </div>
  );
}


