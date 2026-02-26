import { useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/lib/i18n';
import { CROPS, INDIAN_STATES, STORAGE_TYPES } from '@/lib/data';
import { fetchRecommendation, RecommendRequest } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const RecommendPage = () => {
  const { language } = useLanguage();
  const navigate = useNavigate();
  const [selectedCrop, setSelectedCrop] = useState('');
  const [cropSearch, setCropSearch] = useState('');
  const [grade, setGrade] = useState('Medium');
  const [state, setState] = useState('');
  const [district, setDistrict] = useState('');
  const [market, setMarket] = useState('');
  const [storageType, setStorageType] = useState('basic_shed');
  const [transitHours, setTransitHours] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showSoil, setShowSoil] = useState(false);
  const [variety, setVariety] = useState('');

  const filteredCrops = CROPS.filter((c) => c.name.toLowerCase().includes(cropSearch.toLowerCase()));

  const handleSubmit = async () => {
    setError('');
    setIsLoading(true);
    const harvestDate = new Date();
    harvestDate.setDate(harvestDate.getDate() + 7);

    const request: RecommendRequest = {
      crop: selectedCrop,
      variety: variety || 'Local',
      grade,
      state,
      district,
      market: market || district,
      harvest_date: harvestDate.toISOString().split('T')[0],
      ph: 6.5,
      soil_ec: 0.6,
      phosphorus: 20,
      potassium: 150,
      urea: 50,
      tsp: 22,
      mop: 30,
      moisture: 68,
      temperature: 72,
      storage_type: storageType,
      transit_hours: transitHours,
    };

    try {
      const result = await fetchRecommendation(request);
      localStorage.setItem('agrichain-last-result', JSON.stringify(result));
      localStorage.setItem('agrichain-last-request', JSON.stringify(request));
      navigate('/results');
    } catch (e: any) {
      setError(e?.message || 'Failed to fetch recommendation from API');
    } finally {
      setIsLoading(false);
    }
  };

  const storageRiskColor = (risk: string) => {
    switch (risk) {
      case 'high': return 'border-destructive bg-destructive/10';
      case 'medium': return 'border-secondary bg-secondary/10';
      case 'low': return 'border-primary bg-primary/10';
      case 'safe': return 'border-blue-500 bg-blue-50';
      default: return 'border-border';
    }
  };

  if (isLoading) {
    return <LoadingScreen language={language} />;
  }

  return (
    <div className="pb-24 px-4 pt-16 max-w-lg mx-auto">
      <h1 className="text-agri-heading text-foreground mb-4">{t('getRecommendation', language)}</h1>

      {error ? <div className="mb-4 rounded-xl border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">{error}</div> : null}

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="bg-card rounded-2xl p-4 mb-4 border border-border shadow-sm">
        <h2 className="text-lg font-bold text-foreground mb-3">{t('yourCrop', language)}</h2>
        <input type="text" placeholder={t('searchCrop', language)} value={cropSearch} onChange={(e) => setCropSearch(e.target.value)} className="w-full bg-background border border-border rounded-xl px-4 py-3 text-agri-body mb-3 tap-target" />
        <div className="grid grid-cols-4 gap-2 max-h-48 overflow-y-auto mb-3">
          {filteredCrops.slice(0, 16).map((crop) => (
            <button key={crop.name} onClick={() => setSelectedCrop(crop.name)} className={`flex flex-col items-center p-2 rounded-xl btn-press tap-target transition-all ${selectedCrop === crop.name ? 'bg-primary/10 border-2 border-primary scale-105' : 'bg-background border border-border'}`}>
              <span className="text-2xl">{crop.emoji}</span>
              <span className="text-xs mt-1 text-foreground">{crop.name}</span>
            </button>
          ))}
        </div>
        <input type="text" placeholder={t('variety', language) + ' (' + t('optional', language) + ')'} value={variety} onChange={(e) => setVariety(e.target.value)} className="w-full bg-background border border-border rounded-xl px-4 py-3 text-agri-body mb-3 tap-target" />
        <div className="flex gap-2">
          {['Premium', 'Medium', 'Standard'].map((g) => (
            <button key={g} onClick={() => setGrade(g)} className={`flex-1 py-3 rounded-xl font-semibold btn-press tap-target text-sm ${grade === g ? 'bg-primary text-primary-foreground' : 'bg-background border border-border text-foreground'}`}>
              {g === 'Premium' ? t('premium', language) : g === 'Standard' ? t('standard', language) : t('medium', language)}
            </button>
          ))}
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-card rounded-2xl p-4 mb-4 border border-border shadow-sm">
        <h2 className="text-lg font-bold text-foreground mb-3">{t('yourLocation', language)}</h2>
        <select value={state} onChange={(e) => setState(e.target.value)} className="w-full bg-background border border-border rounded-xl px-4 py-3 text-agri-body mb-3 tap-target">
          <option value="">{t('state', language)}</option>
          {INDIAN_STATES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <input type="text" placeholder={t('district', language)} value={district} onChange={(e) => setDistrict(e.target.value)} className="w-full bg-background border border-border rounded-xl px-4 py-3 text-agri-body mb-3 tap-target" />
        <input type="text" placeholder={t('bestMarket', language) + ' (' + t('optional', language) + ')'} value={market} onChange={(e) => setMarket(e.target.value)} className="w-full bg-background border border-border rounded-xl px-4 py-3 text-agri-body tap-target" />
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="bg-card rounded-2xl p-4 mb-4 border border-border shadow-sm">
        <h2 className="text-lg font-bold text-foreground mb-3">{t('storageConditions', language)}</h2>
        <div className="grid grid-cols-2 gap-2 mb-4">
          {STORAGE_TYPES.map((st) => (
            <button key={st.id} onClick={() => setStorageType(st.id)} className={`p-3 rounded-xl border-2 btn-press tap-target text-center transition-all ${storageType === st.id ? storageRiskColor(st.risk) + ' scale-105' : 'border-border bg-background'}`}>
              <span className="text-2xl block">{st.icon}</span>
              <span className="text-sm font-medium text-foreground">{t(st.id === 'open_air' ? 'openAir' : st.id === 'basic_shed' ? 'basicShed' : st.id === 'cool_storage' ? 'coolRoom' : 'coldStorage', language)}</span>
            </button>
          ))}
        </div>
        <div>
          <label className="text-agri-label text-foreground block mb-2">{t('transitHours', language)}: <strong>{transitHours}h</strong></label>
          <input type="range" min={0} max={24} value={transitHours} onChange={(e) => setTransitHours(Number(e.target.value))} className="w-full accent-primary h-2 tap-target" />
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <button onClick={() => setShowSoil(!showSoil)} className="w-full bg-card rounded-2xl p-4 mb-4 border border-border shadow-sm text-left flex justify-between items-center">
          <span className="text-lg font-bold text-foreground">{t('soilInfo', language)}</span>
          <span className="text-sm text-muted-foreground">({t('optional', language)}) {showSoil ? '^' : 'v'}</span>
        </button>
        <AnimatePresence>
          {showSoil && (
            <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden mb-4">
              <div className="bg-card rounded-2xl p-4 border border-border shadow-sm">
                <p className="text-sm text-muted-foreground mb-3">Default soil values are used from backend unless you extend this form.</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      <motion.button initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} onClick={handleSubmit} disabled={!selectedCrop || !state || !district} className="w-full py-4 rounded-2xl gradient-hero text-primary-foreground font-bold text-xl btn-press tap-target shadow-lg disabled:opacity-50 disabled:cursor-not-allowed">
        {t('getMyRecommendation', language)}
      </motion.button>
    </div>
  );
};

const LoadingScreen = ({ language }: { language: string }) => {
  const steps = [
    { key: 'checkingPrices' as const, label: 'Price' },
    { key: 'analyzingWeather' as const, label: 'Weather' },
    { key: 'gettingBestMarket' as const, label: 'Market' },
  ];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6">
      <motion.span className="text-4xl mb-8" animate={{ rotate: [0, 10, -10, 0] }} transition={{ duration: 2, repeat: Infinity }}>AgriChain</motion.span>
      <div className="space-y-4 w-full max-w-xs">
        {steps.map((step, i) => (
          <motion.div key={step.key} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 1.2 }} className="flex items-center gap-3 bg-card rounded-xl p-4 border border-border">
            <span className="text-primary text-xl">OK</span>
            <span className="text-agri-body text-foreground">{step.label} - {t(step.key, language as any)}</span>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default RecommendPage;
