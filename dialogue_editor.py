import datetime

class DialogueEditor:
    def __init__(self):
        self.current_dialogue = []
        self.current_time = datetime.datetime(2025, 1, 15, 22, 44, 49)  # 设置当前时间
        
    def start_new_dialogue(self):
        """开始一个新的对话会话"""
        self.current_dialogue = []
        print(f"新对话已开始 - 当前时间: {self.current_time}")
        
    def add_message(self, speaker, content):
        """添加新的对话消息
        
        参数:
            speaker: 发言人
            content: 消息内容
        """
        message = {
            'speaker': speaker,
            'content': content,
            'timestamp': self.current_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.current_dialogue.append(message)
        print(f"{speaker}: {content}")
        
    def view_dialogue(self):
        """查看当前对话的所有内容"""
        if not self.current_dialogue:
            print("当前对话还没有任何消息。")
            return
            
        for message in self.current_dialogue:
            print(f"[{message['timestamp']}] {message['speaker']}: {message['content']}")
            
    def edit_message(self, index, new_content):
        """编辑对话中的消息
        
        参数:
            index: 要编辑的消息索引
            new_content: 新的消息内容
        """
        if 0 <= index < len(self.current_dialogue):
            self.current_dialogue[index]['content'] = new_content
            print(f"消息 {index} 已成功更新。")
        else:
            print("无效的消息索引。")

if __name__ == "__main__":
    editor = DialogueEditor()
    editor.start_new_dialogue()
    print("对话编辑器已启动。您现在可以添加、查看和编辑消息。")
