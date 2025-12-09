import React from 'react';
import { FileText, Trash2 } from 'lucide-react';

const DocumentList = ({ documents, onDeleteDocument }) => {
  return (
    <div className="flex-1 overflow-y-auto p-4">
      {documents.length === 0 ? (
        <div className="text-center text-light-textSecondary dark:text-dark-textSecondary text-sm mt-8">
          No documents uploaded
        </div>
      ) : (
        <div className="space-y-2">
          {documents.map(doc => (
            <div
              key={doc.id}
              className="p-3 bg-light-hover dark:bg-dark-hover hover:bg-light-border dark:hover:bg-dark-border rounded-xl transition-all group"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <FileText className="w-4 h-4 text-purple-500 flex-shrink-0" />
                    <span className="text-sm font-medium truncate">
                      {doc.name}
                    </span>
                  </div>
                  <div className="text-xs text-light-textSecondary dark:text-dark-textSecondary">
                    {doc.size}
                  </div>
                </div>
                <button
                  onClick={() => onDeleteDocument(doc.id)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-red-500/10 rounded-lg"
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentList;
