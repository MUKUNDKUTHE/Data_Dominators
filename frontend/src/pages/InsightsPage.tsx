import { useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { fetchArrivalPrediction, fetchBypassScore, fetchLossRisk } from '@/lib/api';
import { CROPS } from '@/lib/data';
import { Loader2, TrendingUp, AlertTriangle, CheckCircle, Users, IndianRupee, Shield } from 'lucide-react';

/** Convert ISO year-week to a human-readable date range, e.g. "Mar 2 – Mar 8" */
function weekToDateRange(week: number, year?: number): string {
  const y = year ?? new Date().getFullYear();
  // ISO week 1 = week containing first Thursday of the year
  const jan4 = new Date(y, 0, 4);                      // Jan 4 is always in week 1
  const startOfWeek1 = new Date(jan4);
  startOfWeek1.setDate(jan4.getDate() - ((jan4.getDay() + 6) % 7)); // Monday of week 1
  const start = new Date(startOfWeek1);
  start.setDate(startOfWeek1.getDate() + (week - 1) * 7);
  const end = new Date(start);
  end.setDate(start.getDate() + 6);
  const fmt = (d: Date) => d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
  return `${fmt(start)} – ${fmt(end)}`;
}

const INDIAN_STATES = [
  'Andhra Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Gujarat', 'Haryana',
  'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh',
  'Maharashtra', 'Odisha', 'Punjab', 'Rajasthan', 'Tamil Nadu', 'Telangana',
  'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
];

const STORAGE_TYPES = [
  { value: 'open_air',     label: 'Open Air (Field)' },
  { value: 'basic_shed',  label: 'Basic Shed' },
  { value: 'cool_storage',label: 'Cool Storage' },
  { value: 'cold_storage',label: 'Cold Storage' },
];

export default function InsightsPage() {
  const { language } = useLanguage();

  const [crop, setCrop]       = useState('Tomato');
  const [state, setState]     = useState('Maharashtra');
  const [qty, setQty]         = useState(10);
  const [price, setPrice]     = useState(1500);
  const [trend, setTrend]     = useState('stable');
  const [spoilage, setSpoilage] = useState(30);
  const [storage, setStorage] = useState('basic_shed');

  const [arrivalResult, setArrivalResult] = useState<any>(null);
  const [bypassResult, setBypassResult]   = useState<any>(null);
  const [lossResult, setLossResult]       = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  async function handleAnalyze() {
    setLoading(true);
    setError('');
    try {
      const [arrival, bypass, loss] = await Promise.all([
        fetchArrivalPrediction({ crop, state }),
        fetchBypassScore({ crop, state, quantity_quintals: qty, predicted_price: price, price_trend: trend }),
        fetchLossRisk({ crop, quantity_quintals: qty, predicted_price: price, spoilage_score: spoilage, storage_type: storage }),
      ]);
      setArrivalResult(arrival);
      setBypassResult(bypass);
      setLossResult(loss);
    } catch (e: any) {
      setError(e.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  }

  const adviceBorder = arrivalResult?.advice === 'good_window'
    ? 'bg-green-500/10 border-green-500/30'
    : 'bg-amber-500/10 border-amber-500/30';
  const adviceAccent = arrivalResult?.advice === 'good_window'
    ? 'text-green-400'
    : 'text-amber-300';

  const bypassColor =
    bypassResult?.color === 'green'  ? 'text-green-400'  :
    bypassResult?.color === 'yellow' ? 'text-amber-300'  : 'text-red-400';

  return (
    <div className="min-h-screen bg-background pb-24 pt-4">
      <div className="max-w-lg mx-auto px-4 space-y-5">

        {/* Header */}
        <div>
          <h1 className="text-xl font-bold text-foreground">Market Insights</h1>
          <p className="text-sm text-muted-foreground mt-0.5">Arrival surge · Bypass score · Loss insurance</p>
        </div>

        {/* Input Card */}
        <div className="bg-card border border-border rounded-2xl p-4 space-y-3">
          {/* Crop */}
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Crop</label>
            <select
              value={crop}
              onChange={e => setCrop(e.target.value)}
              className="w-full mt-1 bg-input border border-border rounded-xl px-3 py-2 text-sm text-foreground"
            >
              {CROPS.slice(0, 30).map(c => <option key={c.name} value={c.name}>{c.emoji} {c.name}</option>)}
            </select>
          </div>

          {/* State */}
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">State</label>
            <select
              value={state}
              onChange={e => setState(e.target.value)}
              className="w-full mt-1 bg-input border border-border rounded-xl px-3 py-2 text-sm text-foreground"
            >
              {INDIAN_STATES.map(s => <option key={s}>{s}</option>)}
            </select>
          </div>

          {/* Quantity + Price */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Quantity (qtl)</label>
              <input
                type="number" value={qty} min={1}
                onChange={e => setQty(Number(e.target.value))}
                className="w-full mt-1 bg-input border border-border rounded-xl px-3 py-2 text-sm text-foreground"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Exp. Price (₹/qtl)</label>
              <input
                type="number" value={price} min={100}
                onChange={e => setPrice(Number(e.target.value))}
                className="w-full mt-1 bg-input border border-border rounded-xl px-3 py-2 text-sm text-foreground"
              />
            </div>
          </div>

          {/* Trend */}
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Price Trend</label>
            <select
              value={trend}
              onChange={e => setTrend(e.target.value)}
              className="w-full mt-1 bg-input border border-border rounded-xl px-3 py-2 text-sm text-foreground"
            >
              <option value="rising">Rising ↑</option>
              <option value="stable">Stable →</option>
              <option value="falling">Falling ↓</option>
            </select>
          </div>

          {/* Spoilage + Storage (for Loss Insurance) */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Spoilage Risk (0–100)</label>
              <input
                type="number" value={spoilage} min={0} max={100}
                onChange={e => setSpoilage(Number(e.target.value))}
                className="w-full mt-1 bg-input border border-border rounded-xl px-3 py-2 text-sm text-foreground"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Storage Type</label>
              <select
                value={storage}
                onChange={e => setStorage(e.target.value)}
                className="w-full mt-1 bg-input border border-border rounded-xl px-3 py-2 text-sm text-foreground"
              >
                {STORAGE_TYPES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-semibold text-sm flex items-center justify-center gap-2 btn-press"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <TrendingUp size={16} />}
            {loading ? 'Analyzing…' : 'Analyze Market'}
          </button>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-sm text-red-400">{error}</div>
        )}

        {/* Arrival Surge Result */}
        {arrivalResult && (
          <div className={`border rounded-2xl p-4 space-y-3 ${adviceBorder}`}>
            <div className={`flex items-center gap-2 ${adviceAccent}`}>
              {arrivalResult.advice === 'good_window'
                ? <CheckCircle size={18} />
                : <AlertTriangle size={18} />}
              <h2 className="font-bold text-sm">Arrival Surge Prediction</h2>
            </div>
            <p className="text-sm leading-relaxed text-foreground">{arrivalResult.alert}</p>

            {arrivalResult.upcoming_surges?.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-medium text-muted-foreground">Incoming surge periods — avoid selling then:</p>
                {arrivalResult.upcoming_surges.map((s: any) => (
                  <div key={s.week} className="bg-black/20 rounded-lg px-3 py-2 text-xs space-y-0.5">
                    <div className="flex justify-between">
                      <span className="font-semibold text-foreground">
                        {s.weeks_from_now === 0 ? '🔴 This week' : s.weeks_from_now === 1 ? '🟠 Next week' : `🟡 In ${s.weeks_from_now} weeks`}
                      </span>
                      <span className="font-mono text-red-400">{s.price_impact_pct > 0 ? '+' : ''}{s.price_impact_pct}% price impact</span>
                    </div>
                    <div className="text-muted-foreground">{weekToDateRange(s.week)} <span className="opacity-50">(week {s.week} of year)</span></div>
                  </div>
                ))}
              </div>
            )}

            {arrivalResult.best_price_weeks?.length > 0 && (
              <div className="space-y-1.5">
                <p className="text-xs font-medium text-muted-foreground">✅ Best periods to sell (low arrivals = higher price):</p>
                <div className="flex flex-col gap-1">
                  {arrivalResult.best_price_weeks.slice(0, 3).map((w: number) => (
                    <span key={w} className="text-xs bg-black/20 rounded-lg px-3 py-1.5 text-foreground">
                      📅 {weekToDateRange(w)} <span className="text-muted-foreground">(week {w})</span>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Bypass Score Result */}
        {bypassResult && (
          <div className="bg-card border border-border rounded-2xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users size={18} className="text-primary" />
                <h2 className="font-bold text-sm text-foreground">Middleman Bypass Score</h2>
              </div>
              <span className={`text-2xl font-black ${bypassColor}`}>
                {bypassResult.bypass_score}<span className="text-sm font-normal text-muted-foreground">/10</span>
              </span>
            </div>

            <div className={`rounded-xl px-3 py-2 text-sm font-semibold ${bypassColor} bg-current/5`}>
              {bypassResult.verdict}
            </div>

            {/* Commission saved */}
            <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-xl px-3 py-2">
              <IndianRupee size={16} className="text-green-400" />
              <span className="text-sm text-green-400 font-semibold">
                Potential saving: ₹{bypassResult.commission_saved?.toLocaleString('en-IN')} ({bypassResult.commission_rate_pct}% commission)
              </span>
            </div>

            {/* Reasons */}
            <div className="space-y-1.5">
              {bypassResult.reasons?.map((r: any, i: number) => (
                <div key={i} className="flex items-start gap-2 text-xs">
                  <span className={r.positive ? 'text-green-400 mt-0.5' : 'text-red-400 mt-0.5'}>
                    {r.positive ? '✓' : '✗'}
                  </span>
                  <span className="text-muted-foreground">{r.text}</span>
                </div>
              ))}
            </div>

            {/* Next step */}
            <div className="bg-primary/10 border border-primary/20 rounded-xl px-3 py-2">
              <p className="text-xs text-primary font-medium">Next step:</p>
              <p className="text-xs text-muted-foreground mt-0.5">{bypassResult.next_step}</p>
            </div>
          </div>
        )}

        {/* Loss Insurance Result */}
        {lossResult && (
          <div className="bg-card border border-border rounded-2xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield size={18} className="text-primary" />
                <h2 className="font-bold text-sm text-foreground">Loss Insurance Estimator</h2>
              </div>
              <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                lossResult.urgency === 'high'   ? 'bg-red-500/20 text-red-400' :
                lossResult.urgency === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                                                   'bg-green-500/20 text-green-400'
              }`}>
                {lossResult.urgency?.toUpperCase()} RISK
              </span>
            </div>

            <p className="text-sm text-muted-foreground leading-relaxed">{lossResult.summary}</p>

            {/* Key numbers */}
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-3 py-2">
                <p className="text-xs text-muted-foreground">Value at Risk</p>
                <p className="text-sm font-bold text-red-400">₹{lossResult.value_at_risk?.toLocaleString('en-IN')}</p>
              </div>
              <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl px-3 py-2">
                <p className="text-xs text-muted-foreground">Expected Loss</p>
                <p className="text-sm font-bold text-orange-400">₹{lossResult.expected_loss?.toLocaleString('en-IN')}</p>
              </div>
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl px-3 py-2">
                <p className="text-xs text-muted-foreground">Upgrade Cost</p>
                <p className="text-sm font-bold text-blue-400">₹{lossResult.upgrade_cost?.toLocaleString('en-IN')}</p>
              </div>
              <div className="bg-green-500/10 border border-green-500/20 rounded-xl px-3 py-2">
                <p className="text-xs text-muted-foreground">Loss Saved</p>
                <p className="text-sm font-bold text-green-400">₹{lossResult.loss_saved?.toLocaleString('en-IN')}</p>
              </div>
            </div>

            {/* ROI */}
            {lossResult.roi != null && (
              <div className="flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-xl px-3 py-2">
                <IndianRupee size={15} className="text-primary" />
                <span className="text-sm text-primary font-semibold">
                  Storage upgrade ROI: {lossResult.roi}x &nbsp;·&nbsp; {lossResult.upgrade_tip}
                </span>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
