import * as React from 'react';
import { cn } from '@/lib/utils';

export type CalendarProps = {
  mode?: 'single';
  selected?: Date;
  onSelect?: (date: Date | undefined) => void;
  disabled?: (date: Date) => boolean;
  initialFocus?: boolean;
  className?: string;
};

function Calendar({
  mode = 'single',
  selected,
  onSelect,
  disabled,
  className,
  ...props
}: CalendarProps) {
  // Simple calendar implementation - can be enhanced later with react-day-picker
  const [currentDate, setCurrentDate] = React.useState(selected || new Date());

  const handleDateClick = (date: Date) => {
    if (disabled && disabled(date)) return;
    setCurrentDate(date);
    onSelect?.(date);
  };

  return (
    <div className={cn('p-3', className)} {...props}>
      <div className="text-sm font-medium mb-4 text-center">
        {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
          <div key={day} className="text-xs font-medium text-center p-2">
            {day}
          </div>
        ))}
        {/* Calendar days would go here - simplified for now */}
        <div className="text-xs text-muted-foreground text-center p-2">
          Calendar view coming soon
        </div>
      </div>
    </div>
  );
}
Calendar.displayName = 'Calendar';

export { Calendar };
