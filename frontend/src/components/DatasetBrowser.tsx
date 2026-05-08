import { useState, useRef } from 'react'
import { motion } from 'motion/react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, Legend } from 'recharts'

interface Sample {
  filename: string; language: string; language_code: string
  label: string; duration_sec: number; url: string
}

const pieData = [
  { name: 'FSC (Tagalog)', value: 203000, color: '#4ade80' },
  { name: 'FLEURS Tagalog', value: 1800, color: '#60a5fa' },
  { name: 'FLEURS Cebuano', value: 1800, color: '#a78bfa' },
]

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.03 } },
}

const rowAnim = {
  hidden: { opacity: 0, x: -12 },
  visible: { opacity: 1, x: 0 },
}

function DatasetBrowser({ samples }: { samples: Sample[] }) {
  const [filter, setFilter] = useState('All')
  const [playing, setPlaying] = useState<string | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  const languages = ['All', ...new Set(samples.map(s => s.language))]
  const filtered = filter === 'All' ? samples : samples.filter(s => s.language === filter)

  const play = (filename: string) => {
    if (audioRef.current) audioRef.current.pause()
    if (playing === filename) { setPlaying(null); return }
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
    <motion.section
      className="section"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5 }}
    >
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

      <motion.div
        key={filter}
        className="sample-list"
        variants={stagger}
        initial="hidden"
        animate="visible"
      >
        {filtered.map(sample => (
          <motion.div key={sample.filename} className="sample-row" variants={rowAnim}>
            <button
              className="play-btn"
              onClick={() => play(sample.filename)}
              title={playing === sample.filename ? 'Stop' : 'Play'}
            >
              {playing === sample.filename ? '⏸' : '▶'}
            </button>
            <span className={`lang-badge ${sample.language.toLowerCase()}`}>{sample.language}</span>
            <span className="sample-label">{sample.label}</span>
            <span className="sample-duration">{sample.duration_sec}s</span>
          </motion.div>
        ))}
      </motion.div>

      <div className="chart-grid single-col">
        <div className="chart-card">
          <h3 className="chart-title">Full Training Dataset Composition</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={3}
                dataKey="value"
                label={({ name, percent }) => `${name ?? ''} ${((percent ?? 0) * 100).toFixed(0)}%`}
              >
                {pieData.map(entry => <Cell key={entry.name} fill={entry.color} />)}
              </Pie>
              <Tooltip
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: 12 }}
                formatter={(v) => [`${Number(v).toLocaleString()} samples`, '']}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3 className="chart-title">Dataset Splits by Source</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={[
                { split: 'Train', 'FSC': 165000, 'FLEURS Tagalog': 1000, 'FLEURS Cebuano': 1000 },
                { split: 'Validation', 'FSC': 18000, 'FLEURS Tagalog': 400, 'FLEURS Cebuano': 400 },
                { split: 'Test', 'FSC': 20000, 'FLEURS Tagalog': 400, 'FLEURS Cebuano': 400 },
              ]}
              margin={{ top: 4, right: 4, bottom: 4, left: 4 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" />
              <XAxis dataKey="split" stroke="#555" tick={{ fontSize: 12 }} />
              <YAxis stroke="#555" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: 12 }}
                formatter={(v) => [`${Number(v).toLocaleString()} samples`]}
              />
              <Legend />
              <Bar dataKey="FSC" stackId="s" fill="#4ade80" name="FSC (Tagalog)" radius={[0, 0, 0, 0]} />
              <Bar dataKey="FLEURS Tagalog" stackId="s" fill="#60a5fa" name="FLEURS Tagalog" />
              <Bar dataKey="FLEURS Cebuano" stackId="s" fill="#a78bfa" name="FLEURS Cebuano" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </motion.section>
  )
}

export default DatasetBrowser
