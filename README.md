# DocuMind - RAG Document Assistant

A modern RAG (Retrieval-Augmented Generation) document assistant built with React and FastAPI.

## Features

- 📄 Document Upload & Management (PDF, DOCX, TXT, MD)
- 💬 Intelligent Chat Interface
- 🧠 Mind Map Visualization with Mermaid.js
- 🎨 Modern Dark UI
- 🔄 Real-time Updates

## Project Structure
```
documind-rag-app/
├── src/
│   ├── components/          # React components
│   │   ├── ChatArea.jsx
│   │   ├── ChatInput.jsx
│   │   ├── ChatMessage.jsx
│   │   ├── DocumentList.jsx
│   │   ├── DocumentUpload.jsx
│   │   ├── MainContent.jsx
│   │   ├── MindMapModal.jsx
│   │   ├── Sidebar.jsx
│   │   └── WelcomeScreen.jsx
│   ├── hooks/              # Custom React hooks
│   │   ├── useChat.js
│   │   └── useDocuments.js
│   ├── services/           # API services
│   │   └── api.js
│   ├── utils/              # Utility functions
│   │   └── mermaid.js
│   ├── App.jsx             # Main app component
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles
├── public/                 # Static assets
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── package.json          # Dependencies
├── tailwind.config.js    # Tailwind configuration
├── vite.config.js        # Vite configuration
└── README.md             # This file
```

## Installation

1. **Clone the repository**
```bash
   git clone <your-repo-url>
   cd documind-rag-app
```

2. **Install dependencies**
```bash
   npm install
```

3. **Create environment file**
```bash
   cp .env.example .env
```

4. **Update `.env` with your backend API URL**
```
   VITE_API_URL=http://localhost:8000/api
```

## Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Build for Production
```bash
npm run build
```

The built files will be in the `dist/` directory.

## Preview Production Build
```bash
npm run preview
```

## Environment Variables

- `VITE_API_URL` - Backend API URL (default: `http://localhost:8000/api`)
- `VITE_ENV` - Environment mode (development/production)

## Backend API Integration

This frontend is designed to work with a FastAPI backend. Update the following files to connect to your backend:

### API Endpoints Expected:

1. **Upload Document**
   - `POST /api/documents/upload`
   - Body: `multipart/form-data` with file

2. **Get Documents**
   - `GET /api/documents`
   - Response: Array of document objects

3. **Delete Document**
   - `DELETE /api/documents/{documentId}`

4. **Send Chat Message**
   - `POST /api/chat`
   - Body: `{ query: string, documentIds: string[] }`

5. **Generate Mind Map**
   - `POST /api/mindmap`
   - Body: `{ query: string, documentIds: string[] }`

### Connecting to Backend:

In `src/services/api.js`, uncomment the actual API calls and remove the simulated delays:
```javascript
// Example: Replace simulation in useDocuments.js
export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};
```

## Component Architecture

### Core Components:

- **App.jsx** - Root component managing global state
- **Sidebar.jsx** - Document management sidebar
- **MainContent.jsx** - Main chat and content area
- **MindMapModal.jsx** - Full-screen mind map viewer

### UI Components:

- **DocumentUpload.jsx** - File upload interface
- **DocumentList.jsx** - List of uploaded documents
- **WelcomeScreen.jsx** - Initial welcome view
- **ChatArea.jsx** - Message display area
- **ChatInput.jsx** - User input interface
- **ChatMessage.jsx** - Individual message component

### Custom Hooks:

- **useDocuments.js** - Document management logic
- **useChat.js** - Chat functionality and state

### Services:

- **api.js** - Axios instance and API methods

### Utils:

- **mermaid.js** - Mermaid diagram initialization and rendering

## Styling

This project uses:
- **Tailwind CSS** for utility-first styling
- **Lucide React** for icons
- Custom color palette (dark theme with blue accents)

## Technologies Used

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Mermaid.js** - Diagram rendering
- **Lucide React** - Icon library

## Git Workflow
```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: DocuMind RAG Assistant"

# Add remote
git remote add origin <your-repo-url>

# Push to main branch
git push -u origin main
```

## Customization Guide

### Changing Colors:

Edit `tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      primary: '#your-color',
      secondary: '#your-color',
    }
  }
}
```

### Adding New Components:

1. Create component in `src/components/`
2. Import and use in parent component
3. Update props and state as needed

### Modifying API Endpoints:

Edit `src/services/api.js` to match your backend routes.

## Troubleshooting

### Port Already in Use:
```bash
# Kill process on port 5173
sudo lsof -t -i:5173 | xargs kill -9
```

### Build Errors:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Mermaid Diagrams Not Rendering:
- Check browser console for errors
- Ensure Mermaid syntax is correct
- Verify `mermaid` package is installed

## License

MIT

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For issues and questions, please open an issue on GitHub.

## Roadmap

- [ ] Add document preview functionality
- [ ] Implement real-time collaboration
- [ ] Add more visualization types
- [ ] Support for more document formats
- [ ] Export chat history
- [ ] Dark/Light theme toggle
- [ ] Multi-language support

## Credits

Built with ❤️ using React and FastAPI
