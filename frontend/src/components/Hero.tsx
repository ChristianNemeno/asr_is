import { useEffect, useState } from 'react'
import { motion } from 'motion/react'

interface Models {
  baseline: { id: string; parameters: number; architecture: string; task: string }
  finetuned: { id: string; test_wer: number; test_cer: number; train_steps: number; dataset: string; per_language: Record<string, { mean_wer: number; n: number }> }
}

function CountUp({ end, suffix = '', decimals = 0 }: { end: number; suffix?: string; decimals?: number }) {
  const [val, setVal] = useState(0)
  useEffect(() => {
    if (end == null) return
    let start = 0
    const dur = 1200
    const step = Math.max(1, Math.floor(dur / 30))
    const inc = end / (dur / step)
    const timer = setInterval(() => {
      start += inc
      if (start >= end) { setVal(end); clearInterval(timer) }
      else setVal(start)
    }, step)
    return () => clearInterval(timer)
  }, [end])
  return <>{val.toFixed(decimals)}{suffix}</>
}

function Hero({ models }: { models: Models | null }) {
  return (
    <motion.section
      className="section hero"
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <motion.h1
        className="hero-title"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.6 }}
      >
        Whisper-small — Filipino &amp; Cebuano ASR
      </motion.h1>
      <motion.p
        className="hero-subtitle"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.35, duration: 0.5 }}
      >
        Fine-tuned on Filipino Speech Corpus + FLEURS
      </motion.p>
      <motion.div
        className="stat-cards"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.5 }}
      >
        <div className="stat-card">
          <span className="stat-value">
            {models ? <CountUp end={models.finetuned.test_wer} suffix="%" decimals={1} /> : '—'}
          </span>
          <span className="stat-label">WER</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">
            {models ? <CountUp end={models.finetuned.test_cer} suffix="%" decimals={1} /> : '—'}
          </span>
          <span className="stat-label">CER</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">
            {models ? <CountUp end={models.finetuned.train_steps} /> : '—'}
          </span>
          <span className="stat-label">Steps</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">~70h</span>
          <span className="stat-label">Training Data</span>
        </div>
      </motion.div>
    </motion.section>
  )
}

export default Hero
