'use client';

import { AgentResponse, TaskStatus } from '@/types';
import { getAgentColor, getAgentIcon, formatExecutionTime } from '@/lib/utils';
import { CheckCircle, XCircle, Clock } from 'lucide-react';

interface AgentStatusProps {
  agentResponses: AgentResponse[];
}

export default function AgentStatus({ agentResponses }: AgentStatusProps) {
  if (agentResponses.length === 0) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Agent Activity</h3>
      <div className="space-y-2">
        {agentResponses.map((response, index) => (
          <div key={index} className="flex items-center gap-3 py-2">
            <div
              className={`w-10 h-10 rounded-full ${getAgentColor(
                response.agent_type
              )} flex items-center justify-center text-white text-lg`}
            >
              {getAgentIcon(response.agent_type)}
            </div>
            
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-900 capitalize">
                  {response.agent_type} Agent
                </span>
                {response.status === TaskStatus.COMPLETED && (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                )}
                {response.status === TaskStatus.FAILED && (
                  <XCircle className="w-4 h-4 text-red-500" />
                )}
                {response.status === TaskStatus.IN_PROGRESS && (
                  <Clock className="w-4 h-4 text-yellow-500 animate-pulse" />
                )}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Completed in {formatExecutionTime(response.execution_time)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}