import React from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import './SentimentChart.css'

function SentimentChart({ statistics }) {
  if (!statistics) {
    return null
  }

  const positive = statistics.positive ?? statistics.sentiment?.positive ?? 0
  const neutral = statistics.neutral ?? statistics.sentiment?.neutral ?? 0
  const negative = statistics.negative ?? statistics.sentiment?.negative ?? 0

  const data = [
    { name: 'Positive', value: positive },
    { name: 'Neutral', value: neutral },
    { name: 'Negative', value: negative },
  ]

  const COLORS = {
    Positive: '#10b981',
    Neutral: '#6b7280',
    Negative: '#ef4444',
  }

  const renderCustomLabel = ({ name, percent }) => {
    return `${name}: ${(percent * 100).toFixed(0)}%`
  }

  return (
    <div className="chart-container">
      <h2>📈 Sentiment Distribution</h2>
      <ResponsiveContainer width="100%" height={400}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomLabel}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

export default SentimentChart
