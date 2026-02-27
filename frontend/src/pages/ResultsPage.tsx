import { useLanguage } from '@/contexts/LanguageContext';
import { t, formatINR } from '@/lib/i18n';
import { motion } from 'framer-motion';
import SpoilageGauge from '@/components/SpoilageGauge';
import AnimatedCounter from '@/components/AnimatedCounter';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CalendarCheck, MapPin, TrendingUp, Zap, Thermometer, Droplets, Truck, Route, Info } from 'lucide-react';

// Sanitize LLM text — replace all mojibake variants of ₹ with "Rs."
function sanitize(text: string): string {
  return text
    .replace(/â‚¹/g, 'Rs.')   // classic cp1252 mojibake
    .replace(/â,¹/g, 'Rs.')   // alternate rendering
    .replace(/â\x82¹/g, 'Rs.') // raw bytes variant
    .replace(/₹/g, 'Rs.');    // actual symbol → plain ASCII for safety
}

// Parse "1. text 2. text" style recommendation into array of exactly 4 numbered points.
// Strips any preamble the LLM adds before point 1.
function parseRecommendation(text: string): string[] {
  if (!text) return [];
  const clean = sanitize(text);
  const numbered = clean
    .split(/(?=\d+\.\s)/)
    .map(s => s.trim())
    .filter(s => /^\d+\.\s/.test(s));
  return numbered.length >= 2 ? numbered.slice(0, 4) : [clean];
}

const POINT_META = [
  { Icon: CalendarCheck, label: 'When to Harvest', color: 'text-blue-300' },
  { Icon: MapPin,        label: 'Where to Sell',   color: 'text-emerald-300' },
  { Icon: TrendingUp,   label: 'Price Outlook',    color: 'text-yellow-300' },
  { Icon: Zap,          label: 'Urgent Action',    color: 'text-orange-300' },
];

