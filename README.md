# Dr. Martens Review Analysis System

A full-stack web application that extracts and analyzes customer reviews from Google Places API with AI-powered sentiment analysis.

## 🌟 Features

### Core Features
- **Google Places Integration**: Automatically fetch reviews from any Dr. Martens store location
- **Sentiment Analysis**: AI-powered analysis using TextBlob to classify reviews as positive, negative, or neutral
- **Visual Analytics**: Interactive charts and statistics showing sentiment distribution
- **Real-time Search**: Search for any Dr. Martens store location worldwide
- **Beautiful UI**: Modern, responsive design with gradient backgrounds and smooth animations
- **Detailed Metrics**: View polarity scores, subjectivity ratings, and overall statistics

### 🤖 AI-Powered Features (NEW!)
- **GPT-4 Insights Dashboard**: Comprehensive business intelligence analysis
  - Executive summaries perfect for presentations
  - Automatic theme extraction and categorization
  - Customer strengths and pain points identification
  - Actionable recommendations with priority levels
  - Customer persona identification
  - Competitive intelligence insights
  - Trend analysis and predictions
- **Interactive Chat Assistant**: Ask questions about reviews in natural language
  - Context-aware AI responses
  - Cite specific examples from reviews
  - Instant insights without manual analysis
- **Professional Report Generation**: Export analysis as markdown reports
- **Deep Sentiment Analysis**: Goes beyond positive/negative classification

## 🏗️ Architecture

### Backend (Python/Flask)
- Flask REST API server
- Google Places API integration for review extraction
- TextBlob for natural language processing and sentiment analysis
- CORS enabled for frontend communication

### Frontend (React/Vite)
- Vite for fast development and optimized builds
- React for component-based UI
- Recharts for data visualization
- Axios for API communication
- Responsive design with CSS Grid and Flexbox

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Google Cloud Platform account with Places API enabled
- Google Places API key

## 🚀 Getting Started

### 1. Get Google Places API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Places API"
4. Go to "Credentials" and create an API key
5. (Optional) Restrict the API key to only Places API for security

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download TextBlob corpora
python -m textblob.download_corpora

# Create .env file
copy .env.example .env  # On Windows
# OR
cp .env.example .env    # On macOS/Linux

# Edit .env file and add your Google API key
# GOOGLE_API_KEY=your_actual_api_key_here

# Run the server
python app.py
```

The backend server will start at `http://localhost:5000`

### 3. Frontend Setup

Note: If you encounter PowerShell script execution issues on Windows, you may need to run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will start at `http://localhost:3000`

## 📱 Usage

1. **Start both servers** (backend on port 5000, frontend on port 3000)
2. **Open your browser** to `http://localhost:3000`
3. **Enter a search query** like "Dr. Martens New York" or "Dr. Martens London"
4. **Click "Search & Analyze"** to fetch and analyze reviews
5. **View the results**:
   - Place information with overall rating
   - Statistics dashboard with sentiment breakdown
   - Pie chart visualization
   - Individual review cards with sentiment analysis

## 🔌 API Endpoints

### Backend API (Port 5000)

- `GET /api/health` - Health check
- `POST /api/search` - Search for a place
  ```json
  {
    "query": "Dr. Martens New York"
  }
  ```
- `POST /api/reviews` - Get reviews for a place
  ```json
  {
    "place_id": "ChIJ..."
  }
  ```
- `POST /api/analyze` - Analyze text sentiment
  ```json
  {
    "text": "Great shoes, love them!"
  }
  ```

## 📊 Sentiment Analysis

The system uses TextBlob for sentiment analysis, which provides:

- **Polarity**: Score from -1 (negative) to +1 (positive)
- **Subjectivity**: Score from 0 (objective) to 1 (subjective)
- **Classification**: Positive, Negative, or Neutral based on polarity thresholds

### Classification Rules:
- **Positive**: Polarity > 0.1
- **Negative**: Polarity < -0.1
- **Neutral**: Polarity between -0.1 and 0.1

## 🛠️ Tech Stack

### Backend
- Flask 3.0.0
- Flask-CORS 4.0.0
- TextBlob 0.17.1
- Requests 2.31.0
- Python-dotenv 1.0.0

### Frontend
- React 18.3.1
- Vite 5.4.1
- Axios 1.6.2
- Recharts 2.10.3

## 📝 Project Structure

```
DrMartens/
├── backend/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   └── README.md             # Backend documentation
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── ReviewCard.jsx
│   │   │   ├── Statistics.jsx
│   │   │   └── SentimentChart.jsx
│   │   ├── App.jsx           # Main application
│   │   ├── App.css           # Application styles
│   │   ├── main.jsx          # Entry point
│   │   └── index.css         # Global styles
│   ├── index.html            # HTML template
│   ├── package.json          # Node dependencies
│   ├── vite.config.js        # Vite configuration
│   └── README.md             # Frontend documentation
└── README.md                 # This file
```

## 🎨 Features in Detail

### Review Cards
- Display author name and review time
- Star ratings visualization
- Full review text
- Sentiment badge with emoji
- Polarity and subjectivity scores

### Statistics Dashboard
- Total review count
- Sentiment distribution (positive/negative/neutral)
- Percentage bars for each sentiment
- Average rating from Google
- Average polarity score

### Sentiment Chart
- Interactive pie chart
- Color-coded by sentiment
- Percentage breakdown
- Tooltips on hover

## 🔒 Security Notes

- Keep your `.env` file secure and never commit it to version control
- The `.env.example` file is provided as a template
- Consider implementing rate limiting for production use
- Restrict your Google API key to specific domains/IPs in production

## 🐛 Troubleshooting

### Backend Issues
- **"Google API key not configured"**: Make sure your `.env` file exists and contains `GOOGLE_API_KEY`
- **"No place found"**: Try a more specific search query with city/location
- **Import errors**: Run `pip install -r requirements.txt` and `python -m textblob.download_corpora`

### Frontend Issues
- **Cannot connect to backend**: Ensure backend is running on port 5000
- **CORS errors**: Check that flask-cors is installed and configured
- **PowerShell script errors**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## 📈 Future Enhancements

- [ ] Support for multiple locations comparison
- [ ] Historical data tracking
- [ ] Export reports to PDF/CSV
- [ ] More detailed sentiment analysis (emotions, aspects)
- [ ] User authentication and saved searches
- [ ] Real-time updates via WebSocket
- [ ] Multi-language support
- [ ] Advanced filtering options

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues, questions, or suggestions, please open an issue on the repository.

---

Built with ❤️ for Dr. Martens enthusiasts and data lovers!
