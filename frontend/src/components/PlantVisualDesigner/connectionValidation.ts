/**
 * Connection Validation Rules
 * Validates connections between different node types
 */

export type NodeType =
  | 'solar-panel'
  | 'solar-array'
  | 'wind-turbine'
  | 'inverter'
  | 'transformer'
  | 'bess'
  | 'battery'
  | 'grid'
  | 'consumer'
  | 'scada'
  | 'sensor'
  | 'default';

export interface ValidationResult {
  valid: boolean;
  message?: string;
}

const VALID_CONNECTIONS: Record<NodeType, NodeType[]> = {
  'solar-panel': ['inverter', 'transformer'],
  'solar-array': ['inverter', 'transformer'],
  'wind-turbine': ['inverter', 'transformer'],
  battery: ['inverter', 'transformer', 'grid', 'consumer'],
  bess: ['inverter', 'transformer', 'grid', 'consumer'],
  inverter: ['transformer', 'grid', 'consumer', 'battery', 'bess'],
  transformer: ['grid', 'consumer', 'battery', 'bess'],
  grid: ['consumer', 'battery', 'bess'],
  consumer: [],
  scada: ['*' as any], // Can connect to any
  sensor: ['*' as any], // Can connect to any
  default: ['*' as any], // Fallback - allow all
};

export function validateConnection(sourceType: NodeType, targetType: NodeType): ValidationResult {
  // Check if source type exists in rules
  const allowedTargets = VALID_CONNECTIONS[sourceType];

  if (!allowedTargets) {
    return {
      valid: false,
      message: `Unknown source node type: ${sourceType}`,
    };
  }

  // Check if '*' is in allowed targets (can connect to any)
  if (allowedTargets.includes('*' as any)) {
    return { valid: true };
  }

  // Check if target type is in allowed targets
  if (allowedTargets.includes(targetType)) {
    return { valid: true };
  }

  return {
    valid: false,
    message: `Cannot connect ${sourceType} to ${targetType}. Allowed targets: ${allowedTargets.join(', ')}`,
  };
}

export function getValidTargets(sourceType: NodeType): NodeType[] {
  const allowedTargets = VALID_CONNECTIONS[sourceType] || [];

  if (allowedTargets.includes('*' as any)) {
    // Return all types except the source type
    return Object.keys(VALID_CONNECTIONS).filter(
      (type) => type !== sourceType && type !== 'default'
    ) as NodeType[];
  }

  return allowedTargets as NodeType[];
}
