import React from 'react'

const ComparisonChart = ({ baseline, model }) => {
  const b = baseline || 0
  const m = model || 0
  const max = Math.max(b, m, 1) // avoid zero width
  const bw = Math.round((b / max) * 300)
  const mw = Math.round((m / max) * 300)

  return (
    <div style={{color:'#fff', marginTop:16}}>
      <h4 style={{textAlign:'center'}}>Baseline vs Model (RMSE)</h4>
      <div style={{display:'flex', gap:12, alignItems:'center', justifyContent:'center'}}>
        <div style={{width:360}}>
          <div style={{marginBottom:8}}>Baseline RMSE: {baseline ?? 'N/A'}</div>
          <div style={{background:'#333', height:18, borderRadius:6}}>
            <div style={{width: bw, height:18, background:'#6c757d', borderRadius:6}} />
          </div>
        </div>
        <div style={{width:360}}>
          <div style={{marginBottom:8}}>Model RMSE: {model ?? 'N/A'}</div>
          <div style={{background:'#333', height:18, borderRadius:6}}>
            <div style={{width: mw, height:18, background:'#28a745', borderRadius:6}} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default ComparisonChart
