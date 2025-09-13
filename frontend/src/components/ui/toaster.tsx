import { useState, useEffect } from 'react'

export interface Toast {
  id: string;
  title?: string;
  description: string;
  variant: 'default' | 'destructive';
  duration?: number;
}

let toasts: Toast[] = [];
let listeners: Array<(toasts: Toast[]) => void> = [];

export const toast = (toast: Omit<Toast, 'id'>) => {
  const id = Math.random().toString(36).substring(2, 9);
  const newToast: Toast = { ...toast, id };
  toasts = [...toasts, newToast];
  
  listeners.forEach(listener => listener(toasts));
  
  // Auto remove after duration
  setTimeout(() => {
    dismiss(id);
  }, toast.duration || 5000);
};

export const dismiss = (id: string) => {
  toasts = toasts.filter(t => t.id !== id);
  listeners.forEach(listener => listener(toasts));
};

export function Toaster() {
  const [toastList, setToastList] = useState<Toast[]>([]);

  useEffect(() => {
    const listener = (newToasts: Toast[]) => setToastList(newToasts);
    listeners.push(listener);
    
    return () => {
      listeners = listeners.filter(l => l !== listener);
    };
  }, []);

  if (toastList.length === 0) return null;

  return (
    <div className="fixed top-0 right-0 z-50 w-full md:max-w-[420px] p-4">
      {toastList.map((toast) => (
        <div
          key={toast.id}
          className={`mb-4 p-4 rounded-lg shadow-lg transition-all duration-300 ${
            toast.variant === 'destructive'
              ? 'bg-destructive text-destructive-foreground'
              : 'bg-background border'
          }`}
        >
          {toast.title && (
            <div className="font-semibold mb-1">{toast.title}</div>
          )}
          <div className="text-sm">{toast.description}</div>
          <button
            onClick={() => dismiss(toast.id)}
            className="absolute top-2 right-2 text-sm opacity-70 hover:opacity-100"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}