import React from 'react';
import { Portal } from './portal';

export interface PortalManagerProps {
  children: React.ReactNode;
}

export function PortalManager({ children }: PortalManagerProps) {
  return <>{children}</>;
}

PortalManager.displayName = 'PortalManager';
