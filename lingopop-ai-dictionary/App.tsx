import React, { useState, useEffect } from 'react';
import LanguageSetup from './components/LanguageSetup';
import DictionaryView from './components/DictionaryView';
import NotebookView from './components/NotebookView';
import FlashcardView from './components/FlashcardView';
import { AppMode, DictionaryEntry, Language } from './types';
import { Book, Search, BrainCircuit } from 'lucide-react';

function App() {
  const [mode, setMode] = useState<AppMode>('setup');
  const [nativeLang, setNativeLang] = useState<Language | null>(null);
  const [targetLang, setTargetLang] = useState<Language | null>(null);
  const [notebook, setNotebook] = useState<DictionaryEntry[]>([]);
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());

  // Load from local storage
  useEffect(() => {
    const saved = localStorage.getItem('lingopop_notebook');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setNotebook(parsed);
        setSavedIds(new Set(parsed.map((e: DictionaryEntry) => e.word)));
      } catch (e) {
        console.error("Failed to load notebook", e);
      }
    }
    
    // Check saved language preference
    const savedLangs = localStorage.getItem('lingopop_langs');
    if (savedLangs) {
        const { native, target } = JSON.parse(savedLangs);
        setNativeLang(native);
        setTargetLang(target);
        setMode('dictionary');
    }
  }, []);

  // Save to local storage
  useEffect(() => {
    localStorage.setItem('lingopop_notebook', JSON.stringify(notebook));
  }, [notebook]);

  const handleLanguageComplete = (native: Language, target: Language) => {
    setNativeLang(native);
    setTargetLang(target);
    localStorage.setItem('lingopop_langs', JSON.stringify({ native, target }));
    setMode('dictionary');
  };

  const handleSaveWord = (entry: DictionaryEntry) => {
    if (savedIds.has(entry.word)) {
      // Remove
      setNotebook(prev => prev.filter(e => e.word !== entry.word));
      setSavedIds(prev => {
        const next = new Set(prev);
        next.delete(entry.word);
        return next;
      });
    } else {
      // Add
      setNotebook(prev => [...prev, entry]);
      setSavedIds(prev => new Set(prev).add(entry.word));
    }
  };

  const handleDeleteWord = (id: string) => {
    const entry = notebook.find(e => e.id === id);
    if(entry) {
        setNotebook(prev => prev.filter(e => e.id !== id));
        setSavedIds(prev => {
            const next = new Set(prev);
            next.delete(entry.word);
            return next;
        });
    }
  };

  if (mode === 'setup' || !nativeLang || !targetLang) {
    return <LanguageSetup onComplete={handleLanguageComplete} />;
  }

  return (
    <div className="min-h-screen bg-[#fdfbf7] text-gray-800">
      
      {/* View Container */}
      <main className="min-h-screen">
        {mode === 'dictionary' && (
          <DictionaryView 
            nativeLang={nativeLang} 
            targetLang={targetLang} 
            onSave={handleSaveWord}
            savedIds={savedIds}
          />
        )}
        {mode === 'notebook' && (
          <NotebookView 
            entries={notebook} 
            targetLang={targetLang}
            nativeLang={nativeLang}
            onDelete={handleDeleteWord}
          />
        )}
        {mode === 'flashcards' && (
          <FlashcardView entries={notebook} />
        )}
      </main>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-6 py-2 pb-6 z-40 flex justify-around items-center shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
        <button 
          onClick={() => setMode('notebook')}
          className={`flex flex-col items-center gap-1 p-2 rounded-xl transition-colors w-20 ${mode === 'notebook' ? 'text-violet-600' : 'text-gray-400 hover:text-gray-600'}`}
        >
          <Book className={`w-6 h-6 ${mode === 'notebook' ? 'fill-current' : ''}`} />
          <span className="text-[10px] font-bold">Notebook</span>
        </button>

        <button 
          onClick={() => setMode('dictionary')}
          className="flex flex-col items-center justify-center -mt-8"
        >
          <div className={`w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-transform ${mode === 'dictionary' ? 'bg-yellow-400 text-yellow-900 scale-110' : 'bg-gray-900 text-white hover:scale-105'}`}>
            <Search className="w-6 h-6" />
          </div>
          <span className={`text-[10px] font-bold mt-2 ${mode === 'dictionary' ? 'text-yellow-600' : 'text-gray-400'}`}>Search</span>
        </button>

        <button 
           onClick={() => setMode('flashcards')}
           className={`flex flex-col items-center gap-1 p-2 rounded-xl transition-colors w-20 ${mode === 'flashcards' ? 'text-violet-600' : 'text-gray-400 hover:text-gray-600'}`}
        >
          <BrainCircuit className={`w-6 h-6 ${mode === 'flashcards' ? 'fill-current' : ''}`} />
          <span className="text-[10px] font-bold">Learn</span>
        </button>
      </div>

    </div>
  );
}

export default App;