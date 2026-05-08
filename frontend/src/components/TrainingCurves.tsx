function TrainingCurves() {
  return (
    <section className="section">
      <h2 className="section-title">Training Curves</h2>

      <div className="plot-embed">
        <img
          src="/api/plots/training_curves/training_curves.png"
          alt="Training curves"
          className="plot-img"
        />
      </div>

      <div className="plot-row">
        <div className="plot-embed">
          <img
            src="/api/plots/training_curves/gradient_norm.png"
            alt="Gradient norm"
            className="plot-img"
          />
        </div>
        <div className="plot-embed">
          <img
            src="/api/plots/training_curves/test_metrics.png"
            alt="Test metrics"
            className="plot-img"
          />
        </div>
      </div>
    </section>
  )
}

export default TrainingCurves
