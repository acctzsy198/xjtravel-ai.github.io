// 语音控制相关的功能
export default class VoiceControls {
    constructor(socket) {
        this.socket = socket;
        this.initializeControls();
        this.initializeSocketHandlers();
        this.updateStatus();
        
        // 每5秒更新一次状态
        setInterval(() => this.updateStatus(), 5000);
    }
    
    initializeControls() {
        // 语音输出开关
        this.voiceToggle = document.getElementById('voiceToggle');
        this.voiceToggle.addEventListener('change', () => {
            this.socket.emit('toggle_voice', { enabled: this.voiceToggle.checked });
        });
        
        // 语速控制
        this.speechRate = document.getElementById('speechRate');
        this.speechRate.addEventListener('change', () => {
            this.updateVoiceSettings();
        });
        
        // 音量控制
        this.volume = document.getElementById('volume');
        this.volume.addEventListener('change', () => {
            this.updateVoiceSettings();
        });
        
        // 语音选择
        this.voiceSelect = document.getElementById('voiceSelect');
        this.voiceSelect.addEventListener('change', () => {
            this.updateVoiceSettings();
        });
        
        // 麦克风状态显示
        this.micStatus = document.getElementById('micStatus');
    }
    
    initializeSocketHandlers() {
        // 处理语音状态更新
        this.socket.on('voice_status', (data) => {
            this.updateControlsFromStatus(data);
        });
        
        // 处理错误消息
        this.socket.on('voice_error', (data) => {
            this.showNotification(data.message, 'error');
        });
        
        // 处理成功消息
        this.socket.on('voice_success', (data) => {
            this.showNotification(data.message, 'success');
        });
    }
    
    updateVoiceSettings() {
        const settings = {
            rate: parseInt(this.speechRate.value),
            volume: parseFloat(this.volume.value),
            voice: this.voiceSelect.value
        };
        
        this.socket.emit('voice_settings', settings);
    }
    
    updateStatus() {
        this.socket.emit('get_voice_status');
    }
    
    updateControlsFromStatus(status) {
        // 更新语音输出控件状态
        if (status.voice_output) {
            this.voiceToggle.checked = status.voice_output.enabled;
            this.speechRate.value = status.voice_output.rate;
            this.volume.value = status.voice_output.volume;
            this.voiceSelect.value = status.voice_output.voice;
            
            // 如果正在说话，添加视觉反馈
            if (status.voice_output.speaking) {
                document.body.classList.add('speaking');
            } else {
                document.body.classList.remove('speaking');
            }
            
            // 显示错误信息
            if (status.voice_output.last_error) {
                this.showNotification(status.voice_output.last_error, 'error');
            }
        }
        
        // 更新麦克风状态
        if (status.voice_input) {
            if (status.voice_input.available) {
                if (status.voice_input.listening) {
                    this.micStatus.textContent = '正在听...';
                    this.micStatus.className = 'status-indicator status-ok pulse';
                } else {
                    this.micStatus.textContent = '就绪';
                    this.micStatus.className = 'status-indicator status-ok';
                }
            } else {
                this.micStatus.textContent = '麦克风不可用';
                this.micStatus.className = 'status-indicator status-error';
            }
            
            // 显示错误信息
            if (status.voice_input.last_error) {
                this.showNotification(status.voice_input.last_error, 'error');
            }
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.style.display = 'block';
        
        // 3秒后隐藏通知
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }
}
