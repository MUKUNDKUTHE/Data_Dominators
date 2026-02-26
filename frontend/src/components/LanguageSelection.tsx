import { useLanguage } from '@/contexts/LanguageContext';
import { LANGUAGES, Language } from '@/lib/i18n';
import { t } from '@/lib/i18n';
import { motion } from 'framer-motion';

const LanguageSelection = () => {
  const { language, setLanguage, setHasSelectedLanguage } = useLanguage();

  const handleContinue = () => {
    setHasSelectedLanguage(true);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 gradient-hero relative overflow-hidden">
      {/* Floating leaves */}
      <div className="absolute inset-0 pointer-events-none">
        {['🍃', '🌿', '🌾', '🍂'].map((leaf, i) => (
          <motion.span
            key={i}
            className="absolute text-3xl opacity-20"
            style={{ left: `${20 + i * 20}%`, top: `${10 + i * 15}%` }}
            animate={{ y: [0, -10, 0], rotate: [0, 10, -10, 0] }}
            transition={{ duration: 3 + i, repeat: Infinity, ease: 'easeInOut' }}
          >
            {leaf}
          </motion.span>
        ))}
      </div>

      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-8"
      >
        <span className="text-6xl mb-4 block animate-float">🌾</span>
        <h1 className="text-agri-hero text-primary-foreground">AgriChain</h1>
        <p className="text-primary-foreground/80 text-agri-body mt-2">
          Smart Harvest. Better Price.
        </p>
        <p className="text-primary-foreground/60 text-agri-label mt-1">
          सही फसल। अच्छा दाम।
        </p>
      </motion.div>

      <motion.h2
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="text-xl font-semibold text-primary-foreground/90 mb-6"
      >
        {t('selectLanguage', language)}
      </motion.h2>

      <div className="grid grid-cols-2 gap-3 w-full max-w-sm mb-8">
        {LANGUAGES.map((lang, i) => (
          <motion.button
            key={lang.code}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * i }}
            onClick={() => setLanguage(lang.code)}
            className={`p-4 rounded-2xl text-center btn-press tap-target transition-all duration-200 ${
              language === lang.code
                ? 'bg-card ring-2 ring-secondary shadow-lg scale-105'
                : 'bg-primary-foreground/10 hover:bg-primary-foreground/20'
            }`}
          >
            <span className="text-2xl block mb-1">{lang.flag}</span>
            <span className={`text-lg font-semibold ${
              language === lang.code ? 'text-foreground' : 'text-primary-foreground'
            }`}>
              {lang.label}
            </span>
          </motion.button>
        ))}
      </div>

      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
        onClick={handleContinue}
        className="w-full max-w-sm py-4 rounded-2xl bg-secondary text-secondary-foreground font-bold text-xl btn-press animate-pulse-glow tap-target"
      >
        {t('continue', language)} →
      </motion.button>
    </div>
  );
};

export default LanguageSelection;
