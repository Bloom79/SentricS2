/**
 * Compliance Calendar View
 * Visual calendar showing all compliance deadlines, submissions, and inspections
 * BUSINESS VALUE: Prevent €25-50K penalties, improve deadline tracking
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/services/api/apiClient';
import { cn } from '@/lib/utils';

interface ComplianceEvent {
  id: number;
  title: string;
  requirement_name: string;
  due_date: string;
  type: 'deadline' | 'submission' | 'inspection' | 'renewal';
  status: 'pending' | 'in_progress' | 'completed' | 'overdue';
  priority: 'low' | 'medium' | 'high' | 'critical';
  authority: string;
  plant_name?: string;
  cer_name?: string;
}

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const STATUS_COLORS = {
  pending: 'bg-blue-100 text-blue-700 border-blue-300',
  in_progress: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  completed: 'bg-green-100 text-green-700 border-green-300',
  overdue: 'bg-red-100 text-red-700 border-red-300',
};

const PRIORITY_COLORS = {
  low: 'bg-gray-100 text-gray-700',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
};

export const ComplianceCalendar: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<'month' | 'week'>('month');

  const { data: events = [], isLoading } = useQuery<ComplianceEvent[]>({
    queryKey: ['compliance', 'calendar', currentDate.getFullYear(), currentDate.getMonth()],
    queryFn: async () => {
      const response = await apiClient.get('/compliance/calendar', {
        params: {
          year: currentDate.getFullYear(),
          month: currentDate.getMonth() + 1,
        },
      });
      return response.data.events || [];
    },
  });

  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Generate calendar days
  const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
  const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
  const startingDayOfWeek = firstDay.getDay();
  const daysInMonth = lastDay.getDate();

  const calendarDays: Array<{ date: number; month: 'prev' | 'current' | 'next'; events: ComplianceEvent[] }> = [];

  // Previous month days
  const prevMonthLastDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 0).getDate();
  for (let i = startingDayOfWeek - 1; i >= 0; i--) {
    calendarDays.push({
      date: prevMonthLastDay - i,
      month: 'prev',
      events: [],
    });
  }

  // Current month days
  for (let i = 1; i <= daysInMonth; i++) {
    const dayEvents = events.filter((event) => {
      const eventDate = new Date(event.due_date);
      return eventDate.getDate() === i &&
             eventDate.getMonth() === currentDate.getMonth() &&
             eventDate.getFullYear() === currentDate.getFullYear();
    });

    calendarDays.push({
      date: i,
      month: 'current',
      events: dayEvents,
    });
  }

  // Next month days
  const remainingDays = 42 - calendarDays.length; // 6 weeks * 7 days
  for (let i = 1; i <= remainingDays; i++) {
    calendarDays.push({
      date: i,
      month: 'next',
      events: [],
    });
  }

  // Upcoming deadlines
  const upcomingDeadlines = events
    .filter((event) => {
      const dueDate = new Date(event.due_date);
      const today = new Date();
      const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
      return dueDate >= today && dueDate <= nextWeek && event.status !== 'completed';
    })
    .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime());

  // Overdue items
  const overdueItems = events.filter((event) => event.status === 'overdue');

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Compliance Calendar</h1>
          <p className="text-muted-foreground">Track deadlines, submissions, and inspections</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={goToToday}>
            Today
          </Button>
          <Button variant="outline" onClick={goToPreviousMonth}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button variant="outline" onClick={goToNextMonth}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Alerts */}
      {overdueItems.length > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-semibold text-red-900">
                  {overdueItems.length} Overdue Compliance Item{overdueItems.length > 1 ? 's' : ''}
                </p>
                <p className="text-sm text-red-700 mt-1">
                  Immediate action required to avoid penalties
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Calendar */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>
                  {MONTHS[currentDate.getMonth()]} {currentDate.getFullYear()}
                </CardTitle>
                <div className="flex gap-2">
                  <select
                    className="border rounded px-3 py-1 text-sm"
                    value={view}
                    onChange={(e) => setView(e.target.value as 'month' | 'week')}
                  >
                    <option value="month">Month View</option>
                    <option value="week">Week View</option>
                  </select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Weekday Headers */}
              <div className="grid grid-cols-7 gap-2 mb-2">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                  <div key={day} className="text-center text-sm font-medium text-muted-foreground py-2">
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar Grid */}
              <div className="grid grid-cols-7 gap-2">
                {calendarDays.map((day, index) => {
                  const isToday =
                    day.month === 'current' &&
                    day.date === new Date().getDate() &&
                    currentDate.getMonth() === new Date().getMonth() &&
                    currentDate.getFullYear() === new Date().getFullYear();

                  return (
                    <div
                      key={index}
                      className={cn(
                        'min-h-[100px] border rounded p-2 hover:bg-gray-50 transition-colors',
                        day.month !== 'current' && 'bg-gray-50 text-muted-foreground',
                        isToday && 'border-blue-500 border-2 bg-blue-50'
                      )}
                    >
                      <div className="text-sm font-medium mb-1">{day.date}</div>
                      <div className="space-y-1">
                        {day.events.slice(0, 3).map((event) => (
                          <div
                            key={event.id}
                            className={cn(
                              'text-xs p-1 rounded border truncate cursor-pointer hover:opacity-80',
                              STATUS_COLORS[event.status]
                            )}
                            title={event.requirement_name}
                          >
                            {event.requirement_name}
                          </div>
                        ))}
                        {day.events.length > 3 && (
                          <div className="text-xs text-muted-foreground">
                            +{day.events.length - 3} more
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Upcoming Deadlines Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Upcoming (Next 7 Days)
              </CardTitle>
            </CardHeader>
            <CardContent>
              {upcomingDeadlines.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No upcoming deadlines
                </p>
              ) : (
                <div className="space-y-3">
                  {upcomingDeadlines.map((event) => (
                    <div key={event.id} className="border-l-4 border-orange-500 pl-3 py-2">
                      <div className="font-medium text-sm">{event.requirement_name}</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {new Date(event.due_date).toLocaleDateString()}
                      </div>
                      <div className="flex gap-1 mt-1">
                        <Badge variant="outline" className={`text-xs ${PRIORITY_COLORS[event.priority]}`}>
                          {event.priority}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {event.authority}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Legend */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Status Legend</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2">
                <div className={cn('w-4 h-4 rounded border', STATUS_COLORS.pending)} />
                <span className="text-sm">Pending</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={cn('w-4 h-4 rounded border', STATUS_COLORS.in_progress)} />
                <span className="text-sm">In Progress</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={cn('w-4 h-4 rounded border', STATUS_COLORS.completed)} />
                <span className="text-sm">Completed</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={cn('w-4 h-4 rounded border', STATUS_COLORS.overdue)} />
                <span className="text-sm">Overdue</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ComplianceCalendar;
