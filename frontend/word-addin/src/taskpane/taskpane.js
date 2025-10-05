/* global Office, Word */

import apiService from './api-service.js';
import { UIComponents } from './components.js';
import { QAComponent } from './qa-component.js';

// State management
let currentAnalysis = null;
let currentDocumentText = null;
let isAnalyzing = false;
let qaComponent = null;
let activeTab = 'analysis'; // 'analysis' or 'qa'

Office.onReady((info) => {
  if (info.host === Office.HostType.Word) {
    // Initialize event listeners
    document.getElementById("analyze-btn").onclick = analyzeDocument;
    document.getElementById("test-connection").onclick = testConnection;
    document.getElementById("tab-analysis").onclick = () => switchTab('analysis');
    document.getElementById("tab-qa").onclick = () => switchTab('qa');
    
    // Check backend health on load
    checkBackendHealth();
    
    console.log("Legal AI Assistant loaded successfully!");
    showMessage("Add-in loaded successfully! Click 'Analyze Document' to begin.", "success");
  }
});

/**
 * Switch between tabs
 */
function switchTab(tab) {
  activeTab = tab;
  
  // Update tab buttons
  document.getElementById('tab-analysis').classList.toggle('active', tab === 'analysis');
  document.getElementById('tab-qa').classList.toggle('active', tab === 'qa');
  
  // Show/hide content
  document.getElementById('analysis-content').classList.toggle('hidden', tab !== 'analysis');
  document.getElementById('qa-content').classList.toggle('hidden', tab !== 'qa');
  
  // Initialize Q&A if needed
  if (tab === 'qa' && !qaComponent && currentDocumentText) {
    initializeQA();
  }
}

/**
 * Initialize Q&A component
 */
async function initializeQA() {
  if (!currentDocumentText) {
    const qaContent = document.getElementById('qa-content');
    qaContent.innerHTML = `
      <div class="info-message">
        <p>Please analyze the document first before asking questions.</p>
        <button onclick="document.getElementById('tab-analysis').click()">
          Go to Analysis
        </button>
      </div>
    `;
    return;
  }
  
  const qaContent = document.getElementById('qa-content');
  qaComponent = new QAComponent(qaContent);
  await qaComponent.initialize(currentDocumentText);
}

/**
 * Check if backend is running
 */
async function checkBackendHealth() {
  try {
    const isHealthy = await apiService.healthCheck();
    if (!isHealthy) {
      showMessage(
        "⚠ Backend API is not responding. Make sure your FastAPI server is running on http://localhost:8000",
        "error"
      );
    } else {
      console.log("Backend health check: OK");
    }
  } catch (error) {
    console.warn("Health check failed:", error);
  }
}

/**
 * Test connection to Word document
 */
async function testConnection() {
  try {
    showMessage("Testing connection...", "");
    
    await Word.run(async (context) => {
      const body = context.document.body;
      body.load("text");
      
      await context.sync();
      
      const textLength = body.text.trim().length;
      
      if (textLength === 0) {
        showMessage(
          "⚠ Document is empty. Please add some text to test.",
          "error"
        );
      } else {
        showMessage(
          `✓ Connection successful! Document has ${textLength} characters.`,
          "success"
        );
      }
    });
  } catch (error) {
    console.error("Test failed:", error);
    showMessage(`✗ Test failed: ${error.message}`, "error");
  }
}

/**
 * Analyze the current document
 */
async function analyzeDocument() {
  if (isAnalyzing) {
    showMessage("Analysis already in progress...", "");
    return;
  }

  try {
    isAnalyzing = true;
    setButtonsDisabled(true);
    
    // Show loading state
    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML = UIComponents.createLoadingState(
      "Analyzing your document... This may take a minute."
    );

    // Get document text
    const documentText = await getDocumentText();
    
    if (!documentText || documentText.trim().length === 0) {
      resultDiv.innerHTML = UIComponents.createEmptyState();
      return;
    }

    // Store for Q&A
    currentDocumentText = documentText;

    console.log(`Analyzing document (${documentText.length} characters)...`);

    // Call backend API
    const apiResponse = await apiService.analyzeContract(documentText);
    
    console.log('Received analysis:', apiResponse);
    
    // Store analysis
    currentAnalysis = apiResponse;
    
    // Display results
    displayAnalysisResults(apiResponse);
    
    // Enable Q&A tab
    document.getElementById('tab-qa').disabled = false;
    
    console.log("Analysis complete! Q&A is now available.");
    
  } catch (error) {
    console.error("Analysis failed:", error);
    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML = UIComponents.createErrorMessage(error.message);
    
    const retryBtn = document.querySelector('.retry-btn');
    if (retryBtn) {
      retryBtn.onclick = analyzeDocument;
    }
  } finally {
    isAnalyzing = false;
    setButtonsDisabled(false);
  }
}

