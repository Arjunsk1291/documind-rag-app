import React from 'react';
import { Brain, User, Sparkles } from 'lucide-react';

const ChatMessage = ({ message, onViewMindMap }) => {
  const isUser = message.role === 'user';

  return (
    <div className="flex items-start gap-4">
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
        isUser 
          ? 'bg-light-border dark:bg-dark-border' 
          : 'bg-gradient-to-br from-purple-500 to-pink-500'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-light-text dark:text-dark-text" />
        ) : (
          <Sparkles className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className="flex-1 space-y-2">
        <div className={`rounded-2xl p-4 ${
          isUser
            ? 'bg-transparent'
            : message.isError
            ? 'bg-red-500/10 border border-red-500/20'
            : 'bg-light-sidebar dark:bg-dark-sidebar border border-light-border dark:border-dark-border'
        }`}>
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <p className="whitespace-pre-wrap m-0 leading-relaxed">
              {message.content}
            </p>
          </div>
        </div>

        {/* Mind Map Button */}
        {message.hasMindMap && !isUser && (
          <button
            onClick={() => onViewMindMap(message.mermaidCode)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-xl text-sm font-medium transition-colors"
          >
            <Brain className="w-4 h-4" />
            View Mind Map
          </button>
        )}

        {/* Timestamp */}
        <div className="text-xs text-light-textSecondary dark:text-dark-textSecondary">
          {message.timestamp}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
