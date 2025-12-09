import React, { useState, useRef, useEffect } from 'react';
import { Send, StopCircle } from 'lucide-react';

const ChatInput = ({ onSendMessage, disabled, isLoading }) => {
  const [inputMessage, setInputMessage] = useState('');
  const textareaRef = useRef(null);

  const handleSend = () => {
    if (!inputMessage.trim() || isLoading || disabled) return;
    onSendMessage(inputMessage);
    setInputMessage('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [inputMessage]);

  return (
    <div className="border-t border-light-border dark:border-dark-border bg-light-bg dark:bg-dark-bg">
      <div className="max-w-3xl mx-auto px-4 py-4">
        <div className="relative flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={disabled ? "Upload documents to start chatting..." : "Ask anything about your documents..."}
              disabled={disabled || isLoading}
              className="w-full bg-light-sidebar dark:bg-dark-sidebar border border-light-border dark:border-dark-border rounded-2xl px-4 py-3 pr-12 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all max-h-32 text-light-text dark:text-dark-text placeholder:text-light-textSecondary dark:placeholder:text-dark-textSecondary"
              rows="1"
            />
          </div>
          
          <button
            onClick={handleSend}
            disabled={!inputMessage.trim() || isLoading || disabled}
            className="w-10 h-10 bg-purple-500 hover:bg-purple-600 disabled:bg-light-border dark:disabled:bg-dark-border disabled:cursor-not-allowed rounded-xl transition-colors flex items-center justify-center flex-shrink-0"
          >
            {isLoading ? (
              <StopCircle className="w-5 h-5 text-white" />
            ) : (
              <Send className="w-5 h-5 text-white" />
            )}
          </button>
        </div>
        
        <div className="text-xs text-light-textSecondary dark:text-dark-textSecondary mt-2 text-center">
          AI can make mistakes. Verify important information.
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
