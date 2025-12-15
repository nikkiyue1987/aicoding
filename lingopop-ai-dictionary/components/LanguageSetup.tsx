import React from 'react';
import { LANGUAGES } from '../constants';
import { Language, LanguageCode } from '../types';
import { ArrowRight, Globe } from 'lucide-react';

interface LanguageSetupProps {
  onComplete: (native: Language, target: Language) => void;
}

const LanguageSetup: React.FC<LanguageSetupProps> = ({ onComplete }) => {
  const [native, setNative] = React.useState<LanguageCode>('zh');
  const [target, setTarget] = React.useState<LanguageCode>('en');

  const handleStart = () => {
    const nativeLang = LANGUAGES.find(l => l.code === native)!;
    const targetLang = LANGUAGES.find(l => l.code === target)!;
    onComplete(nativeLang, targetLang);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-yellow-50">
      <div className="max-w-md w-full bg-white rounded-3xl shadow-xl p-8 space-y-8 border-2 border-yellow-100">
        <div className="text-center space-y-2">
          <div className="bg-yellow-400 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg rotate-3">
            <Globe className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-800">LingoPop</h1>
          <p className="text-gray-500">Let's set up your language journey!</p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-2">My Native Language</label>
            <div className="grid grid-cols-2 gap-2">
              {LANGUAGES.map(lang => (
                <button
                  key={`native-${lang.code}`}
                  onClick={() => setNative(lang.code)}
                  className={`p-3 rounded-xl border-2 text-left flex items-center transition-all ${
                    native === lang.code 
                      ? 'border-yellow-400 bg-yellow-50 text-yellow-900 shadow-sm' 
                      : 'border-transparent bg-gray-50 hover:bg-gray-100 text-gray-600'
                  }`}
                >
                  <span className="mr-2 text-xl">{lang.flag}</span>
                  <span className="text-sm font-medium">{lang.name.split(' ')[0]}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-gray-100">
            <label className="block text-sm font-bold text-gray-700 mb-2">I want to learn</label>
             <div className="grid grid-cols-2 gap-2">
              {LANGUAGES.map(lang => (
                <button
                  key={`target-${lang.code}`}
                  onClick={() => setTarget(lang.code)}
                  className={`p-3 rounded-xl border-2 text-left flex items-center transition-all ${
                    target === lang.code 
                      ? 'border-violet-500 bg-violet-50 text-violet-900 shadow-sm' 
                      : 'border-transparent bg-gray-50 hover:bg-gray-100 text-gray-600'
                  }`}
                >
                   <span className="mr-2 text-xl">{lang.flag}</span>
                  <span className="text-sm font-medium">{lang.name.split(' ')[0]}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <button
          onClick={handleStart}
          className="w-full bg-gray-900 text-white py-4 rounded-2xl font-bold text-lg hover:bg-gray-800 transition-transform active:scale-95 flex items-center justify-center gap-2 shadow-lg"
        >
          Get Started <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default LanguageSetup;