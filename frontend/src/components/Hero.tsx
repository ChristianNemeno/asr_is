interface Models {
  baseline: { id: string; parameters: number; architecture: string; task: string }
  finetuned: { id: string; test_wer: number; test_cer: number; train_steps: number; dataset: string; per_language: Record<string, { mean_wer: number; n: number }> }
}

function Hero({ models }: { models: Models | null }) {
  return (
    <section className="section hero">
      <h1 className="hero-title">Whisper-small — Filipino &amp; Cebuano ASR</h1>
      <p className="hero-subtitle">Fine-tuned on Filipino Speech Corpus + FLEURS</p>
      <div className="stat-cards">
        <div className="stat-card">
          <span className="stat-value">{models ? `${models.finetuned.test_wer}%` : '—'}</span>
          <span className="stat-label">WER</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{models ? `${models.finetuned.test_cer}%` : '—'}</span>
          <span className="stat-label">CER</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{models ? models.finetuned.train_steps.toLocaleString() : '—'}</span>
          <span className="stat-label">Steps</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">~70h</span>
          <span className="stat-label">Training Data</span>
        </div>
      </div>
    </section>
  )
}

export default Hero
