/**
 * Bulk Import Dialog
 * Import panels from CSV file
 */

import React, { useState, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Upload, Download, X, CheckCircle, AlertCircle, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { apiClient } from '@/services/api/apiClient';
import { useToast } from '@/components/ui/use-toast';

interface BulkImportDialogProps {
  open: boolean;
  onClose: () => void;
  plantId: number;
  arrayId?: number;
}

interface ImportResult {
  success: number;
  failed: number;
  errors: string[];
  imported_panels: Array<{
    id: number;
    name: string;
    string_number?: number;
  }>;
}

export function BulkImportDialog({ open, onClose, plantId, arrayId }: BulkImportDialogProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [csvContent, setCsvContent] = useState('');
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [hasHeader, setHasHeader] = useState(true);
  const [isImporting, setIsImporting] = useState(false);

  // Import mutation
  const importMutation = useMutation({
    mutationFn: async (data: { csv_content: string; has_header: boolean }) => {
      const params = arrayId ? `?array_id=${arrayId}` : '';
      const response = await apiClient.post(
        `/assets/plants/${plantId}/assets/bulk-import${params}`,
        data
      );
      return response.data as ImportResult;
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['plant-assets', plantId] });
      queryClient.invalidateQueries({ queryKey: ['array-strings', arrayId] });
      
      toast({
        title: 'Import Completed',
        description: `Successfully imported ${result.success} panels. ${result.failed} failed.`,
        variant: result.failed > 0 ? 'destructive' : 'default',
      });

      if (result.errors.length > 0) {
        console.error('Import errors:', result.errors);
      }

      setIsImporting(false);
      onClose();
    },
    onError: (error: any) => {
      toast({
        title: 'Import Failed',
        description: error.response?.data?.detail || 'Failed to import panels',
        variant: 'destructive',
      });
      setIsImporting(false);
    },
  });

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setCsvContent(content);
      parsePreview(content);
    };
    reader.readAsText(file);
  }, []);

  const parsePreview = (content: string) => {
    const lines = content.split('\n').filter((line) => line.trim());
    const preview = lines.slice(0, 10); // First 10 lines
    setPreviewData(preview.map((line, idx) => ({ line: idx + 1, content: line })));
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await apiClient.get(`/assets/plants/${plantId}/assets/bulk-import/template`, {
        responseType: 'blob',
      });
      
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'panel_import_template.csv';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to download template',
        variant: 'destructive',
      });
    }
  };

  const handleImport = () => {
    if (!csvContent.trim()) {
      toast({
        title: 'Error',
        description: 'Please upload a CSV file',
        variant: 'destructive',
      });
      return;
    }

    setIsImporting(true);
    importMutation.mutate({
      csv_content: csvContent,
      has_header: hasHeader,
    });
  };

  const handlePaste = (event: React.ClipboardEvent<HTMLTextAreaElement>) => {
    const content = event.clipboardData.getData('text');
    setCsvContent(content);
    parsePreview(content);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Bulk Import Panels
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Instructions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Instructions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>1. Download the CSV template to see the required format</p>
              <p>2. Fill in your panel data following the template</p>
              <p>3. Upload the CSV file or paste the content below</p>
              {arrayId && (
                <p className="text-primary font-medium">
                  4. Include string_number column to assign panels to strings automatically
                </p>
              )}
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleDownloadTemplate}>
              <Download className="mr-2 h-4 w-4" />
              Download Template
            </Button>
            <label className="cursor-pointer">
              <Button variant="outline" asChild>
                <span>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload CSV File
                </span>
              </Button>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
          </div>

          {/* Options */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="hasHeader"
              checked={hasHeader}
              onChange={(e) => setHasHeader(e.target.checked)}
              className="rounded"
            />
            <label htmlFor="hasHeader" className="text-sm">
              CSV file has header row
            </label>
          </div>

          {/* CSV Content Editor */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">CSV Content</CardTitle>
            </CardHeader>
            <CardContent>
              <textarea
                value={csvContent}
                onChange={(e) => {
                  setCsvContent(e.target.value);
                  parsePreview(e.target.value);
                }}
                onPaste={handlePaste}
                placeholder="Paste CSV content here or upload a file..."
                className="w-full h-48 p-2 border rounded font-mono text-sm"
              />
            </CardContent>
          </Card>

          {/* Preview */}
          {previewData.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Preview (First 10 rows)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm border-collapse">
                    <thead>
                      {hasHeader && previewData.length > 0 && (
                        <tr className="border-b">
                          {previewData[0].content.split(',').map((cell: string, idx: number) => (
                            <th key={idx} className="text-left p-2 border-r">
                              {cell.trim()}
                            </th>
                          ))}
                        </tr>
                      )}
                    </thead>
                    <tbody>
                      {previewData.slice(hasHeader ? 1 : 0).map((row, idx) => (
                        <tr key={idx} className="border-b">
                          {row.content.split(',').map((cell: string, cellIdx: number) => (
                            <td key={cellIdx} className="p-2 border-r">
                              {cell.trim()}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Import Results */}
          {importMutation.data && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Import Results</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="font-medium">Success: {importMutation.data.success} panels</span>
                </div>
                {importMutation.data.failed > 0 && (
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-red-500" />
                    <span className="font-medium">Failed: {importMutation.data.failed} panels</span>
                  </div>
                )}
                {importMutation.data.errors.length > 0 && (
                  <div className="mt-2 p-2 bg-red-50 rounded text-sm">
                    <p className="font-semibold mb-1">Errors:</p>
                    <ul className="list-disc list-inside space-y-1">
                      {importMutation.data.errors.slice(0, 10).map((error, idx) => (
                        <li key={idx} className="text-red-700">{error}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose} disabled={isImporting}>
              Cancel
            </Button>
            <Button onClick={handleImport} disabled={isImporting || !csvContent.trim()}>
              {isImporting ? 'Importing...' : 'Import Panels'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

