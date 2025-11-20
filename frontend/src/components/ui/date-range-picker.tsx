/**
 * Date Range Picker Component
 * Allows users to select custom date ranges for filtering data
 */
import React, { useState } from 'react';
import { Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';

export interface DateRange {
  from: Date | undefined;
  to: Date | undefined;
}

interface DateRangePickerProps {
  value?: DateRange;
  onChange?: (range: DateRange) => void;
  className?: string;
  presets?: boolean;
}

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  value,
  onChange,
  className,
  presets = true,
}) => {
  const [open, setOpen] = useState(false);
  const [localRange, setLocalRange] = useState<DateRange>(
    value || { from: undefined, to: undefined }
  );

  const formatDateRange = () => {
    if (!localRange.from) {
      return 'Select date range';
    }
    if (!localRange.to) {
      return localRange.from.toLocaleDateString();
    }
    return `${localRange.from.toLocaleDateString()} - ${localRange.to.toLocaleDateString()}`;
  };

  const applyPreset = (preset: string) => {
    const today = new Date();
    const from = new Date();
    let to = new Date();

    switch (preset) {
      case 'today':
        from.setHours(0, 0, 0, 0);
        to = new Date(from);
        break;
      case 'yesterday':
        from.setDate(today.getDate() - 1);
        from.setHours(0, 0, 0, 0);
        to = new Date(from);
        break;
      case 'last7days':
        from.setDate(today.getDate() - 7);
        from.setHours(0, 0, 0, 0);
        break;
      case 'last30days':
        from.setDate(today.getDate() - 30);
        from.setHours(0, 0, 0, 0);
        break;
      case 'last90days':
        from.setDate(today.getDate() - 90);
        from.setHours(0, 0, 0, 0);
        break;
      case 'thisMonth':
        from.setDate(1);
        from.setHours(0, 0, 0, 0);
        break;
      case 'lastMonth':
        from.setMonth(today.getMonth() - 1);
        from.setDate(1);
        from.setHours(0, 0, 0, 0);
        to = new Date(today.getFullYear(), today.getMonth(), 0);
        break;
      case 'thisYear':
        from.setMonth(0);
        from.setDate(1);
        from.setHours(0, 0, 0, 0);
        break;
      default:
        return;
    }

    const newRange = { from, to };
    setLocalRange(newRange);
    onChange?.(newRange);
    setOpen(false);
  };

  const handleApply = () => {
    onChange?.(localRange);
    setOpen(false);
  };

  const handleClear = () => {
    const clearedRange = { from: undefined, to: undefined };
    setLocalRange(clearedRange);
    onChange?.(clearedRange);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            'justify-start text-left font-normal',
            !localRange.from && 'text-muted-foreground',
            className
          )}
        >
          <Calendar className="mr-2 h-4 w-4" />
          {formatDateRange()}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <div className="p-4 space-y-4">
          {presets && (
            <div className="space-y-2">
              <p className="text-sm font-medium">Quick Select</p>
              <div className="grid grid-cols-2 gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => applyPreset('today')}
                >
                  Today
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => applyPreset('yesterday')}
                >
                  Yesterday
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => applyPreset('last7days')}
                >
                  Last 7 days
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => applyPreset('last30days')}
                >
                  Last 30 days
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => applyPreset('thisMonth')}
                >
                  This Month
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => applyPreset('lastMonth')}
                >
                  Last Month
                </Button>
              </div>
            </div>
          )}

          <div className="space-y-2">
            <p className="text-sm font-medium">Custom Range</p>
            <div className="space-y-2">
              <div>
                <label className="text-xs text-muted-foreground">From</label>
                <input
                  type="date"
                  className="w-full border rounded px-3 py-2 text-sm"
                  value={
                    localRange.from
                      ? localRange.from.toISOString().split('T')[0]
                      : ''
                  }
                  onChange={(e) => {
                    const date = e.target.value ? new Date(e.target.value) : undefined;
                    setLocalRange({ ...localRange, from: date });
                  }}
                />
              </div>
              <div>
                <label className="text-xs text-muted-foreground">To</label>
                <input
                  type="date"
                  className="w-full border rounded px-3 py-2 text-sm"
                  value={
                    localRange.to
                      ? localRange.to.toISOString().split('T')[0]
                      : ''
                  }
                  onChange={(e) => {
                    const date = e.target.value ? new Date(e.target.value) : undefined;
                    setLocalRange({ ...localRange, to: date });
                  }}
                  min={
                    localRange.from
                      ? localRange.from.toISOString().split('T')[0]
                      : undefined
                  }
                />
              </div>
            </div>
          </div>

          <div className="flex justify-between gap-2">
            <Button variant="ghost" size="sm" onClick={handleClear}>
              Clear
            </Button>
            <Button size="sm" onClick={handleApply}>
              Apply
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
};
