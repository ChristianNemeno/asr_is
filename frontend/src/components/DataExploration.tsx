import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface Bin {
  range: string
  count: number
}

interface ExplorationData {
  source: string
  total_samples: number
  durations: Bin[]
  word_counts: Bin[]
  languages: string[]
}

function DataExploration({ section = 'all' }: { section?: 'all' | 'duration' | 'wordcount' | 'language' | 'waveform' }) {
  const showAll = section === 'all'
  const [data, setData] = useState<ExplorationData | null>(null)

  useEffect(() => {
    fetch('/api/training/data-exploration')
      .then(r => r.json())
      .then(setData)
      .catch(console.error)
  }, [])

  if (!data) return null

  const langCounts = data.languages
    ? Object.entries(
        data.languages.reduce((acc, l) => { acc[l] = (acc[l] || 0) + 1; return acc }, {} as Record<string, number>)
      ).map(([name, count]) => ({ name, count }))
    : []

  return (
    <section className="section">
      <h2 className="section-title">Data Exploration</h2>
      {(showAll || section !== 'waveform') && (
        <p className="section-desc">
          {data.total_samples} samples from FLEURS (fil_ph + ceb_ph) — audio duration, word count distributions.
        </p>
      )}

      {(showAll || section !== 'waveform') && (
      <div className="chart-grid">
        {(showAll || section === 'duration') && (
        <div className="chart-card">
          <h3 className="chart-title">Audio Duration Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.durations} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" />
              <XAxis dataKey="range" stroke="#555" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" height={50} />
              <YAxis stroke="#555" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: 12 }}
                formatter={(v: unknown) => [`${Number(v)} samples`, 'Count']}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {data.durations.map((d, i) => (
                  <Cell key={d.range} fill={['#60a5fa', '#e0e0e0', '#a78bfa', '#f59e0b', '#f87171', '#60a5fa'][i % 6]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        )}

        {(showAll || section === 'wordcount') && (
        <div className="chart-card">
          <h3 className="chart-title">Word Count Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.word_counts} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" />
              <XAxis dataKey="range" stroke="#555" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" height={50} />
              <YAxis stroke="#555" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: 12 }}
                formatter={(v: unknown) => [`${Number(v)} samples`, 'Count']}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {data.word_counts.map((d, i) => (
                  <Cell key={d.range} fill={['#a78bfa', '#60a5fa', '#e0e0e0', '#f59e0b', '#f87171', '#a78bfa'][i % 6]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        )}

        {(showAll || section === 'language') && langCounts.length > 0 && (
          <div className="chart-card">
            <h3 className="chart-title">Language Distribution (FLEURS Samples)</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={langCounts} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" />
                <XAxis dataKey="name" stroke="#555" tick={{ fontSize: 12 }} />
                <YAxis stroke="#555" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: 12 }}
                  formatter={(v: unknown) => [`${Number(v)} samples`, 'Count']}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {langCounts.map((d, i) => (
                    <Cell key={d.name} fill={i === 0 ? '#f87171' : '#a78bfa'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
      )}

      {(showAll || section === 'waveform') && (
        <div className="chart-card exploration-card">
          <h3 className="chart-title">Sample Waveforms &amp; Mel Spectrograms</h3>
          <img
            src="/api/plots/data_exploration/sample_waveforms.png"
            alt="Sample waveforms and mel spectrograms"
            className="plot-img"
          loading="lazy"
          />
        </div>
      )}
    </section>
  )
}

export default DataExploration
