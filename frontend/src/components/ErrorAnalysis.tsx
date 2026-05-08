interface Breakdown {
  substitutions: number; deletions: number; insertions: number; hits: number
}

interface Metrics {
  test_wer: number; test_cer: number; train_steps: number
  per_language: Record<string, { mean_wer: number; n: number }>
  error_breakdown: Breakdown
  n_samples: number
}

interface Transcription {
  rank: number; wer: number; cer: number; language: string
  reference: string; prediction: string
}

function ErrorAnalysis({
  metrics,
  transcriptions,
}: {
  metrics: Metrics | null
  transcriptions: Transcription[]
}) {
  return (
    <section className="section">
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

      <div className="plot-row">
        <div className="plot-embed">
          <img
            src="/api/plots/error_analysis/wer_distribution.png"
            alt="WER distribution"
            className="plot-img"
          />
        </div>
        <div className="plot-embed">
          <img
            src="/api/plots/error_analysis/wer_by_language.png"
            alt="WER by language"
            className="plot-img"
          />
        </div>
      </div>

      <div className="plot-embed">
        <img
          src="/api/plots/error_analysis/error_breakdown.png"
          alt="Error breakdown"
          className="plot-img"
        />
      </div>

      {transcriptions.length > 0 && (
        <>
          <h3 className="subsection-title">Sample Transcriptions</h3>
          <div className="sample-table-wrap">
            <table className="sample-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>WER</th>
                  <th>CER</th>
                  <th>Language</th>
                  <th>Reference</th>
                  <th>Prediction</th>
                </tr>
              </thead>
              <tbody>
                {transcriptions.map(t => (
                  <tr key={t.rank} className={t.wer === 0 ? 'best-row' : t.wer > 50 ? 'worst-row' : ''}>
                    <td>{t.rank}</td>
                    <td>{t.wer}%</td>
                    <td>{t.cer}%</td>
                    <td><span className={`lang-badge ${t.language}`}>{t.language}</span></td>
                    <td className="text-cell">{t.reference}</td>
                    <td className="text-cell">{t.prediction}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  )
}

export default ErrorAnalysis
