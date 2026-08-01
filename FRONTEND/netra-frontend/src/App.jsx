import { useEffect, useMemo, useState } from 'react'
import './App.css'

const attackTypes = [
  { value: 'port_scan', label: 'Port Scan' },
  { value: 'ddos', label: 'DDoS / Traffic Spike' },
  { value: 'normal', label: 'Normal Traffic' },
]

const apiFetch = async (path, token, options = {}) => {
  const response = await fetch(`/api/${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Token ${token}` } : {}),
    },
    ...options,
  })
  const data = await response.json()
  if (!response.ok) throw data
  return data
}

const formatApiError = (error) => {
  if (!error) return 'Unknown error'
  if (typeof error === 'string') return error
  if (Array.isArray(error)) return error.join(' ')
  if (typeof error === 'object') {
    return Object.values(error).flat().join(' ')
  }
  return 'Unknown error'
}

function App() {
  const [token, setToken] = useState(localStorage.getItem('netra_token') || '')
  const [username, setUsername] = useState(localStorage.getItem('netra_user') || '')
  const [authMode, setAuthMode] = useState('login')
  const [authError, setAuthError] = useState('')
  const [devices, setDevices] = useState([])
  const [alerts, setAlerts] = useState([])
  const [alertsWithContext, setAlertsWithContext] = useState([])
  const [events, setEvents] = useState([])
  const [selectedDevice, setSelectedDevice] = useState(null)
  const [attackType, setAttackType] = useState('port_scan')
  const [newDeviceName, setNewDeviceName] = useState('')
  const [newDeviceIp, setNewDeviceIp] = useState('')
  const [newDeviceLocation, setNewDeviceLocation] = useState('')
  const [deviceError, setDeviceError] = useState('')
  const [loading, setLoading] = useState(false)
  const [statusMessage, setStatusMessage] = useState('')

  const isAuthenticated = Boolean(token)

  const headers = useMemo(
    () => ({ Authorization: token ? `Token ${token}` : '' }),
    [token],
  )

  const refreshData = async () => {
    if (!isAuthenticated) return
    setLoading(true)
    try {
      const [deviceResponse, alertResponse, alertContextResponse, eventResponse] = await Promise.all([
        apiFetch('devices/', token),
        apiFetch('alerts/', token),
        apiFetch('alerts/with_context/', token),
        apiFetch('events/', token),
      ])
      setDevices(deviceResponse)
      setAlerts(alertResponse)
      setAlertsWithContext(alertContextResponse)
      setEvents(eventResponse)
    } catch (error) {
      setStatusMessage(error?.error || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refreshData()
  }, [token])

  useEffect(() => {
    if (!isAuthenticated) return

    const interval = window.setInterval(() => {
      refreshData()
    }, 8000)

    return () => window.clearInterval(interval)
  }, [isAuthenticated])

  useEffect(() => {
    if (devices.length && !selectedDevice) {
      setSelectedDevice(devices[0].id)
    }
  }, [devices, selectedDevice])

  const activeAlert = alertsWithContext.find((alert) => !alert.resolved && alert.risk_score >= 0.75)
  const alertDeviceIds = new Set(alertsWithContext
    .filter((alert) => !alert.resolved && alert.risk_score >= 0.75)
    .map((alert) => alert['event__device__id']))
  const hasActiveAlert = Boolean(activeAlert)

  const handleRegister = async (e) => {
    e.preventDefault()
    const form = e.target
    const username = form.username.value.trim()
    const email = form.email.value.trim()
    const password = form.password.value

    if (!username || !password) {
      setAuthError('Username and password are required.')
      return
    }

    setLoading(true)
    try {
      const data = await apiFetch('auth/register/', null, {
        method: 'POST',
        body: JSON.stringify({ username, email, password }),
      })
      setToken(data.token)
      setUsername(data.username)
      setAuthError('')
      localStorage.setItem('netra_token', data.token)
      localStorage.setItem('netra_user', data.username)
    } catch (error) {
      setAuthError(formatApiError(error))
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    const form = e.target
    const username = form.username.value.trim()
    const password = form.password.value

    if (!username || !password) {
      setAuthError('Username and password are required.')
      return
    }

    setLoading(true)
    try {
      const data = await apiFetch('auth/login/', null, {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      })
      setToken(data.token)
      setUsername(data.username)
      setAuthError('')
      localStorage.setItem('netra_token', data.token)
      localStorage.setItem('netra_user', data.username)
    } catch (error) {
      setAuthError(formatApiError(error))
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    if (!token) return
    await apiFetch('auth/logout/', token, { method: 'POST' })
    setToken('')
    setUsername('')
    localStorage.removeItem('netra_token')
    localStorage.removeItem('netra_user')
    setDevices([])
    setAlerts([])
    setEvents([])
  }

  const createDevice = async () => {
    if (!newDeviceName || !newDeviceIp) {
      setDeviceError('Device name and IP address are required.')
      return
    }

    setLoading(true)
    try {
      const data = await apiFetch('devices/', token, {
        method: 'POST',
        body: JSON.stringify({
          device_name: newDeviceName,
          ip_address: newDeviceIp,
          location: newDeviceLocation,
        }),
      })
      setDevices((prev) => [...prev, data])
      setSelectedDevice(data.id)
      setNewDeviceName('')
      setNewDeviceIp('')
      setNewDeviceLocation('')
      setDeviceError('')
      setStatusMessage(`Device ${data.device_name} added.`)
    } catch (error) {
      setDeviceError(formatApiError(error))
    } finally {
      setLoading(false)
    }
  }

  const injectAttack = async () => {
    if (!selectedDevice) {
      setStatusMessage('Select a device before injecting an attack.')
      return
    }

    setLoading(true)
    try {
      const response = await apiFetch('simulate_attack/', token, {
        method: 'POST',
        body: JSON.stringify({ device_id: selectedDevice, attack_type: attackType }),
      })
      setStatusMessage(`Injected ${response.attack_type} on device ${selectedDevice} (${response.created_events} events)`) 
      refreshData()
    } catch (error) {
      setStatusMessage(formatApiError(error))
    } finally {
      setLoading(false)
    }
  }

  const recentAlerts = alerts.slice(0, 8)
  const recentEvents = events.slice(0, 8)

  if (!isAuthenticated) {
    return (
      <div className="page-shell">
        <div className="auth-card auth-card--compact">
          <h1>Netra Intrusion Dashboard</h1>
          <p className="subtitle">Sign in or create an account to access the security dashboard.</p>
          <div className="auth-switcher">
            <button type="button" className={authMode === 'login' ? 'active' : ''} onClick={() => { setAuthMode('login'); setAuthError('') }}>
              Login
            </button>
            <button type="button" className={authMode === 'register' ? 'active' : ''} onClick={() => { setAuthMode('register'); setAuthError('') }}>
              Register
            </button>
          </div>
          <form onSubmit={authMode === 'login' ? handleLogin : handleRegister} className="auth-form auth-form--single">
            <h2>{authMode === 'login' ? 'Sign In' : 'Create Account'}</h2>
            <label>
              Username
              <input name="username" />
            </label>
            {authMode === 'register' && (
              <label>
                Email
                <input name="email" type="email" />
              </label>
            )}
            <label>
              Password
              <input type="password" name="password" />
            </label>
            <button disabled={loading} type="submit">
              {authMode === 'login' ? 'Sign In' : 'Register'}
            </button>
          </form>
          {authError && <div className="alert-banner">{authError}</div>}
        </div>
      </div>
    )
  }

  return (
    <div className="page-shell">
      {hasActiveAlert && (
        <div className="alert-overlay">
          <div className="alert-callout">
            <h1>Active Alert</h1>
            <p>
              {activeAlert?.alert_type || 'Critical network activity detected'} on your monitored devices.
              An immediate response is required.
            </p>
            <span className="alert-label">Risk score: {activeAlert?.risk_score?.toFixed(2)}</span>
          </div>
        </div>
      )}

      <header className="topbar">
        <div>
          <h1>Netra Dashboard</h1>
          <p>Welcome back, {username}. Monitor shared alerts and traffic in real time.</p>
        </div>
        <div className="topbar-actions">
          <button onClick={refreshData} disabled={loading}>Refresh</button>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </header>

      <section className="network-graph-panel">
        <article className="network-graph-card">
          <div className="network-graph-header">
            <div>
              <h2>Network Topology</h2>
              <p>Visual map of your server, switch, and connected endpoints.</p>
            </div>
            <span className="network-graph-chip">{devices.length} devices</span>
          </div>
          <div className="network-graph-shell">
            <div className={`graph-node graph-server ${hasActiveAlert ? 'alerted' : ''}`}>
              <span>Server</span>
            </div>
            <div className={`graph-node graph-switch ${hasActiveAlert ? 'alerted' : ''}`}>
              <span>Switch</span>
            </div>
            <div className="graph-connectors">
              {devices.length === 0 ? (
                <div className="graph-empty">Add devices to see the network graph.
                  When an attack occurs, the affected path turns red and an alert is shown.</div>
              ) : (
                devices.slice(0, 6).map((device, index) => (
                  <div
                    key={device.id}
                    className={`graph-node device-node ${alertDeviceIds.has(device.id) ? 'alerted' : ''}`}
                    style={{ '--order': index + 1 }}
                  >
                    <span>{device.device_name}</span>
                    <small>{device.ip_address}</small>
                  </div>
                ))
              )}
            </div>
          </div>
          <div className="graph-note">
            {hasActiveAlert
              ? `Alert active on ${activeAlert['event__device__device_name']} — the path is highlighted in red.`
              : 'No active alerts. Your topology is stable.'}
          </div>
        </article>
      </section>

      <section className="flow-panel">
        <article className="flow-card">
          <div className="flow-heading">
            <div>
              <h2>Live Network Flow</h2>
              <p>Real-time packet movement and attack alert visualization.</p>
            </div>
            <span className="flow-chip">{events.length} events</span>
          </div>
          <div className="traffic-animation">
            {Array.from({ length: 6 }, (_, index) => (
              <div key={index} className={`traffic-bar bar-${index}`} />
            ))}
          </div>
          <div className="flow-details">
            <span>{devices.length} devices connected</span>
            <span>{alerts.filter((alert) => !alert.resolved).length} active alerts</span>
            <span>{events.length} total flows</span>
          </div>
        </article>
      </section>

      <section className="summary-grid">
        <article className="summary-card">
          <h2>Devices</h2>
          <p>{devices.length} active devices</p>
        </article>
        <article className="summary-card">
          <h2>Alerts</h2>
          <p>{alerts.length} total alerts</p>
        </article>
        <article className="summary-card">
          <h2>Events</h2>
          <p>{events.length} traffic events</p>
        </article>
        <article className="summary-card accent">
          <h2>Simulation</h2>
          {devices.length === 0 ? (
            <div className="device-empty">
              <p>No devices found. Add a device first to simulate an attack.</p>
              <label>
                Device name
                <input value={newDeviceName} onChange={(e) => setNewDeviceName(e.target.value)} />
              </label>
              <label>
                IP address
                <input value={newDeviceIp} onChange={(e) => setNewDeviceIp(e.target.value)} />
              </label>
              <label>
                Location
                <input value={newDeviceLocation} onChange={(e) => setNewDeviceLocation(e.target.value)} />
              </label>
              <button type="button" onClick={createDevice} disabled={loading}>
                Add Device
              </button>
              {deviceError && <div className="alert-banner">{deviceError}</div>}
            </div>
          ) : (
            <>
              <select value={selectedDevice || ''} onChange={(e) => setSelectedDevice(e.target.value)}>
                <option value="">Select device</option>
                {devices.map((device) => (
                  <option key={device.id} value={device.id}>{device.device_name}</option>
                ))}
              </select>
              <select value={attackType} onChange={(e) => setAttackType(e.target.value)}>
                {attackTypes.map((attack) => (
                  <option key={attack.value} value={attack.value}>{attack.label}</option>
                ))}
              </select>
              <button onClick={injectAttack} disabled={loading || !selectedDevice}>
                Inject Attack
              </button>
            </>
          )}
        </article>
      </section>

      <section className="tables-grid">
        <div className="table-card">
          <h2>Recent Alerts</h2>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Risk</th>
                  <th>Resolved</th>
                </tr>
              </thead>
              <tbody>
                {recentAlerts.map((alert) => (
                  <tr key={alert.id}>
                    <td>{alert.alert_type}</td>
                    <td>{alert.risk_score.toFixed(2)}</td>
                    <td>{alert.resolved ? 'Yes' : 'No'}</td>
                  </tr>
                ))}
                {!recentAlerts.length && <tr><td colSpan="3">No alerts yet.</td></tr>}
              </tbody>
            </table>
          </div>
        </div>

        <div className="table-card">
          <h2>Recent Traffic</h2>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Src</th>
                  <th>Dst</th>
                  <th>Port</th>
                </tr>
              </thead>
              <tbody>
                {recentEvents.map((event) => (
                  <tr key={event.id}>
                    <td>{event.src_ip}</td>
                    <td>{event.dst_ip}</td>
                    <td>{event.port}</td>
                  </tr>
                ))}
                {!recentEvents.length && <tr><td colSpan="3">No events yet.</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <div className="status-row">
        {loading && <span className="status-chip">Loading…</span>}
        {statusMessage && <span className="status-chip">{statusMessage}</span>}
      </div>
    </div>
  )
}

export default App
