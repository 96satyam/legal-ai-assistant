# Legal AI Assistant - Microsoft Word Add-in

## Overview

The Legal AI Assistant is a powerful Microsoft Word add-in designed to revolutionize contract analysis by integrating advanced AI capabilities directly into your workflow. Built with Office.js and React for the frontend, and a robust FastAPI backend leveraging LangGraph multi-agent systems and OpenAI's GPT models, this solution provides real-time, intelligent insights into legal documents. It helps legal professionals, businesses, and individuals quickly identify risks, ensure compliance, and understand complex contractual language with unprecedented efficiency.

## Key Features & Benefits

### 1. AI-Powered Contract Analysis
- **Real-time Insights**: Analyze contracts directly within Word with a single click, transforming lengthy review processes into instant assessments.
- **Risk Identification & Scoring**: Automatically identify potential legal risks within clauses, categorized by severity (Critical, High, Medium, Low).
- **Clause Extraction & Categorization**: Intelligently extract and categorize various contract clauses, providing a structured overview of the document's components.
- **Compliance Checking**: Automatically assess contracts against common legal standards and regulations (e.g., GDPR), ensuring adherence and minimizing legal exposure.
- **Comprehensive Risk Reports**: Generate detailed reports that summarize overall risk, compliance status, and actionable insights.

### 2. Interactive Risk Highlighting
- **Visual Risk Cues**: Instantly highlight risky clauses directly in the Word document, making critical areas easy to spot.
- **Color-Coded Severity**: Risks are color-coded based on their severity for quick visual comprehension:
  - **Red**: Critical risks requiring immediate attention.
  - **Orange**: High risks with significant potential impact.
  - **Yellow**: Medium risks that should be reviewed.
  - **Light Green**: Low risks with minor implications.
- **Click-to-Highlight**: Seamlessly navigate from the analysis report to the corresponding clause in the document with a single click.

### 3. Conversational Q&A
- **Natural Language Interaction**: Ask questions about your contract in plain English and receive AI-powered answers.
- **Contextual Responses**: Get accurate answers derived directly from the document's content, ensuring relevance and precision.
- **Session History**: Maintain a continuous conversation history within the add-in, allowing for iterative questioning and deeper understanding.
- **Citation Support**: Answers include citations, which can be clicked to highlight the source text in the document, enhancing trustworthiness and verifiability.

### 4. Professional User Interface
- **Intuitive Design**: A clean, modern, and user-friendly interface built with Microsoft Fluent Design principles.
- **Tabbed Navigation**: Easily switch between "Analysis" and "Q&A" modes for a streamlined user experience.
- **Responsive & Robust**: Features loading states, comprehensive error handling, and a responsive design for optimal performance across different screen sizes.

## Use Cases

- **Legal Professionals**: Expedite contract review, identify potential liabilities, and ensure compliance with regulations.
- **Business Owners**: Quickly understand legal documents, assess risks in agreements, and make informed decisions.
- **Compliance Officers**: Automate compliance checks against internal policies and external regulations.
- **Anyone dealing with contracts**: Gain clarity and confidence when reviewing leases, service agreements, terms & conditions, and more.

## Technology Stack

### Frontend (Microsoft Word Add-in)
- **Office.js**: Microsoft Office Add-in API for deep integration with Word functionalities.
- **React**: A declarative, component-based JavaScript library for building dynamic user interfaces.
- **JavaScript (ES6+)**: Modern JavaScript for robust and maintainable code.
- **Webpack**: Essential for module bundling, asset management, and running a local development server.
- **office-addin-dev-certs**: Manages SSL certificates for secure local development.

