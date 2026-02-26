import { useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/lib/i18n';
import { CROPS, STORAGE_TYPES } from '@/lib/data';
import { fetchSpoilage } from '@/lib/api';
import { motion } from 'framer-motion';
import SpoilageGauge from '@/components/SpoilageGauge';

const SpoilagePage = () => {
  const { language } = useLanguage();
  const [selectedCrop, setSelectedCrop] = useState('');
  const [state, setState] = useState('Maharashtra');
  const [district, setDistrict] = useState('Pune');
  const [storageType, setStorageType] = useState('basic_shed');
  const [transitHours, setTransitHours] = useState(2);
  const [result, setResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

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
          {STORAGE_TYPES.map((st) => (
            <button key={st.id} onClick={() => setStorageType(st.id)} className={`p-3 rounded-xl border-2 btn-press tap-target text-center ${storageType === st.id ? 'border-primary bg-primary/10' : 'border-border bg-background'}`}>
              <span className="text-xl block">{st.icon}</span>
              <span className="text-xs font-medium text-foreground">{t(st.id === 'open_air' ? 'openAir' : st.id === 'basic_shed' ? 'basicShed' : st.id === 'cool_storage' ? 'coolRoom' : 'coldStorage', language)}</span>
            </button>
          ))}
        </div>

        <label className="text-agri-label text-foreground block mb-2">{t('transitHours', language)}: <strong>{transitHours}h</strong></label>
        <input type="range" min={0} max={24} value={transitHours} onChange={(e) => setTransitHours(Number(e.target.value))} className="w-full accent-primary h-2 tap-target mb-4" />

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
