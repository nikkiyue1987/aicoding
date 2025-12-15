import React, { useState, useRef, useEffect } from 'react';
import { Search, Volume2, Bookmark, Send, Sparkles, MessageCircle, X, ChevronRight } from 'lucide-react';
import { DictionaryEntry, Language, ChatMessage } from '../types';
import * as geminiService from '../services/geminiService';
import { Chat } from '@google/genai';

interface DictionaryViewProps {
  nativeLang: Language;
  targetLang: Language;
  onSave: (entry: DictionaryEntry) => void;
  savedIds: Set<string>;
}

const DictionaryView: React.FC<DictionaryViewProps> = ({ nativeLang, targetLang, onSave, savedIds }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DictionaryEntry | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [speaking, setSpeaking] = useState<string | null>(null);
  
  const chatSessionRef = useRef<Chat | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSearch = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setResult(null);
    setChatOpen(false);
    setMessages([]);
    chatSessionRef.current = null;

    try {
      // Parallel execution for text and image
      const textPromise = geminiService.lookupWord(query, nativeLang.name, targetLang.name);
      const imagePromise = geminiService.generateImageForWord(query);

      const [textData, imageUrl] = await Promise.all([textPromise, imagePromise]);

      const entry: DictionaryEntry = {
        id: Date.now().toString(),
        word: query,
        ...textData,
        imageUrl,
        timestamp: Date.now(),
      };

      setResult(entry);
      
      // Initialize chat session
      chatSessionRef.current = geminiService.createChatSession(query, targetLang.name, nativeLang.name);
      setMessages([{ role: 'model', text: `Hi! Ask me anything about "${query}"!` }]);

    } catch (error) {
      console.error(error);
      alert("Oops! AI took a nap. Try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSpeak = async (text: string, id: string) => {
    if (speaking) return;
    setSpeaking(id);
    await geminiService.speakText(text);
    setSpeaking(null);
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim() || !chatSessionRef.current) return;
    
    const userMsg = chatInput;
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setChatInput('');

    try {
      const response = await chatSessionRef.current.sendMessage({ message: userMsg });
      if (response.text) {
        setMessages(prev => [...prev, { role: 'model', text: response.text! }]);
      }
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="pb-24 max-w-2xl mx-auto">
      {/* Sticky Search Bar */}
      <div className="sticky top-0 bg-[#fdfbf7]/90 backdrop-blur-md z-10 p-4 border-b border-gray-100">
        <form onSubmit={handleSearch} className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={`Type in ${targetLang.name} or ${nativeLang.name}...`}
            className="w-full bg-white border-2 border-gray-200 rounded-full py-3 pl-12 pr-4 text-lg focus:border-yellow-400 focus:outline-none shadow-sm transition-colors"
          />
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
          <button 
            type="submit"
            disabled={loading || !query}
            className="absolute right-2 top-1/2 -translate-y-1/2 bg-yellow-400 text-yellow-900 p-2 rounded-full hover:bg-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? <Sparkles className="w-5 h-5 animate-spin" /> : <ChevronRight className="w-5 h-5" />}
          </button>
        </form>
      </div>

      {/* Welcome State */}
      {!result && !loading && (
        <div className="text-center mt-20 px-6">
          <div className="w-32 h-32 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-6xl">👋</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Ready to learn?</h2>
          <p className="text-gray-500">Enter a word above to see AI magic happen!</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="p-4 space-y-6 animate-fade-in-up">
          {/* Header Card */}
          <div className="bg-white rounded-3xl shadow-lg overflow-hidden border border-gray-100">
            {result.imageUrl && (
              <div className="h-48 w-full bg-gray-100 relative">
                <img src={result.imageUrl} alt={result.word} className="w-full h-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
              </div>
            )}
            
            <div className="p-6 relative">
              <button 
                onClick={() => onSave(result)}
                className={`absolute top-6 right-6 p-2 rounded-full transition-colors ${
                  savedIds.has(result.word) ? 'bg-yellow-100 text-yellow-600' : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                }`}
              >
                <Bookmark className={`w-6 h-6 ${savedIds.has(result.word) ? 'fill-current' : ''}`} />
              </button>

              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-4xl font-bold text-gray-900">{result.word}</h1>
                <button 
                  onClick={() => handleSpeak(result.word, 'headword')}
                  className="p-2 bg-violet-100 text-violet-600 rounded-full hover:bg-violet-200 active:scale-95 transition-transform"
                >
                  <Volume2 className={`w-5 h-5 ${speaking === 'headword' ? 'animate-pulse' : ''}`} />
                </button>
              </div>
              
              <p className="text-xl text-gray-600 font-medium mb-4">{result.explanation}</p>
              
              <div className="flex flex-wrap gap-2 mb-4">
                {result.synonyms.map(syn => (
                  <span key={syn} className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm font-medium">
                    {syn}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Casual Note */}
          <div className="bg-gradient-to-br from-violet-500 to-fuchsia-600 rounded-3xl p-6 text-white shadow-lg relative overflow-hidden">
             <div className="absolute -top-4 -right-4 w-24 h-24 bg-white/10 rounded-full blur-2xl"></div>
             <div className="flex items-start gap-3 relative z-10">
               <div className="bg-white/20 p-2 rounded-lg backdrop-blur-sm">
                 <Sparkles className="w-5 h-5 text-yellow-300" />
               </div>
               <div>
                 <h3 className="font-bold text-lg mb-1 opacity-90">Quick Note</h3>
                 <p className="leading-relaxed opacity-95">{result.casualNote}</p>
               </div>
             </div>
          </div>

          {/* Examples */}
          <div className="space-y-4">
            <h3 className="font-bold text-gray-900 text-lg px-2">Examples</h3>
            {result.examples.map((ex, idx) => (
              <div key={idx} className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm flex gap-4">
                 <button 
                  onClick={() => handleSpeak(ex.target, `ex-${idx}`)}
                  className="shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-yellow-50 text-yellow-600 hover:bg-yellow-100 mt-1"
                >
                  <Volume2 className={`w-4 h-4 ${speaking === `ex-${idx}` ? 'animate-pulse' : ''}`} />
                </button>
                <div>
                  <p className="text-lg font-medium text-gray-800 mb-1">{ex.target}</p>
                  <p className="text-gray-500">{ex.native}</p>
                </div>
              </div>
            ))}
          </div>
          
          {/* Chat Trigger */}
          <button 
            onClick={() => setChatOpen(true)}
            className="w-full bg-gray-900 text-white p-4 rounded-2xl flex items-center justify-center gap-2 font-bold shadow-lg active:scale-95 transition-all"
          >
            <MessageCircle className="w-5 h-5" />
            Ask more about this word
          </button>
        </div>
      )}

      {/* Bottom Sheet Chat */}
      {chatOpen && (
        <div className="fixed inset-0 z-50 flex flex-col justify-end bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-t-3xl h-[80vh] flex flex-col shadow-2xl animate-slide-up">
            <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-white rounded-t-3xl">
              <h3 className="font-bold text-lg">Chatting about "{result?.word}"</h3>
              <button onClick={() => setChatOpen(false)} className="p-2 bg-gray-100 rounded-full hover:bg-gray-200">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed ${
                    msg.role === 'user' 
                      ? 'bg-gray-900 text-white rounded-tr-none' 
                      : 'bg-white border border-gray-200 text-gray-800 rounded-tl-none shadow-sm'
                  }`}>
                    {msg.text}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <div className="p-4 bg-white border-t border-gray-100">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask a question..."
                  className="flex-1 bg-gray-100 rounded-full px-5 py-3 focus:outline-none focus:ring-2 focus:ring-yellow-400"
                />
                <button 
                  onClick={handleSendMessage}
                  disabled={!chatInput.trim()}
                  className="bg-yellow-400 text-yellow-900 p-3 rounded-full hover:bg-yellow-500 disabled:opacity-50 transition-colors"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DictionaryView;