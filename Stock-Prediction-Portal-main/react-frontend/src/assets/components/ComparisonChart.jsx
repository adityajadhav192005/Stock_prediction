import React from 'react'

const ComparisonChart = ({ baseline, model }) => {
  const baselineValue = Number.isFinite(baseline) ? baseline : null
  const modelValue = Number.isFinite(model) ? model : null
  const max = Math.max(baselineValue ?? 0, modelValue ?? 0, 1)
  const barMax = 300
  const baselineWidth = baselineValue != null ? Math.round((baselineValue / max) * barMax) : 0
  const modelWidth = modelValue != null ? Math.round((modelValue / max) * barMax) : 0

  return (
    <div style={{color:'#fff', marginTop:16}}>
      <h4 style={{textAlign:'center'}}>Baseline vs Model (RMSE)</h4>
      <svg
        width="360"
        height="120"
        viewBox="0 0 360 120"
        role="img"
        aria-label="Baseline vs Model RMSE comparison"
        style={{display:'block', margin:'0 auto'}}
      >
        <rect x="20" y="30" width="320" height="16" rx="6" fill="#333" />
        <rect x="20" y="30" width={baselineWidth} height="16" rx="6" fill="#6c757d" />
        <text x="20" y="24" fill="#fff" fontSize="12">
          Baseline RMSE: {baselineValue ?? 'N/A'}
        </text>

        <rect x="20" y="80" width="320" height="16" rx="6" fill="#333" />
        <rect x="20" y="80" width={modelWidth} height="16" rx="6" fill="#28a745" />
        <text x="20" y="74" fill="#fff" fontSize="12">
          Model RMSE: {modelValue ?? 'N/A'}
        </text>
      </svg>
    </div>
  )
}

export default ComparisonChart
