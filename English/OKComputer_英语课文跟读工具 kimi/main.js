// 英语课文跟读工具 - 设置页面 JavaScript

class ReadingSetup {
    constructor() {
        this.data = {
            englishText: '',
            chineseText: '',
            wordDetails: '',
            imageData: null,
            settings: {
                fontSize: '32px',
                speechRate: 1,
                voiceType: 'female',
                pauseDuration: 2
            }
        };
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSavedData();
        this.updateCharCounts();
        this.validateForm();
    }

    bindEvents() {
        // 文本输入事件
        document.getElementById('englishText').addEventListener('input', (e) => {
            this.data.englishText = e.target.value;
            this.updateCharCount('englishCharCount', e.target.value.length);
            this.validateForm();
        });

        document.getElementById('chineseText').addEventListener('input', (e) => {
            this.data.chineseText = e.target.value;
            this.updateCharCount('chineseCharCount', e.target.value.length);
            this.validateForm();
        });

        document.getElementById('wordDetails').addEventListener('input', (e) => {
            this.data.wordDetails = e.target.value;
            this.updateWordCount(e.target.value);
            this.validateForm();
        });

        // 参数设置事件
        document.getElementById('fontSize').addEventListener('change', (e) => {
            this.data.settings.fontSize = e.target.value;
            this.saveData();
        });

        document.getElementById('speechRate').addEventListener('change', (e) => {
            this.data.settings.speechRate = parseFloat(e.target.value);
            this.saveData();
        });

        document.getElementById('voiceType').addEventListener('change', (e) => {
            this.data.settings.voiceType = e.target.value;
            this.saveData();
        });

        document.getElementById('pauseDuration').addEventListener('input', (e) => {
            this.data.settings.pauseDuration = parseFloat(e.target.value);
            document.getElementById('pauseValue').textContent = e.target.value;
            this.saveData();
        });

        // 图片上传事件
        this.setupImageUpload();

        // 开始跟读按钮
        document.getElementById('startReading').addEventListener('click', () => {
            this.startReading();
        });
    }

    setupImageUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const imageUpload = document.getElementById('imageUpload');
        const removeImage = document.getElementById('removeImage');

        // 点击上传
        uploadArea.addEventListener('click', () => {
            imageUpload.click();
        });

