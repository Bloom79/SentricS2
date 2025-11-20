/**
 * Global Search Component
 * Search across all modules with keyboard shortcut (Cmd/Ctrl + K)
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Search,
  FileText,
  Building2,
  Wrench,
  Users,
  ClipboardList,
  FileCheck,
  X,
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/services/api/apiClient';
import { cn } from '@/lib/utils';

interface SearchResult {
  id: string | number;
  type: 'plant' | 'cer' | 'asset' | 'workflow' | 'document' | 'compliance';
  title: string;
  subtitle?: string;
  status?: string;
  url: string;
}

const MODULE_ICONS = {
  plant: Building2,
  cer: Users,
  asset: Wrench,
  workflow: ClipboardList,
  document: FileText,
  compliance: FileCheck,
};

const MODULE_COLORS = {
  plant: 'bg-blue-100 text-blue-700',
  cer: 'bg-green-100 text-green-700',
  asset: 'bg-purple-100 text-purple-700',
  workflow: 'bg-orange-100 text-orange-700',
  document: 'bg-gray-100 text-gray-700',
  compliance: 'bg-red-100 text-red-700',
};

interface GlobalSearchProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export const GlobalSearch: React.FC<GlobalSearchProps> = ({
  open: controlledOpen,
  onOpenChange,
}) => {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const navigate = useNavigate();

  const isControlled = controlledOpen !== undefined;
  const isOpen = isControlled ? controlledOpen : open;

  const handleOpenChange = (newOpen: boolean) => {
    if (isControlled) {
      onOpenChange?.(newOpen);
    } else {
      setOpen(newOpen);
    }
    if (!newOpen) {
      setQuery('');
      setSelectedIndex(0);
    }
  };

  // Global keyboard shortcut (Cmd/Ctrl + K)
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        handleOpenChange(!isOpen);
      }
      if (e.key === 'Escape' && isOpen) {
        handleOpenChange(false);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, [isOpen]);

  // Search API call
  const { data: results = [], isLoading } = useQuery<SearchResult[]>({
    queryKey: ['global-search', query],
    queryFn: async () => {
      if (!query || query.length < 2) {
        return [];
      }

      const response = await apiClient.get('/search/global', {
        params: { q: query, limit: 20 },
      });
      return response.data.results || [];
    },
    enabled: query.length >= 2 && isOpen,
    staleTime: 30000, // 30 seconds
  });

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter' && results[selectedIndex]) {
        e.preventDefault();
        handleSelect(results[selectedIndex]);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, results]);

  const handleSelect = (result: SearchResult) => {
    navigate(result.url);
    handleOpenChange(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-2xl max-h-[600px] p-0">
        <DialogHeader className="px-4 pt-4 pb-0">
          <DialogTitle className="sr-only">Global Search</DialogTitle>
        </DialogHeader>

        <div className="flex items-center border-b px-4 py-2">
          <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
          <Input
            placeholder="Search plants, CERs, assets, workflows, documents..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            className="flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-none border-0 focus-visible:ring-0 focus-visible:ring-offset-0"
            autoFocus
          />
          {query && (
            <button
              onClick={() => setQuery('')}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        <div className="max-h-[400px] overflow-y-auto p-2">
          {isLoading ? (
            <div className="p-8 text-center text-sm text-muted-foreground">
              Searching...
            </div>
          ) : query.length < 2 ? (
            <div className="p-8 text-center">
              <p className="text-sm text-muted-foreground mb-2">
                Start typing to search across all modules
              </p>
              <div className="flex flex-wrap justify-center gap-2 mt-4">
                <Badge variant="outline" className="text-xs">
                  <Building2 className="h-3 w-3 mr-1" />
                  Plants
                </Badge>
                <Badge variant="outline" className="text-xs">
                  <Users className="h-3 w-3 mr-1" />
                  CER Communities
                </Badge>
                <Badge variant="outline" className="text-xs">
                  <Wrench className="h-3 w-3 mr-1" />
                  Assets
                </Badge>
                <Badge variant="outline" className="text-xs">
                  <ClipboardList className="h-3 w-3 mr-1" />
                  Workflows
                </Badge>
                <Badge variant="outline" className="text-xs">
                  <FileText className="h-3 w-3 mr-1" />
                  Documents
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-4">
                Tip: Press <kbd className="px-2 py-1 bg-gray-100 rounded">⌘K</kbd> or{' '}
                <kbd className="px-2 py-1 bg-gray-100 rounded">Ctrl+K</kbd> to open search
              </p>
            </div>
          ) : results.length === 0 ? (
            <div className="p-8 text-center text-sm text-muted-foreground">
              No results found for "{query}"
            </div>
          ) : (
            <div className="space-y-1">
              {results.map((result, index) => {
                const Icon = MODULE_ICONS[result.type];
                const colorClass = MODULE_COLORS[result.type];

                return (
                  <button
                    key={`${result.type}-${result.id}`}
                    onClick={() => handleSelect(result)}
                    className={cn(
                      'w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-gray-100 transition-colors text-left',
                      index === selectedIndex && 'bg-gray-100'
                    )}
                  >
                    <div className={cn('p-2 rounded', colorClass)}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">
                        {result.title}
                      </div>
                      {result.subtitle && (
                        <div className="text-xs text-muted-foreground truncate">
                          {result.subtitle}
                        </div>
                      )}
                    </div>
                    {result.status && (
                      <Badge variant="outline" className="text-xs">
                        {result.status}
                      </Badge>
                    )}
                    <Badge variant="secondary" className="text-xs capitalize">
                      {result.type}
                    </Badge>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        <div className="border-t px-4 py-2 text-xs text-muted-foreground flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span>
              <kbd className="px-2 py-1 bg-gray-100 rounded">↑↓</kbd> Navigate
            </span>
            <span>
              <kbd className="px-2 py-1 bg-gray-100 rounded">↵</kbd> Select
            </span>
            <span>
              <kbd className="px-2 py-1 bg-gray-100 rounded">Esc</kbd> Close
            </span>
          </div>
          {results.length > 0 && (
            <span>{results.length} results</span>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Hook for easy access
export const useGlobalSearch = () => {
  const [open, setOpen] = useState(false);

  return {
    open,
    setOpen,
    openSearch: () => setOpen(true),
    closeSearch: () => setOpen(false),
  };
};
