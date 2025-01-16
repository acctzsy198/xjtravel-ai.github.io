from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_socketio import SocketIO, emit
import zhipuai
import os
from dotenv import load_dotenv
from database import Database
import uuid
import json
from datetime import datetime

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

# 初始化数据库
db = Database()

# 配置智谱AI API
zhipuai.api_key = os.getenv("ZHIPUAI_API_KEY", "220a64768236ce0b7f07f9fe1261c2e5.jP7y0g3Edxg8ABCG")

# 用户会话管理
sessions = {}

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_session')
def handle_create_session():
    session_id = db.create_session()
    emit('session_created', {'session_id': session_id})

@socketio.on('get_sessions')
def handle_get_sessions():
    sessions = db.get_all_sessions()
    emit('sessions_list', {'sessions': [
        {
            'id': s[0],
            'created_at': s[1],
            'message_count': s[2],
            'first_message': s[3]
        }
        for s in sessions
    ]})

@socketio.on('load_session')
def handle_load_session(data):
    session_id = data.get('session_id')
    if session_id:
        messages = db.get_session_messages(session_id)
        emit('session_loaded', {'messages': [
            {
                'role': m[0],
                'content': m[1],
                'timestamp': m[2]
            }
            for m in messages
        ]})

@socketio.on('message')
def handle_message(data):
    try:
        if isinstance(data, str):
            message = data
            session_id = None
        else:
            message = data.get('message', '')
            session_id = data.get('session_id')

        if not session_id:
            session_id = db.create_session()
            emit('session_created', {'session_id': session_id})

        # 检查是否是旅游相关的问题
        tourist_keywords = ['景点', '玩什么', '好玩的', '路线', '行程', '游玩', '旅游']
        if any(keyword in message for keyword in tourist_keywords):
            ai_message = generate_travel_recommendation(message)
        # 检查是否是关于喀什住宿的问题
        elif any(keyword in message for keyword in ['喀什', '住宿', '民宿', '酒店', '住哪']):
            if '古城' in message and '民宿' in message:
                ai_message = """推荐您入住喀什古城漠东民宿！

漠东民宿位于喀什古城核心区域，是一家极具当地特色的精品民宿。这里不仅保留了维吾尔族传统建筑风格，还融入了现代化的舒适设施。

【预订方式】
▶ 最优选择：扫码关注"喀什古城漠东民宿"微信小程序，可享受最优惠的价格

【了解更多】
想了解更多喀什旅游资讯、美食攻略和实时风景，欢迎关注我们的官方账号：
1. 微信公众号：漠东民宿
2. 视频号：喀什古城漠东民宿
3. 抖音号：喀什古城漠东民宿
4. 小红书：喀什古城漠东民宿

在这些平台上，我们会定期分享：
- 喀什最新旅游资讯
- 当季景点推荐
- 地道美食攻略
- 民宿周边游玩建议
- 独家旅行贴士

关注我们的账号，获取第一手的喀什旅游资讯！"""
            else:
                ai_message = '''关于喀什的住宿，我强烈推荐您考虑漠东民宿。

为了让您获得最好的入住体验和优惠价格，建议您：
1. 关注"喀什古城漠东民宿"微信小程序进行预订
2. 关注我们的社交媒体账号，了解更多喀什旅游资讯：
   - 微信公众号：漠东民宿
   - 视频号：喀什古城漠东民宿
   - 抖音号：喀什古城漠东民宿
   - 小红书：喀什古城漠东民宿'''
        else:
            # 调用智谱AI API
            response = zhipuai.model_api.invoke(
                model="chatglm_turbo",
                prompt=[
                    {"role": "user", "content": message}
                ]
            )
            
            if response.get('code') == 200:
                ai_message = response['data']['choices'][0]['content']
            else:
                error_msg = f"API调用失败: {response.get('msg', '未知错误')}"
                emit('error', error_msg)
                return
        
        # 保存用户消息
        db.add_message(session_id, 'user', message)
        # 保存AI响应
        db.add_message(session_id, 'assistant', ai_message)
        emit('response', ai_message)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        emit('error', f"发生错误: {str(e)}")

