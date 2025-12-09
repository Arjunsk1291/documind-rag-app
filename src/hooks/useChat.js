import { useState, useCallback } from 'react';
import { sendChatMessage } from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (content, documentIds = []) => {
    try {
      console.log('useChat - Sending:', content, 'DocIDs:', documentIds);
      
      // Call backend API
      const response = await sendChatMessage(content, documentIds);
      console.log('useChat - Received:', response);
      
      return response;
    } catch (error) {
      console.error('useChat - Error:', error);
      throw error;
    }
  }, []);

  return {
    messages,
    isLoading,
    sendMessage,
    setMessages
  };
};
