import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value)
}

// Función para formatear fechas con zona horaria local (UTC+2 para España/Andorra)
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Europe/Madrid' // UTC+2 para España/Andorra
  });
}

// Función para formatear fecha y hora actual con zona horaria local
export function formatCurrentDateTime(): string {
  return new Date().toLocaleString('es-ES', {
    timeZone: 'Europe/Madrid' // UTC+2 para España/Andorra
  });
}

// Función para formatear solo fecha (sin hora) con zona horaria local
export function formatDateOnly(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    timeZone: 'Europe/Madrid' // UTC+2 para España/Andorra
  });
}
