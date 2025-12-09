import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import MainContent from './components/MainContent';
import MindMapModal from './components/MindMapModal';
import { useConversations } from './context/ConversationContext';
import { getDocuments } from './services/api';
import { initializeMermaid } from './utils/mermaid';

initializeMermaid();

const App = () => {
  const [documents, setDocuments] = useState([]);
  const [showMindMap, setShowMindMap] = useState(false);
  const [currentMermaid, setCurrentMermaid] = useState('');
  
  const { currentConversation, createNewConversation } = useConversations();

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Error loading documents:', error);
    }
  };

  const handleNewChat = async () => {
    const documentIds = documents.map(d => d.id);
    await createNewConversation(documentIds);
  };

  // Create initial conversation if none exists
  useEffect(() => {
    if (!currentConversation) {
      handleNewChat();
    }
  }, []);

  return (
    <div className="flex h-screen bg-light-bg dark:bg-dark-bg text-light-text dark:text-dark-text transition-colors duration-200">
      <Sidebar 
        documents={documents}
        setDocuments={setDocuments}
        onNewChat={handleNewChat}
        onDocumentsUpdate={loadDocuments}
      />
      
      <MainContent
        documents={documents}
        currentConversation={currentConversation}
        setShowMindMap={setShowMindMap}
        setCurrentMermaid={setCurrentMermaid}
      />

      {showMindMap && (
        <MindMapModal
          mermaidCode={currentMermaid}
          onClose={() => setShowMindMap(false)}
        />
      )}
    </div>
  );
};

export default App;
