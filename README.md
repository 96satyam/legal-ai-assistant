# legal-ai-assistant

# Legal AI Assistant - MS Word Add-in

## Overview

A production-ready Microsoft Word add-in that provides AI-powered contract analysis directly within Word. Built with Office.js, React, and integrated with a FastAPI backend using LangGraph multi-agent systems.

## Features

### 1. Real-time Contract Analysis
- Analyze contracts directly in Word with a single click
- Identify risks with severity scoring (Critical, High, Medium, Low)
- Extract and categorize contract clauses
- Compliance checking against common standards (GDPR, etc.)
- Overall risk assessment with detailed reports

### 2. Interactive Risk Highlighting
- Click-to-highlight risky clauses in the document
- Color-coded highlighting based on risk severity:
  - **Red**: Critical risks
  - **Orange**: High risks
  - **Yellow**: Medium risks
  - **Light Green**: Low risks

### 3. Conversational Q&A
- Ask questions about your contract in natural language
- Get AI-powered answers with context from the document
- Conversation history maintained during session
- Citation support with click-to-highlight

### 4. Professional UI
- Clean, modern interface with Microsoft Fluent Design
- Tabbed navigation (Analysis / Q&A)
- Loading states and error handling
- Responsive design

## Technology Stack

### Frontend
- **Office.js**: Microsoft Office Add-in API
- **JavaScript (ES6+)**: Modern JavaScript with modules
- **Webpack**: Module bundling and dev server
- **office-addin-dev-certs**: SSL certificate management for local development

### Backend Integration
- **FastAPI**: Python REST API
- **LangGraph**: Multi-agent workflow orchestration
- **OpenAI GPT-4/3.5**: Language models for analysis and Q&A

## Project Structure
frontend/word-addin/
├── src/
│   ├── taskpane/
│   │   ├── taskpane.html          # Main UI
│   │   ├── taskpane.js            # Main logic
│   │   ├── api-service.js         # Backend API client
│   │   ├── components.js          # UI components
│   │   └── qa-component.js        # Q&A interface
│   └── commands/
│       └── commands.js            # Add-in commands
├── assets/                        # Icons and images
├── manifest.xml                   # Add-in manifest
├── webpack.config.js              # Webpack configuration
└── package.json                   # Dependencies

## Prerequisites

- **Node.js**: 18.0.0 or higher
- **npm**: 8.0.0 or higher
- **Microsoft Word**: Desktop version (Windows/Mac)
- **Backend API**: Running on `http://localhost:8000`

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/legal-ai-assistant.git
cd legal-ai-assistant/frontend/word-addin
2. Install Dependencies
bashnpm install
3. Install SSL Certificates
The add-in requires HTTPS for local development:
bashnpm run cert:install
Windows: May require running terminal as Administrator
Mac: May prompt for password to install certificate
4. Verify Certificate Installation
bashnpm run cert:verify
Expected output: You already have trusted access to https://localhost
Development
Start Development Server
bashnpm run dev-server
This starts the webpack dev server on https://localhost:3000
Load Add-in in Word
Option 1: Automatic (Recommended)
bashnpm run start:desktop
This will:

Start the dev server
Open Word automatically
Sideload the add-in

Option 2: Manual Sideloading
Windows:

Open Word
Go to Insert → Get Add-ins → Upload My Add-in
Browse to manifest.xml and upload

Mac:

Copy manifest.xml to:

   /Users/{username}/Library/Containers/com.microsoft.Word/Data/Documents/wef

Restart Word
Go to Insert → Add-ins → My Add-ins

Configuration
Backend API URL
Edit src/taskpane/api-service.js:
javascriptconst API_BASE_URL = 'http://localhost:8000/api';
Change to your backend URL if different.
Manifest Configuration
Edit manifest.xml to customize:

Add-in name and description
Icon URLs
Support URL
Default settings

Building for Production
Development Build
bashnpm run build:dev
Production Build
bashnpm run build
Output: dist/ directory with all compiled assets
API Integration
Required Backend Endpoints
The add-in expects these endpoints:
1. Health Check
GET /health
Response: { "status": "healthy" }
2. Contract Analysis
POST /api/analysis/
Body: { "document_text": "..." }
Response: {
  "report": "...",
  "risks": [
    {
      "clause_text": "...",
      "risk_level": "high",
      "risk_type": "liability",
      "description": "...",
      "mitigation": "..."
    }
  ]
}
3. Q&A
POST /api/qa/ask
Body: {
  "document_id": "...",
  "question": "...",
  "document_text": "..."
}
Response: {
  "answer": "...",
  "citations": [],
  "document_id": "..."
}
CORS Configuration
Backend must allow requests from https://localhost:3000:
pythonapp.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Features in Detail
Analysis Workflow

User clicks "Analyze Document"
Add-in reads document text via Office.js
Sends text to backend /api/analysis/ endpoint
Backend processes through LangGraph agents:

Document Parser
Risk Assessor
Compliance Checker
Report Aggregator


Results displayed in task pane with:

Overall risk score badge
Analysis report
Risk summary cards
Individual risk details


User can click "Highlight in Document" on any risk

Q&A Workflow

