import React, { useState } from 'react';
import { DictionaryEntry, Language } from '../types';
import { BookOpen, Sparkles, Volume2, Trash2 } from 'lucide-react';
import * as geminiService from '../services/geminiService';

interface NotebookViewProps {
  entries: DictionaryEntry[];
  targetLang: Language;
  nativeLang: Language;
  onDelete: (id: string) => void;
}

const NotebookView: React.FC<NotebookViewProps> = ({ entries, targetLang, nativeLang, onDelete }) => {
  const [story, setStory] = useState<string | null>(null);
  const [loadingStory, setLoadingStory] = useState(false);

  const handleGenerateStory = async () => {
    if (entries.length < 3) {
      alert("Save at least 3 words to generate a story!");
      return;
    }
    setLoadingStory(true);
    setStory(null);
    try {
      const words = entries.slice(-10).map(e => e.word); // Use last 10 words max
      const generatedStory = await geminiService.generateStoryFromWords(words, targetLang.name, nativeLang.name);
      setStory(generatedStory);
    } catch (error) {
      console.error(error);
    } finally {
      setLoadingStory(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto pb-24 p-4">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">My Notebook</h2>
        <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-bold">
          {entries.length} words
        </span>
      </div>

      {entries.length === 0 ? (
        <div className="text-center mt-20 text-gray-400">
          <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-20" />
          <p>No saved words yet.</p>
          <p className="text-sm">Start searching to fill your notebook!</p>
        </div>
      ) : (
        <>
          {/* Story Generator Card */}
          <div className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-3xl p-6 text-white shadow-xl mb-8 relative overflow-hidden">
             <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-3xl transform translate-x-10 -translate-y-10"></div>
             
             <div className="relative z-10">
               <h3 className="font-bold text-xl mb-2 flex items-center gap-2">
                 <Sparkles className="w-5 h-5 text-yellow-300" /> 
                 Story Mode
               </h3>
               <p className="text-white/90 text-sm mb-4">
                 Turn your recent words into a fun mini-story to help you remember them better!
               </p>
               
               {story ? (
                 <div className="bg-white/10 rounded-xl p-4 backdrop-blur-md border border-white/20 animate-fade-in">
                   <p className="whitespace-pre-line leading-relaxed mb-4 font-medium">{story}</p>
                   <button 
                     onClick={() => setStory(null)} 
                     className="text-xs bg-white/20 hover:bg-white/30 px-3 py-1 rounded-lg transition-colors"
                   >
                     Close Story
                   </button>
                 </div>
               ) : (
                 <button
                   onClick={handleGenerateStory}
                   disabled={loadingStory}
                   className="bg-white text-purple-600 font-bold py-3 px-6 rounded-xl hover:bg-gray-50 active:scale-95 transition-all shadow-md disabled:opacity-70 disabled:cursor-not-allowed w-full md:w-auto"
                 >
                   {loadingStory ? "Weaving magic..." : "Generate Story"}
                 </button>
               )}
             </div>
          </div>

          {/* Word List */}
          <div className="grid gap-4">
            {entries.slice().reverse().map((entry) => (
              <div key={entry.id} className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 flex items-start gap-4 group">
                {entry.imageUrl ? (
                  <img src={entry.imageUrl} alt={entry.word} className="w-16 h-16 rounded-xl object-cover bg-gray-50 shrink-0" />
                ) : (
                   <div className="w-16 h-16 rounded-xl bg-gray-100 flex items-center justify-center text-2xl shrink-0">
                     📖
                   </div>
                )}
                
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start">
                    <h3 className="font-bold text-lg text-gray-900 truncate">{entry.word}</h3>
                    <button 
                      onClick={() => onDelete(entry.id)}
                      className="text-gray-300 hover:text-red-500 transition-colors p-1"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <p className="text-gray-600 text-sm line-clamp-2">{entry.explanation}</p>
                  
                  <div className="mt-2 flex gap-2">
                    <button 
                       onClick={() => geminiService.speakText(entry.word)}
                       className="p-1.5 bg-gray-100 rounded-full text-gray-600 hover:bg-violet-100 hover:text-violet-600 transition-colors"
                    >
                      <Volume2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default NotebookView;