### Backend (FastAPI & AI Agents)
- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
- **Uvicorn**: An ASGI server for running FastAPI applications.
- **LangGraph**: A library for building robust, stateful, and multi-agent applications with LLMs, enabling complex AI workflows.
- **LangChain**: Framework for developing applications powered by language models.
- **OpenAI GPT-4/3.5**: Advanced large language models used for core analysis, risk assessment, compliance checks, and Q&A.
- **ChromaDB**: An open-source embedding database, used as a vector store for efficient retrieval-augmented generation (RAG).
- **SQLAlchemy**: Python SQL toolkit and Object Relational Mapper (ORM) for database interactions.
- **python-docx & PyPDF2**: Libraries for parsing and extracting text from `.docx` and `.pdf` documents.
- **spaCy**: An industrial-strength natural language processing (NLP) library for entity extraction and text processing.
- **python-dotenv**: For managing environment variables securely.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── agents/              # LangGraph agents (parser, risk, compliance, RAG, supervisor)
│   │   ├── api/                 # FastAPI endpoints (analysis, qa, documents)
│   │   ├── core/                # Configuration, database setup
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic schemas for data validation
│   │   └── utils/               # Document parsing, embeddings
│   ├── legal_ai.db              # SQLite database file
│   ├── requirements.txt         # Python dependencies
│   └── main.py                  # FastAPI application entry point
├── frontend/
│   └── word-addin/
│       ├── src/
│       │   ├── taskpane/        # Main UI logic, API service, components
│       │   └── commands/        # Add-in commands
│       ├── assets/              # Icons and images
│       ├── manifest.xml         # Office Add-in manifest
│       ├── webpack.config.js    # Webpack configuration
│       └── package.json         # Frontend dependencies
├── data/                        # Stores ChromaDB embeddings and uploaded documents
└── README.md                    # Project documentation
```

## Prerequisites

Before you begin, ensure you have the following installed:

-   **Node.js**: Version 18.0.0 or higher
-   **npm**: Version 8.0.0 or higher
-   **Python**: Version 3.9 or higher
-   **pip**: Python package installer
-   **Microsoft Word**: Desktop version (Windows/Mac)
-   **OpenAI API Key**: Required for the backend to interact with GPT models.

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/legal-ai-assistant.git
cd legal-ai-assistant
```

### 2. Backend Setup

Navigate to the `backend` directory:

```bash
cd backend
```

**Create a Virtual Environment (Recommended):**

```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

**Install Python Dependencies:**

```bash
pip install -r requirements.txt
```

**Configure Environment Variables:**

Create a `.env` file in the `backend/` directory and add your OpenAI API key:

```
OPENAI_API_KEY="your_openai_api_key_here"
```

**Run the Backend Server:**

```bash
uvicorn app.main:app --reload --port 8000
```
The backend API will be running on `http://localhost:8000`.

### 3. Frontend (Word Add-in) Setup

Open a new terminal and navigate to the `frontend/word-addin` directory:

```bash
cd ../frontend/word-addin
```

**Install Node.js Dependencies:**

```bash
npm install
```

**Install SSL Certificates:**

The add-in requires HTTPS for local development. This command installs the necessary self-signed certificates:

```bash
npm run cert:install
```
*Note: On Windows, you may need to run your terminal as an Administrator. On Mac, you may be prompted for your password.*

**Verify Certificate Installation:**

```bash
npm run cert:verify
```
Expected output: `You already have trusted access to https://localhost`

**Start the Development Server:**

```bash
npm run dev-server
```
This starts the webpack dev server on `https://localhost:3000`. Keep this running.

### 4. Load the Add-in in Word

**Option 1: Automatic (Recommended)**

Open a **new** terminal (while the `dev-server` is still running) in the `frontend/word-addin` directory and run:

```bash
npm run start:desktop
```
This command will automatically:
-   Start the dev server (if not already running)
-   Open Microsoft Word
-   Sideload the add-in into Word

**Option 2: Manual Sideloading**

If automatic sideloading doesn't work or you prefer manual control:

-   **Windows:**
    1.  Open Microsoft Word.
    2.  Go to `Insert` tab -> `Get Add-ins` -> `My Add-ins` tab.
    3.  Click `Upload My Add-in` (or `Manage My Add-ins` -> `Upload My Add-in`).
    4.  Browse to the `manifest.xml` file located in `frontend/word-addin/` and click `Upload`.

