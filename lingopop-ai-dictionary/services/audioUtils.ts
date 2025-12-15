export function decodeBase64(base64: string): Uint8Array {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

export async function playPCMData(base64Audio: string, sampleRate: number = 24000) {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
      sampleRate,
    });

    const arrayBuffer = decodeBase64(base64Audio).buffer;
    const dataInt16 = new Int16Array(arrayBuffer);

    // Create an audio buffer
    const audioBuffer = audioContext.createBuffer(1, dataInt16.length, sampleRate);
    const channelData = audioBuffer.getChannelData(0);

    // Convert Int16 to Float32 (-1.0 to 1.0)
    for (let i = 0; i < dataInt16.length; i++) {
      channelData[i] = dataInt16[i] / 32768.0;
    }

    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    source.start();

    // Clean up after playback (optional, context management can be complex)
    source.onended = () => {
      // audioContext.close(); // Keep context open if we expect frequent plays
    };

  } catch (error) {
    console.error("Error playing audio:", error);
  }
}

/**
 * Play MP3 audio from base64 encoded string (used by MiniMax T2A API)
 */
export async function playMp3FromBase64(base64Audio: string) {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();

    // Add proper base64 padding if needed
    const paddedBase64 = base64Audio.replace(/-/g, '+').replace(/_/g, '/');
    const binaryData = decodeBase64(paddedBase64);

    // Decode the MP3 data
    const audioBuffer = await audioContext.decodeAudioData(binaryData.buffer);

    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    source.start();

  } catch (error) {
    console.error("Error playing MP3 audio:", error);
  }
}

/**
 * Play audio from a URL (fallback for URL-based audio responses)
 */
export async function playAudioFromUrl(url: string) {
  try {
    const audio = new Audio(url);
    await audio.play();
  } catch (error) {
    console.error("Error playing audio from URL:", error);
  }
}