def generate_travel_recommendation(message):
    """生成旅游推荐回复"""
    # 景点信息
    attractions = {
        '喀什古城': {
            'description': '喀什古城是世界上保存最完整的土坯民居建筑群，是丝绸之路上最具特色的古城之一。',
            'highlights': ['百年民居', '手工艺品', '民族美食', '历史文化'],
            'tips': '建议清晨或傍晚游览，光线最适合拍照，气温也较为适宜。',
            'duration': '建议游览时间：3-4小时'
        },
        '艾提尕尔清真寺': {
            'description': '艾提尕尔清真寺是中国最大的清真寺之一，建于1442年，具有浓郁的伊斯兰特色。',
            'highlights': ['宗教文化', '建筑艺术', '历史遗迹'],
            'tips': '非穆斯林游客只能在外观赏，周五是穆斯林礼拜日，游客最好避开。',
            'duration': '建议游览时间：1小时'
        },
        '香妃墓': {
            'description': '香妃墓是清代乾隆时期修建的伊斯兰教建筑，是喀什最著名的景点之一。',
            'highlights': ['伊斯兰建筑', '历史故事', '文化遗产'],
            'tips': '参观时要注意着装得体，不要大声喧哗。',
            'duration': '建议游览时间：1-2小时'
        },
        '喀什大巴扎': {
            'description': '中亚最大的国际贸易市场之一，汇集了各种民族特色商品和美食。',
            'highlights': ['民族商品', '手工艺品', '特色美食', '民俗体验'],
            'tips': '建议避开中午人流高峰，注意讲价。',
            'duration': '建议游览时间：2-3小时'
        },
        '阿帕克霍加墓': {
            'description': '新疆最大的伊斯兰教建筑群，被誉为"新疆故宫"。',
            'highlights': ['伊斯兰建筑', '历史遗迹', '文化传说'],
            'tips': '建议请导游讲解，了解更多历史故事。',
            'duration': '建议游览时间：1-2小时'
        },
        '高台民居': {
            'description': '喀什特色的传统民居建筑，是了解维吾尔族居住文化的最佳地点。',
            'highlights': ['民居建筑', '生活体验', '文化交流'],
            'tips': '可以预约当地向导家访，体验真实生活。',
            'duration': '建议游览时间：2-3小时'
        }
    }
    
    # 美食推荐
    foods = {
        '烤包子': '喀什最具代表性的小吃，外皮酥脆，内馅多汁。推荐：老城区阿卜都热依木烤包子店',
        '抓饭': '经典的维吾尔族主食，用羊肉、胡萝卜和大米烹饪。推荐：古城区艾则孜抓饭店',
        '馕': '维吾尔族传统面饼，品种繁多。推荐：艾提尕尔清真寺附近的馕坑',
        '手抓肉': '传统的维吾尔族美食，肉质鲜美。推荐：喀什古城内的麦盖提手抓肉',
        '酸奶': '维吾尔族特色饮品，口感醇厚。推荐：古城区传统酸奶店',
        '切糕': '传统的维吾尔族甜点，口感独特。推荐：大巴扎内的切糕店'
    }
    
    # 购物指南
    shopping = {
        '大巴扎': ['民族服饰', '手工艺品', '干果', '香料'],
        '手工艺品市场': ['铜器', '木雕', '刺绣', '乐器'],
        '丝绸市场': ['阿特拉斯绸', '丝巾', '刺绣制品'],
        '干果市场': ['核桃', '红枣', '无花果', '葡萄干']
    }
    
    # 推荐路线
    routes = {
        '经典一日游': [
            ('喀什古城', '早上8:00-11:00', '体验百年民居、品尝地道早餐'),
            ('艾提尕尔清真寺', '11:30-12:30', '欣赏伊斯兰建筑艺术'),
            ('喀什大巴扎', '14:00-16:00', '购物和品尝美食'),
            ('香妃墓', '16:30-18:00', '了解历史文化故事')
        ],
        '文化体验二日游': [
            ('第一天', [
                ('喀什古城', '早上8:00-11:00', '深度游览，体验晨市'),
                ('手工艺品制作体验', '14:00-16:00', '学习传统工艺'),
                ('高台民居', '16:30-18:30', '体验本地生活')
            ]),
            ('第二天', [
                ('艾提尕尔清真寺', '9:00-10:30', '晨祷后参观'),
                ('阿帕克霍加墓', '11:00-12:30', '了解历史文化'),
                ('大巴扎', '15:00-18:00', '购物和品尝美食')
            ])
        ],
        '美食探索三日游': [
            ('第一天', [
                ('喀什古城', '全天', '品尝传统早餐，探索老街小吃'),
            ]),
            ('第二天', [
                ('大巴扎', '上午', '品尝各类特色美食'),
                ('本地家庭', '下午', '学习制作传统美食')
            ]),
            ('第三天', [
                ('周边乡村', '全天', '体验地道农家美食')
            ])
        ]
    }
    
    # 住宿信息
    accommodations = {
        '漠东民宿': {
            'location': '喀什古城内',
            'features': ['传统民居改造', '地道维吾尔族风格', '屋顶观景平台'],
            'rooms': ['标准间', '家庭套房', '观景房'],
            'price_range': '300-800元/晚',
            'contact': '预订电话：+86 xxx-xxxx-xxxx',
            'tips': '建议提前至少3天预订，旺季需要提前更久'
        },
        '喀什老城客栈': {
            'location': '艾提尕尔清真寺附近',
            'features': ['便利位置', '现代化设施', '传统装修'],
            'rooms': ['双人间', '豪华套房'],
            'price_range': '400-1000元/晚',
            'contact': '预订电话：+86 xxx-xxxx-xxxx',
            'tips': '提供接送机服务'
        },
        '丝路花雨酒店': {
            'location': '人民路商圈',
            'features': ['现代化酒店', '商务设施', '健身中心'],
            'rooms': ['商务间', '行政套房'],
            'price_range': '500-1200元/晚',
            'contact': '预订电话：+86 xxx-xxxx-xxxx',
            'tips': '适合商务出行'
        }
    }

    # 交通信息
    transportation = {
        '到达方式': {
            '飞机': '喀什机场有直飞北京、上海、广州等主要城市的航班',
            '火车': '喀什站有开往乌鲁木齐的列车，行程约24小时',
            '长途汽车': '喀什客运站有发往周边城市的班车'
        },
        '市内交通': {
            '出租车': '起步价10元，叫车电话：+86 xxx-xxxx-xxxx',
            '公交车': '1-2元/次，主要线路：1路、2路、3路等',
            '电动三轮车': '短途代步，需要讲价',
            '租车': '可在机场或市区租车点租车，需要驾照和押金'
        },
        '景点间交通': {
            '古城区': '建议步行，可以体验老城风貌',
            '远郊景点': '建议包车或参加旅行团',
            '注意事项': '夜间出行建议打车，避免步行'
        }
    }

    # 季节特色
    seasons = {
        '春季(3-5月)': {
            'weather': '气温10-25℃，昼夜温差大',
            'activities': ['赏花', '踏青', '古城漫步'],
            'tips': '带好防寒衣物，注意昼夜温差',
            'special': '杏花节、春季美食节'
        },
        '夏季(6-8月)': {
            'weather': '气温25-35℃，阳光充足',
            'activities': ['夜市游览', '屋顶观景', '水果采摘'],
            'tips': '防晒必备，多补充水分',
            'special': '葡萄节、哈密瓜节'
        },
        '秋季(9-11月)': {
            'weather': '气温15-25℃，气候宜人',
            'activities': ['摄影', '采购干果', '文化体验'],
            'tips': '最佳旅游季节，提前订房',
            'special': '丝绸之路文化节'
        },
        '冬季(12-2月)': {
            'weather': '气温-5-10℃，偶有降雪',
            'activities': ['温泉', '美食之旅', '民俗体验'],
            'tips': '带好保暖衣物',
            'special': '冬季美食节'
        }
    }

    # 民俗节日
    festivals = {
        '肉孜节': {
            'time': '伊斯兰历每年两次',
            'activities': ['清真寺礼拜', '民族歌舞', '传统美食'],
            'places': '艾提尕尔清真寺、各大广场',
            'tips': '节日期间景点人流量大，需提前规划'
        },
        '古尔邦节': {
            'time': '伊斯兰历12月10日',
            'activities': ['宰牲仪式', '民族表演', '美食节'],
            'places': '清真寺、民俗广场',
            'tips': '可以体验最地道的节日氛围'
        },
        '诺鲁孜节': {
            'time': '每年3月21日',
            'activities': ['民族运动会', '歌舞表演', '美食品尝'],
            'places': '人民广场、民族公园',
            'tips': '春季重要节日，可以体验特色文化'
        }
    }
    
    # 紧急联系方式
    emergency_contacts = {
        '急救中心': '120',
        '报警中心': '110',
        '火警': '119',
        '交通事故': '122',
        '旅游投诉': '12301',
        '天气预报': '12121',
        '喀什市旅游局': '+86 xxx-xxxx-xxxx',
        '喀什市医院': '+86 xxx-xxxx-xxxx',
        '喀什市公安局': '+86 xxx-xxxx-xxxx'
    }
    
    # 旅游注意事项
    travel_tips = {
        '证件准备': [
            '身份证',
            '护照（如需）',
            '银行卡',
            '医保卡',
            '现金'
        ],
        '物品准备': [
            '防晒用品',
            '帽子',
            '舒适鞋子',
            '保暖衣物',
            '常用药品'
        ],
        '安全事项': [
            '保管好随身物品',
            '注意交通安全',
            '避免单独夜行',
            '留意天气变化',
            '记录紧急联系方式'
        ],
        '健康建议': [
            '适应高原气候',
            '防止中暑',
            '饮食卫生',
            '适量运动',
            '充足休息'
        ]
    }
    
    # 当地习俗禁忌
    customs = {
        '礼仪禁忌': [
            '不要触摸他人的帽子',
            '进入清真寺需脱鞋',
            '不要用左手递接物品',
            '不要打听个人隐私',
            '拍照前要征得同意'
        ],
        '饮食禁忌': [
            '不要浪费食物',
            '不要食用猪肉制品',
            '不要饮酒',
            '不要在斋月期间公开进食',
            '进餐时不要踩踏面食'
        ],
        '着装要求': [
            '着装要得体',
            '进入宗教场所要遮盖肩膀和膝盖',
            '避免穿着暴露',
            '建议女性准备头巾',
            '注意防晒'
        ],
        '行为举止': [
            '尊重当地宗教信仰',
            '保持安静',
            '避免政治话题',
            '保持微笑和友善',
            '遵守当地规矩'
        ]
    }
    
    # 特色体验活动
    experiences = {
        '文化体验': {
            '民居家访': '体验维吾尔族传统生活',
            '手工艺制作': '学习制作传统手工艺品',
            '民族服饰体验': '穿着民族服装拍照',
            '传统乐器学习': '体验弹奏热瓦普',
            '书法艺术': '学习维吾尔文书法'
        },
        '美食体验': {
            '烤包子制作': '跟随大厨学习制作',
            '抓饭烹饪': '参与传统抓饭制作',
            '馕坑体验': '观看并参与馕的制作',
            '甜点制作': '学习制作切糕和其他甜点',
            '市集采购': '跟随当地人逛市场'
        },
        '户外活动': {
            '日出观景': '古城屋顶观看日出',
            '骑马漫游': '草原骑马体验',
            '沙漠探险': '塔克拉玛干沙漠之旅',
            '摄影创作': '专业摄影师指导拍摄',
            '农家乐': '体验农家生活'
        },
        '节日活动': {
            '民族节日': '参与传统节日庆典',
            '民族歌舞': '欣赏并学习民族舞蹈',
            '集市游览': '体验传统巴扎文化',
            '手工艺市集': '参观传统工艺制作',
            '美食节': '品尝各类特色美食'
        }
    }

    # 根据关键词生成回复
    if '注意事项' in message or '准备' in message:
        response = """⚠️ 喀什旅游注意事项：

1. 证件准备
   - 身份证（必备）
   - 护照（如需）
   - 银行卡
   - 医保卡
   - 现金（部分商家不支持电子支付）

2. 物品准备
   - 防晒用品（帽子、防晒霜）
   - 舒适的步行鞋
   - 保暖衣物（昼夜温差大）
   - 常用药品
   - 充电宝和转换插头

3. 安全事项
   - 保管好随身物品
   - 注意交通安全
   - 避免单独夜行
   - 留意天气变化
   - 记录紧急联系方式

4. 健康建议
   - 适应高原气候
   - 防止中暑
   - 注意饮食卫生
   - 适量运动
   - 保证充足休息

5. 出行建议
   - 提前规划行程
   - 错峰出行
   - 关注天气预报
   - 预订住宿和车票
   - 购买旅游保险

🌟 温馨提示：
1. 建议提前3-7天预订住宿
2. 准备充足现金
3. 保存紧急联系方式
4. 遵守当地习俗
5. 注意文明旅游

需要更详细的建议或其他信息，请告诉我！"""

    elif '联系' in message or '紧急' in message:
        response = """🆘 喀什紧急联系方式：

1. 紧急救援
   - 急救中心：120
   - 报警中心：110
   - 火警：119
   - 交通事故：122

2. 旅游服务
   - 旅游投诉：12301
   - 天气预报：12121
   - 喀什市旅游局：+86 xxx-xxxx-xxxx

3. 医疗服务
   - 喀什市医院：+86 xxx-xxxx-xxxx
   - 24小时药店：+86 xxx-xxxx-xxxx
   - 急诊中心：+86 xxx-xxxx-xxxx

4. 交通服务
   - 机场问询：+86 xxx-xxxx-xxxx
   - 火车站问询：+86 xxx-xxxx-xxxx
   - 出租车投诉：+86 xxx-xxxx-xxxx

5. 其他服务
   - 天气预报：+86 xxx-xxxx-xxxx
   - 旅游咨询：+86 xxx-xxxx-xxxx
   - 领事保护：+86 xxx-xxxx-xxxx

🌟 温馨提示：
1. 建议保存这些号码
2. 准备好当地联系人电话
3. 记录住宿和导游电话
4. 存好保险公司热线
5. 下载离线地图

需要更多帮助或其他信息，请告诉我！"""

    elif '习俗' in message or '禁忌' in message:
        response = """🎭 喀什民俗禁忌指南：

1. 礼仪禁忌
   - 不要触摸他人的帽子
   - 进入清真寺需脱鞋
   - 不要用左手递接物品
   - 不要打听个人隐私
   - 拍照前要征得同意

2. 饮食禁忌
   - 不要浪费食物
   - 不要食用猪肉制品
   - 不要饮酒
   - 不要在斋月期间公开进食
   - 不要踩踏面食

3. 着装要求
   - 着装要得体
   - 进入宗教场所要遮盖肩膀和膝盖
   - 避免穿着暴露
   - 建议女性准备头巾
   - 注意防晒

4. 行为举止
   - 尊重当地宗教信仰
   - 保持安静
   - 避免政治话题
   - 保持微笑和友善
   - 遵守当地规矩

5. 宗教场所
   - 遵守开放时间
   - 注意着装要求
   - 不要大声喧哗
   - 遵守拍照规定
   - 尊重祈祷时间

🌟 文明旅游提示：
1. 入乡随俗
2. 保持友善
3. 尊重差异
4. 谨言慎行
5. 注意礼貌

需要更详细的解释或其他建议，请告诉我！"""

    elif '体验' in message or '活动' in message:
        response = """🎨 喀什特色体验活动：

1. 文化体验
   - 民居家访
     * 体验维吾尔族传统生活
     * 学习日常礼仪
     * 品尝家常美食
   
   - 手工艺制作
     * 地毯编织
     * 铜器制作
     * 刺绣学习
   
   - 传统艺术
     * 民族服饰体验
     * 乐器学习
     * 书法艺术

2. 美食体验
   - 烤包子制作
     * 跟随大厨学习
     * 亲手制作
     * 品尝成果
   
   - 传统美食
     * 抓饭烹饪
     * 馕坑体验
     * 甜点制作
   
   - 市集采购
     * 逛传统市场
     * 认识食材
     * 学习讲价

3. 户外活动
   - 观景摄影
     * 日出观景
     * 专业摄影指导
     * 最佳机位推荐
   
   - 探险体验
     * 骑马漫游
     * 沙漠探险
     * 农家乐
   
   - 特色游览
     * 屋顶漫步
     * 古城徒步
     * 夜市探索

4. 节日活动
   - 传统节日
     * 参与庆典
     * 学习习俗
     * 互动体验
   
   - 文化活动
     * 民族歌舞
     * 手工艺市集
     * 美食节

🌟 体验建议：
1. 提前预约体验活动
2. 准备适合的服装
3. 带上相机记录
4. 保持开放心态
5. 积极互动交流

需要具体活动预订或更多推荐，请告诉我！"""
    
    else:
        # 使用之前的回复
        response = """🏰 喀什精选景点推荐：
{{ ... }}"""
    
    return response

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': '没有文件'}, 400
    file = request.files['file']
    if file.filename == '':
        return {'error': '没有选择文件'}, 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return {'filename': filename}, 200
    return {'error': '不支持的文件类型'}, 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@socketio.on('upload_message')
