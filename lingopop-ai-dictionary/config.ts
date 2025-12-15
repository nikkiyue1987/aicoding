// Feature flags for MiniMax API
// Code Plan subscription may not include all features

export const FEATURES = {
    // Text generation - supported by Code Plan
    TEXT_GENERATION: true,

    // Image generation - may require separate API key
    IMAGE_GENERATION: true,

    // Text-to-Speech - NOT supported by Code Plan
    // Set to false to hide speaker buttons
    TTS: false,

    // Chat - supported by Code Plan
    CHAT: true,
};
