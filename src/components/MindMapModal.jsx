import React, { useRef, useEffect, useState } from 'react';
import { Brain, X, Download, Copy, Check } from 'lucide-react';
import { renderMermaid } from '../utils/mermaid';

const MindMapModal = ({ mermaidCode, onClose }) => {
  const mermaidRef = useRef(null);
  const [isRendering, setIsRendering] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (mermaidCode && mermaidRef.current) {
      const renderDiagram = async () => {
        try {
          setIsRendering(true);
          setError(null);
          
          // Set the text content first
          mermaidRef.current.textContent = mermaidCode;
          
          // Wait a tick for the DOM to update
          await new Promise(resolve => setTimeout(resolve, 100));
          
          // Render the diagram
          await renderMermaid(mermaidRef.current);
          
          setIsRendering(false);
        } catch (err) {
          console.error('Mermaid rendering error:', err);
          setError(err.message);
          setIsRendering(false);
        }
      };
      renderDiagram();
    }
  }, [mermaidCode]);

  const handleDownload = () => {
    const svg = mermaidRef.current?.querySelector('svg');
    if (svg) {
      const svgData = new XMLSerializer().serializeToString(svg);
      const blob = new Blob([svgData], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'mindmap.svg';
      link.click();
      URL.revokeObjectURL(url);
    }
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(mermaidCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
      <div className="bg-light-bg dark:bg-dark-bg rounded-2xl w-full max-w-6xl max-h-[90vh] flex flex-col shadow-2xl border border-light-border dark:border-dark-border">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-light-border dark:border-dark-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Mind Map Visualization</h3>
              <p className="text-sm text-light-textSecondary dark:text-dark-textSecondary">
                Interactive diagram generated from your documents
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyCode}
              className="flex items-center gap-2 px-3 py-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-xl transition-colors text-sm"
              title="Copy Mermaid code"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-green-500" />
                  <span className="text-green-500">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span>Copy Code</span>
                </>
              )}
            </button>
            {!error && !isRendering && (
              <button
                onClick={handleDownload}
                className="p-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-xl transition-colors"
                title="Download as SVG"
              >
                <Download className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-xl transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-auto p-8 bg-light-sidebar dark:bg-dark-sidebar">
          {isRendering ? (
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-light-textSecondary dark:text-dark-textSecondary">
                  Rendering mind map...
                </p>
              </div>
            </div>
          ) : (
            <div 
              ref={mermaidRef}
              className="mermaid flex items-center justify-center min-h-[400px]"
            />
          )}
        </div>

        {/* Raw Code Preview (for debugging) */}
        {error && (
          <div className="border-t border-light-border dark:border-dark-border p-4 bg-red-500/5">
            <details>
              <summary className="cursor-pointer text-sm font-medium mb-2 hover:text-purple-500">
                View Raw Mermaid Code
              </summary>
              <pre className="text-xs bg-dark-bg dark:bg-black p-4 rounded-lg overflow-auto max-h-40 border border-light-border dark:border-dark-border">
                {mermaidCode}
              </pre>
            </details>
          </div>
        )}
      </div>
    </div>
  );
};

export default MindMapModal;
