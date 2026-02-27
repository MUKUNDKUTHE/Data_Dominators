import { useState, useRef } from 'react';
import { fetchGradeCrop, fetchLossRisk } from '@/lib/api';
import { CROPS } from '@/lib/data';
import { Camera, Upload, Loader2, Star, AlertTriangle, IndianRupee, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const STORAGE_TYPES = [
  { value: 'open_air',    label: 'Open Air' },
  { value: 'basic_shed',  label: 'Basic Shed' },
  { value: 'cool_storage',label: 'Cool Storage' },
  { value: 'cold_storage',label: 'Cold Storage' },
];

export default function GradePage() {
  const navigate   = useNavigate();
  const fileRef    = useRef<HTMLInputElement>(null);

  const [crop, setCrop]               = useState('Tomato');
  const [imagePreview, setPreview]    = useState<string | null>(null);
  const [base64, setBase64]           = useState<string>('');
  const [gradeResult, setGradeResult] = useState<any>(null);

  const [showLoss, setShowLoss]       = useState(false);
  const [qty, setQty]                 = useState(10);
  const [price, setPrice]             = useState(1500);
  const [spoilage, setSpoilage]       = useState(40);
  const [storage, setStorage]         = useState('basic_shed');
  const [lossResult, setLossResult]   = useState<any>(null);

  const [loading, setLoading]         = useState(false);
  const [lossLoading, setLossLoading] = useState(false);
  const [error, setError]             = useState('');

  function handleFile(file: File) {
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setPreview(dataUrl);
      // Strip the data:image/jpeg;base64, prefix
      setBase64(dataUrl.split(',')[1]);
    };
    reader.readAsDataURL(file);
  }

  async function handleGrade() {
    if (!base64) { setError('Please select or take a photo first'); return; }
    setLoading(true);
    setError('');
    try {
      const result = await fetchGradeCrop({ crop, image_base64: base64 });
      setGradeResult(result);
    } catch (e: any) {
      setError(e.message || 'Grading failed');
    } finally {
      setLoading(false);
    }
  }

  async function handleLossRisk() {
    setLossLoading(true);
    try {
      const result = await fetchLossRisk({
        crop, quantity_quintals: qty, predicted_price: price,
        spoilage_score: spoilage, storage_type: storage,
      });
      setLossResult(result);
    } catch (e: any) {
      setError(e.message || 'Loss risk calculation failed');
    } finally {
      setLossLoading(false);
    }
  }

  const gradeColor =
    gradeResult?.grade === 'A' ? 'text-green-400 bg-green-500/10 border-green-500/30' :
    gradeResult?.grade === 'B' ? 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30' :
                                  'text-red-400 bg-red-500/10 border-red-500/30';

  const urgencyColor =
    lossResult?.urgency === 'critical' ? 'text-red-400' :
    lossResult?.urgency === 'high'     ? 'text-orange-400' :
    lossResult?.urgency === 'medium'   ? 'text-yellow-400' : 'text-green-400';

  return (
    <div className="min-h-screen bg-background pb-24 pt-4">
      <div className="max-w-lg mx-auto px-4 space-y-5">

        {/* Header */}
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="p-2 rounded-xl hover:bg-card btn-press">
            <ArrowLeft size={18} className="text-muted-foreground" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-foreground">Grade My Crop</h1>
            <p className="text-sm text-muted-foreground">AI-powered AGMARK quality grading</p>
          </div>
        </div>

        {/* Crop Select */}
        <div className="bg-card border border-border rounded-2xl p-4 space-y-3">
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Crop</label>
            <select
              value={crop}
              onChange={e => setCrop(e.target.value)}
              className="w-full mt-1 bg-input border border-border rounded-xl px-3 py-2 text-sm text-foreground"
            >
              {CROPS.slice(0, 30).map(c => <option key={c.name} value={c.name}>{c.emoji} {c.name}</option>)}
            </select>
          </div>

          {/* Image Upload */}
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
          />

          {imagePreview ? (
            <div className="relative">
              <img src={imagePreview} alt="Crop preview" className="w-full h-48 object-cover rounded-xl border border-border" />
              <button
                onClick={() => { setPreview(null); setBase64(''); setGradeResult(null); }}
                className="absolute top-2 right-2 bg-black/60 text-white rounded-full w-7 h-7 flex items-center justify-center text-xs"
              >✕</button>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => fileRef.current?.click()}
                className="flex flex-col items-center gap-2 py-6 border-2 border-dashed border-border rounded-xl text-muted-foreground text-sm btn-press hover:border-primary/50 transition-colors"
              >
                <Camera size={24} />
                Take Photo
              </button>
              <button
                onClick={() => { if(fileRef.current) { fileRef.current.removeAttribute('capture'); fileRef.current.click(); }}}
                className="flex flex-col items-center gap-2 py-6 border-2 border-dashed border-border rounded-xl text-muted-foreground text-sm btn-press hover:border-primary/50 transition-colors"
              >
                <Upload size={24} />
                Upload Image
              </button>
            </div>
          )}

          <button
            onClick={handleGrade}
            disabled={loading || !base64}
            className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-semibold text-sm flex items-center justify-center gap-2 btn-press disabled:opacity-50"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Star size={16} />}
            {loading ? 'Grading…' : 'Grade This Crop'}
          </button>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-sm text-red-400">{error}</div>
        )}

        {/* Grade Result */}
        {gradeResult && (
          <div className="bg-card border border-border rounded-2xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="font-bold text-sm text-foreground">Grading Result</h2>
              <div className={`border rounded-xl px-4 py-1 text-2xl font-black ${gradeColor}`}>
                Grade {gradeResult.grade}
              </div>
            </div>

            {gradeResult.confidence > 0 && (
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full"
                    style={{ width: `${gradeResult.confidence}%` }}
                  />
                </div>
                <span className="text-xs text-muted-foreground">{gradeResult.confidence}% confidence</span>
              </div>
            )}

            {/* Quality attributes */}
            {[
              ['Color Uniformity', gradeResult.color_uniformity],
              ['Size Consistency', gradeResult.size_consistency],
              ['Surface Defects',  gradeResult.surface_defects],
              ['Bruising',         gradeResult.bruising],
            ].filter(([, v]) => v).map(([k, v]) => (
              <div key={String(k)} className="flex justify-between text-xs py-1 border-b border-border last:border-0">
                <span className="text-muted-foreground">{k}</span>
                <span className="text-foreground font-medium">{v}</span>
              </div>
            ))}

            {/* Reason + tip */}
            <div className="bg-muted/30 rounded-xl p-3 space-y-2">
              <p className="text-sm text-foreground">{gradeResult.short_reason}</p>
              {gradeResult.actionable_tip && (
                <div className="flex items-start gap-2">
                  <AlertTriangle size={14} className="text-yellow-400 mt-0.5 shrink-0" />
                  <p className="text-xs text-yellow-400">{gradeResult.actionable_tip}</p>
                </div>
              )}
            </div>

            {/* Price premium */}
            {gradeResult.price_premium_pct > 0 && (
              <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-xl px-3 py-2">
                <IndianRupee size={14} className="text-green-400" />
                <p className="text-xs text-green-400 font-semibold">
                  Sorting to Grade A could earn {gradeResult.price_premium_pct}% more per quintal
                </p>
              </div>
            )}
          </div>
        )}

        {/* Loss Insurance Section */}
        <div className="bg-card border border-border rounded-2xl overflow-hidden">
          <button
            onClick={() => setShowLoss(!showLoss)}
            className="w-full flex items-center justify-between px-4 py-3 btn-press"
          >
            <div className="flex items-center gap-2">
              <IndianRupee size={18} className="text-primary" />
              <span className="text-sm font-semibold text-foreground">Loss Insurance Estimator</span>
            </div>
            <span className="text-muted-foreground text-lg">{showLoss ? '−' : '+'}</span>
          </button>

          {showLoss && (
            <div className="px-4 pb-4 space-y-3 border-t border-border pt-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-muted-foreground">Quantity (qtl)</label>
                  <input type="number" value={qty} min={1} onChange={e => setQty(Number(e.target.value))}
                    className="w-full mt-1 bg-input border border-border rounded-xl px-3 py-2 text-sm text-foreground" />
                </div>
                <div>
                  <label className="text-xs text-muted-foreground">Price (₹/qtl)</label>
                  <input type="number" value={price} min={100} onChange={e => setPrice(Number(e.target.value))}
                    className="w-full mt-1 bg-input border border-border rounded-xl px-3 py-2 text-sm text-foreground" />
                </div>
                <div>
                  <label className="text-xs text-muted-foreground">Spoilage Score (0-100)</label>
                  <input type="number" value={spoilage} min={0} max={100} onChange={e => setSpoilage(Number(e.target.value))}
                    className="w-full mt-1 bg-input border border-border rounded-xl px-3 py-2 text-sm text-foreground" />
                </div>
                <div>
                  <label className="text-xs text-muted-foreground">Storage Type</label>
                  <select value={storage} onChange={e => setStorage(e.target.value)}
                    className="w-full mt-1 bg-input border border-border rounded-xl px-3 py-2 text-sm text-foreground">
                    {STORAGE_TYPES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                  </select>
                </div>
              </div>

              <button
                onClick={handleLossRisk}
                disabled={lossLoading}
                className="w-full py-2.5 rounded-xl bg-primary text-primary-foreground font-semibold text-sm flex items-center justify-center gap-2 btn-press"
              >
                {lossLoading ? <Loader2 size={14} className="animate-spin" /> : <IndianRupee size={14} />}
                Calculate My Risk
              </button>

              {/* Loss Risk Result */}
              {lossResult && (
                <div className="space-y-3 mt-1">
                  <p className="text-sm text-muted-foreground">{lossResult.summary}</p>

                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { label: 'Value at Risk',   value: `₹${lossResult.value_at_risk?.toLocaleString('en-IN')}` },
                      { label: 'Expected Loss',   value: `₹${lossResult.expected_loss?.toLocaleString('en-IN')}` },
                      { label: 'Upgrade Cost',    value: lossResult.upgrade_cost > 0 ? `₹${lossResult.upgrade_cost}` : 'N/A' },
                      { label: 'Loss Saved',      value: `₹${lossResult.loss_saved?.toLocaleString('en-IN')}` },
                    ].map(item => (
                      <div key={item.label} className="bg-muted/30 rounded-xl p-3">
                        <p className="text-xs text-muted-foreground">{item.label}</p>
                        <p className="text-base font-bold text-foreground">{item.value}</p>
                      </div>
                    ))}
                  </div>

                  {lossResult.roi > 0 && (
                    <div className="bg-green-500/10 border border-green-500/20 rounded-xl px-3 py-2">
                      <p className={`text-sm font-semibold ${urgencyColor}`}>
                        ROI on storage upgrade: {lossResult.roi}x
                      </p>
                      <p className="text-xs text-muted-foreground mt-0.5">{lossResult.upgrade_tip}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
