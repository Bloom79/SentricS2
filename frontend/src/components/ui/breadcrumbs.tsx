/**
 * Breadcrumbs Navigation Component
 * Provides contextual navigation and current location
 */
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
  className?: string;
  showHome?: boolean;
  separator?: React.ReactNode;
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({
  items,
  className,
  showHome = true,
  separator = <ChevronRight className="h-4 w-4" />,
}) => {
  const location = useLocation();

  // Auto-generate breadcrumbs from path if not provided
  const breadcrumbItems = items || generateBreadcrumbsFromPath(location.pathname);

  // Add home item if requested
  const allItems: BreadcrumbItem[] = showHome
    ? [{ label: 'Home', href: '/', icon: <Home className="h-4 w-4" /> }, ...breadcrumbItems]
    : breadcrumbItems;

  if (allItems.length === 0) {
    return null;
  }

  return (
    <nav
      aria-label="Breadcrumb"
      className={cn('flex items-center space-x-1 text-sm text-muted-foreground', className)}
    >
      {allItems.map((item, index) => {
        const isLast = index === allItems.length - 1;

        return (
          <React.Fragment key={`breadcrumb-${index}`}>
            {index > 0 && (
              <span className="text-muted-foreground/50">{separator}</span>
            )}
            {isLast ? (
              <span className="font-medium text-foreground flex items-center gap-1">
                {item.icon}
                {item.label}
              </span>
            ) : item.href ? (
              <Link
                to={item.href}
                className="hover:text-foreground transition-colors flex items-center gap-1"
              >
                {item.icon}
                {item.label}
              </Link>
            ) : (
              <span className="flex items-center gap-1">
                {item.icon}
                {item.label}
              </span>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};

// Auto-generate breadcrumbs from URL path
function generateBreadcrumbsFromPath(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean);

  if (segments.length === 0) {
    return [];
  }

  const breadcrumbs: BreadcrumbItem[] = [];
  let currentPath = '';

  segments.forEach((segment, index) => {
    currentPath += `/${segment}`;

    // Don't link the last segment (current page)
    const isLast = index === segments.length - 1;

    // Format label (remove IDs, capitalize, etc.)
    const label = formatSegmentLabel(segment);

    breadcrumbs.push({
      label,
      href: isLast ? undefined : currentPath,
    });
  });

  return breadcrumbs;
}

// Format path segment into readable label
function formatSegmentLabel(segment: string): string {
  // If it's a number (ID), return as is
  if (/^\d+$/.test(segment)) {
    return `#${segment}`;
  }

  // Convert kebab-case and snake_case to Title Case
  return segment
    .replace(/[-_]/g, ' ')
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Hook for programmatic breadcrumb control
export const useBreadcrumbs = (items: BreadcrumbItem[]) => {
  return { items };
};
