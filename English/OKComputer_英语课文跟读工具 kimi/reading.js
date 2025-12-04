// 英语课文跟读工具 - 跟读页面 JavaScript

class ReadingSession {
    constructor() {
        this.data = null;
        this.currentSentenceIndex = 0;
        this.isPlaying = false;
        this.isChineseMode = false;
        this.autoPlay = false;
        this.sentences = [];
        this.wordDetails = [];
        this.synthesis = null;
        this.currentUtterance = null;
        
        this.init();
    }

    init() {
        this.loadReadingData();
        this.bindEvents();
        this.processContent();
        this.renderContent();
        this.updateStats();
        this.initializeSpeech();
    }

    loadReadingData() {
        const readingData = localStorage.getItem('readingData');
        if (!readingData) {
            alert('没有找到学习数据，请先设置课程内容');
            window.location.href = 'index.html';
            return;
        }
        
        try {
            this.data = JSON.parse(readingData);
        } catch (e) {
            console.error('Failed to load reading data:', e);
            alert('数据加载失败，请重新设置');
            window.location.href = 'index.html';
        }
    }

    bindEvents() {
        // 播放控制
        document.getElementById('playPause').addEventListener('click', () => {
            this.togglePlayPause();
        });

        document.getElementById('prevSentence').addEventListener('click', () => {
            this.previousSentence();
        });

        document.getElementById('nextSentence').addEventListener('click', () => {
            this.nextSentence();
        });

        // 中英切换
        document.getElementById('toggleLanguage').addEventListener('click', () => {
            this.toggleLanguageMode();
        });

        // 返回设置
        document.getElementById('backToSettings').addEventListener('click', () => {
            window.location.href = 'index.html';
        });

        // 自动播放
        document.getElementById('autoPlay').addEventListener('change', (e) => {
            this.autoPlay = e.target.checked;
        });

        // 句子点击
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('sentence-text')) {
                const index = parseInt(e.target.dataset.index);
                this.playSentence(index);
            }
        });

        // 词汇点击
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('vocabulary-word')) {
                const word = e.target.dataset.word;
                this.showWordDetail(word);
            }
        });

        // 模态框关闭
        document.getElementById('closeModal').addEventListener('click', () => {
            this.hideWordDetail();
        });

        document.getElementById('wordDetailModal').addEventListener('click', (e) => {
            if (e.target.id === 'wordDetailModal') {
                this.hideWordDetail();
            }
        });

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.togglePlayPause();
            } else if (e.code === 'ArrowLeft') {
                e.preventDefault();
                this.previousSentence();
            } else if (e.code === 'ArrowRight') {
                e.preventDefault();
                this.nextSentence();
            }
        });
    }

    initializeSpeech() {
        if ('speechSynthesis' in window) {
            this.synthesis = window.speechSynthesis;
            
            // 获取可用的语音
            const voices = this.synthesis.getVoices();
            console.log('Available voices:', voices);
            
            // 监听语音加载完成
            if (voices.length === 0) {
                this.synthesis.addEventListener('voiceschanged', () => {
                    console.log('Voices loaded:', this.synthesis.getVoices());
                });
            }
        } else {
            console.warn('Speech synthesis not supported');
            this.showMessage('您的浏览器不支持语音合成功能', 'warning');
        }
    }

    processContent() {
        if (!this.data) return;

        // 分句处理
        const englishText = this.data.englishText;
        this.sentences = englishText.split(/[.!?。！？]+/).filter(s => s.trim());

        // 处理单词详情
        this.wordDetails = this.data.wordDetails || [];

        // 计算词汇统计
        this.calculateWordStats();
    }

    calculateWordStats() {
        let nounCount = 0;
        let verbCount = 0;
        let adjCount = 0;

        this.wordDetails.forEach(word => {
            const type = word.type.toLowerCase();
            if (type.includes('n')) nounCount++;
            else if (type.includes('v')) verbCount++;
            else if (type.includes('adj')) adjCount++;
        });

        this.wordStats = {
            total: this.wordDetails.length,
            nouns: nounCount,
            verbs: verbCount,
            adjectives: adjCount
        };
    }

    renderContent() {
        this.renderStats();
        this.renderImage();
        this.renderTextContent();
        this.renderVocabulary();
        this.updateProgress();
    }

    renderStats() {
        document.getElementById('totalWords').textContent = `${this.wordStats.total}个`;
        document.getElementById('nounCount').textContent = `${this.wordStats.nouns}个`;
        document.getElementById('verbCount').textContent = `${this.wordStats.verbs}个`;
        document.getElementById('adjCount').textContent = `${this.wordStats.adjectives}个`;
        document.getElementById('totalSentences').textContent = this.sentences.length;
    }

    renderImage() {
        const imageContainer = document.getElementById('lessonImage');
        if (this.data.imageData) {
            imageContainer.innerHTML = `<img src="${this.data.imageData}" alt="课程插图" class="w-full h-full object-cover">`;
        }
    }

    renderTextContent() {
        const container = document.getElementById('textContent');
        container.innerHTML = '';

        this.sentences.forEach((sentence, index) => {
            const sentenceDiv = document.createElement('div');
            sentenceDiv.className = `sentence-block ${index === this.currentSentenceIndex ? 'active' : ''}`;
            
            const processedText = this.processSentenceText(sentence.trim());
            
            sentenceDiv.innerHTML = `
                <div class="sentence-text english-font cursor-pointer" data-index="${index}" style="font-size: ${this.data.settings.fontSize}; line-height: 1.6;">
                    ${processedText}
                </div>
                <div class="chinese-translation mt-2 text-gray-600 ${this.isChineseMode ? '' : 'hidden'}">
                    ${this.getChineseTranslation(index)}
                </div>
            `;
            
            container.appendChild(sentenceDiv);
        });
    }

    processSentenceText(sentence) {
        let processed = sentence;
        
        // 高亮词汇
        this.wordDetails.forEach(word => {
            const regex = new RegExp(`\\b${word.word}\\b`, 'gi');
            const className = this.getFrequencyClass(word.frequency);
            processed = processed.replace(regex, `<span class="${className} vocabulary-word cursor-pointer" data-word="${word.word}">${word.word}</span>`);
        });

        return processed;
    }

    getFrequencyClass(frequency) {
        switch (frequency) {
            case 'high': return 'word-high-frequency';
            case 'medium': return 'word-medium-frequency';
            case 'low': return 'word-low-frequency';
            default: return '';
        }
    }

    getChineseTranslation(index) {
        if (this.data.chineseText) {
            const translations = this.data.chineseText.split(/[\n。！？]+/).filter(s => s.trim());
            return translations[index] || '';
        }
        return '';
    }

    renderVocabulary() {
        const container = document.getElementById('vocabularyList');
        container.innerHTML = '';

        this.wordDetails.forEach(word => {
            const wordDiv = document.createElement('div');
            wordDiv.className = 'vocabulary-card p-3 bg-gray-50 rounded-lg cursor-pointer';
            
            const frequencyColor = this.getFrequencyColor(word.frequency);
            
            wordDiv.innerHTML = `
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <h4 class="font-semibold text-gray-800 english-font" style="color: ${frequencyColor}">${word.word}</h4>
                        <p class="text-sm text-blue-600 english-font">${word.phonetic}</p>
                        <p class="text-sm text-green-600">${word.type}</p>
                        <p class="text-xs text-gray-600 mt-1">${word.meaning}</p>
                    </div>
                    <div class="w-3 h-3 rounded-full ml-2" style="background-color: ${frequencyColor}"></div>
                </div>
            `;
            
            wordDiv.addEventListener('click', () => {
                this.showWordDetail(word.word);
            });
            
            container.appendChild(wordDiv);
        });
    }

    getFrequencyColor(frequency) {
        switch (frequency) {
            case 'high': return '#dc2626';
            case 'medium': return '#7c3aed';
            case 'low': return '#ea580c';
            default: return '#6b7280';
        }
    }

    togglePlayPause() {
        if (this.isPlaying) {
            this.pauseReading();
        } else {
            this.startReading();
        }
    }

    startReading() {
        if (!this.synthesis) {
            this.showMessage('语音合成功能不可用', 'error');
            return;
        }

        this.isPlaying = true;
        this.updatePlayButton();
        this.playCurrentSentence();
    }

    pauseReading() {
        this.isPlaying = false;
        this.updatePlayButton();
        
        if (this.synthesis.speaking) {
            this.synthesis.cancel();
        }
    }

    playCurrentSentence() {
        if (!this.isPlaying || this.currentSentenceIndex >= this.sentences.length) {
            this.pauseReading();
            return;
        }

        const sentence = this.sentences[this.currentSentenceIndex];
        this.playSentence(this.currentSentenceIndex);
    }

    playSentence(index) {
        if (!this.synthesis) return;

        this.currentSentenceIndex = index;
        this.updateActiveSentence();
        this.updateProgress();

        const sentence = this.sentences[index];
        const textToSpeak = this.isChineseMode ? this.getChineseTranslation(index) : sentence;

        if (this.currentUtterance) {
            this.synthesis.cancel();
        }

        this.currentUtterance = new SpeechSynthesisUtterance(textToSpeak);
        
        // 设置语音参数
        this.currentUtterance.rate = this.data.settings.speechRate;
        this.currentUtterance.pitch = 1;
        this.currentUtterance.volume = 1;

        // 选择语音
        const voices = this.synthesis.getVoices();
        if (voices.length > 0) {
            // 优先选择英文语音
            const englishVoices = voices.filter(voice => voice.lang.startsWith('en'));
            if (englishVoices.length > 0) {
                this.currentUtterance.voice = englishVoices[0];
            }
        }

        this.currentUtterance.onend = () => {
            setTimeout(() => {
                if (this.isPlaying && this.autoPlay) {
                    this.nextSentence();
                }
            }, this.data.settings.pauseDuration * 1000);
        };

        this.synthesis.speak(this.currentUtterance);
    }

    previousSentence() {
        if (this.currentSentenceIndex > 0) {
            this.currentSentenceIndex--;
            this.updateActiveSentence();
            this.updateProgress();
            
            if (this.isPlaying) {
                if (this.synthesis.speaking) {
                    this.synthesis.cancel();
                }
                this.playCurrentSentence();
            }
        }
    }

    nextSentence() {
        if (this.currentSentenceIndex < this.sentences.length - 1) {
            this.currentSentenceIndex++;
            this.updateActiveSentence();
            this.updateProgress();
            
            if (this.isPlaying) {
                if (this.synthesis.speaking) {
                    this.synthesis.cancel();
                }
                this.playCurrentSentence();
            }
        } else if (this.isPlaying) {
            // 播放完成
            this.pauseReading();
            this.showMessage('跟读完成！', 'success');
        }
    }

    toggleLanguageMode() {
        this.isChineseMode = !this.isChineseMode;
        this.renderTextContent();
        
        const toggleBtn = document.getElementById('toggleLanguage');
        if (this.isChineseMode) {
            toggleBtn.textContent = '切换英文';
            toggleBtn.classList.add('active');
        } else {
            toggleBtn.textContent = '中英切换';
            toggleBtn.classList.remove('active');
        }
    }

    updateActiveSentence() {
        const sentenceBlocks = document.querySelectorAll('.sentence-block');
        sentenceBlocks.forEach((block, index) => {
            block.classList.remove('active');
            if (index === this.currentSentenceIndex) {
                block.classList.add('active');
            }
        });

        document.getElementById('currentSentence').textContent = this.currentSentenceIndex + 1;
    }

    updateProgress() {
        const progress = this.sentences.length > 0 ? 
            Math.round(((this.currentSentenceIndex + 1) / this.sentences.length) * 100) : 0;
        
        document.getElementById('progressText').textContent = `${progress}%`;
        
        const progressCircle = document.getElementById('progressCircle');
        const degrees = (progress / 100) * 360;
        progressCircle.style.background = `conic-gradient(#3b82f6 ${degrees}deg, #e5e7eb ${degrees}deg)`;
    }

    updatePlayButton() {
        const playIcon = document.getElementById('playIcon');
        const playButton = document.getElementById('playPause');
        
        if (this.isPlaying) {
            playIcon.className = 'fas fa-pause';
            playButton.classList.add('active');
        } else {
            playIcon.className = 'fas fa-play';
            playButton.classList.remove('active');
        }
    }

    showWordDetail(word) {
        const wordDetail = this.wordDetails.find(w => w.word.toLowerCase() === word.toLowerCase());
        if (!wordDetail) return;

        document.getElementById('modalWord').textContent = wordDetail.word;
        document.getElementById('modalPhonetic').textContent = wordDetail.phonetic;
        document.getElementById('modalType').textContent = wordDetail.type;
        document.getElementById('modalMeaning').textContent = wordDetail.meaning;

        document.getElementById('wordDetailModal').classList.remove('hidden');
        document.getElementById('wordDetailModal').classList.add('flex');
    }

    hideWordDetail() {
        document.getElementById('wordDetailModal').classList.add('hidden');
        document.getElementById('wordDetailModal').classList.remove('flex');
    }

    updateStats() {
        // 更新页面标题和统计信息
        document.getElementById('lessonTitle').textContent = '英语文章';
    }

    showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'error' ? 'bg-red-500 text-white' : 
            type === 'success' ? 'bg-green-500 text-white' : 
            'bg-blue-500 text-white'
        }`;
        messageDiv.textContent = message;
        
        document.body.appendChild(messageDiv);
        
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new ReadingSession();
    
    // 添加页面动画
    anime({
        targets: '.animate-slide-in',
        opacity: [0, 1],
        translateX: [20, 0],
        delay: anime.stagger(100),
        duration: 600,
        easing: 'easeOutQuad'
    });
});