User switches to Q&A tab
Types question or clicks suggestion
Add-in sends question with document context to backend
Backend processes through RAG agent
Answer displayed in conversation format
Citations (if available) can be clicked to highlight

Highlighting System
The add-in uses Word's search and highlighting API:
javascript// Search for text
const searchResults = context.document.body.search(text, {
  matchCase: false,
  matchWholeWord: false
});

// Apply highlight color
range.font.highlightColor = '#ff0000';

// Select/scroll to text
range.select();
Troubleshooting
Certificate Errors
Symptom: "NET::ERR_CERT_AUTHORITY_INVALID"
Solution:
bash# Uninstall and reinstall certificates
npm run cert:install

# Clear browser cache
# Restart Word
Add-in Not Loading
Check:

Dev server is running (npm run dev-server)
Can access https://localhost:3000/taskpane.html in browser
No firewall blocking port 3000
Manifest URLs are correct

CORS Errors
Symptom: "Access to fetch blocked by CORS"
Solution: Verify backend CORS configuration includes https://localhost:3000
Backend Connection Failed
Check:

Backend is running on port 8000
Can access http://localhost:8000/health
Firewall allows connections

Testing
Manual Testing Checklist

 Add-in loads in Word without errors
 "Test Connection" button works
 "Analyze Document" processes sample contract
 Risk cards display correctly
 Highlighting works when clicking risk cards
 Q&A tab enables after analysis
 Can ask questions and get responses
 Conversation history persists
 No console errors in browser DevTools (F12)

Sample Test Contract
NON-DISCLOSURE AGREEMENT

1. CONFIDENTIAL INFORMATION
The Receiving Party acknowledges access to confidential information.

2. LIABILITY
The Receiving Party agrees to UNLIMITED LIABILITY for any breach.

3. TERMINATION
Either party may terminate at any time without notice.

4. INTELLECTUAL PROPERTY
All IP becomes property of Disclosing Party.

5. GOVERNING LAW
Governed by laws of unspecified jurisdiction.
Expected results:

4-5 risks identified
"High" or "Critical" overall risk
Multiple clause categories
Q&A answers based on content

Performance Considerations
Token Usage

Analysis: ~500-2000 tokens per request
Q&A: ~300-1000 tokens per question
Consider implementing caching for repeated queries

Document Size Limits

Recommended max: 10,000 words
Large documents may timeout (>30 seconds)
Consider chunking for very large contracts

Rate Limiting

OpenAI API has rate limits
Implement exponential backoff for retries
Show appropriate error messages to users

Security Considerations
Data Privacy

Document text sent to backend API
No data stored persistently in add-in
Backend should implement proper data handling
Consider encryption for sensitive contracts

API Keys

Never commit API keys to repository
Use environment variables
Implement proper authentication in production

SSL/TLS

Development uses self-signed certificates
Production should use valid SSL certificates
Update manifest URLs for production deployment

Deployment
Production Checklist

Update Manifest:

Change localhost URLs to production URLs
Update version number
Set production icon URLs


Build Assets:

bash   npm run build

Host Files:

Upload dist/ folder to web server
Ensure HTTPS is configured
Test all URLs are accessible


Update Backend:

Update CORS to allow production domain
Configure production API endpoints
Implement authentication


Distribute Manifest:

Share manifest.xml with users
Or submit to Office Add-ins Store
Provide installation instructions



Known Limitations

Exact Text Matching: Highlighting requires exact text matches. Paraphrased risks may not highlight.
Single Document: Currently processes one document at a time. No multi-document comparison in add-in.
Session Storage: Analysis results not persisted. Closing Word loses data.
Network Dependency: Requires active internet connection and backend availability.
Token Limits: Very large documents may exceed API token limits.

Future Enhancements
Potential improvements for future versions:

 Offline mode with cached responses
 Multi-document comparison
 Export analysis to PDF/DOCX
 Custom risk templates
 Team collaboration features
 Analysis history
 Advanced citation extraction
 Voice input for Q&A
 Mobile support (Word Online)

Browser Console Debugging
Access browser console in Word:
Windows: F12 or Ctrl+Shift+I
Mac: Cmd+Option+I
Useful console commands:
javascript// Check current state
console.log(currentAnalysis);
console.log(currentDocumentText);

// Test API connection
await apiService.healthCheck();

// Reload add-in
location.reload();
Contributing
Contributions welcome! Please:

Fork the repository
Create a feature branch
Make your changes
Test thoroughly
Submit a pull request

License
MIT License - See LICENSE file for details
Support
For issues and questions:

GitHub Issues: [repository-url]/issues
Documentation: [repository-url]/wiki

Acknowledgments

Microsoft Office.js team for excellent documentation
LangChain community for LangGraph framework
OpenAI for GPT models


Note: This add-in is for educational/portfolio purposes. For production use with sensitive legal documents, implement additional security measures, data encryption, and compliance with relevant regulations.

---

This README is:
- Comprehensive and professional
- Safe for public GitHub (no personal info, API keys, or credentials)
- Includes installation, setup, and troubleshooting
- Has proper warnings about security and production use
- Provides clear examples and testing procedures
- Documents known limitations honestly
- Ready for immediate upload to GitHub

You can copy this directly to a file named `README.md` in your `frontend/word-addin/` directory.