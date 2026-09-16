import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AlertTriangle, BarChart3, CheckCircle2, Clock, RefreshCw, ShieldAlert, ShieldCheck } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import './styles.css';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const examples = {
  safe: {
    label: 'Safe transaction',
    values: {
      amount: 1800,
      transaction_frequency: 3,
      transaction_hour: 14,
      account_age_days: 420,
      previous_transaction_count: 55,
      failed_transaction_count: 0,
      device_change: false,
      location_mismatch: false,
      international_transaction: false,
      unusual_transaction: false
    }
  },
  suspicious: {
    label: 'Suspicious transaction',
    values: {
      amount: 22000,
      transaction_frequency: 10,
      transaction_hour: 22,
      account_age_days: 45,
      previous_transaction_count: 10,
      failed_transaction_count: 1,
      device_change: true,
      location_mismatch: false,
      international_transaction: true,
      unusual_transaction: false
    }
  },
  high: {
    label: 'Highly suspicious transaction',
    values: {
      amount: 115000,
      transaction_frequency: 31,
      transaction_hour: 2,
      account_age_days: 4,
      previous_transaction_count: 1,
      failed_transaction_count: 5,
      device_change: true,
      location_mismatch: true,
      international_transaction: true,
      unusual_transaction: true
    }
  }
};

const emptyForm = examples.safe.values;
const colors = { LOW: '#1f9d72', MEDIUM: '#c47a13', HIGH: '#d64545' };

function riskClass(level) {
  return `badge ${String(level).toLowerCase()}`;
}

