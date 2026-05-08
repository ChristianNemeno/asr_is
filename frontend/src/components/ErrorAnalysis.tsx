import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'

interface Breakdown {
  substitutions: number; deletions: number; insertions: number; hits: number
}

interface Metrics {
  test_wer: number; test_cer: number; train_steps: number
  per_language: Record<string, { mean_wer: number; n: number }>
  error_breakdown: Breakdown
  n_samples: number
}

interface ComparisonRow {
  rank: number; language: string; reference: string
  baseline_prediction: string; baseline_wer: number; baseline_cer: number
  finetuned_prediction: string; finetuned_wer: number; finetuned_cer: number
}

const breakdownColors: Record<string, string> = {
  Substitutions: '#f87171',
  Deletions: '#60a5fa',
  Insertions: '#4ade80',
  Hits: '#94a3b8',
}

function ComparisonRow({ c }: { c: ComparisonRow }) {
  const [open, setOpen] = useState(false)
  const delta = c.baseline_wer - c.finetuned_wer
  const better = delta > 1 ? 'finetuned' : delta < -1 ? 'baseline' : 'tie'

  return (
    <>
      <tr
        className={`transcript-row ${open ? 'expanded' : ''}`}
        onClick={() => setOpen(!open)}
      >
        <td>{c.rank}</td>
        <td><span className={`lang-badge ${c.language}`}>{c.language || '—'}</span></td>
        <td className="text-cell">{c.reference}</td>
        <td className={`mono ${better === 'baseline' ? 'better' : ''}`}>{c.baseline_wer.toFixed(1)}%</td>
        <td className={`mono ${better === 'finetuned' ? 'better' : ''}`}>{c.finetuned_wer.toFixed(1)}%</td>
        <td className={`mono ${delta > 0 ? 'positive' : delta < 0 ? 'negative' : ''}`}>{delta > 0 ? '+' : ''}{delta.toFixed(1)}%</td>
      </tr>
      <AnimatePresence>
        {open && (
          <motion.tr
            className="comparison-expand"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            <td colSpan={6}>
              <div className="expand-compare">
                <div className="expand-col">
                  <span className="expand-label">Reference</span>
                  <p>{c.reference}</p>
                </div>
                <div className="expand-col baseline-col">
                  <span className="expand-label">Baseline <span className="model-tag">zero-shot</span></span>
                  <p>{c.baseline_prediction}</p>
                  <div className="expand-metrics">
                    <span>WER: <strong>{c.baseline_wer.toFixed(1)}%</strong></span>
                    <span>CER: <strong>{c.baseline_cer.toFixed(1)}%</strong></span>
                  </div>
                </div>
                <div className="expand-col finetuned-col">
                  <span className="expand-label">Fine-tuned <span className="model-tag fine-tuned">our model</span></span>
                  <p>{c.finetuned_prediction}</p>
                  <div className="expand-metrics">
                    <span>WER: <strong>{c.finetuned_wer.toFixed(1)}%</strong></span>
                    <span>CER: <strong>{c.finetuned_cer.toFixed(1)}%</strong></span>
                  </div>
                </div>
              </div>
            </td>
          </motion.tr>
        )}
      </AnimatePresence>
    </>
  )
}

function ErrorAnalysis({
  metrics,
  comparisons,
}: {
  metrics: Metrics | null
  comparisons: ComparisonRow[]
}) {
  return (
    <motion.section
      className="section"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="section-title">Error Analysis</h2>

      {metrics && (
        <div className="error-stats">
          <div className="stat-cards mini">
            <div className="stat-card">
              <span className="stat-value">{metrics.per_language?.tagalog?.mean_wer?.toFixed(1)}%</span>
              <span className="stat-label">Tagalog WER</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{metrics.per_language?.cebuano?.mean_wer?.toFixed(1)}%</span>
              <span className="stat-label">Cebuano WER</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{metrics.n_samples?.toLocaleString()}</span>
              <span className="stat-label">Test Samples</span>
            </div>
          </div>
        </div>
      )}

      <div className="chart-grid">
        {metrics?.per_language && (
          <div className="chart-card">
            <h3 className="chart-title">WER by Language</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={Object.entries(metrics.per_language).map(([lang, v]) => ({
                  language: lang,
                  wer: v.mean_wer * 100,
                  n: v.n,
                }))}
                margin={{ top: 4, right: 4, bottom: 4, left: 4 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" />
                <XAxis dataKey="language" stroke="#555" tick={{ fontSize: 12 }} />
                <YAxis stroke="#555" tick={{ fontSize: 11 }} unit="%" />
                <Tooltip
                  contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: 12 }}
                  formatter={(v) => [`${Number(v).toFixed(1)}%`, 'WER']}
                />
                <Bar dataKey="wer" radius={[6, 6, 0, 0]}>
                  {Object.keys(metrics.per_language).map((lang, i) => (
                    <Cell key={lang} fill={i === 0 ? '#f87171' : '#a78bfa'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {metrics?.error_breakdown && (
          <div className="chart-card">
            <h3 className="chart-title">Error Breakdown (S/D/I/H)</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={[
                  { label: 'Substitutions', value: metrics.error_breakdown.substitutions },
                  { label: 'Deletions', value: metrics.error_breakdown.deletions },
                  { label: 'Insertions', value: metrics.error_breakdown.insertions },
                  { label: 'Hits', value: metrics.error_breakdown.hits },
                ]}
                margin={{ top: 4, right: 4, bottom: 4, left: 4 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" />
                <XAxis dataKey="label" stroke="#555" tick={{ fontSize: 12 }} />
                <YAxis stroke="#555" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: 12 }}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {['Substitutions', 'Deletions', 'Insertions', 'Hits'].map(label => (
                    <Cell key={label} fill={breakdownColors[label]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {comparisons.length > 0 && (
        <>
          <h3 className="subsection-title">Sample Comparison: Baseline vs Fine-tuned</h3>
          <p className="section-desc">
            {comparisons.length} random test samples. Click any row to expand full text.
            <span className="better-note"> Green = better model per row.</span>
          </p>
          <div className="sample-table-wrap">
            <table className="sample-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Lang</th>
                  <th>Reference</th>
                  <th>Baseline WER</th>
                  <th>Fine-tuned WER</th>
                  <th>Δ WER</th>
                </tr>
              </thead>
              <tbody>
                {comparisons.map(c => (
                  <ComparisonRow key={c.rank} c={c} />
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </motion.section>
  )
}

export default ErrorAnalysis
