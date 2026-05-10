import { motion } from 'motion/react'

interface HyperparamsData {
  base_model: string; parameters: number; per_device_train_batch_size: number
  gradient_accumulation_steps: number; effective_batch_size: number
  learning_rate: number; warmup_steps: number; max_steps: number
  gradient_checkpointing: boolean; mixed_precision: string
  generation_max_length: number; seed: number
}

function formatParam(key: string, value: string | number | boolean): string {
  if (key === 'learning_rate') return '1 × 10⁻⁵'
  if (key === 'parameters') return `${(Number(value) / 1e6).toFixed(0)}M`
  if (key === 'gradient_checkpointing') return value ? 'True' : 'False'
  return String(value)
}

function paramLabel(key: string): string {
  const labels: Record<string, string> = {
    base_model: 'Base Model',
    parameters: 'Parameters',
    per_device_train_batch_size: 'Batch Size (per GPU)',
    gradient_accumulation_steps: 'Gradient Accumulation',
    effective_batch_size: 'Effective Batch Size',
    learning_rate: 'Learning Rate',
    warmup_steps: 'Warmup Steps',
    max_steps: 'Max Steps',
    gradient_checkpointing: 'Gradient Checkpointing',
    mixed_precision: 'Mixed Precision',
    generation_max_length: 'Max Generation Length',
    seed: 'Seed',
  }
  return labels[key] || key
}

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.04 } },
}

const row = {
  hidden: { opacity: 0, x: -12 },
  visible: { opacity: 1, x: 0 },
}

function Hyperparams({ hyperparams }: { hyperparams: HyperparamsData | null }) {
  if (!hyperparams) return null

  const order = [
    'base_model', 'parameters', 'per_device_train_batch_size',
    'gradient_accumulation_steps', 'effective_batch_size', 'learning_rate',
    'warmup_steps', 'max_steps', 'gradient_checkpointing',
    'mixed_precision', 'generation_max_length', 'seed',
  ]

  return (
    <section className="section">
      <h2 className="section-title">Hyperparameters</h2>
      <motion.table
        className="params-table"
        variants={stagger}
        initial="hidden"
        animate="visible"
      >
        <tbody>
          {order.map(key => {
            const val = hyperparams[key as keyof HyperparamsData]
            return (
              <motion.tr key={key} variants={row}>
                <td className="param-name">{paramLabel(key)}</td>
                <td className="param-value">{formatParam(key, String(val ?? ''))}</td>
              </motion.tr>
            )
          })}
        </tbody>
      </motion.table>
    </section>
  )
}

export default Hyperparams