function App() {
  const [analytics, setAnalytics] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [result, setResult] = useState(null);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function fetchJson(path) {
    const response = await fetch(`${API}${path}`);
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    return response.json();
  }

  async function refresh() {
    try {
      setError('');
      const [analyticsData, transactionData, alertData] = await Promise.all([
        fetchJson('/api/analytics'),
        fetchJson('/api/transactions'),
        fetchJson('/api/alerts')
      ]);
      setAnalytics(analyticsData);
      setTransactions(transactionData);
      setAlerts(alertData);
    } catch (err) {
      setError('Backend is not reachable. Start FastAPI on port 8000.');
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function analyze(event) {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || 'Prediction failed');
      }
      const data = await response.json();
      setResult(data);
      await refresh();
    } catch (err) {
      setError(String(err.message || err));
    } finally {
      setLoading(false);
    }
  }

  const cards = useMemo(() => {
    const data = analytics || {};
    return [
      ['Total Transactions', data.total_transactions ?? 0, BarChart3],
      ['High Risk', data.high_risk ?? 0, ShieldAlert],
      ['Medium Risk', data.medium_risk ?? 0, AlertTriangle],
      ['Low Risk', data.low_risk ?? 0, ShieldCheck],
      ['Estimated Fraud Rate', `${data.estimated_fraud_rate ?? 0}%`, Clock]
    ];
  }, [analytics]);

  return (
    <main>
      <header className="topbar">
        <div>
          <p className="eyebrow">Prototype payment risk manager</p>
          <h1>RiskLens AI</h1>
          <p className="tagline">See the risk before it becomes a loss.</p>
        </div>
        <button className="iconButton" onClick={refresh} title="Refresh dashboard">
          <RefreshCw size={18} />
        </button>
      </header>

      {error && <div className="error">{error}</div>}

      <section className="metricGrid">
        {cards.map(([label, value, Icon]) => (
          <article className="metric" key={label}>
            <Icon size={20} />
            <span>{label}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </section>

      <section className="workspace">
        <div className="panel analyzer">
          <div className="panelHeader">
            <h2>Live Transaction Analyzer</h2>
            <span>Demo mode</span>
          </div>
          <div className="examples">
            {Object.entries(examples).map(([key, item]) => (
              <button key={key} type="button" onClick={() => setForm(item.values)}>
                {item.label}
              </button>
            ))}
          </div>
          <form onSubmit={analyze} className="formGrid">
            <NumberField label="Amount" name="amount" value={form.amount} setForm={setForm} />
            <NumberField label="Transaction frequency" name="transaction_frequency" value={form.transaction_frequency} setForm={setForm} />
            <NumberField label="Transaction hour" name="transaction_hour" value={form.transaction_hour} setForm={setForm} />
            <NumberField label="Account age days" name="account_age_days" value={form.account_age_days} setForm={setForm} />
            <NumberField label="Previous transactions" name="previous_transaction_count" value={form.previous_transaction_count} setForm={setForm} />
            <NumberField label="Failed transactions" name="failed_transaction_count" value={form.failed_transaction_count} setForm={setForm} />
            <Toggle label="Device changed" name="device_change" value={form.device_change} setForm={setForm} />
            <Toggle label="Location mismatch" name="location_mismatch" value={form.location_mismatch} setForm={setForm} />
            <Toggle label="International" name="international_transaction" value={form.international_transaction} setForm={setForm} />
            <Toggle label="Unusual behavior" name="unusual_transaction" value={form.unusual_transaction} setForm={setForm} />
            <button className="primary" disabled={loading}>
              {loading ? 'Analyzing...' : 'Analyze Transaction'}
            </button>
          </form>
        </div>

        <ResultPanel result={result} />
      </section>

      <section className="charts">
        <div className="panel">
          <h2>Risk Distribution</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={analytics?.risk_distribution || []}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {(analytics?.risk_distribution || []).map((entry) => (
                  <Cell key={entry.name} fill={colors[entry.name]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="panel">
          <h2>Transaction Risk Trend</h2>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={analytics?.trend || []}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Line type="monotone" dataKey="avgRisk" stroke="#2d5bd1" strokeWidth={3} dot />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="tables">
        <div className="panel">
          <h2>Recent Transactions</h2>
          <TransactionTable transactions={transactions} onSelect={setSelected} />
        </div>
        <div className="panel">
          <h2>High-Risk Alerts</h2>
          <div className="alertList">
            {alerts.length === 0 && <p className="muted">No high-risk alerts yet.</p>}
            {alerts.map((alert) => (
              <button className="alertItem" key={alert.transaction_id} onClick={() => setSelected(alert)}>
                <strong>{alert.transaction_id}</strong>
                <span>{alert.risk_score}/100</span>
                <small>{alert.reasons?.[0]}</small>
              </button>
            ))}
          </div>
        </div>
      </section>

      {selected && <Details record={selected} close={() => setSelected(null)} />}
    </main>
  );
}

function NumberField({ label, name, value, setForm }) {
  return (
    <label>
      <span>{label}</span>
      <input
        type="number"
        value={value}
        onChange={(event) => setForm((current) => ({ ...current, [name]: Number(event.target.value) }))}
      />
    </label>
  );
}

function Toggle({ label, name, value, setForm }) {
  return (
    <label className="toggle">
      <span>{label}</span>
      <input
        type="checkbox"
        checked={value}
        onChange={(event) => setForm((current) => ({ ...current, [name]: event.target.checked }))}
      />
    </label>
  );
}

function ResultPanel({ result }) {
  if (!result) {
    return (
      <div className="panel result empty">
        <CheckCircle2 size={42} />
        <h2>Ready to score</h2>
        <p>Load a demo transaction or enter details to generate a real API prediction.</p>
      </div>
    );
  }
  return (
    <div className={`panel result ${result.risk_level.toLowerCase()}`}>
      <div className="score">{result.risk_score}</div>
      <span className={riskClass(result.risk_level)}>{result.risk_level}</span>
      <h2>{result.decision}</h2>
      <p>Fraud probability: {(result.fraud_probability * 100).toFixed(1)}%</p>
      <ul>
        {result.reasons.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>
    </div>
  );
}

function TransactionTable({ transactions, onSelect }) {
  if (transactions.length === 0) return <p className="muted">No transactions yet. Analyze one to populate history.</p>;
  return (
    <div className="tableWrap">
      <table>
        <thead>
          <tr>
            <th>Transaction ID</th>
            <th>Amount</th>
            <th>Time</th>
            <th>Score</th>
            <th>Level</th>
            <th>Decision</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((txn) => (
            <tr key={txn.transaction_id} onClick={() => onSelect(txn)}>
              <td>{txn.transaction_id}</td>
              <td>Rs {Number(txn.amount).toLocaleString('en-IN')}</td>
              <td>{new Date(txn.timestamp).toLocaleString()}</td>
              <td>{txn.risk_score}</td>
              <td><span className={riskClass(txn.risk_level)}>{txn.risk_level}</span></td>
              <td>{txn.decision}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Details({ record, close }) {
  return (
    <div className="modalBackdrop" onClick={close}>
      <aside className="modal" onClick={(event) => event.stopPropagation()}>
        <button className="close" onClick={close}>Close</button>
        <p className="eyebrow">Transaction details</p>
        <h2>{record.transaction_id}</h2>
        <div className="detailGrid">
          <span>Risk score</span><strong>{record.risk_score}/100</strong>
          <span>Classification</span><strong>{record.risk_level}</strong>
          <span>Model probability</span><strong>{(record.fraud_probability * 100).toFixed(1)}%</strong>
          <span>Recommended action</span><strong>{record.decision}</strong>
          <span>Timestamp</span><strong>{new Date(record.timestamp).toLocaleString()}</strong>
        </div>
        <h3>Main risk factors</h3>
        <ul>{record.reasons?.map((reason) => <li key={reason}>{reason}</li>)}</ul>
      </aside>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
