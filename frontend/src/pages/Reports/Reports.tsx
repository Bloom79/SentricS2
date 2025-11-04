/**
 * Reports Page
 * Analytics, reports, and data exports
 */

import { useState } from 'react';
import { FileBarChart, Download, Filter, Calendar, TrendingUp, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function Reports() {
  const [selectedReport, setSelectedReport] = useState<string | null>(null);

  const reportTemplates = [
    {
      id: 'plant-performance',
      name: 'Plant Performance Report',
      description: 'Production metrics and efficiency analysis',
      icon: TrendingUp,
    },
    {
      id: 'compliance-status',
      name: 'Compliance Status Report',
      description: 'Regulatory compliance overview',
      icon: FileBarChart,
    },
    {
      id: 'financial-summary',
      name: 'Financial Summary',
      description: 'Revenue, costs, and profitability analysis',
      icon: BarChart3,
    },
    {
      id: 'maintenance-report',
      name: 'Maintenance Report',
      description: 'Maintenance activities and costs',
      icon: Calendar,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reports & Analytics</h1>
          <p className="text-muted-foreground mt-1">
            Generate custom reports and advanced analytics
          </p>
        </div>
        <Button>
          <Download className="mr-2 h-4 w-4" />
          Export All
        </Button>
      </div>

      {/* Report Templates */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {reportTemplates.map((report) => {
          const Icon = report.icon;
          return (
            <div
              key={report.id}
              className="border rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelectedReport(report.id)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="p-3 bg-primary/10 rounded-lg">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
              </div>
              <h3 className="font-semibold text-lg mb-2">{report.name}</h3>
              <p className="text-sm text-muted-foreground mb-4">
                {report.description}
              </p>
              <Button variant="outline" className="w-full">
                Generate Report
              </Button>
            </div>
          );
        })}
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">Total Reports</p>
          <p className="text-2xl font-bold">24</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">This Month</p>
          <p className="text-2xl font-bold">8</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">Scheduled</p>
          <p className="text-2xl font-bold">5</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">Exported</p>
          <p className="text-2xl font-bold">156</p>
        </div>
      </div>
    </div>
  );
}


