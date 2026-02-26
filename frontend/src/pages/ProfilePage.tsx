import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/lib/i18n';
import { LANGUAGES } from '@/lib/i18n';
import { motion } from 'framer-motion';

const ProfilePage = () => {
  const { language, setLanguage, setHasSelectedLanguage } = useLanguage();

  return (
    <div className="pb-24 px-4 pt-16 max-w-lg mx-auto">
      <h1 className="text-agri-heading text-foreground mb-6">👤 {t('profile', language)}</h1>

      {/* Language */}
      <div className="bg-card rounded-2xl p-4 mb-4 border border-border shadow-sm">
        <h2 className="font-bold text-foreground mb-3">{t('selectLanguage', language)}</h2>
        <div className="grid grid-cols-3 gap-2">
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              onClick={() => setLanguage(lang.code)}
              className={`p-3 rounded-xl btn-press tap-target text-center ${
                language === lang.code ? 'bg-primary text-primary-foreground' : 'bg-background border border-border text-foreground'
              }`}
            >
              <span className="block text-lg">{lang.flag}</span>
              <span className="text-xs font-medium">{lang.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Settings */}
      <div className="bg-card rounded-2xl p-4 mb-4 border border-border shadow-sm space-y-3">
        <h2 className="font-bold text-foreground">{t('settings', language)}</h2>
        <div className="flex justify-between items-center py-2">
          <span className="text-foreground">Default State</span>
          <span className="text-muted-foreground">Maharashtra</span>
        </div>
        <div className="flex justify-between items-center py-2">
          <span className="text-foreground">Default Crops</span>
          <span className="text-muted-foreground">🍅 🧅 🌾</span>
        </div>
      </div>

      {/* About */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-card rounded-2xl p-5 border border-border shadow-sm">
        <h2 className="font-bold text-foreground mb-3">{t('about', language)}</h2>
        <div className="space-y-2 text-sm text-muted-foreground">
          <p>📊 8,80,475+ price records analyzed</p>
          <p>🗺️ 28 states covered</p>
          <p>🌾 78 crops supported</p>
          <p>🌤️ Live weather from OpenWeather</p>
          <p>🚛 Real transit time from OLA Maps</p>
          <p>🤖 AI powered by LLaMA 3.3 70B</p>
          <p className="pt-2 text-xs">Powered by Government Mandi Data</p>
        </div>
      </motion.div>

      <button
        onClick={() => {
          setHasSelectedLanguage(false);
        }}
        className="w-full mt-4 py-3 rounded-xl bg-background border border-border text-muted-foreground btn-press tap-target"
      >
        Change Language (Full Screen)
      </button>
    </div>
  );
};

export default ProfilePage;
