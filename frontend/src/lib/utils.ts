import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatExecutionTime(seconds: number): string {
  if (seconds < 1) {
    return `${(seconds * 1000).toFixed(0)}ms`;
  }
  return `${seconds.toFixed(2)}s`;
}

export function getAgentColor(agentType: string): string {
  const colors: Record<string, string> = {
    research: 'bg-blue-500',
    analysis: 'bg-purple-500',
    summary: 'bg-green-500',
    report: 'bg-orange-500',
  };
  return colors[agentType] || 'bg-gray-500';
}

export function getAgentIcon(agentType: string): string {
  const icons: Record<string, string> = {
    research: '🔍',
    analysis: '📊',
    summary: '📝',
    report: '📄',
  };
  return icons[agentType] || '🤖';
}