import sys
import argparse
from agent import Agent
import config
from knowledge_base import KnowledgeBase
from roles import RoleManager
from export import DialogueExporter
from voice import VoiceInputInterface, VoiceOutputInterface
from web_server import run_server

def run_cli_mode(use_voice=False):
    """运行命令行模式"""
    print(f"欢迎使用 {config.AGENT_NAME}!")
    print(config.AGENT_DESCRIPTION)
    print("\n可用命令：")
    print("1. 输入 'quit' 退出对话")
    print("2. 输入 'clear' 清空对话历史")
    print("3. 输入 'export <format>' 导出对话 (支持的格式: json, markdown, docx)")
    print("4. 输入 'role <role_id>' 切换角色")
    print("5. 输入 'roles' 查看所有可用角色")
    
    agent = Agent()
    knowledge_base = KnowledgeBase()
    role_manager = RoleManager()
    voice_input = None
    voice_output = None
    
    if use_voice:
        # 初始化语音输出（即使没有麦克风也可以使用）
        voice_output = VoiceOutputInterface()
        voice_output.start_voice_output_thread()
        
        # 尝试初始化语音输入
        voice_input = VoiceInputInterface()
        if not voice_input.microphone_available:
            print("\n提示: 将使用文本输入和语音输出的混合模式")
            voice_input = None
        else:
            print("\n语音输入模式已启动，您可以开始说话...")
    
    try:
        while True:
            try:
                if voice_input:
                    print("\n请说话...")
                    user_input = voice_input.listen()
                    if user_input:
                        print(f"\n你: {user_input}")
                    else:
                        continue
                else:
                    user_input = input("\n你: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n检测到输入结束，程序退出")
                break
                
            if not user_input:
                continue
                
            # 处理命令
            if user_input.lower() == 'quit':
                print("\n感谢使用！再见！")
                break
                
            elif user_input.lower() == 'clear':
                agent.clear_history()
                print("\n对话历史已清空！")
                continue
                
            elif user_input.lower() == 'roles':
                print("\n可用角色：")
                for role_id, name, desc in role_manager.list_roles():
                    print(f"- {role_id}: {name} ({desc})")
                continue
                
            elif user_input.lower().startswith('role '):
                role_id = user_input.split(' ')[1]
                role = role_manager.get_role(role_id)
                if role:
                    agent.system_prompt = {"role": "system", "content": role.system_prompt}
                    print(f"\n已切换到角色: {role.name}")
                else:
                    print(f"\n未找到角色: {role_id}")
                continue
                
            elif user_input.lower().startswith('export '):
                format_type = user_input.split(' ')[1]
                history = agent.get_history()
                
                try:
                    if format_type == 'json':
                        DialogueExporter.to_json(history, 'dialogue_export.json')
                    elif format_type == 'markdown':
                        DialogueExporter.to_markdown(history, 'dialogue_export.md')
                    elif format_type == 'docx':
                        DialogueExporter.to_docx(history, 'dialogue_export.docx')
                    else:
                        print(f"\n不支持的导出格式: {format_type}")
                        continue
                        
                    print(f"\n对话已导出为 {format_type} 格式")
                except Exception as e:
                    print(f"\n导出失败: {str(e)}")
                continue
            
            # 生成回复
            try:
                response = agent.get_response(user_input)
                print(f"\n{config.AGENT_NAME}: {response}")
                
                if voice_output and voice_output.voice_output_enabled:
                    voice_output.speak(response)
            except Exception as e:
                print(f"\n发生错误: {str(e)}")
                
    except Exception as e:
        print(f"\n程序发生错误: {str(e)}")
    finally:
        print("\n程序已退出")

def main():
    parser = argparse.ArgumentParser(description='智能助手')
    parser.add_argument('--web', action='store_true', help='启动Web界面')
    parser.add_argument('--voice', action='store_true', help='启用语音交互')
    args = parser.parse_args()
    
    if args.web:
        print("启动Web服务器...")
        run_server()
    else:
        run_cli_mode(use_voice=args.voice)

if __name__ == "__main__":
    main()
