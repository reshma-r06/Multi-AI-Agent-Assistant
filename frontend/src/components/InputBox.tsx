'use client';

import { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';

interface InputBoxProps {
  onSubmit: (query: string) => void;
  disabled?: boolean;
}

export default function InputBox({ onSubmit, disabled }: InputBoxProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = () => {
    if (query.trim() && !disabled) {
      onSubmit(query.trim());
      setQuery('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex gap-3 items-end">
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Ask about market research, competitors, funding, or anything..."
        className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        rows={3}
        disabled={disabled}
      />
      <button
        onClick={handleSubmit}
        disabled={disabled || !query.trim()}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
      >
        <Send className="w-5 h-5" />
        Send
      </button>
    </div>
  );
}