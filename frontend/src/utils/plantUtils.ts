/**
 * Plant utility functions for status and type mapping
 */

export function getPlantStatusLabel(status: string): string {
  const statusMap: Record<string, string> = {
    IN_OPERATION: 'In Operation',
    IN_AUTHORIZATION: 'In Authorization',
    UNDER_CONSTRUCTION: 'Under Construction',
    DECOMMISSIONED: 'Decommissioned',
    // Legacy support
    'In Operation': 'In Operation',
    'In Authorization': 'In Authorization',
    'Under Construction': 'Under Construction',
    Decommissioned: 'Decommissioned',
  };

  return statusMap[status] || status;
}

export function getPlantTypeLabel(type: string): string {
  const typeMap: Record<string, string> = {
    PHOTOVOLTAIC: 'Photovoltaic',
    WIND: 'Wind',
    HYDROELECTRIC: 'Hydroelectric',
    BIOMASS: 'Biomass',
    GEOTHERMAL: 'Geothermal',
    // Legacy support
    Photovoltaic: 'Photovoltaic',
    Wind: 'Wind',
    Hydroelectric: 'Hydroelectric',
    Biomass: 'Biomass',
    Geothermal: 'Geothermal',
  };

  return typeMap[type] || type;
}

export function getPlantStatusVariant(
  status: string
): 'default' | 'secondary' | 'destructive' | 'outline' {
  const normalizedStatus = status.toUpperCase();

  if (normalizedStatus === 'IN_OPERATION' || normalizedStatus === 'IN OPERATION') {
    return 'default';
  }

  if (normalizedStatus === 'DECOMMISSIONED' || normalizedStatus === 'DECOMMISSIONED') {
    return 'destructive';
  }

  if (normalizedStatus === 'UNDER_CONSTRUCTION' || normalizedStatus === 'UNDER CONSTRUCTION') {
    return 'outline';
  }

  return 'secondary';
}

export function isPlantOperational(status: string): boolean {
  const normalizedStatus = status.toUpperCase();
  return normalizedStatus === 'IN_OPERATION' || normalizedStatus === 'IN OPERATION';
}
