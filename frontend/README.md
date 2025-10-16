# Dr. Martens Review Analysis - Frontend

Modern React frontend built with Vite for analyzing Dr. Martens store reviews.

## Features

- 🎨 Beautiful gradient UI design
- 📱 Fully responsive layout
- 📊 Interactive charts with Recharts
- 🔍 Real-time search
- 💬 Review cards with sentiment analysis
- 📈 Statistics dashboard

## Tech Stack

- React 18.3
- Vite 5.4
- Axios for API calls
- Recharts for data visualization

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

Runs on http://localhost:3000

## Build

```bash
npm run build
```

## Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── ReviewCard.jsx       # Individual review display
│   ├── ReviewCard.css
│   ├── Statistics.jsx       # Stats dashboard
│   ├── Statistics.css
│   ├── SentimentChart.jsx   # Pie chart
│   └── SentimentChart.css
├── App.jsx                  # Main application
├── App.css
├── main.jsx                 # Entry point
└── index.css                # Global styles
```

## Configuration

The frontend is configured to proxy API requests to the backend:

- Development: `http://localhost:5000`
- API requests to `/api/*` are automatically proxied

To change the backend URL, edit `vite.config.js` and `App.jsx`.

## Components

### App.jsx
Main application component that handles:
- Search functionality
- API communication
- State management
- Layout and routing

### ReviewCard
Displays individual review with:
- Author and timestamp
- Star rating
- Review text
- Sentiment badge
- Polarity/subjectivity scores

### Statistics
Shows aggregate metrics:
- Total review count
- Sentiment distribution
- Percentage breakdown
- Average rating
- Average polarity

### SentimentChart
Interactive pie chart showing:
- Sentiment distribution
- Color-coded segments
- Percentage labels
- Interactive tooltips
