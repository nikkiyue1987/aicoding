export type LanguageCode = 'en' | 'zh' | 'es' | 'fr' | 'de' | 'jp' | 'ko' | 'ru' | 'pt' | 'ar';

export interface Language {
  code: LanguageCode;
  name: string;
  flag: string; // Emoji
}

export interface ExampleSentence {
  target: string;
  native: string;
}

export interface DictionaryEntry {
  id: string;
  word: string; // The input word/phrase
  explanation: string; // Native language explanation
  examples: ExampleSentence[];
  casualNote: string; // Fun context, tone, cultural nuance
  synonyms: string[]; // Related words
  imageUrl?: string; // Base64 or URL
  timestamp: number;
}

export interface ChatMessage {
  role: 'user' | 'model';
  text: string;
}

export type AppMode = 'setup' | 'dictionary' | 'notebook' | 'flashcards';
