import { GoogleGenAI, Type, Modality } from "@google/genai";
import { DictionaryEntry } from '../types';
import { playPCMData } from './audioUtils';

const apiKey = process.env.API_KEY || '';
const ai = new GoogleGenAI({ apiKey });

/**
 * Look up a word/phrase explanation, examples, and casual notes.
 */
export const lookupWord = async (
  text: string,
  nativeLang: string,
  targetLang: string
): Promise<Omit<DictionaryEntry, 'id' | 'timestamp' | 'imageUrl'>> => {
  
  const prompt = `
    Analyze the text "${text}". 
    Target Language: ${targetLang}. 
    User's Native Language: ${nativeLang}.

    Provide a JSON response with:
    1. explanation: A natural definition in ${nativeLang}.
    2. examples: Two sentences in ${targetLang} with ${nativeLang} translation.
    3. casualNote: A fun, brief, chatty note about usage, tone, or culture. Like a friend explaining it. NOT a textbook. Mention synonyms or false friends if applicable.
    4. synonyms: A list of 1-3 related words in ${targetLang}.
  `;

  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: prompt,
    config: {
      responseMimeType: 'application/json',
      responseSchema: {
        type: Type.OBJECT,
        properties: {
          word: { type: Type.STRING },
          explanation: { type: Type.STRING },
          examples: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                target: { type: Type.STRING },
                native: { type: Type.STRING },
              },
            },
          },
          casualNote: { type: Type.STRING },
          synonyms: { type: Type.ARRAY, items: { type: Type.STRING } },
        },
        required: ['explanation', 'examples', 'casualNote', 'synonyms'],
      },
    },
  });

  if (!response.text) throw new Error("No text response from Gemini");
  return JSON.parse(response.text);
};

/**
 * Generate a visual representation of the word.
 */
export const generateImageForWord = async (word: string): Promise<string | undefined> => {
  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash-image',
      contents: `A fun, vibrant, minimalist vector art illustration representing the concept of "${word}". Bright colors, simple shapes. White background.`,
      config: {
        responseMimeType: 'image/png' // Requesting image mime type for output if possible, but mainly relying on parts
      }
    });

    // Extract base64 image from parts
    const parts = response.candidates?.[0]?.content?.parts;
    if (parts) {
      for (const part of parts) {
        if (part.inlineData) {
          return `data:${part.inlineData.mimeType};base64,${part.inlineData.data}`;
        }
      }
    }
    return undefined;
  } catch (error) {
    console.warn("Image generation failed", error);
    return undefined; // Fail gracefully
  }
};

/**
 * Text-to-Speech generation.
 */
export const speakText = async (text: string, voiceName: string = 'Kore') => {
  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash-preview-tts",
      contents: [{ parts: [{ text: text }] }],
      config: {
        responseModalities: [Modality.AUDIO],
        speechConfig: {
          voiceConfig: {
            prebuiltVoiceConfig: { voiceName },
          },
        },
      },
    });

    const base64Audio = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
    if (base64Audio) {
      await playPCMData(base64Audio, 24000);
    }
  } catch (error) {
    console.error("TTS failed", error);
  }
};

/**
 * Generate a story from a list of words.
 */
export const generateStoryFromWords = async (words: string[], targetLang: string, nativeLang: string): Promise<string> => {
  const prompt = `
    Write a short, creative, and funny story (max 150 words) using the following words in ${targetLang}: ${words.join(', ')}.
    Append a full translation in ${nativeLang} below the story.
    Make the words bold in the ${targetLang} text if possible.
  `;

  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: prompt,
  });

  return response.text || "Story generation failed.";
};

/**
 * Chat with context of a word.
 */
export const createChatSession = (word: string, targetLang: string, nativeLang: string, initialHistory: any[] = []) => {
    return ai.chats.create({
        model: 'gemini-2.5-flash',
        history: initialHistory,
        config: {
            systemInstruction: `You are a helpful and fun language tutor assisting a user with the word "${word}". 
            Target Language: ${targetLang}. Native Language: ${nativeLang}.
            Keep answers concise, encouraging, and easy to understand.`
        }
    });
}