const ResultsPage = () => {
  const { language } = useLanguage();
  const navigate = useNavigate();
  const [result, setResult] = useState<any>(null);
  const [request, setRequest] = useState<any>(null);
  const [quintals, setQuintals] = useState(10);

  useEffect(() => {
    const r = localStorage.getItem('agrichain-last-result');
    const req = localStorage.getItem('agrichain-last-request');
    if (r) setResult(JSON.parse(r));
    if (req) setRequest(JSON.parse(req));
    if (!r) navigate('/recommend');
  }, [navigate]);

  if (!result) return null;

  const pp = result.price_prediction || {};
  const bm = result.best_markets || {};
  const yourMarketPrice = Number(pp.predicted_price || 0);
  const bestMarketPrice = Number(bm.best_price || yourMarketPrice || 0);
  const diff = bestMarketPrice - yourMarketPrice;
  const extraIncome = diff * quintals;

  const monthly = (result.price_trend?.monthly_prices || []).map((x: any) => Number(x.Modal_Price || 0));
  const trendLabel = result.price_trend?.trend || 'stable';
  const trendPct = Number(result.price_trend?.change_pct || 0);

  const shareText = `AgriChain Recommendation\nCrop: ${request?.crop}\nBest Market: ${bm.best_market || 'N/A'}\nExpected Price: ${formatINR(bestMarketPrice)}/quintal\nSpoilage Risk: ${result.spoilage?.risk_level || 'N/A'}; sell within ${result.spoilage?.days_safe || '?'} day(s).`;
  const handleShare = () => window.open(`https://wa.me/?text=${encodeURIComponent(shareText)}`, '_blank');

  const cardAnim = (i: number) => ({ initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 }, transition: { delay: 0.15 * i } });

  return (
    <div className="pb-32 px-4 pt-16 max-w-lg mx-auto space-y-4">
      <motion.div {...cardAnim(0)} className="gradient-hero rounded-2xl p-5 shadow-lg">
        <p className="text-sm text-primary-foreground/70 mb-3 font-semibold tracking-wide uppercase">{t('aiRecommendation', language)}</p>
        {(() => {
          const points = parseRecommendation(result.recommendation);
          return points.length > 1 ? (
            <div className="space-y-2.5">
              {points.map((point, i) => {
                const meta = POINT_META[i];
                return (
                  <div key={i} className="flex gap-3 bg-white/10 rounded-xl p-3 items-start">
                    {meta && <meta.Icon size={18} className={`flex-shrink-0 mt-0.5 ${meta.color}`} strokeWidth={2} />}
                    <div>
                      <p className="text-xs text-primary-foreground/60 font-semibold uppercase tracking-wide mb-0.5">{meta?.label ?? ''}</p>
                      <p className="text-primary-foreground text-sm leading-relaxed">{point.replace(/^\d+\.\s*/, '')}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-primary-foreground text-agri-body leading-relaxed">{sanitize(result.recommendation)}</p>
          );
        })()}
      </motion.div>

      {result.explainability?.top_reasons?.length ? (
        <motion.div {...cardAnim(1)} className="bg-card rounded-2xl p-5 border border-border shadow-sm">
          <h3 className="font-bold text-foreground mb-2">Why this recommendation</h3>
          <ul className="list-disc pl-5 text-sm text-foreground space-y-1">
            {result.explainability.top_reasons.map((reason: string) => <li key={reason}>{reason}</li>)}
          </ul>
          <p className="text-sm text-muted-foreground mt-2">Confidence: {result.explainability.confidence}</p>
        </motion.div>
      ) : null}

      <motion.div {...cardAnim(2)} className="bg-card rounded-2xl p-5 border border-border shadow-sm">
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <p className="text-xs text-muted-foreground mb-1">{t('yourMarket', language)}</p>
            <p className="text-xl font-bold text-foreground">{formatINR(yourMarketPrice)}</p>
          </div>
          <div className="bg-secondary/20 rounded-xl p-2">
            <p className="text-xs text-muted-foreground mb-1">{t('bestMarket', language)}</p>
            <p className="text-xl font-bold text-secondary">{formatINR(bestMarketPrice)}</p>
            <p className="text-xs text-muted-foreground">{bm.best_market || 'N/A'}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">{t('difference', language)}</p>
            <p className="text-xl font-bold text-primary"><AnimatedCounter value={diff} /></p>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-sm font-semibold text-foreground mb-2">{t('calculateIncome', language)}</p>
          <div className="flex items-center gap-3 mb-2">
            <input type="number" value={quintals} onChange={(e) => setQuintals(Number(e.target.value))} className="w-24 bg-background border border-border rounded-xl px-3 py-2 text-center font-bold tap-target" min={1} />
            <span className="text-sm text-muted-foreground">{t('quintals', language)}</span>
          </div>
          <div className="bg-primary/5 rounded-xl p-3">
            <div className="flex justify-between mb-1"><span className="text-sm text-muted-foreground">{t('atLocalMarket', language)}</span><span className="font-semibold text-foreground">{formatINR(yourMarketPrice * quintals)}</span></div>
            <div className="flex justify-between mb-1"><span className="text-sm text-muted-foreground">{t('atBestMarket', language)}</span><span className="font-semibold text-secondary">{formatINR(bestMarketPrice * quintals)}</span></div>
            <div className="flex justify-between pt-2 border-t border-border"><span className="font-bold text-foreground">{t('extraEarning', language)}</span><span className="font-bold text-xl text-primary"><AnimatedCounter value={extraIncome} /></span></div>
          </div>
        </div>
      </motion.div>

      {result.price_trend ? (
        <motion.div {...cardAnim(3)} className="bg-card rounded-2xl p-5 border border-border shadow-sm">
          <h3 className="font-bold text-foreground mb-2">{t('priceTrend', language)}</h3>
          {monthly.length ? (
            <div className="flex items-end gap-1 h-24 mb-2">
              {monthly.map((val: number, i: number) => {
                const max = Math.max(...monthly, 1);
                const height = (val / max) * 100;
                const isLast = i === monthly.length - 1;
                return <motion.div key={i} initial={{ height: 0 }} animate={{ height: `${height}%` }} transition={{ delay: 0.1 * i, duration: 0.4 }} className={`flex-1 rounded-t-lg ${isLast ? 'bg-secondary' : trendLabel === 'falling' ? 'bg-destructive/40' : 'bg-primary/40'}`} />;
              })}
            </div>
          ) : null}
          <p className={`text-lg font-bold ${trendLabel === 'falling' ? 'text-destructive' : 'text-primary'}`}>{trendLabel.toUpperCase()} ({trendPct}%)</p>
        </motion.div>
      ) : null}

      {result.spoilage ? (
        <motion.div {...cardAnim(4)} className="bg-card rounded-2xl p-5 border border-border shadow-sm">
          <h3 className="font-bold text-foreground mb-3">{t('spoilageRisk', language)}</h3>
          <SpoilageGauge score={Number(result.spoilage.risk_score || 0)} />
          <p className="text-center text-xl font-bold text-foreground mt-2">{t('daysSafe', language)}: {result.spoilage.days_safe}</p>
        </motion.div>
      ) : null}

      {result.spoilage?.actions?.length ? (
        <motion.div {...cardAnim(5)} className="bg-card rounded-2xl p-5 border border-border shadow-sm">
          <h3 className="font-bold text-foreground mb-3">{t('preservationActions', language)}</h3>
          <div className="space-y-3">
            {result.spoilage.actions.map((action: any, i: number) => (
              <div key={i} className={`rounded-xl p-3 border ${action.cost === 'Free' ? 'bg-primary/5 border-primary/20' : 'border-border'}`}>
                <div className="flex items-center justify-between mb-1"><span className="font-semibold text-foreground">{action.action}</span><span className="text-xs font-bold px-2 py-1 rounded-full bg-secondary/20 text-secondary-foreground">{action.cost}</span></div>
                <p className="text-sm text-muted-foreground">{action.description}</p>
              </div>
            ))}
          </div>
        </motion.div>
      ) : null}

      <motion.div {...cardAnim(6)} className="grid grid-cols-2 gap-3">
        {result.weather ? (
          <div className="bg-card rounded-2xl p-4 border border-border shadow-sm">
            <div className="flex items-center gap-1.5 mb-3">
              <Thermometer size={15} className="text-primary" />
              <h4 className="font-bold text-foreground text-sm">{t('weather', language)}</h4>
            </div>
            <p className="text-2xl font-bold text-foreground">{result.weather.temperature}°C</p>
            <div className="flex items-center gap-1 mt-1">
              <Droplets size={13} className="text-blue-400" />
              <p className="text-sm text-muted-foreground">Humidity {result.weather.humidity}%</p>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5 capitalize">{result.weather.description}</p>
          </div>
        ) : null}
        {result.transit_info ? (
          <div className="bg-card rounded-2xl p-4 border border-border shadow-sm">
            <div className="flex items-center gap-1.5 mb-3">
              <Truck size={15} className="text-primary" />
              <h4 className="font-bold text-foreground text-sm">{t('transit', language)}</h4>
            </div>
            <p className="text-2xl font-bold text-foreground">{result.transit_info.transit_hours}h</p>
            <div className="flex items-center gap-1 mt-1">
              <Route size={13} className="text-muted-foreground" />
              <p className="text-sm text-muted-foreground">{result.transit_info.distance_km} km</p>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">{result.transit_info.route_summary}</p>
          </div>
        ) : null}
      </motion.div>

      <div className="fixed bottom-20 left-0 right-0 px-4 z-40"><button onClick={handleShare} className="w-full max-w-lg mx-auto block py-4 rounded-2xl bg-[hsl(142_70%_45%)] text-primary-foreground font-bold text-lg btn-press tap-target shadow-lg">{t('shareWhatsApp', language)}</button></div>
    </div>
  );
};

export default ResultsPage;
