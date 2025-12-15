import { DictionaryEntry } from '../types';
import { playAudioFromUrl, playMp3FromBase64 } from './audioUtils';

const apiKey = process.env.API_KEY || '';
// Use Vite proxy to avoid CORS issues
const API_BASE_URL = '/api';

// Extract group_id from JWT token
function getGroupId(): string {
    try {
        const parts = apiKey.split('.');
        if (parts.length !== 3) return '';
        const payload = JSON.parse(atob(parts[1]));
        return payload.GroupID || '';
    } catch {
        return '';
    }
}

const groupId = getGroupId();

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

    Response format:
    {
      "word": "the word",
      "explanation": "...",
      "examples": [{"target": "...", "native": "..."}],
      "casualNote": "...",
      "synonyms": ["..."]
    }
  `;

    try {
        console.log('Calling MiniMax API with fetch', { groupId });

        const response = await fetch(`${API_BASE_URL}/v1/text/chatcompletion_v2?GroupId=${groupId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: 'MiniMax-M2',
                messages: [
                    { role: 'user', content: prompt }
                ],
                tokens_to_generate: 2048,
            }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('MiniMax API Error Response:', errorText);
            throw new Error(`API request failed: ${response.status} ${errorText}`);
        }

        const data = await response.json();
        console.log('MiniMax API Response:', data);

        const content = data.choices?.[0]?.message?.content;
        if (!content) throw new Error("No response from MiniMax");

        // Parse JSON from response
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            return JSON.parse(jsonMatch[0]);
        }
        return JSON.parse(content);
    } catch (error: any) {
        console.error('MiniMax API Error:', {
            message: error.message,
            status: error.status,
            error: error.error,
            fullError: error
        });
        throw new Error(`MiniMax API failed: ${error.message || 'Unknown error'}`);
    }
};

/**
 * Generate a visual representation of the word using MiniMax Image API.
 */
export const generateImageForWord = async (word: string): Promise<string | undefined> => {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/image_generation?GroupId=${groupId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: 'image-01',
                prompt: `A fun, vibrant, minimalist vector art illustration representing the concept of "${word}". Bright colors, simple shapes. White background.`,
                n: 1,
                aspect_ratio: '1:1',
            }),
        });

        if (!response.ok) {
            console.warn("Image generation failed:", await response.text());
            return undefined;
        }

        const data = await response.json();
        // MiniMax returns image URL or base64
        if (data.data && data.data[0]) {
            const imageData = data.data[0];
            if (imageData.url) {
                return imageData.url;
            } else if (imageData.b64_json) {
                return `data:image/png;base64,${imageData.b64_json}`;
            }
        }
        return undefined;
    } catch (error) {
        console.warn("Image generation failed", error);
        return undefined;
    }
};

/**
 * Text-to-Speech generation using MiniMax T2A API.
 * Note: TTS is not included in Code Plan subscription.
 */
export const speakText = async (text: string, voiceName: string = 'male-qn-qingse') => {
    // TTS is not available in Code Plan subscription
    console.warn('⚠️ TTS功能在 Code Plan 套餐中不可用');
    // Silently return without showing error to user
    return;
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

    try {
        const response = await fetch(`${API_BASE_URL}/v1/text/chatcompletion_v2?GroupId=${groupId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: 'MiniMax-M2',
                messages: [
                    { role: 'user', content: prompt }
                ],
                tokens_to_generate: 1024,
            }),
        });

        if (!response.ok) {
            return "Story generation failed.";
        }

        const data = await response.json();
        return data.choices?.[0]?.message?.content || "Story generation failed.";
    } catch (error) {
        console.error('Story generation error:', error);
        return "Story generation failed.";
    }
};

/**
 * Chat session class for word-related conversations.
 */
export class ChatSession {
    private messages: Array<{ role: string; content: string }>;
    private systemPrompt: string;

    constructor(word: string, targetLang: string, nativeLang: string, initialHistory: Array<{ role: string; content: string }> = []) {
        this.systemPrompt = `You are a helpful and fun language tutor assisting a user with the word "${word}". 
    Target Language: ${targetLang}. Native Language: ${nativeLang}.
    Keep answers concise, encouraging, and easy to understand.`;
        this.messages = initialHistory;
    }

    async sendMessage(message: string): Promise<string> {
        this.messages.push({ role: 'user', content: message });

        try {
            const response = await fetch(`${API_BASE_URL}/v1/text/chatcompletion_v2?GroupId=${groupId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model: 'MiniMax-M2',
                    messages: this.messages,
                    tokens_to_generate: 1024,
                }),
            });

            if (!response.ok) {
                return 'Sorry, I encountered an error. Please try again.';
            }

            const data = await response.json();
            const assistantMessage = data.choices?.[0]?.message?.content || '';
            this.messages.push({ role: 'assistant', content: assistantMessage });

            return assistantMessage;
        } catch (error) {
            console.error('Chat error:', error);
            return 'Sorry, I encountered an error. Please try again.';
        }
    }
}

/**
 * Create a chat session for word context.
 * This maintains API compatibility with the original Gemini service.
 */
export const createChatSession = (word: string, targetLang: string, nativeLang: string, initialHistory: any[] = []) => {
    return new ChatSession(word, targetLang, nativeLang, initialHistory);
};
