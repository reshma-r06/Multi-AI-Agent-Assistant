'use client';

import { ChatMessage, MessageRole } from '@/types';
import { formatTimestamp, getAgentIcon } from '@/lib/utils';
import { Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageListProps {
  messages: ChatMessage[];
}

export default function MessageList({ messages }: MessageListProps) {
  return (
    <div className="space-y-4">
      {messages.map((message, index) => (
        <MessageBubble key={index} message={message} />
      ))}
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === MessageRole.USER;
  const isAgent = message.role === MessageRole.AGENT;
  
  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="flex-shrink-0">
          {isAgent && message.agent_type ? (
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm">
              {getAgentIcon(message.agent_type)}
            </div>
          ) : (
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
          )}
        </div>
      )}
      
      <div className={`flex flex-col max-w-[70%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-white border border-gray-200 text-gray-900'
          }`}
        >
          {isAgent && message.agent_type && (
            <div className="text-xs font-semibold mb-1 opacity-70">
              {message.agent_type.toUpperCase()} AGENT
            </div>
          )}
          
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        </div>
        
        <div className="text-xs text-gray-500 mt-1 px-1">
          {formatTimestamp(message.timestamp)}
        </div>
      </div>
      
      {isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center">
            <User className="w-5 h-5 text-white" />
          </div>
        </div>
      )}
    </div>
  );
}