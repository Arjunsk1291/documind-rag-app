import mermaid from 'mermaid';

export const initializeMermaid = () => {
  mermaid.initialize({ 
    startOnLoad: false,
    theme: 'dark',
    securityLevel: 'loose',
    themeVariables: {
      primaryColor: '#a855f7',
      primaryTextColor: '#fff',
      primaryBorderColor: '#7c3aed',
      lineColor: '#c084fc',
      secondaryColor: '#1e1e1e',
      tertiaryColor: '#2a2a2a',
      background: '#171717',
      mainBkg: '#212121',
      secondBkg: '#2a2a2a',
      nodeBorder: '#7c3aed',
      clusterBkg: '#2a2a2a',
      clusterBorder: '#7c3aed',
      titleColor: '#fff',
      edgeLabelBackground: '#2a2a2a',
      nodeTextColor: '#fff'
    },
    flowchart: {
      htmlLabels: true,
      curve: 'basis',
      padding: 15
    }
  });
};

export const renderMermaid = async (element) => {
  try {
    // Clear previous content
    element.innerHTML = '';
    
    // Get the mermaid code
    let mermaidCode = element.textContent || element.innerText;
    
    // Clean up the code
    mermaidCode = mermaidCode.trim();
    
    // Remove markdown code blocks if present
    mermaidCode = mermaidCode.replace(/```mermaid\n?/g, '').replace(/```\n?/g, '');
    
    // Ensure it starts with a graph type
    if (!mermaidCode.match(/^(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|journey|gantt|pie)/)) {
      mermaidCode = 'graph TD\n' + mermaidCode;
    }
    
    console.log('Rendering Mermaid code:', mermaidCode);
    
    // Create a unique ID for this diagram
    const id = `mermaid-${Date.now()}`;
    
    // Render the diagram
    const { svg } = await mermaid.render(id, mermaidCode);
    
    // Insert the SVG
    element.innerHTML = svg;
    
    console.log('Mermaid diagram rendered successfully');
  } catch (error) {
    console.error('Mermaid rendering error:', error);
    element.innerHTML = `
      <div class="p-6 text-center">
        <div class="text-red-500 mb-2">
          <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <p class="text-red-500 font-semibold mb-1">Error Rendering Diagram</p>
        <p class="text-sm text-gray-500 dark:text-gray-400">${error.message}</p>
        <details class="mt-4 text-left">
          <summary class="cursor-pointer text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
            View diagram code
          </summary>
          <pre class="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded text-xs overflow-auto max-h-60">
${element.textContent}
          </pre>
        </details>
      </div>
    `;
    throw error;
  }
};

export default mermaid;
