/**
 * Agenda Page
 * Calendar and deadline management
 */

import React, { useState } from 'react';
import {
  Calendar,
  Clock,
  AlertCircle,
  CheckCircle,
  Filter,
  ChevronLeft,
  ChevronRight,
  Plus,
  FileText,
  Euro,
  Shield,
  Activity,
  Link2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Deadline {
  id: string;
  title: string;
  description: string;
  date: string;
  type: 'Declaration' | 'Payment' | 'Communication' | 'Verification' | 'Deadline' | 'Meeting';
  entity: 'Customs' | 'GSE' | 'Terna' | 'DSO' | 'Internal';
  priority: 'High' | 'Medium' | 'Low';
  status: 'Completed' | 'In Progress' | 'Planned' | 'Delayed';
  plant?: string;
}

export default function Agenda() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<'month' | 'list'>('month');
  const [filterEntity, setFilterEntity] = useState<string>('all');

  const deadlines: Deadline[] = [
    {
      id: '1',
      title: 'Dichiarazione Annuale Dogane',
      description: 'Invio dichiarazione annuale consumo energia elettrica',
      date: '2024-03-31',
      type: 'Declaration',
      entity: 'Customs',
      priority: 'High',
      status: 'In Progress',
      plant: 'Solare Verdi 1',
    },
    {
      id: '2',
      title: 'Pagamento Diritto Annuale',
      description: 'Versamento diritto annuale licenza officina elettrica',
      date: '2024-12-16',
      type: 'Payment',
      entity: 'Customs',
      priority: 'High',
      status: 'Planned',
    },
    {
      id: '3',
      title: 'Comunicazione Fine Lavori',
      description: 'Invio comunicazione fine lavori a E-Distribuzione',
      date: '2024-03-20',
      type: 'Communication',
      entity: 'DSO',
      priority: 'Medium',
      status: 'Completed',
      plant: 'Solare Verdi 2',
    },
  ];

  const getEntityColor = (entity: string) => {
    switch (entity) {
      case 'Customs':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'GSE':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'Terna':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'DSO':
        return 'bg-purple-100 text-purple-800 border-purple-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const filteredDeadlines = deadlines.filter(d =>
    filterEntity === 'all' || d.entity === filterEntity
  );

  const stats = {
    total: filteredDeadlines.length,
    completed: filteredDeadlines.filter(d => d.status === 'Completed').length,
    inProgress: filteredDeadlines.filter(d => d.status === 'In Progress').length,
    planned: filteredDeadlines.filter(d => d.status === 'Planned').length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Agenda & Deadlines</h1>
          <p className="text-muted-foreground mt-1">
            Manage all regulatory and administrative deadlines
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Deadline
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total</p>
              <p className="text-2xl font-bold">{stats.total}</p>
            </div>
            <Calendar className="h-8 w-8 text-primary opacity-20" />
          </div>
        </div>
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Completed</p>
              <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-600 opacity-20" />
          </div>
        </div>
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">In Progress</p>
              <p className="text-2xl font-bold text-blue-600">{stats.inProgress}</p>
            </div>
            <Clock className="h-8 w-8 text-blue-600 opacity-20" />
          </div>
        </div>
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Planned</p>
              <p className="text-2xl font-bold">{stats.planned}</p>
            </div>
            <Calendar className="h-8 w-8 text-primary opacity-20" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4 items-center">
        <select
          value={filterEntity}
          onChange={(e) => setFilterEntity(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="all">All Entities</option>
          <option value="Customs">Customs</option>
          <option value="GSE">GSE</option>
          <option value="Terna">Terna</option>
          <option value="DSO">DSO</option>
          <option value="Internal">Internal</option>
        </select>
        <div className="flex gap-2">
          <Button
            variant={view === 'month' ? 'default' : 'outline'}
            onClick={() => setView('month')}
          >
            Month
          </Button>
          <Button
            variant={view === 'list' ? 'default' : 'outline'}
            onClick={() => setView('list')}
          >
            List
          </Button>
        </div>
      </div>

      {/* Calendar View */}
      {view === 'month' && (
        <div className="border rounded-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">
              {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </h2>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={() => setCurrentDate(new Date())}>
                Today
              </Button>
              <Button variant="outline" size="sm">
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="text-center text-muted-foreground py-12">
            Calendar view coming soon - showing list view
          </div>
        </div>
      )}

      {/* List View */}
      {view === 'list' && (
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium">Deadline</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Date</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Entity</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-6 py-3 text-right text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredDeadlines.map((deadline) => (
                <tr key={deadline.id} className="hover:bg-muted/50">
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium">{deadline.title}</p>
                      <p className="text-sm text-muted-foreground">{deadline.description}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    {new Date(deadline.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs border ${getEntityColor(deadline.entity)}`}>
                      {deadline.entity}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-2 py-1 rounded text-sm ${
                        deadline.status === 'Completed'
                          ? 'bg-green-100 text-green-800'
                          : deadline.status === 'In Progress'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {deadline.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Button variant="ghost" size="sm">View</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}


