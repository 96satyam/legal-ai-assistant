/* global Word */

import apiService from './api-service.js';

export class QAComponent {
  constructor(containerElement) {
    this.container = containerElement;
    this.conversationHistory = [];
    this.isProcessing = false;
    this.documentText = null;
  }

  /**
   * Initialize the Q&A interface
   */
  async initialize(documentText) {
    this.documentText = documentText;
    this.render();
    this.attachEventListeners();
  }

  /**
   * Render the Q&A interface
   */
  render() {
    this.container.innerHTML = `
      <div class="qa-panel">
        <div class="qa-header">
          <h3>Ask Questions</h3>
          <p class="qa-subtitle">Ask anything about this contract</p>
        </div>
        
        <div class="qa-conversation" id="qa-conversation">
          ${this.renderConversation()}
        </div>
        
        <div class="qa-input-container">
          <textarea 
            id="qa-input" 
            class="qa-input" 
            placeholder="e.g., What are the termination conditions?"
            rows="3"
          ></textarea>
          <button id="qa-send-btn" class="qa-send-btn">
            <span class="btn-text">Ask Question</span>
            <span class="btn-icon">→</span>
          </button>
        </div>
        
        <div class="qa-suggestions">
          <p class="suggestions-label">Suggestions:</p>
          <button class="suggestion-btn" data-question="What are the main obligations of each party?">
            Main obligations
          </button>
          <button class="suggestion-btn" data-question="What are the liability provisions?">
            Liability provisions
          </button>
          <button class="suggestion-btn" data-question="How can this agreement be terminated?">
            Termination conditions
          </button>
        </div>
      </div>
    `;
  }

  /**
   * Render conversation history
   */
  renderConversation() {
    if (this.conversationHistory.length === 0) {
      return `
        <div class="qa-empty-state">
          <p>No questions asked yet. Try asking about:</p>
          <ul>
            <li>Specific clauses or terms</li>
            <li>Obligations and responsibilities</li>
            <li>Risks and liabilities</li>
            <li>Termination conditions</li>
          </ul>
        </div>
      `;
    }

    return this.conversationHistory.map((item, index) => `
      <div class="qa-message-group">
        <div class="qa-message user">
          <div class="message-icon">Q</div>
          <div class="message-content">${item.question}</div>
        </div>
        <div class="qa-message assistant">
          <div class="message-icon">A</div>
          <div class="message-content">
            ${item.answer}
            ${item.citations && item.citations.length > 0 ? `
              <div class="citations">
                <p class="citations-label">Sources:</p>
                ${item.citations.map((citation, citIndex) => `
                  <button class="citation-link" data-msg-index="${index}" data-cite-index="${citIndex}">
                    ${citation.text || `Citation ${citIndex + 1}`}
                  </button>
                `).join('')}
              </div>
            ` : ''}
          </div>
        </div>
      </div>
    `).join('');
  }

  /**
   * Attach event listeners
   */
  attachEventListeners() {
    const sendBtn = document.getElementById('qa-send-btn');
    const input = document.getElementById('qa-input');
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');

    // Send button
    sendBtn.onclick = () => this.handleSendQuestion();

    // Enter key
    input.onkeypress = (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.handleSendQuestion();
      }
    };

    // Suggestion buttons
    suggestionBtns.forEach(btn => {
      btn.onclick = () => {
        input.value = btn.dataset.question;
        this.handleSendQuestion();
      };
    });

    // Citation links
    this.attachCitationListeners();
  }

  /**
   * Handle sending a question
   */
  async handleSendQuestion() {
    if (this.isProcessing) return;

    const input = document.getElementById('qa-input');
    const question = input.value.trim();

    if (!question) return;

    try {
      this.isProcessing = true;
      input.value = '';
      document.getElementById('qa-send-btn').disabled = true;

      // Add user message immediately
      this.conversationHistory.push({
        question: question,
        answer: 'Thinking...',
        citations: []
      });
      this.updateConversation();

      // Get answer from backend
      const response = await apiService.askQuestion(question, this.documentText);

      // Update with actual answer
      this.conversationHistory[this.conversationHistory.length - 1] = {
        question: question,
        answer: response.answer,
        citations: response.citations || []
      };

      this.updateConversation();

    } catch (error) {
      console.error('Q&A error:', error);
      this.conversationHistory[this.conversationHistory.length - 1] = {
        question: question,
        answer: `Error: ${error.message}`,
        citations: []
      };
      this.updateConversation();
    } finally {
      this.isProcessing = false;
      document.getElementById('qa-send-btn').disabled = false;
      input.focus();
    }
  }

  /**
   * Update conversation display
   */
  updateConversation() {
    const conversationDiv = document.getElementById('qa-conversation');
    conversationDiv.innerHTML = this.renderConversation();
    
    // Scroll to bottom
    conversationDiv.scrollTop = conversationDiv.scrollHeight;
    
    // Reattach citation listeners
    this.attachCitationListeners();
  }

  /**
   * Attach listeners to citation links
   */
  attachCitationListeners() {
    const citationLinks = document.querySelectorAll('.citation-link');
    citationLinks.forEach(link => {
      link.onclick = async () => {
        const msgIndex = parseInt(link.dataset.msgIndex);
        const citeIndex = parseInt(link.dataset.citeIndex);
        const citation = this.conversationHistory[msgIndex].citations[citeIndex];
        
        if (citation && citation.text) {
          await this.highlightCitation(citation.text);
        }
      };
    });
  }

  /**
   * Highlight citation text in document
   */
  async highlightCitation(text) {
    try {
      await Word.run(async (context) => {
        const searchResults = context.document.body.search(text, {
          matchCase: false,
          matchWholeWord: false
        });
        
        searchResults.load("items");
        await context.sync();

        if (searchResults.items.length > 0) {
          const range = searchResults.items[0];
          range.font.highlightColor = '#FFEB3B'; // Yellow highlight
          range.select();
          await context.sync();
        }
      });
    } catch (error) {
      console.error('Citation highlight error:', error);
    }
  }
}