import { useState, useRef } from 'react'

interface Sample {
  filename: string; language: string; language_code: string
  label: string; duration_sec: number; url: string
}

function DatasetBrowser({ samples }: { samples: Sample[] }) {
  const [filter, setFilter] = useState('All')
  const [playing, setPlaying] = useState<string | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  const languages = ['All', ...new Set(samples.map(s => s.language))]
  const filtered = filter === 'All' ? samples : samples.filter(s => s.language === filter)

  const play = (filename: string) => {
    if (audioRef.current) {
      audioRef.current.pause()
    }
    if (playing === filename) {
      setPlaying(null)
      return
    }
    const sample = samples.find(s => s.filename === filename)
    if (sample) {
      const audio = new Audio(sample.url)
      audio.onended = () => setPlaying(null)
      audio.play()
      audioRef.current = audio
      setPlaying(filename)
    }
  }

  if (!samples.length) return null

  return (
    <section className="section">
      <h2 className="section-title">Dataset Samples</h2>
      <p className="section-desc">
        40 audio samples from FLEURS (20 Tagalog, 20 Cebuano) used as test/evaluation references.
      </p>

      <div className="filter-tabs">
        {languages.map(lang => (
          <button
            key={lang}
            className={`filter-tab ${filter === lang ? 'active' : ''}`}
            onClick={() => setFilter(lang)}
          >
            {lang}
          </button>
        ))}
      </div>

      <div className="sample-list">
        {filtered.map(sample => (
          <div key={sample.filename} className="sample-row">
            <button
              className="play-btn"
              onClick={() => play(sample.filename)}
              title={playing === sample.filename ? 'Stop' : 'Play'}
            >
              {playing === sample.filename ? '⏸' : '▶'}
            </button>
            <span className={`lang-badge ${sample.language.toLowerCase()}`}>
              {sample.language}
            </span>
            <span className="sample-label">{sample.label}</span>
            <span className="sample-duration">{sample.duration_sec}s</span>
          </div>
        ))}
      </div>

      <div className="plot-embed">
        <img
          src="/api/plots/splits/summary_dashboard.png"
          alt="Dataset split summary"
          className="plot-img"
        />
      </div>
    </section>
  )
}

export default DatasetBrowser
