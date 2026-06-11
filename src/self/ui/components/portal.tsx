import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';

export interface PortalProps {
  children: React.ReactNode;
  container?: Element | null;
}

export function Portal({ children, container }: PortalProps) {
  const mountRef = useRef<Element | null>(null);

  useEffect(() => {
    mountRef.current = container ?? document.body;
  }, [container]);

  if (!mountRef.current && typeof document !== 'undefined') {
    mountRef.current = document.body;
  }

  return mountRef.current ? createPortal(children, mountRef.current) : null;
}
