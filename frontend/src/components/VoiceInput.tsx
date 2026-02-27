import { useState, useRef, useCallback } from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import type { Language } from '@/lib/i18n';

// Maps app language codes to BCP-47 codes recognised by the Web Speech API.
// Using Indian regional variants where available for best accuracy on crop/place names.
const LANG_TO_BCP47: Record<Language, string> = {
  en: 'en-IN',
  hi: 'hi-IN',
  mr: 'mr-IN',
  te: 'te-IN',
  ta: 'ta-IN',
  kn: 'kn-IN',
};

interface VoiceInputProps {
  language: Language;
  onResult: (transcript: string) => void;
  /** Extra classes forwarded to the button wrapper */
  className?: string;
  /** Tooltip / aria-label text */
  label?: string;
}

type State = 'idle' | 'listening' | 'processing' | 'unsupported';

const VoiceInput = ({ language, onResult, className = '', label = 'Speak' }: VoiceInputProps) => {
  const [micState, setMicState] = useState<State>(
    typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)
      ? 'idle'
      : 'unsupported'
  );
  const recognitionRef = useRef<any>(null);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    recognitionRef.current = null;
    setMicState('idle');
  }, []);

  const start = useCallback(() => {
    if (micState === 'listening') { stop(); return; }
    if (micState === 'unsupported') return;

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) { setMicState('unsupported'); return; }

    const rec = new SpeechRecognition();
    rec.lang = LANG_TO_BCP47[language] ?? 'en-IN';
    rec.continuous = false;
    rec.interimResults = false;
    rec.maxAlternatives = 1;

    rec.onstart = () => setMicState('listening');

    rec.onresult = (e: any) => {
      setMicState('processing');
      const transcript: string = e.results[0][0].transcript.trim();
      onResult(transcript);
      setMicState('idle');
    };

    rec.onerror = () => setMicState('idle');
    rec.onend   = () => setMicState((s) => (s === 'listening' || s === 'processing' ? 'idle' : s));

    recognitionRef.current = rec;
    rec.start();
  }, [language, micState, onResult, stop]);

  if (micState === 'unsupported') return null;

  const isListening  = micState === 'listening';
  const isProcessing = micState === 'processing';

  return (
    <button
      type="button"
      onClick={start}
      aria-label={label}
      title={label}
      className={[
        'relative flex items-center justify-center rounded-xl transition-all tap-target',
        'w-11 h-11 border-2',
        isListening
          ? 'border-destructive bg-destructive/10 text-destructive scale-110'
          : isProcessing
          ? 'border-primary/40 bg-primary/10 text-primary cursor-wait'
          : 'border-border bg-background text-muted-foreground hover:border-primary hover:text-primary',
        className,
      ].join(' ')}
    >
      {/* Pulse ring while listening */}
      {isListening && (
        <span className="absolute inset-0 rounded-xl animate-ping bg-destructive/30 pointer-events-none" />
      )}

      {isProcessing ? (
        <Loader2 size={18} className="animate-spin" />
      ) : isListening ? (
        <MicOff size={18} strokeWidth={2} />
      ) : (
        <Mic size={18} strokeWidth={2} />
      )}
    </button>
  );
};

export default VoiceInput;
