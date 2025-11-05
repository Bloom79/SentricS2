/**
 * Visual Designer Tab Component
 * React Flow canvas for plant layout design
 */

import React, { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactFlowProvider, ReactFlow, Controls, Background, useReactFlow } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Save, Edit, Eye, Download, Upload, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/services/api/apiClient';
import {
  Node,
  Edge,
  Connection,
  applyNodeChanges,
  applyEdgeChanges,
  NodeChange,
  EdgeChange,
} from '@xyflow/react';
import { nodeTypes, FlowNodeData } from './FlowNodeTypes';
import { ComponentsPalette, PaletteComponent } from './ComponentsPalette';
import { NodePropertiesSidebar } from './NodePropertiesSidebar';
import { EdgeConfigDialog } from './EdgeConfigDialog';
import { validateConnection } from './connectionValidation';
import { useToast } from '@/components/ui/use-toast';

interface VisualDesignerTabProps {
  plantId: number;
}

interface PlantLayout {
  id: number;
  plant_id: number;
  nodes: Node[];
  edges: Edge[];
  version: number;
  is_active: boolean;
}

function FlowCanvas({ plantId }: { plantId: number }) {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);
  const queryClient = useQueryClient();
  const { fitView, screenToFlowPosition } = useReactFlow();
  const [draggedComponent, setDraggedComponent] = useState<PaletteComponent | null>(null);
  const { toast } = useToast();

  // Load layout
  const { data: layout, isLoading } = useQuery<PlantLayout | null>({
    queryKey: ['plant-layout', plantId],
    queryFn: async () => {
      try {
        const response = await apiClient.get(`/plants/${plantId}/layout`);
        return response.data;
      } catch (error: any) {
        if (error.response?.status === 404) {
          return null;
        }
        throw error;
      }
    },
  });

  // Initialize nodes/edges from layout
  React.useEffect(() => {
    if (layout) {
      setNodes(layout.nodes || []);
      setEdges(layout.edges || []);
    } else {
      setNodes([]);
      setEdges([]);
    }
    // Clear selections when layout changes
    setSelectedNode(null);
    setSelectedEdge(null);
  }, [layout]);

  // Save layout mutation
  const saveMutation = useMutation({
    mutationFn: async (data: { nodes: Node[]; edges: Edge[] }) => {
      const response = await apiClient.post(`/plants/${plantId}/layout`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plant-layout', plantId] });
    },
  });

  // Generate from assets mutation
  const generateMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post(`/plants/${plantId}/layout/generate-from-assets`);
      return response.data;
    },
    onSuccess: (data) => {
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
      queryClient.invalidateQueries({ queryKey: ['plant-layout', plantId] });
      setTimeout(() => fitView(), 100);
    },
  });

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      if (isEditMode) {
        setNodes((nds) => applyNodeChanges(changes, nds));
      }
    },
    [isEditMode]
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      if (isEditMode) {
        setEdges((eds) => applyEdgeChanges(changes, eds));
      }
    },
    [isEditMode]
  );

  const onConnect = useCallback(
    (params: Connection) => {
      if (!isEditMode || !params.source || !params.target) return;

      // Find source and target nodes
      const sourceNode = nodes.find((n) => n.id === params.source);
      const targetNode = nodes.find((n) => n.id === params.target);

      if (!sourceNode || !targetNode) return;

      // Validate connection
      const validation = validateConnection(
        (sourceNode.type || 'default') as any,
        (targetNode.type || 'default') as any
      );

      if (!validation.valid) {
        toast({
          title: 'Invalid Connection',
          description: validation.message || 'Cannot create this connection',
          variant: 'destructive',
        });
        return;
      }

      // Create edge
      const newEdge: Edge = {
        ...params,
        id: `edge-${Date.now()}`,
        animated: false,
        data: {},
      };

      setEdges((eds) => [...eds, newEdge]);
    },
    [isEditMode, nodes, toast]
  );

  const handleNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      if (isEditMode) {
        setSelectedNode(node);
        setSelectedEdge(null);
      }
    },
    [isEditMode]
  );

  const handleEdgeClick = useCallback(
    (event: React.MouseEvent, edge: Edge) => {
      if (isEditMode) {
        setSelectedEdge(edge);
        setSelectedNode(null);
      }
    },
    [isEditMode]
  );

  const handleNodeUpdate = useCallback((nodeId: string, data: Partial<FlowNodeData>) => {
    setNodes((nds) =>
      nds.map((node) => (node.id === nodeId ? { ...node, data: { ...node.data, ...data } } : node))
    );
    setSelectedNode(null);
  }, []);

  const handleNodeDelete = useCallback((nodeId: string) => {
    setNodes((nds) => nds.filter((node) => node.id !== nodeId));
    setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId));
  }, []);

  const handleEdgeUpdate = useCallback((edgeId: string, data: Partial<Edge>) => {
    setEdges((eds) => eds.map((edge) => (edge.id === edgeId ? { ...edge, ...data } : edge)));
    setSelectedEdge(null);
  }, []);

  const handleEdgeDelete = useCallback((edgeId: string) => {
    setEdges((eds) => eds.filter((edge) => edge.id !== edgeId));
  }, []);

  const handleDragStart = useCallback((component: PaletteComponent, event: React.DragEvent) => {
    setDraggedComponent(component);
    event.dataTransfer.setData('application/reactflow', component.type);
    event.dataTransfer.effectAllowed = 'move';
  }, []);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      if (!draggedComponent) return;

      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode: Node = {
        id: `${draggedComponent.type}-${Date.now()}`,
        type: draggedComponent.type,
        position,
        data: {
          id: `${draggedComponent.type}-${Date.now()}`,
          label: draggedComponent.label,
          type: draggedComponent.type,
          specs: {},
          status: 'active',
        },
        draggable: true,
        connectable: true,
      };

      setNodes((nds) => [...nds, newNode]);
      setDraggedComponent(null);
    },
    [draggedComponent, screenToFlowPosition]
  );

  const handleSave = useCallback(() => {
    // Validate before saving
    const hasInvalidConnections = edges.some((edge) => {
      const sourceNode = nodes.find((n) => n.id === edge.source);
      const targetNode = nodes.find((n) => n.id === edge.target);
      if (!sourceNode || !targetNode) return true;

      const validation = validateConnection(
        (sourceNode.type || 'default') as any,
        (targetNode.type || 'default') as any
      );
      return !validation.valid;
    });

    if (hasInvalidConnections) {
      toast({
        title: 'Validation Error',
        description: 'Some connections are invalid. Please fix them before saving.',
        variant: 'destructive',
      });
      return;
    }

    saveMutation.mutate({ nodes, edges });
    toast({
      title: 'Layout Saved',
      description: 'Plant layout has been saved successfully.',
    });
  }, [nodes, edges, saveMutation, toast]);

  const handleGenerate = useCallback(() => {
    if (
      window.confirm('Generate layout from existing assets? This will replace the current layout.')
    ) {
      generateMutation.mutate();
    }
  }, [generateMutation]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <Button
            variant={isEditMode ? 'default' : 'outline'}
            size="sm"
            onClick={() => setIsEditMode(!isEditMode)}
          >
            {isEditMode ? (
              <>
                <Eye className="mr-2 h-4 w-4" />
                View Mode
              </>
            ) : (
              <>
                <Edit className="mr-2 h-4 w-4" />
                Edit Mode
              </>
            )}
          </Button>
          {isEditMode && (
            <>
              <Button size="sm" onClick={handleSave} disabled={saveMutation.isPending}>
                <Save className="mr-2 h-4 w-4" />
                Save Layout
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleGenerate}
                disabled={generateMutation.isPending}
              >
                <RotateCcw className="mr-2 h-4 w-4" />
                Generate from Assets
              </Button>
            </>
          )}
        </div>
        <div className="text-sm text-muted-foreground">
          {nodes.length} nodes, {edges.length} edges
        </div>
      </div>

      {/* Canvas */}
      <Card>
        <CardContent className="p-0 relative">
          {isEditMode && (
            <div className="absolute left-4 top-4 z-10">
              <ComponentsPalette onDragStart={handleDragStart} isEditMode={isEditMode} />
            </div>
          )}
          <div className="relative">
            <div className="h-[600px] w-full">
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                onNodeClick={handleNodeClick}
                onEdgeClick={handleEdgeClick}
                onDragOver={onDragOver}
                onDrop={onDrop}
                nodeTypes={nodeTypes}
                nodesDraggable={isEditMode}
                nodesConnectable={isEditMode}
                elementsSelectable={isEditMode}
                deleteKeyCode={isEditMode ? 'Delete' : null}
                fitView
              >
                <Background />
                <Controls />
              </ReactFlow>
            </div>
            {selectedNode && isEditMode && (
              <div className="absolute right-4 top-4 z-10">
                <NodePropertiesSidebar
                  node={selectedNode}
                  onClose={() => setSelectedNode(null)}
                  onUpdate={handleNodeUpdate}
                  onDelete={handleNodeDelete}
                />
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Edge Configuration Dialog */}
      {selectedEdge && (
        <EdgeConfigDialog
          open={!!selectedEdge}
          onClose={() => setSelectedEdge(null)}
          edge={selectedEdge}
          onUpdate={handleEdgeUpdate}
          onDelete={handleEdgeDelete}
        />
      )}

      {!layout && (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground mb-4">No layout configured for this plant</p>
            <div className="flex gap-2 justify-center">
              <Button onClick={() => setIsEditMode(true)}>
                <Edit className="mr-2 h-4 w-4" />
                Start Designing
              </Button>
              <Button variant="outline" onClick={handleGenerate}>
                <RotateCcw className="mr-2 h-4 w-4" />
                Generate from Assets
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export function VisualDesignerTab({ plantId }: VisualDesignerTabProps) {
  return (
    <ReactFlowProvider>
      <FlowCanvas plantId={plantId} />
    </ReactFlowProvider>
  );
}
