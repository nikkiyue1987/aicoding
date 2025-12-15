import React, { useState } from 'react';
import { DictionaryEntry } from '../types';
import { RefreshCw, ArrowRight, ArrowLeft, Volume2 } from 'lucide-react';
import * as geminiService from '../services/geminiService';

interface FlashcardViewProps {
  entries: DictionaryEntry[];
}

const FlashcardView: React.FC<FlashcardViewProps> = ({ entries }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);

  if (entries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-gray-400 p-6 text-center">
        <div className="bg-gray-100 p-6 rounded-full mb-4">
          <RefreshCw className="w-10 h-10 opacity-30" />
        </div>
        <h3 className="text-xl font-bold text-gray-600 mb-2">No Cards Yet</h3>
        <p>Save some words to the notebook to start learning!</p>
      </div>
    );
  }

  const currentCard = entries[currentIndex];

  const nextCard = () => {
    setFlipped(false);
    setTimeout(() => {
        setCurrentIndex((prev) => (prev + 1) % entries.length);
    }, 200);
  };

  const prevCard = () => {
    setFlipped(false);
    setTimeout(() => {
        setCurrentIndex((prev) => (prev - 1 + entries.length) % entries.length);
    }, 200);
  };

  const handleSpeak = (e: React.MouseEvent) => {
    e.stopPropagation();
    geminiService.speakText(currentCard.word);
  };

  return (
    <div className="max-w-md mx-auto h-[calc(100vh-8rem)] flex flex-col justify-center p-6">
      <div className="text-center mb-6">
        <span className="bg-white px-4 py-1 rounded-full text-sm font-bold text-gray-500 shadow-sm border border-gray-100">
          Card {currentIndex + 1} / {entries.length}
        </span>
      </div>

      <div className="relative w-full aspect-[3/4] perspective-1000 group cursor-pointer" onClick={() => setFlipped(!flipped)}>
        <div className={`relative w-full h-full text-center transition-all duration-500 transform-style-3d ${flipped ? 'rotate-y-180' : ''}`}>
          
          {/* Front */}
          <div className="absolute inset-0 w-full h-full bg-white rounded-3xl shadow-xl border border-gray-100 backface-hidden flex flex-col items-center justify-between p-8 overflow-hidden">
             {currentCard.imageUrl && (
                 <div className="w-full h-48 mb-6 rounded-2xl overflow-hidden bg-gray-50">
                     <img src={currentCard.imageUrl} alt="Hint" className="w-full h-full object-contain" />
                 </div>
             )}
             <div className="flex-1 flex flex-col items-center justify-center">
                 <h2 className="text-4xl font-bold text-gray-800 mb-4">{currentCard.word}</h2>
                 <button onClick={handleSpeak} className="p-3 bg-violet-50 text-violet-600 rounded-full hover:bg-violet-100 transition-colors">
                     <Volume2 className="w-6 h-6" />
                 </button>
             </div>
             <p className="text-gray-400 text-sm mt-4">Tap to flip</p>
          </div>

          {/* Back */}
          <div className="absolute inset-0 w-full h-full bg-gradient-to-br from-yellow-50 to-orange-50 rounded-3xl shadow-xl border border-yellow-100 backface-hidden rotate-y-180 flex flex-col items-center justify-center p-8">
            <h3 className="text-xl font-bold text-gray-800 mb-2">Definition</h3>
            <p className="text-lg text-gray-700 mb-8 leading-relaxed">{currentCard.explanation}</p>
            
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">Example</h3>
            <p className="text-gray-600 italic">"{currentCard.examples[0].target}"</p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex justify-between items-center mt-8 px-8">
        <button 
            onClick={prevCard}
            className="p-4 bg-white rounded-full text-gray-600 shadow-md hover:scale-110 transition-transform active:bg-gray-50"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>
        <button 
            onClick={nextCard}
            className="p-4 bg-gray-900 rounded-full text-white shadow-lg hover:scale-110 transition-transform active:bg-gray-800"
        >
          <ArrowRight className="w-6 h-6" />
        </button>
      </div>
    </div>
  );
};

export default FlashcardView;