def handle_upload_message(data):
    try:
        session_id = data.get('session_id')
        filename = data.get('filename')
        message_type = data.get('type', 'image')  # 'image' 或 'document'
        
        if not session_id or not filename:
            emit('error', '无效的请求')
            return
            
        file_url = f'/uploads/{filename}'
        
        # 根据文件类型生成不同的消息
        if message_type == 'image':
            message = f'![{filename}]({file_url})'
        else:
            message = f'[下载文件：{filename}]({file_url})'
            
        # 保存消息到数据库
        db.add_message(session_id, 'user', message)
        
        # 发送确认消息
        emit('message_confirmed', {'message': message})
        
        # 如果是图片，生成图片描述
        if message_type == 'image':
            response = zhipuai.model_api.invoke(
                model="chatglm_turbo",
                prompt=[
                    {"role": "user", "content": f"这是一张在喀什拍摄的照片。请描述一下照片内容，并给出相关的旅游建议。"}
                ]
            )
            if response.get('code') == 200:
                ai_message = response['data']['choices'][0]['content']
                db.add_message(session_id, 'assistant', ai_message)
                emit('response', ai_message)
            
    except Exception as e:
        print(f"Error in handle_upload_message: {str(e)}")
        emit('error', '处理文件时出错')

@socketio.on('delete_session')
def handle_delete_session(data):
    session_id = data.get('session_id')
    if session_id:
        db.delete_session(session_id)
        emit('session_deleted', {'session_id': session_id})

@socketio.on('export_session')
def handle_export_session(data):
    session_id = data.get('session_id')
    format_type = data.get('format', 'json')
    if session_id:
        try:
            content = db.export_session(session_id, format_type)
            filename = f"chat_export_{session_id}.{format_type}"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            emit('export_ready', {'filename': filename})
        except Exception as e:
            emit('error', f"导出失败: {str(e)}")

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('response', '世间旅友，你好！我是AI疆旅精灵，有什么我可以帮你的吗？')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)