-   **Mac:**
    1.  Copy the `manifest.xml` file from `frontend/word-addin/` to the following directory:
        `/Users/{your_username}/Library/Containers/com.microsoft.Word/Data/Documents/wef`
    2.  Restart Microsoft Word.
    3.  Go to `Insert` tab -> `Add-ins` -> `My Add-ins`. The Legal AI Assistant should appear.

## Configuration

### Backend API URL

If your backend API is running on a different host or port, update the `API_BASE_URL` in `frontend/word-addin/src/taskpane/api-service.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api'; // Change to your backend URL if different
```

### Manifest Configuration

Edit `frontend/word-addin/manifest.xml` to customize add-in details such as:
-   Add-in name and description
-   Icon URLs
-   Support URL
-   Default settings

## Building for Production

### Development Build

```bash
cd frontend/word-addin
npm run build:dev
```

### Production Build

```bash
cd frontend/word-addin
npm run build
```
The compiled assets will be located in the `dist/` directory.

## API Integration Details

The Word add-in communicates with the FastAPI backend via the following endpoints:

### 1. Health Check
-   **GET** `/` (or `/docs` for FastAPI's auto-generated docs)
-   **Response**: `{"status": "ok", "message": "Welcome to the AI Legal Assistant API!"}` (from `/`) or a successful HTTP 200 for `/docs`.

### 2. Contract Analysis
-   **POST** `/api/analysis/`
-   **Body**:
    ```json
    {
      "document_text": "string (full text of the document)"
    }
    ```
-   **Response**:
    ```json
    {
      "report": "string (markdown formatted analysis report)",
      "risks": [
        {
          "clause_text": "string",
          "risk_level": "string (e.g., 'high', 'medium')",
          "risk_type": "string (e.g., 'liability', 'compliance')",
          "description": "string",
          "mitigation": "string"
        }
      ]
    }
    ```

### 3. Conversational Q&A
-   **POST** `/api/qa/ask`
-   **Body**:
    ```json
    {
      "document_id": "string (unique ID for the document session)",
      "question": "string (the user's question)",
      "document_text": "string (optional: full text of the document, if not previously sent)"
    }
    ```
-   **Response**:
    ```json
    {
      "answer": "string (AI-generated answer)",
      "citations": ["string (relevant text snippets from the document)"],
      "document_id": "string"
    }
    ```

### CORS Configuration

The backend must be configured to allow requests from your frontend's URL (e.g., `https://localhost:3000` for local development). This is handled in `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000", "http://localhost:3000"], # Ensure your frontend URL is here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Detailed Feature Workflows

### Analysis Workflow

1.  User opens a document in Word and clicks the "Analyze Document" button in the add-in.
2.  The add-in uses Office.js to read the entire text content of the active Word document.
3.  The document text is sent to the backend's `/api/analysis/` endpoint.
4.  The backend initiates a LangGraph multi-agent workflow:
    *   **Document Parser Agent**: Extracts clauses and key entities from the raw text.
    *   **Risk Assessor Agent**: Identifies potential legal risks within the extracted clauses and assigns severity levels.
    *   **Compliance Checker Agent**: Evaluates the document against predefined compliance standards.
    *   **Report Aggregator Agent**: Synthesizes findings from all agents into a comprehensive executive summary, key risk analysis, and compliance assessment report.
5.  The backend returns the aggregated report and a list of identified risks (including their text and severity) to the frontend.
6.  The frontend displays the overall risk score, the detailed analysis report, and interactive risk summary cards in the task pane.
7.  Users can click on individual risk cards to automatically highlight the corresponding clause in the Word document.

### Q&A Workflow

1.  User switches to the "Q&A" tab in the add-in.
2.  The user types a question about the document or selects a suggested query.
3.  The add-in sends the question along with the document's context (or a reference ID) to the backend's `/api/qa/ask` endpoint.
4.  The backend activates the RAG (Retrieval Augmented Generation) agent:
    *   It retrieves relevant document chunks from the ChromaDB vector store based on the user's question.
    *   It uses an LLM (e.g., GPT-4) to generate a concise and accurate answer, grounded in the retrieved document content.
5.  The backend returns the AI-generated answer and any supporting citations (text snippets from the document).
6.  The frontend displays the answer in a conversational format, maintaining the chat history.
7.  If citations are provided, users can click on them to highlight the source text in the Word document, verifying the answer's origin.

### Highlighting System

The add-in leverages Word's native search and highlighting API via Office.js:

```javascript
// Example: Search for text and apply highlight
const searchResults = context.document.body.search(text, {
  matchCase: false,
  matchWholeWord: false
});

// Iterate through results and apply color
searchResults.items.forEach(range => {
  range.font.highlightColor = '#ff0000'; // Example: Red for critical risks
  range.select(); // Optionally select/scroll to the text
});
```

## Troubleshooting

### Certificate Errors (`NET::ERR_CERT_AUTHORITY_INVALID`)

-   **Symptom**: Browser or add-in displays certificate warnings or errors.
-   **Solution**:
    1.  Uninstall and reinstall development certificates: `npm run cert:install`
    2.  Clear your browser's cache.
    3.  Restart Microsoft Word.

### Add-in Not Loading

-   **Symptom**: The add-in pane remains blank or shows an error.
-   **Solution**:
    1.  Ensure the frontend development server is running (`npm run dev-server`).
    2.  Verify you can access `https://localhost:3000/taskpane.html` directly in your browser.
    3.  Check if any firewall is blocking port `3000`.
    4.  Confirm that the URLs in `manifest.xml` are correct.

### CORS Errors (`Access to fetch blocked by CORS`)

-   **Symptom**: Requests to the backend fail with Cross-Origin Resource Sharing errors.
-   **Solution**: Verify that your backend's CORS configuration (in `backend/app/main.py`) explicitly includes `https://localhost:3000` (and any other frontend origins you are using).

### Backend Connection Failed

-   **Symptom**: The add-in cannot connect to the backend API.
-   **Solution**:
    1.  Ensure the backend server is running on port `8000` (`uvicorn app.main:app --reload --port 8000`).
    2.  Verify you can access `http://localhost:8000/` or `http://localhost:8000/docs` in your browser.
    3.  Check if any firewall is blocking port `8000`.

## Testing

### Manual Testing Checklist

-   [ ] The add-in loads successfully in Microsoft Word without errors.
-   [ ] The "Analyze Document" button correctly processes a sample contract.
-   [ ] Risk cards and the analysis report are displayed accurately in the task pane.
-   [ ] Clicking on a risk card highlights the corresponding text in the Word document.
-   [ ] The "Q&A" tab is functional after document analysis.
-   [ ] You can ask questions about the document and receive relevant AI-generated responses.
-   [ ] The conversation history persists within the Q&A session.
-   [ ] Citations (if provided) can be clicked to highlight source text.
-   [ ] No console errors are present in the browser's Developer Tools (F12).

### Sample Test Contract

You can use the following text as a sample contract for testing the analysis and Q&A features:

```
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
```

**Expected Analysis Results:**
-   Approximately 4-5 risks identified.
-   An overall risk assessment of "High" or "Critical" due to "UNLIMITED LIABILITY" and "unspecified jurisdiction".
-   Multiple clause categories (e.g., Confidentiality, Liability, Termination, IP, Governing Law).
-   Q&A answers should be based directly on the content of this sample.

## Performance Considerations

-   **Token Usage**: Be mindful of LLM token limits. Analysis typically uses ~500-2000 tokens per request, and Q&A ~300-1000 tokens per question.
-   **Document Size Limits**: Recommended maximum document size is around 10,000 words. Very large documents may lead to timeouts (>30 seconds) or exceed API token limits. Consider implementing document chunking strategies for extremely large contracts.
-   **Rate Limiting**: OpenAI API has rate limits. Implement exponential backoff for retries and provide informative error messages to users during high usage.

## Security Considerations

-   **Data Privacy**: Document text is sent to the backend API for processing. Ensure your backend implements robust data handling, storage, and encryption practices, especially for sensitive legal documents. The add-in itself does not persistently store document data.
-   **API Keys**: Never hardcode or commit API keys directly into the repository. Use environment variables (e.g., `.env` file) for secure management. Implement proper authentication and authorization mechanisms for production APIs.
-   **SSL/TLS**: Local development uses self-signed certificates. For production deployment, ensure valid SSL certificates are used, and update manifest URLs accordingly.

## Deployment

For deploying the Legal AI Assistant to a production environment:

1.  **Update Manifest**:
    *   Change all `localhost` URLs in `frontend/word-addin/manifest.xml` to your production domain URLs.
    *   Update the version number and set production icon URLs.
2.  **Build Frontend Assets**:
    ```bash
    cd frontend/word-addin
    npm run build
    ```
3.  **Host Frontend Files**:
    *   Upload the contents of the `dist/` folder to a web server (e.g., Azure Static Web Apps, AWS S3, Nginx).
    *   Ensure HTTPS is configured for your hosting environment.
    *   Verify all production URLs are accessible.
4.  **Update Backend**:
    *   Update the CORS configuration in `backend/app/main.py` to allow your production frontend domain.
    *   Configure production API endpoints and database connections.
    *   Implement robust authentication and authorization.
5.  **Distribute Manifest**:
    *   Share the updated `manifest.xml` with your users for sideloading.
    *   Alternatively, consider submitting your add-in to the Office Add-ins Store for broader distribution.

## Known Limitations

-   **Exact Text Matching**: The highlighting feature relies on exact text matches. Minor variations or paraphrased risks may not highlight correctly.
-   **Single Document Processing**: The current add-in processes one document at a time. Multi-document comparison is a future enhancement.
-   **Session Storage**: Analysis results and Q&A history are not persistently stored across Word sessions. Closing Word will clear the data.
-   **Network Dependency**: Requires an active internet connection and availability of the backend API.
-   **Token Limits**: Very large documents may exceed LLM API token limits, leading to incomplete analysis or errors.

## Future Enhancements

Potential improvements and features for future versions include:

-   Offline mode with cached responses for improved user experience.
-   Multi-document comparison capabilities within the add-in.
-   Option to export analysis reports to PDF or DOCX formats.
-   Customizable risk templates and compliance standards.
-   Team collaboration features for shared document analysis.
-   Analysis history and versioning for tracking changes over time.
-   Advanced citation extraction and summarization.
-   Voice input integration for Q&A.
-   Support for Word Online and mobile versions of Word.

## Browser Console Debugging

To access the browser console for debugging the add-in within Word:

-   **Windows**: Press `F12` or `Ctrl+Shift+I`.
-   **Mac**: Press `Cmd+Option+I`.

Useful console commands:

```javascript
// Check current state variables
console.log(currentAnalysis);
console.log(currentDocumentText);

// Test API connection
await apiService.healthCheck();

// Reload the add-in
location.reload();
```

## Contributing

Contributions are welcome! If you'd like to contribute:

1.  Fork the repository.
2.  Create a new feature branch (`git checkout -b feature/YourFeature`).
3.  Make your changes and ensure they are well-tested.
4.  Commit your changes (`git commit -m 'Add new feature'`).
5.  Push to the branch (`git push origin feature/YourFeature`).
6.  Submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Support

For issues, questions, or feature requests, please use:

-   **GitHub Issues**: [https://github.com/yourusername/legal-ai-assistant/issues](https://github.com/yourusername/legal-ai-assistant/issues)
-   **Documentation**: (If a separate wiki or documentation site is created, link it here)

## Acknowledgments

-   Microsoft Office.js team for providing the framework for Office Add-ins.
-   LangChain and LangGraph communities for powerful LLM orchestration tools.
-   OpenAI for their cutting-edge language models.

---

**Disclaimer**: This add-in is provided for educational and portfolio purposes. For production use with sensitive legal documents, it is imperative to implement additional security measures, robust data encryption, and ensure full compliance with all relevant legal and data protection regulations.
