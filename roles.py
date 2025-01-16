class Role:
    def __init__(self, name, description, system_prompt):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt

class RoleManager:
    def __init__(self):
        self.roles = {}
        self._init_default_roles()
        
    def _init_default_roles(self):
        """初始化默认角色"""
        # 通用助手
        self.add_role(
            "general",
            "通用AI助手",
            "我是一个专业的助手，可以帮助你解决各种问题。"
        )
        
        # 程序员
        self.add_role(
            "programmer",
            "编程专家",
            "我是一个专业的程序员，擅长软件开发、代码审查和技术问题解答。"
        )
        
        # 作家
        self.add_role(
            "writer",
            "写作助手",
            "我是一个专业的写作助手，可以帮助你进行创作、修改和润色文章。"
        )
        
        # 教师
        self.add_role(
            "teacher",
            "教育专家",
            "我是一个专业的教师，可以帮助你学习和理解各种知识。"
        )
        
    def add_role(self, role_id, name, description, system_prompt=None):
        """添加新角色"""
        if system_prompt is None:
            system_prompt = f"我是{name}，{description}"
            
        self.roles[role_id] = Role(name, description, system_prompt)
        
    def get_role(self, role_id):
        """获取角色"""
        return self.roles.get(role_id)
        
    def list_roles(self):
        """列出所有可用角色"""
        return [(role_id, role.name, role.description) 
                for role_id, role in self.roles.items()]
