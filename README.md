# M-Pesa Analyzer Pro 📊

A production-ready Streamlit application for analyzing M-Pesa statements (PDF and CSV) with AI-powered financial insights using Google Gemini.

## Features

- **Multi-Format Support**: Upload standard M-Pesa PDF or CSV statements.
- **Interactive Dashboard**:
    - Financial Overview (Income, Expenses, Savings).
    - Monthly Trends.
    - Category Breakdown (Airtime, Pay Bill, etc.).
    - Daily Activity Heatmaps.
- **Transaction Explorer**: Searchable and filterable transaction history.
- **AI Financial Advisor**: Get personalized spending summaries and recommendations powered by Google Gemini.
- **Privacy First**: Data is processed locally in memory. Only summarized statistics are sent to the AI (and only when you request it).

## Installation

### Prerequisites
- Python 3.10+
- A Google Gemini API Key (Get one [here](https://aistudio.google.com/app/apikey))

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd pesaView
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**
   Copy `.env.example` to `.env` and add your API key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

## M-Pesa Statement Formats

### CSV
Supported columns (auto-detected):
- `Receipt No.`
- `Completion Time`
- `Details`
- `Paid In`
- `Withdrawn`
- `Balance`

### PDF
The parser supports standard personal M-Pesa statements generated from the mySafaricom App or USSD *234#.

## Development

Run unit tests:
```bash
pytest
```

## Technologies
- **Streamlit**: Web UI
- **Pandas**: Data processing
- **Plotly**: Interactive visualizations
- **pdfplumber**: PDF extraction
- **Google Generative AI**: Financial insights
