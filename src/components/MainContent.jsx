import React, { useState, useEffect } from 'react';
import WelcomeScreen from './WelcomeScreen';
import ChatArea from './ChatArea';
import ChatInput from './ChatInput';
import DocumentBadge from './DocumentBadge';
import { sendMessage, updateConversationDocuments } from '../services/api';
import { useConversations } from '../context/ConversationContext';

const MainContent = ({ 
  documents,
  currentConversation,
  setShowMindMap,
  setCurrentMermaid 
}) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationDocuments, setConversationDocuments] = useState([]);
  const { loadConversations } = useConversations();

  // Load messages and documents when conversation changes
  useEffect(() => {
    if (currentConversation) {
      setMessages(currentConversation.messages || []);
      
      // Load conversation documents from all documents list
      const convDocs = documents.filter(doc => 
        currentConversation.document_ids?.includes(doc.id)
      );
      setConversationDocuments(convDocs);
    } else {
      setMessages([]);
      setConversationDocuments([]);
    }
  }, [currentConversation, documents]);

  const handleRemoveDocument = async (docId) => {
    if (!currentConversation) return;
    
    const newDocIds = currentConversation.document_ids.filter(id => id !== docId);
    await updateConversationDocuments(currentConversation.id, newDocIds);
    await loadConversations();
  };

  const handleSendMessage = async (content) => {
    if (!content.trim() || !currentConversation) return;
    
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    try {
      const documentIds = currentConversation.document_ids || [];
      
      const response = await sendMessage(
        currentConversation.id,
        content,
        documentIds
      );
      
      const aiResponse = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.response || 'No response received',
        timestamp: new Date(response.timestamp).toLocaleTimeString(),
        hasMindMap: response.has_mindmap,
        mermaidCode: response.mermaid_code,
        sources: response.sources
      };
      
      setMessages(prev => [...prev, aiResponse]);
      await loadConversations();
      
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message || 'Failed to get response from server'}`,
        timestamp: new Date().toLocaleTimeString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewMindMap = (mermaidCode) => {
    setCurrentMermaid(mermaidCode);
    setShowMindMap(true);
  };

  if (!currentConversation) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-light-textSecondary dark:text-dark-textSecondary">
            Loading...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Document Badge */}
      {conversationDocuments.length > 0 && (
        <DocumentBadge 
          documents={conversationDocuments}
          onRemove={handleRemoveDocument}
        />
      )}

      {messages.length === 0 ? (
        <WelcomeScreen documents={conversationDocuments} />
      ) : (
        <ChatArea 
          messages={messages}
          isLoading={isLoading}
          onViewMindMap={handleViewMindMap}
        />
      )}

      <ChatInput
        onSendMessage={handleSendMessage}
        disabled={conversationDocuments.length === 0}
        isLoading={isLoading}
      />
    </div>
  );
};

export default MainContent;
