/**
 * API Service for communicating with FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
    this.currentDocumentId = null;
  }

  /**
   * Analyze a contract document
   */
  async analyzeContract(documentText) {
    try {
      const response = await fetch(`${this.baseUrl}/analysis/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_text: documentText
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }

      const data = await response.json();
      console.log('API Response:', data);
      
      // Store document ID for Q&A
      this.currentDocumentId = 'doc_from_word_' + Date.now();
      
      return data;
      
    } catch (error) {
      console.error('Analysis API error:', error);
      throw new Error(`Failed to analyze document: ${error.message}`);
    }
  }

  /**
   * Ask a question about the document
   */
  async askQuestion(question, documentText) {
    try {
      const documentId = this.currentDocumentId || 'doc_from_word_' + Date.now();
      
      const response = await fetch(`${this.baseUrl}/qa/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          question: question,
          document_text: documentText
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }

      return await response.json();
      
    } catch (error) {
      console.error('Q&A API error:', error);
      throw new Error(`Failed to get answer: ${error.message}`);
    }
  }

  /**
   * Health check to verify backend is running
   */
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseUrl.replace('/api', '')}/docs`, {
        method: 'GET',
      });
      return response.ok;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }
}

// Export singleton instance
const apiService = new ApiService();
export default apiService;