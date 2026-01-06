import React, { use, useEffect, useState } from 'react'
import axiosInstance from '../../axiosInstance'
import ComparisonChart from '../../ComparisonChart'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSpinner } from '@fortawesome/free-solid-svg-icons'
import axios from 'axios'

const Dashboard = () => {
    const [data, setData] = useState('')
    const [ticker, setTicker] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [plot, setPlot] = useState()
    const [plot100, setPlot100] = useState()
    const [plot200, setPlot200] = useState()
    const [plotPct, setplotPct] = useState()
    const [prediction, setPrediction] = useState()
    const [mode, setMode] = useState('live')
    const [mse, setMSE] = useState()
    const [rmse, setRMSE] = useState()
    const [r2_score, setR2_score] = useState()
    const [baselineMSE, setBaselineMSE] = useState()
    const [baselineRMSE, setBaselineRMSE] = useState()
    const [baselineR2, setBaselineR2] = useState()
    const [modelMSE, setModelMSE] = useState()
    const [modelRMSE, setModelRMSE] = useState()
    const [modelR2, setModelR2] = useState()

    useEffect(() => {
        const fetchProtectedData = async () => {
            try{
                const response = await axiosInstance.get('/protected-view/')
                setData(response.data.status)
            }catch(error){
                console.log(error)
            }
        }
        fetchProtectedData()
    }, [])

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        try{
            const response = await axiosInstance.post('/predict/', {'ticker': ticker, 'mode': mode})
            console.log(response.data)
            setPlot(response.data.plot)
            setPlot100(response.data.plot_100)
            setPlot200(response.data.plot_200)
            setplotPct(response.data.plot_pct)
            setPrediction(response.data.prediction)
            setMSE(response.data.mse)
            setRMSE(response.data.rmse)
            setR2_score(response.data.r2)
            setBaselineMSE(response.data.baseline_mse)
            setBaselineRMSE(response.data.baseline_rmse)
            setBaselineR2(response.data.baseline_r2)
            setModelMSE(response.data.model_mse)
            setModelRMSE(response.data.model_rmse)
            setModelR2(response.data.model_r2)
            if(response.data.error){
                setError(response.data.error)
            }
            else{
                setError()
            }
        }catch(error){
            console.log(error)
        }finally{
            setLoading(false)
        }
    }

  return (
    <div className="container mb-5">
        <div className="col-md-6 mx-auto">
            <div className="mb-3">
                {error && <div className="alert alert-danger">{error}</div> }
            </div> 
            <form onSubmit={handleSubmit}>
                <input className='form-control mb-3' type="text" placeholder='Enter ticker (e.g. TSLA, AAPL) or try: TSLA, AAPL, MSFT' onChange={(e) => setTicker(e.target.value)} required/>
                <div className="mb-2">
                    <label className="me-3">Mode:</label>
                    <div className="form-check form-check-inline">
                        <input className="form-check-input" type="radio" name="modeOptions" id="modeLive" value="live" checked={mode==='live'} onChange={(e)=>setMode(e.target.value)} />
                        <label className="form-check-label" htmlFor="modeLive">Live</label>
                    </div>
                    <div className="form-check form-check-inline">
                        <input className="form-check-input" type="radio" name="modeOptions" id="modeDemo" value="demo" checked={mode==='demo'} onChange={(e)=>setMode(e.target.value)} />
                        <label className="form-check-label" htmlFor="modeDemo">Demo</label>
                    </div>
                </div>
                {!loading ? (<button type='submit' className='btn btn-info'>See Prediction</button>) : (<button type='submit' className='btn btn-info' disabled><FontAwesomeIcon icon={faSpinner} spin/>Please wait...</button>)}
            </form>
        </div>
        <div className='text-center mt-4'>
            {plot && (() => {
                const base = import.meta.env.VITE_BACKEND_BASE_URL || 'http://127.0.0.1:8000/api/v1/'
                const backendRoot = base.replace(/\/api\/v1\/?$/,'/').replace(/\/$/, '') || 'http://127.0.0.1:8000'
                return <img style={{maxWidth : '100%'}} src={backendRoot + plot} alt="Stock Closing Price" />
            })() }
        </div>
        <div className='text-center mt-4'>
            {plot && (() => {
                const base = import.meta.env.VITE_BACKEND_BASE_URL || 'http://127.0.0.1:8000/api/v1/'
                const backendRoot = base.replace(/\/api\/v1\/?$/,'/').replace(/\/$/, '') || 'http://127.0.0.1:8000'
                return <img style={{maxWidth : '100%'}} src={backendRoot + plot100} alt="100 DMA" />
            })() }
        </div>
        <div className='text-center mt-4'>
            {plot && (() => {
                const base = import.meta.env.VITE_BACKEND_BASE_URL || 'http://127.0.0.1:8000/api/v1/'
                const backendRoot = base.replace(/\/api\/v1\/?$/,'/').replace(/\/$/, '') || 'http://127.0.0.1:8000'
                return <img style={{maxWidth : '100%'}} src={backendRoot + plot200} alt="200 DMA" />
            })() }
        </div>
        <div className='text-center mt-4 mb-4'>
            {plot && (() => {
                const base = import.meta.env.VITE_BACKEND_BASE_URL || 'http://127.0.0.1:8000/api/v1/'
                const backendRoot = base.replace(/\/api\/v1\/?$/,'/').replace(/\/$/, '') || 'http://127.0.0.1:8000'
                return <img style={{maxWidth : '100%'}} src={backendRoot + plotPct} alt="200 DMA" />
            })() }
        </div>
        {plot && <h2 className='text-light text-center'><hr />Prediction <hr /></h2>}
        <div className='text-center mt-4'>
            {plot && prediction && (() => {
                const base = import.meta.env.VITE_BACKEND_BASE_URL || 'http://127.0.0.1:8000/api/v1/'
                const backendRoot = base.replace(/\/api\/v1\/?$/,'/').replace(/\/$/, '') || 'http://127.0.0.1:8000'
                return <img style={{maxWidth : '100%'}} src={backendRoot + prediction} alt="Prediction" />
            })() }
        </div>

        {plot && 
        <div className='text-light mt-4'>
            <h3 className='text-center'>Baseline Evaluation</h3>
            <hr />
            <big>Mean Squared Error: {baselineMSE ?? 'N/A'}</big>
            <hr />
            <big>Root Mean Squared Error: {baselineRMSE ?? 'N/A'}</big>
            <hr />
            <big>R-Squared: {baselineR2 ?? 'N/A'}</big>

            <h3 className='text-center mt-4'>Model Evaluation</h3>
            <hr />
            <big>Mean Squared Error: {modelMSE ?? 'Model not available'}</big>
            <hr />
            <big>Root Mean Squared Error: {modelRMSE ?? 'Model not available'}</big>
            <hr />
            <big>R-Squared: {modelR2 ?? 'Model not available'}</big>
        </div>
        }
                {plot && baselineRMSE != null && modelRMSE != null && (
                    <div style={{marginTop:20}}>
                        <ComparisonChart baseline={baselineRMSE} model={modelRMSE} />
                    </div>
                )}
    </div>
  )
}

export default Dashboard