/**
 * Get the full text from the Word document
 */
async function getDocumentText() {
  return await Word.run(async (context) => {
    const body = context.document.body;
    body.load("text");
    await context.sync();
    return body.text;
  });
}

/**
 * Display analysis results in the UI
 */
function displayAnalysisResults(apiResponse) {
  const resultDiv = document.getElementById("result");
  
  const risks = apiResponse.risks || [];
  const report = apiResponse.report || '';
  
  let html = '';

  const overallScore = determineOverallScore(risks);
  
  html += UIComponents.createAnalysisSummary({
    overall_risk_score: overallScore,
    summary: `Analysis complete. Identified ${risks.length} risk(s).`
  });

  if (report) {
    html += `
      <div class="report-section">
        <h3>Analysis Report</h3>
        <div class="report-content">
          ${formatReport(report)}
        </div>
      </div>
    `;
  }

  html += UIComponents.createRiskSummary(risks);
  html += UIComponents.createRiskCards(risks);

  resultDiv.innerHTML = html;

  attachHighlightListeners(risks);
}

/**
 * Determine overall risk score from risks array
 */
function determineOverallScore(risks) {
  if (!risks || risks.length === 0) return 'low';
  
  const hasCritical = risks.some(r => r.risk_level === 'critical');
  const hasHigh = risks.some(r => r.risk_level === 'high');
  const hasMedium = risks.some(r => r.risk_level === 'medium');
  
  if (hasCritical) return 'critical';
  if (hasHigh) return 'high';
  if (hasMedium) return 'medium';
  return 'low';
}

/**
 * Format the report text for display
 */
function formatReport(report) {
  return report
    .split('\n')
    .map(line => {
      if (line.trim().startsWith('##')) {
        return `<h4>${line.replace(/^#+\s*/, '')}</h4>`;
      } else if (line.trim().startsWith('**')) {
        return `<strong>${line.replace(/\*\*/g, '')}</strong>`;
      } else if (line.trim()) {
        return `<p>${line}</p>`;
      }
      return '';
    })
    .join('');
}

/**
 * Attach click listeners to highlight buttons
 */
function attachHighlightListeners(risks) {
  const highlightButtons = document.querySelectorAll('.highlight-btn');
  
  highlightButtons.forEach((button, index) => {
    button.onclick = async () => {
      const risk = risks[index];
      if (risk && risk.clause_text) {
        await highlightTextInDocument(risk.clause_text, risk.risk_level);
        showMessage(`Highlighted ${risk.risk_level} risk in document`, "success");
      }
    };
  });
}

/**
 * Highlight text in the Word document
 */
async function highlightTextInDocument(searchText, riskLevel) {
  try {
    await Word.run(async (context) => {
      let searchResults = context.document.body.search(searchText, {
        matchCase: false,
        matchWholeWord: false
      });
      
      searchResults.load("items");
      await context.sync();

      if (searchResults.items.length === 0) {
        const shortText = searchText.substring(0, 100);
        searchResults = context.document.body.search(shortText, {
          matchCase: false,
          matchWholeWord: false
        });
        searchResults.load("items");
        await context.sync();
      }

      if (searchResults.items.length === 0) {
        console.warn("Text not found in document:", searchText.substring(0, 50));
        showMessage("Could not locate text in document", "error");
        return;
      }

      const range = searchResults.items[0];
      
      const highlightColors = {
        'critical': '#ff0000',
        'high': '#ffa500',
        'medium': '#ffff00',
        'low': '#90ee90'
      };
      
      range.font.highlightColor = highlightColors[riskLevel] || '#ffff00';
      range.select();
      await context.sync();
    });
  } catch (error) {
    console.error("Highlighting failed:", error);
    showMessage("Could not highlight text in document", "error");
  }
}

/**
 * Show a message in the result area
 */
function showMessage(message, type = "") {
  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML = `<p class="${type}">${message}</p>`;
}

/**
 * Enable/disable buttons during operations
 */
function setButtonsDisabled(disabled) {
  document.getElementById("analyze-btn").disabled = disabled;
  document.getElementById("test-connection").disabled = disabled;
}