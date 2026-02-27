import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/lib/i18n';
import { LANGUAGES } from '@/lib/i18n';
import { useLocation, useNavigate } from 'react-router-dom';
import { Home, Sparkles, BarChart2, ShieldAlert, TrendingUp } from 'lucide-react';

const tabs = [
  { key: 'home'      as const, Icon: Home,        path: '/' },
  { key: 'recommend' as const, Icon: Sparkles,    path: '/recommend' },
  { key: 'markets'   as const, Icon: BarChart2,   path: '/markets' },
  { key: 'spoilage'  as const, Icon: ShieldAlert, path: '/spoilage' },
  { key: 'insights'  as const, Icon: TrendingUp,  path: '/insights' },
];

const BottomNav = () => {
  const { language, setLanguage } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();
  const currentLang = LANGUAGES.find(l => l.code === language);

  return (
    <>
      {/* Language switcher floating button */}
      <button
        onClick={() => {
          const idx = LANGUAGES.findIndex(l => l.code === language);
          const next = LANGUAGES[(idx + 1) % LANGUAGES.length];
          setLanguage(next.code);
        }}
        className="fixed top-4 right-4 z-50 bg-card rounded-full px-3 py-2 shadow-lg btn-press tap-target flex items-center gap-1 border border-border"
        aria-label="Change language"
      >
        <span className="text-sm">{currentLang?.flag}</span>
        <span className="text-xs font-medium text-foreground">{currentLang?.label}</span>
      </button>

      <nav className="fixed bottom-0 left-0 right-0 z-50 bg-card border-t border-border safe-bottom">
        <div className="flex justify-around items-center max-w-lg mx-auto">
          {tabs.map((tab) => {
            const isActive = tab.path === '/'
              ? location.pathname === '/'
              : location.pathname.startsWith(tab.path);

            return (
              <button
                key={tab.key}
                onClick={() => navigate(tab.path)}
                className={`flex flex-col items-center py-3 px-2 tap-target btn-press transition-colors min-w-[64px] ${
                  isActive ? 'text-primary' : 'text-muted-foreground'
                }`}
                aria-label={t(tab.key, language)}
              >
                <tab.Icon
                  size={22}
                  strokeWidth={isActive ? 2.2 : 1.8}
                  className={`transition-transform ${isActive ? 'scale-110' : ''}`}
                />
                <span className="text-xs font-medium mt-0.5">{t(tab.key, language)}</span>
              </button>
            );
          })}
        </div>
      </nav>
    </>
  );
};

export default BottomNav;
