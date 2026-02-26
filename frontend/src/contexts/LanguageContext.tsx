import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Language } from '@/lib/i18n';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  hasSelectedLanguage: boolean;
  setHasSelectedLanguage: (v: boolean) => void;
}

const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  hasSelectedLanguage: false,
  setHasSelectedLanguage: () => {},
});

export const useLanguage = () => useContext(LanguageContext);

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    return (localStorage.getItem('agrichain-lang') as Language) || 'en';
  });
  const [hasSelectedLanguage, setHasSelectedLanguage] = useState(() => {
    return localStorage.getItem('agrichain-lang-selected') === 'true';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('agrichain-lang', lang);
  };

  useEffect(() => {
    if (hasSelectedLanguage) {
      localStorage.setItem('agrichain-lang-selected', 'true');
    }
  }, [hasSelectedLanguage]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, hasSelectedLanguage, setHasSelectedLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};
