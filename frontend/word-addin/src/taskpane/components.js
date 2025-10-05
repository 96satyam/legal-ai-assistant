/**
 * UI Component builders for the task pane
 */

export class UIComponents {
  /**
   * Create a loading spinner
   */
  static createLoadingState(message = 'Processing...') {
    return `
      <div class="loading-container">
        <div class="spinner"></div>
        <p class="loading-text">${message}</p>
      </div>
    `;
  }

  /**
   * Create risk summary cards
   */
  static createRiskSummary(risks) {
    if (!risks || risks.length === 0) {
      return '<div class="info-message">No risks detected in this document.</div>';
    }

    const risksByLevel = {
      critical: risks.filter(r => r.risk_level === 'critical'),
      high: risks.filter(r => r.risk_level === 'high'),
      medium: risks.filter(r => r.risk_level === 'medium'),
      low: risks.filter(r => r.risk_level === 'low')
    };

    return `
      <div class="risk-summary">
        <h3>Risk Summary</h3>
        <div class="risk-stats">
          ${risksByLevel.critical.length > 0 ? `
            <div class="risk-stat critical">
              <span class="risk-count">${risksByLevel.critical.length}</span>
              <span class="risk-label">Critical</span>
            </div>
          ` : ''}
          ${risksByLevel.high.length > 0 ? `
            <div class="risk-stat high">
              <span class="risk-count">${risksByLevel.high.length}</span>
              <span class="risk-label">High</span>
            </div>
          ` : ''}
          ${risksByLevel.medium.length > 0 ? `
            <div class="risk-stat medium">
              <span class="risk-count">${risksByLevel.medium.length}</span>
              <span class="risk-label">Medium</span>
            </div>
          ` : ''}
          ${risksByLevel.low.length > 0 ? `
            <div class="risk-stat low">
              <span class="risk-count">${risksByLevel.low.length}</span>
              <span class="risk-label">Low</span>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }

  /**
   * Create detailed risk cards
   */
  static createRiskCards(risks) {
    if (!risks || risks.length === 0) return '';

    return `
      <div class="risk-details">
        <h3>Risk Details</h3>
        ${risks.map((risk, index) => `
          <div class="risk-card ${risk.risk_level}">
            <div class="risk-header">
              <span class="risk-badge ${risk.risk_level}">${risk.risk_level.toUpperCase()}</span>
              <span class="risk-type">${risk.risk_type || 'Legal Risk'}</span>
            </div>
            <div class="risk-content">
              <p class="risk-description">${risk.description}</p>
              ${risk.clause_text ? `
                <div class="risk-clause">
                  <strong>Problematic Clause:</strong>
                  <p>"${this.truncateText(risk.clause_text, 150)}"</p>
                </div>
              ` : ''}
              ${risk.mitigation ? `
                <div class="risk-mitigation">
                  <strong>Suggested Action:</strong>
                  <p>${risk.mitigation}</p>
                </div>
              ` : ''}
            </div>
            <button class="btn-link highlight-btn" data-risk-index="${index}">
              Highlight in Document
            </button>
          </div>
        `).join('')}
      </div>
    `;
  }

  /**
   * Create clause breakdown
   */
  static createClauseBreakdown(clauses) {
    if (!clauses || clauses.length === 0) {
      return '<div class="info-message">No clauses identified.</div>';
    }

    // Group clauses by type
    const clausesByType = {};
    clauses.forEach(clause => {
      const type = clause.type || clause.clause_type || 'Other';
      if (!clausesByType[type]) {
        clausesByType[type] = [];
      }
      clausesByType[type].push(clause);
    });

    return `
      <div class="clause-breakdown">
        <h3>Clause Breakdown</h3>
        <div class="clause-stats">
          <div class="stat-item">
            <span class="stat-number">${clauses.length}</span>
            <span class="stat-label">Total Clauses</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">${Object.keys(clausesByType).length}</span>
            <span class="stat-label">Categories</span>
          </div>
        </div>
        <div class="clause-list">
          ${Object.entries(clausesByType).map(([type, typeClauses]) => `
            <div class="clause-category">
              <div class="clause-category-header">
                <h4>${type}</h4>
                <span class="clause-count">${typeClauses.length}</span>
              </div>
              <ul class="clause-items">
                ${typeClauses.slice(0, 3).map(clause => `
                  <li class="clause-item">
                    ${this.truncateText(clause.text || clause.content || '', 80)}
                  </li>
                `).join('')}
                ${typeClauses.length > 3 ? `
                  <li class="clause-item more">+ ${typeClauses.length - 3} more</li>
                ` : ''}
              </ul>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  /**
   * Create compliance checklist
   */
  static createComplianceCheck(compliance) {
    if (!compliance) return '';

    return `
      <div class="compliance-section">
        <h3>Compliance Check</h3>
        <div class="compliance-items">
          ${compliance.checks ? compliance.checks.map(check => `
            <div class="compliance-item ${check.status}">
              <span class="compliance-icon">${check.status === 'passed' ? '✓' : '✗'}</span>
              <div class="compliance-content">
                <p class="compliance-requirement">${check.requirement}</p>
                ${check.status === 'failed' ? `
                  <p class="compliance-note">Missing or insufficient</p>
                ` : ''}
              </div>
            </div>
          `).join('') : '<p class="info-message">No compliance data available</p>'}
        </div>
      </div>
    `;
  }

  /**
   * Create overall analysis summary
   */
  static createAnalysisSummary(analysis) {
    const overallScore = analysis.overall_risk_score || 'unknown';
    const scoreColor = {
      'low': 'success',
      'medium': 'warning',
      'high': 'danger',
      'critical': 'danger',
      'unknown': 'neutral'
    }[overallScore.toLowerCase()] || 'neutral';

    return `
      <div class="analysis-summary">
        <div class="overall-score ${scoreColor}">
          <h3>Overall Risk Level</h3>
          <div class="score-badge ${scoreColor}">
            ${overallScore.toUpperCase()}
          </div>
        </div>
        ${analysis.summary ? `
          <p class="summary-text">${analysis.summary}</p>
        ` : ''}
      </div>
    `;
  }

  /**
   * Utility: Truncate text
   */
  static truncateText(text, maxLength) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }

  /**
   * Create error message
   */
  static createErrorMessage(error) {
    return `
      <div class="error-container">
        <div class="error-icon">⚠</div>
        <h3>Analysis Failed</h3>
        <p class="error-message">${error}</p>
        <button class="btn-secondary retry-btn">Try Again</button>
      </div>
    `;
  }

  /**
   * Create empty state
   */
  static createEmptyState() {
    return `
      <div class="empty-state">
        <div class="empty-icon">📄</div>
        <h3>No Document Content</h3>
        <p>Please add some text to the document before analyzing.</p>
      </div>
    `;
  }
}