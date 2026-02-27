import { useState, useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/lib/i18n';
import { CROPS, STORAGE_TYPES } from '@/lib/data';
import { fetchSpoilage, fetchTransit } from '@/lib/api';
import { motion } from 'framer-motion';
import SpoilageGauge from '@/components/SpoilageGauge';
import { Sun, Warehouse, Wind, Thermometer, Navigation, AlertCircle, Loader2 } from 'lucide-react';

const STORAGE_ICONS: Record<string, React.ElementType> = {
  sun: Sun, warehouse: Warehouse, wind: Wind, thermometer: Thermometer,
};

const SpoilagePage = () => {
  const { language } = useLanguage();
  const [selectedCrop, setSelectedCrop] = useState('');
  const [state, setState] = useState('Maharashtra');
  const [district, setDistrict] = useState('Pune');
  const [storageType, setStorageType] = useState('basic_shed');
  const [transitHours, setTransitHours] = useState(2);
  const [isLoadingTransit, setIsLoadingTransit] = useState(false);
  const [transitSource, setTransitSource] = useState<'manual'>('manual');
  const [transitError, setTransitError] = useState('');
  const [result, setResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch transit time from OLA Maps API
  const fetchTransitTime = async () => {
    if (!state || !district) {
      setTransitError('Please select state and district first');
      return;
    }
    
    setIsLoadingTransit(true);
    setTransitError('');
    try {
      const result = await fetchTransit(district, state, district);
      if (result.success && result.transit_hours !== undefined) {
        setTransitHours(result.transit_hours);
        setTransitSource('manual'); // Mark as set
      } else {
        setTransitError('Could not calculate transit time');
      }
    } catch (err: any) {
      console.error('Failed to fetch transit time:', err);
      setTransitError(err?.message || 'Failed to fetch transit time');
      // Set default 6 hours on error
      setTransitHours(6);
    } finally {
      setIsLoadingTransit(false);
    }
  };

  const handleCheck = async () => {
    setError('');
    setIsLoading(true);
    try {
      const apiResult = await fetchSpoilage({
        crop: selectedCrop,
        state,
        district,
        storage_type: storageType,
        transit_hours: transitHours,
      });
      setResult(apiResult);
    } catch (e: any) {
      setError(e?.message || 'Could not check spoilage risk');
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  const spoilage = result?.spoilage;

  return (
    <div className="pb-24 px-4 pt-16 max-w-lg mx-auto">
      <h1 className="text-agri-heading text-foreground mb-4">{t('spoilageCheck', language)}</h1>
      {error ? <div className="mb-4 rounded-xl border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">{error}</div> : null}

      <div className="bg-card rounded-2xl p-4 mb-4 border border-border shadow-sm">
        <h2 className="font-bold text-foreground mb-3">{t('crop', language)}</h2>
        <div className="grid grid-cols-5 gap-2 mb-4">
          {CROPS.slice(0, 10).map((crop) => (
            <button key={crop.name} onClick={() => setSelectedCrop(crop.name)} className={`flex flex-col items-center p-2 rounded-xl btn-press tap-target ${selectedCrop === crop.name ? 'bg-primary/10 border-2 border-primary' : 'bg-background border border-border'}`}>
              <span className="text-xl">{crop.emoji}</span>
              <span className="text-[10px] mt-0.5 text-foreground">{crop.name}</span>
            </button>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-2 mb-4">
          <input value={state} onChange={(e) => setState(e.target.value)} placeholder={t('state', language)} className="bg-background border border-border rounded-xl px-3 py-2" />
          <input value={district} onChange={(e) => setDistrict(e.target.value)} placeholder={t('district', language)} className="bg-background border border-border rounded-xl px-3 py-2" />
        </div>

        <h2 className="font-bold text-foreground mb-3">{t('storageType', language)}</h2>
        <div className="grid grid-cols-2 gap-2 mb-4">
          {STORAGE_TYPES.map((st) => {
            const Icon = STORAGE_ICONS[st.iconKey] ?? Sun;
            return (
              <button key={st.id} onClick={() => setStorageType(st.id)} className={`p-3 rounded-xl border-2 btn-press tap-target text-center ${storageType === st.id ? 'border-primary bg-primary/10' : 'border-border bg-background'}`}>
                <Icon size={20} className="mx-auto mb-1 text-primary" strokeWidth={1.8} />
                <span className="text-xs font-medium text-foreground">{t(st.id === 'open_air' ? 'openAir' : st.id === 'basic_shed' ? 'basicShed' : st.id === 'cool_storage' ? 'coolRoom' : 'coldStorage', language)}</span>
              </button>
            );
          })}
        </div>

        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <label className="text-agri-label text-foreground">
              {t('transitHours', language)}: <strong>{transitHours}h</strong>
              {isLoadingTransit && <span className="ml-2 inline-flex items-center gap-1 text-xs text-muted-foreground"><Loader2 size={11} className="animate-spin" /> Calculating...</span>}
            </label>
            <button
              onClick={fetchTransitTime}
              disabled={!state || !district || isLoadingTransit}
              className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-primary bg-primary/10 text-primary font-semibold tap-target disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Navigation size={12} strokeWidth={2} />
              Auto-Calculate
            </button>
          </div>
          <input
            type="range"
            min={0}
            max={24}
            value={transitHours}
            onChange={(e) => {
              setTransitHours(Number(e.target.value));
              setTransitError('');
            }}
            className="w-full accent-primary h-2 tap-target"
          />
          {transitError && (
            <p className="flex items-start gap-1.5 text-xs text-destructive mt-1">
              <AlertCircle size={12} className="mt-0.5 flex-shrink-0" />{transitError}
            </p>
          )}
        </div>

        <button onClick={handleCheck} disabled={!selectedCrop || isLoading} className="w-full py-4 rounded-2xl gradient-hero text-primary-foreground font-bold text-lg btn-press tap-target disabled:opacity-50">
          {isLoading ? t('loading', language) : t('checkRisk', language)}
        </button>
      </div>

      {spoilage ? (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <div className="bg-card rounded-2xl p-5 border border-border shadow-sm">
            <SpoilageGauge score={spoilage.risk_score || 0} />
            <p className="text-center text-xl font-bold text-foreground mt-2">{t('daysSafe', language)}: {spoilage.days_safe}</p>
            <p className="text-center text-sm text-muted-foreground mt-1">{spoilage.summary}</p>
          </div>
          <div className="bg-card rounded-2xl p-4 border border-border shadow-sm space-y-2">
            {(spoilage.actions || []).map((a: any, i: number) => (
              <div key={i} className="flex justify-between items-center p-3 bg-background rounded-xl">
                <span className="text-foreground font-medium">{a.action}</span>
                <span className="text-xs font-bold text-primary bg-primary/10 px-2 py-1 rounded-full">{a.cost}</span>
              </div>
            ))}
          </div>
        </motion.div>
      ) : null}
    </div>
  );
};

export default SpoilagePage;
