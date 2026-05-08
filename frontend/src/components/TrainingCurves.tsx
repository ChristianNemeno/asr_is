import { motion } from 'motion/react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts'

interface CurvePoint {
  step: number
  loss: number | null
  eval_loss: number | null
  eval_wer: number | null
  eval_cer: number | null
  learning_rate: number | null
  grad_norm: number | null
}

const chartColors = {
  loss: '#60a5fa',
  evalLoss: '#f59e0b',
  wer: '#f87171',
  cer: '#4ade80',
  lr: '#a78bfa',
  grad: '#94a3b8',
}

function TrainingCurves({ curves }: { curves: CurvePoint[] }) {
  if (!curves.length) return null

  return (
    <motion.section
      className="section"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="section-title">Training Curves</h2>

      <div className="chart-grid">
        <div className="chart-card">
          <h3 className="chart-title">Loss</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={curves} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" />
              <XAxis dataKey="step" stroke="#555" tick={{ fontSize: 11 }} />
              <YAxis stroke="#555" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: '#aaa' }}
              />
              <Legend />
              <Line type="monotone" dataKey="loss" stroke={chartColors.loss} dot={false} strokeWidth={1.5} name="Train Loss" connectNulls />
              <Line type="monotone" dataKey="eval_loss" stroke={chartColors.evalLoss} dot={{ r: 2 }} strokeWidth={1.5} name="Eval Loss" connectNulls />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3 className="chart-title">WER / CER</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={curves} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" />
              <XAxis dataKey="step" stroke="#555" tick={{ fontSize: 11 }} />
              <YAxis stroke="#555" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: '#aaa' }}
              />
              <Legend />
              <Line type="monotone" dataKey="eval_wer" stroke={chartColors.wer} dot={{ r: 2 }} strokeWidth={1.5} name="WER %" connectNulls />
              <Line type="monotone" dataKey="eval_cer" stroke={chartColors.cer} dot={{ r: 2 }} strokeWidth={1.5} name="CER %" connectNulls />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3 className="chart-title">Learning Rate Schedule</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={curves} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" />
              <XAxis dataKey="step" stroke="#555" tick={{ fontSize: 11 }} />
              <YAxis stroke="#555" tick={{ fontSize: 11 }} tickFormatter={v => `${(v * 1e6).toFixed(0)}e-6`} />
              <Tooltip
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: '#aaa' }}
              />
              <Line type="monotone" dataKey="learning_rate" stroke={chartColors.lr} dot={false} strokeWidth={1.5} name="LR" connectNulls />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3 className="chart-title">Gradient Norm</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={curves} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" />
              <XAxis dataKey="step" stroke="#555" tick={{ fontSize: 11 }} />
              <YAxis stroke="#555" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: '#aaa' }}
              />
              <Line type="monotone" dataKey="grad_norm" stroke={chartColors.grad} dot={false} strokeWidth={1.5} name="grad_norm" connectNulls />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </motion.section>
  )
}

export default TrainingCurves