        // 文件选择
        imageUpload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleImageUpload(file);
            }
        });

        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                this.handleImageUpload(file);
            }
        });

        // 移除图片
        removeImage.addEventListener('click', (e) => {
            e.stopPropagation();
            this.removeImage();
        });
    }

    handleImageUpload(file) {
        // 验证文件大小和类型
        if (file.size > 5 * 1024 * 1024) {
            this.showMessage('图片大小不能超过5MB', 'error');
            return;
        }

        if (!file.type.startsWith('image/')) {
            this.showMessage('请选择图片文件', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            this.data.imageData = e.target.result;
            this.showImagePreview(e.target.result);
            this.saveData();
        };
        reader.readAsDataURL(file);
    }

    showImagePreview(imageData) {
        const uploadContent = document.getElementById('uploadContent');
        const imagePreview = document.getElementById('imagePreview');
        const previewImg = document.getElementById('previewImg');

        uploadContent.classList.add('hidden');
        imagePreview.classList.remove('hidden');
        previewImg.src = imageData;
    }

    removeImage() {
        this.data.imageData = null;
        const uploadContent = document.getElementById('uploadContent');
        const imagePreview = document.getElementById('imagePreview');
        const imageUpload = document.getElementById('imageUpload');

        uploadContent.classList.remove('hidden');
        imagePreview.classList.add('hidden');
        imageUpload.value = '';
        this.saveData();
    }

    updateCharCount(elementId, count) {
        document.getElementById(elementId).textContent = `${count} 字符`;
    }

    updateWordCount(text) {
        const lines = text.trim().split('\n').filter(line => line.trim());
        document.getElementById('wordCount').textContent = `${lines.length} 个单词`;
    }

    updateCharCounts() {
        const englishText = document.getElementById('englishText').value;
        const chineseText = document.getElementById('chineseText').value;
        const wordDetails = document.getElementById('wordDetails').value;

        this.updateCharCount('englishCharCount', englishText.length);
        this.updateCharCount('chineseCharCount', chineseText.length);
        this.updateWordCount(wordDetails);
    }

    validateForm() {
        const startButton = document.getElementById('startReading');
        const messageElement = document.getElementById('validationMessage');

        let isValid = true;
        let message = ''

        if (!this.data.englishText.trim()) {
            isValid = false;
            message = '请输入英语短文内容';
        } else if (!this.data.wordDetails.trim()) {
            isValid = false;
            message = '请输入单词详情';
        }

        startButton.disabled = !isValid;
        
        if (isValid) {
            message = '准备就绪，可以开始跟读学习！';
            messageElement.className = 'text-sm text-green-500 mt-2 h-5';
        } else {
            messageElement.className = 'text-sm text-red-500 mt-2 h-5';
        }
        
        messageElement.textContent = message;
    }

    saveData() {
        localStorage.setItem('readingSetup', JSON.stringify(this.data));
    }

    loadSavedData() {
        const saved = localStorage.getItem('readingSetup');
        if (saved) {
            try {
                this.data = JSON.parse(saved);
                this.populateForm();
            } catch (e) {
                console.error('Failed to load saved data:', e);
            }
        }
    }

    populateForm() {
        document.getElementById('englishText').value = this.data.englishText || '';
        document.getElementById('chineseText').value = this.data.chineseText || '';
        document.getElementById('wordDetails').value = this.data.wordDetails || '';
        document.getElementById('fontSize').value = this.data.settings.fontSize;
        document.getElementById('speechRate').value = this.data.settings.speechRate;
        document.getElementById('voiceType').value = this.data.settings.voiceType;
        document.getElementById('pauseDuration').value = this.data.settings.pauseDuration;
        document.getElementById('pauseValue').textContent = this.data.settings.pauseDuration;

        if (this.data.imageData) {
            this.showImagePreview(this.data.imageData);
        }
    }

    startReading() {
        // 处理单词详情
        const wordDetails = this.processWordDetails(this.data.wordDetails);
        
        // 保存到localStorage供reading页面使用
        const readingData = {
            englishText: this.data.englishText,
            chineseText: this.data.chineseText,
            wordDetails: wordDetails,
            imageData: this.data.imageData,
            settings: this.data.settings
        };
        
        localStorage.setItem('readingData', JSON.stringify(readingData));
        
        // 跳转到跟读页面
        window.location.href = 'reading.html';
    }

    processWordDetails(text) {
        const lines = text.trim().split('\n').filter(line => line.trim());
        const wordDetails = [];

        lines.forEach(line => {
            const parts = line.trim().split(/\s+/);
            if (parts.length >= 3) {
                const word = parts[0];
                const phonetic = parts[1];
                const type = parts[2];
                const meaning = parts.slice(3).join(' ');

                wordDetails.push({
                    word: word,
                    phonetic: phonetic,
                    type: type,
                    meaning: meaning,
                    frequency: this.calculateWordFrequency(word, this.data.englishText)
                });
            }
        });

        return wordDetails;
    }

    calculateWordFrequency(word, text) {
        if (!text) return 'low';
        
        const regex = new RegExp(`\\b${word}\\b`, 'gi');
        const matches = text.match(regex);
        const count = matches ? matches.length : 0;

        if (count >= 3) return 'high';
        if (count >= 2) return 'medium';
        return 'low';
    }

    showMessage(message, type = 'info') {
        // 创建临时消息提示
        const messageDiv = document.createElement('div');
        messageDiv.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'error' ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
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
    new ReadingSetup();
    
    // 添加页面动画
    anime({
        targets: '.animate-fade-in',
        opacity: [0, 1],
        translateY: [20, 0],
        delay: anime.stagger(100),
        duration: 600,
        easing: 'easeOutQuad'
    });
});