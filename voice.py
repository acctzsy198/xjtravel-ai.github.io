import speech_recognition as sr
import platform
import threading
import queue
import subprocess
import os
import time

class VoiceInputInterface:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone_available = self._check_microphone()
        self.listening = False
        self.last_error = None
        
    def _check_microphone(self):
        """检查是否有可用的麦克风"""
        try:
            mics = sr.Microphone.list_microphone_names()
            print(f"检测到 {len(mics)} 个麦克风设备")
            return len(mics) > 0
        except (OSError, AttributeError) as e:
            print(f"麦克风检测错误: {str(e)}")
            return False
            
    def listen(self):
        """监听用户语音输入"""
        if not self.microphone_available:
            self.last_error = "麦克风不可用"
            return None
            
        max_retries = 3
        retry_count = 0
        self.listening = True
        
        while retry_count < max_retries and self.listening:
            try:
                with sr.Microphone() as source:
                    print("正在听......")
                    # 调整麦克风的环境噪声阈值
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    # 设置超时和短语阈值
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                try:
                    # 尝试使用Google的语音识别服务
                    text = self.recognizer.recognize_google(audio, language='zh-CN')
                    if text.strip():  # 确保识别的文本不为空
                        self.listening = False
                        self.last_error = None
                        return text
                    print("未能识别到有效的语音输入，请重试")
                    self.last_error = "未能识别到有效的语音输入"
                except sr.UnknownValueError:
                    retry_count += 1
                    print(f"未能识别语音 (尝试 {retry_count}/{max_retries})")
                    self.last_error = f"未能识别语音 (尝试 {retry_count}/{max_retries})"
                except sr.RequestError as e:
                    print(f"语音识别服务错误: {str(e)}")
                    self.last_error = "语音识别服务暂时不可用"
                    return None
            except (OSError, AttributeError) as e:
                print(f"麦克风错误: {str(e)}")
                self.last_error = f"麦克风错误: {str(e)}"
                return None
                
        self.listening = False
        return None
        
    def stop_listening(self):
        """停止监听"""
        self.listening = False
        
    def get_status(self):
        """获取当前状态"""
        return {
            'available': self.microphone_available,
            'listening': self.listening,
            'last_error': self.last_error
        }

class VoiceOutputInterface:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_macos = platform.system() == 'Darwin'
        self.voice_output_enabled = False  # 默认关闭语音输出
        self.speech_rate = 200  # 默认语速 (words per minute)
        self.volume = 1.0  # 默认音量 (0.0 到 1.0)
        self.voice = 'Ting-Ting'  # 默认中文声音
        self.speaking = False
        self.last_error = None
        self.output_thread = None
        
    def set_speech_rate(self, rate):
        """设置语速 (100-400 wpm)"""
        self.speech_rate = max(100, min(400, rate))
        
    def set_volume(self, volume):
        """设置音量 (0.0-1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        
    def set_voice(self, voice):
        """设置声音"""
        self.voice = voice
        
    def _speak_macos(self, text):
        """使用 macOS 的 say 命令进行语音输出"""
        try:
            rate_arg = f"-r {self.speech_rate}"
            voice_arg = f"-v {self.voice}"
            volume_arg = f"--volume={self.volume}"
            
            cmd = ["say", rate_arg, voice_arg, volume_arg, text]
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"语音输出错误: {str(e)}")
            self.last_error = f"语音输出错误: {str(e)}"
            return False
            
    def speak(self, text):
        """文字转语音输出"""
        if not self.voice_output_enabled:
            return
            
        self.audio_queue.put(text)
        
    def process_audio_queue(self):
        """处理语音输出队列"""
        while True:
            try:
                if not self.voice_output_enabled:
                    time.sleep(0.1)
                    continue
                    
                text = self.audio_queue.get(timeout=0.1)
                self.speaking = True
                
                if self.is_macos:
                    success = self._speak_macos(text)
                else:
                    success = self._speak_other(text)
                    
                if success:
                    self.last_error = None
                    
                self.speaking = False
                self.audio_queue.task_done()
                
            except queue.Empty:
                pass
            except Exception as e:
                print(f"语音输出线程错误: {str(e)}")
                self.last_error = f"语音输出错误: {str(e)}"
                self.speaking = False
                
    def start_voice_output_thread(self):
        """启动语音输出线程"""
        if self.output_thread is None or not self.output_thread.is_alive():
            self.output_thread = threading.Thread(
                target=self.process_audio_queue,
                daemon=True
            )
            self.output_thread.start()
            
    def get_status(self):
        """获取当前状态"""
        return {
            'enabled': self.voice_output_enabled,
            'speaking': self.speaking,
            'voice': self.voice,
            'rate': self.speech_rate,
            'volume': self.volume,
            'last_error': self.last_error
        }
