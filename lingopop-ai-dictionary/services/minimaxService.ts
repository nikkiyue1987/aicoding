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
 */
export const speakText = async (text: string, voiceName: string = 'male-qn-qingse') => {
    try {
        console.log('🔊 TTS Request:', { text, voiceName, groupId });

        const response = await fetch(`${API_BASE_URL}/v1/t2a_v2?GroupId=${groupId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: 'speech-02-hd',
                text: text,
                voice_setting: {
                    voice_id: voiceName,
                    speed: 1.0,
                    vol: 1.0,
                    pitch: 0,
                },
                audio_setting: {
                    sample_rate: 32000,
                    bitrate: 128000,
                    format: 'mp3',
                },
            }),
        });

        console.log('🔊 TTS Response Status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error("❌ TTS failed:", errorText);
            alert(`语音合成失败: ${response.status}\n${errorText}`);
            return;
        }

        const data = await response.json();
        console.log('🔊 TTS Response Data:', JSON.stringify(data, null, 2));

        // Try multiple possible locations for audio data
        let audioData = null;
        let audioSource = '';

        if (data.data && data.data.audio) {
            audioData = data.data.audio;
            audioSource = 'data.data.audio (base64)';
        } else if (data.audio_file) {
            audioData = data.audio_file;
            audioSource = 'data.audio_file (URL)';
        } else if (data.audio) {
            audioData = data.audio;
            audioSource = 'data.audio';
        } else if (data.base_resp && data.base_resp.status_code !== 1000) {
            // Check for error in base_resp
            console.error('❌ TTS API Error:', data.base_resp);
            alert(`语音合成失败: ${data.base_resp.status_msg || 'Unknown error'}`);
            return;
        }

        if (audioData) {
            console.log(`✅ Found audio data in: ${audioSource}`);
            if (audioSource.includes('URL')) {
                await playAudioFromUrl(audioData);
            } else {
                await playMp3FromBase64(audioData);
            }
        } else {
            console.warn('⚠️ No audio data found in response. Full response:', data);
            alert('语音合成API返回成功，但没有找到音频数据。\n可能Code Plan不包含TTS功能，请使用普通API Key。');
        }
    } catch (error: any) {
        console.error("❌ TTS error:", error);
        alert(`语音合成错误: ${error.message}`);
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
