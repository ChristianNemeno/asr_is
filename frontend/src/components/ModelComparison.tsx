import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const barColors = {
  baseline: '#60a5fa',
  finetuned: '#e0e0e0',
}

function ModelComparison() {
  const data = [
    { metric: 'WER', baseline: 52.1, finetuned: 20.3 },
    { metric: 'CER', baseline: 17.7, finetuned: 8.6 },
  ]

  return (
    <section className="section">
      <h2 className="section-title">Model Comparison</h2>

      <div className="chart-grid single-col">
        <div className="chart-card">
          <h3 className="chart-title">Baseline (zero-shot) vs Fine-tuned</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" />
              <XAxis dataKey="metric" stroke="#555" tick={{ fontSize: 13 }} />
              <YAxis stroke="#555" tick={{ fontSize: 11 }} unit="%" />
              <Tooltip
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: 12 }}
                formatter={(v: unknown) => [v != null ? `${Number(v).toFixed(1)}%` : '—']}
              />
              <Legend />
              <Bar dataKey="baseline" name="Baseline (zero-shot)" fill={barColors.baseline} radius={[6, 6, 0, 0]} />
              <Bar dataKey="finetuned" name="Fine-tuned" fill={barColors.finetuned} radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>


    </section>
  )
}

export default ModelComparison
