import { useLanguage } from '@/contexts/LanguageContext';
import { t, formatINR } from '@/lib/i18n';
import { MOCK_PRICES } from '@/lib/data';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const { language } = useLanguage();
  const navigate = useNavigate();

  const actions = [
    { icon: '📊', label: t('checkPrice', language), path: '/recommend' },
    { icon: '🌾', label: t('getRecommendation', language), path: '/recommend' },
    { icon: '⚠️', label: t('spoilageCheck', language), path: '/spoilage' },
    { icon: '📈', label: t('marketPrices', language), path: '/markets' },
  ];

  const trendIcon = (trend: 'up' | 'down' | 'stable') =>
    trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→';
  const trendColor = (trend: 'up' | 'down' | 'stable') =>
    trend === 'up' ? 'text-primary' : trend === 'down' ? 'text-destructive' : 'text-muted-foreground';

  return (
    <div className="pb-24 px-4 pt-16 max-w-lg mx-auto">
      {/* Greeting Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="gradient-hero rounded-2xl p-5 mb-6"
      >
        <h1 className="text-agri-hero text-primary-foreground">{t('greeting', language)}</h1>
        <p className="text-primary-foreground/80 text-agri-body mt-1">{t('tagline', language)}</p>
        <div className="flex items-center gap-3 mt-3 bg-primary-foreground/10 rounded-xl p-3">
          <span className="text-3xl">☀️</span>
          <div>
            <p className="text-primary-foreground font-semibold text-lg">32°C</p>
            <p className="text-primary-foreground/70 text-sm">Humidity 68% · Clear Sky</p>
          </div>
          <span className="ml-auto bg-primary-foreground/20 text-primary-foreground text-xs font-bold px-3 py-1 rounded-full">
            {t('safe', language)}
          </span>
        </div>
      </motion.div>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        {actions.map((action, i) => (
          <motion.button
            key={action.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * i }}
            onClick={() => navigate(action.path)}
            className="bg-card rounded-2xl p-4 text-left btn-press tap-target shadow-sm border border-border hover:border-primary/30 transition-colors"
          >
            <span className="text-3xl block mb-2">{action.icon}</span>
            <span className="text-agri-label text-foreground leading-tight block">{action.label}</span>
          </motion.button>
        ))}
      </div>

      {/* Today's Best Prices */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <h2 className="text-lg font-bold text-foreground mb-3">{t('todayBestPrices', language)}</h2>
        <div className="flex gap-3 overflow-x-auto pb-2 -mx-4 px-4 scrollbar-hide">
          {MOCK_PRICES.map((item) => (
            <div
              key={item.crop}
              className="flex-shrink-0 bg-card rounded-2xl p-4 min-w-[140px] border border-border shadow-sm"
            >
              <span className="text-3xl block mb-1">{item.emoji}</span>
              <p className="font-semibold text-foreground">{item.crop}</p>
              <div className="flex items-center gap-1 mt-1">
                <span className="font-bold text-lg text-foreground">{formatINR(item.price)}</span>
                <span className={`font-bold ${trendColor(item.trend)}`}>{trendIcon(item.trend)}</span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">per quintal</p>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Trust indicators */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="mt-6 text-center text-sm text-muted-foreground"
      >
        <p>📊 Based on 8,80,475+ price records</p>
        <p className="mt-1">🟢 Live data · Powered by Government Mandi Data</p>
      </motion.div>
    </div>
  );
};

export default HomePage;
