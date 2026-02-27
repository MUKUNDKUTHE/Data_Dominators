import { useMemo, useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t, formatINR } from '@/lib/i18n';
import { INDIAN_STATES } from '@/lib/data';
import { fetchPrice } from '@/lib/api';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, MapPin, BarChart2 } from 'lucide-react';

const MarketsPage = () => {
  const { language } = useLanguage();
  const [stateFilter, setStateFilter] = useState('Maharashtra');
  const [district, setDistrict] = useState('Pune');
  const [market, setMarket] = useState('Pune');
  const [crop, setCrop] = useState('Tomato');
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<any>(null);

  const markets = useMemo(() => result?.best_markets?.markets || [], [result]);

  const handleCheck = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchPrice({ crop, state: stateFilter, district, market, date });
      setResult(data);
    } catch (e: any) {
      setError(e?.message || 'Could not fetch market prices');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pb-24 px-4 pt-16 max-w-lg mx-auto">
      <h1 className="text-agri-heading text-foreground mb-4">{t('marketPrices', language)}</h1>

      <div className="bg-card rounded-2xl p-4 border border-border shadow-sm mb-4 space-y-2">
        <input value={crop} onChange={(e) => setCrop(e.target.value)} className="w-full bg-background border border-border rounded-xl px-3 py-2" placeholder={t('crop', language)} />
        <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} className="w-full bg-background border border-border rounded-xl px-3 py-2">
          {INDIAN_STATES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <input value={district} onChange={(e) => setDistrict(e.target.value)} className="w-full bg-background border border-border rounded-xl px-3 py-2" placeholder={t('district', language)} />
        <input value={market} onChange={(e) => setMarket(e.target.value)} className="w-full bg-background border border-border rounded-xl px-3 py-2" placeholder={t('bestMarket', language)} />
        <input type="date" value={date} onChange={(e) => setDate(e.target.value)} className="w-full bg-background border border-border rounded-xl px-3 py-2" />
        <button onClick={handleCheck} disabled={loading} className="w-full rounded-xl py-3 bg-primary text-primary-foreground font-semibold disabled:opacity-50">
          {loading ? t('loading', language) : t('checkPrice', language)}
        </button>
      </div>

      {error ? <div className="mb-4 rounded-xl border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">{error}</div> : null}

      {result ? (
        <>
          <div className="bg-card rounded-2xl p-4 border border-border shadow-sm mb-3">
            <div className="flex items-center gap-1.5 mb-1">
              <BarChart2 size={15} className="text-primary" />
              <p className="text-sm text-muted-foreground font-medium">Predicted market price</p>
            </div>
            <p className="text-2xl font-bold text-foreground">{formatINR(Number(result.price_prediction?.predicted_price || 0))}</p>
            <div className="flex items-center gap-1 mt-1">
              <MapPin size={12} className="text-muted-foreground" />
              <p className="text-sm text-muted-foreground">{result.price_prediction?.market} · {result.price_prediction?.state}</p>
            </div>
            <div className="flex items-center gap-1.5 mt-1">
              {result.price_trend?.trend === 'rising' ? <TrendingUp size={14} className="text-primary" /> : result.price_trend?.trend === 'falling' ? <TrendingDown size={14} className="text-destructive" /> : <Minus size={14} className="text-muted-foreground" />}
              <p className="text-sm text-muted-foreground">Trend: {result.price_trend?.trend} ({result.price_trend?.change_pct}%)</p>
            </div>
          </div>

          <div className="space-y-2">
            {markets.map((m: any, i: number) => (
              <motion.div
                key={`${m.Market}-${i}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 * i }}
                className="bg-card rounded-2xl p-4 border border-border shadow-sm flex items-center justify-between"
              >
                <div>
                  <p className="font-bold text-foreground">{m.Market}</p>
                  <p className="text-sm text-muted-foreground">Data points: {m.data_points}</p>
                </div>
                <p className="text-lg font-bold text-foreground">{formatINR(Number(m.avg_price || 0))}</p>
              </motion.div>
            ))}
          </div>
        </>
      ) : null}

      <p className="text-center text-xs text-muted-foreground mt-4">Last updated: {new Date().toLocaleString('en-IN')}</p>
    </div>
  );
};

export default MarketsPage;

