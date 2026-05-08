"""《动物习作AI智能助教》—— Flask本地Web应用
使用说明：
1. 当前为模拟模式（USE_MOCK = True），无需真实API Key即可演示
2. 需要真实API时：将 config.py 中的 DEEPSEEK_API_KEY 设为有效Key，并将下方 USE_MOCK 改为 False
3. 本工具严格遵守《中小学生成式人工智能使用指南（2025年版）》：
   - 定位为教师教学辅助工具，须在教师指导下使用
   - 写作分析建议模块仅供教师参考，禁止直接使用AI生成内容评价学生
   - 小学阶段禁止学生独自使用开放式内容生成功能
"""

import json
import os
import sys
from flask import Flask, render_template, request, jsonify
from config import SECRET_KEY, DEBUG, HOST, PORT

# ===== 解决 .app 打包后的路径问题 =====
if getattr(sys, 'frozen', False):
    base_dir = os.environ.get('RESOURCEPATH', os.path.dirname(__file__))
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# ===== 模式切换 =====
# True = 使用模拟回复（无需API Key，适合演示和开发报告截图）
# False = 使用DeepSeek真实API（需在config.py中配置有效API Key）
USE_MOCK = False

# 静态数据函数（不受模式切换影响）
from mock_responses import (
    get_writing_steps, get_word_bank, get_writing_tips,
    get_checklist, get_challenge_step
)

if USE_MOCK:
    from mock_responses import get_write_guide, get_review, get_qa_response
else:
    from openai import OpenAI
    from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, DEEPSEEK_REASONING, DEEPSEEK_MAX_TOKENS
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

    def call_deepseek(messages, temperature=0.7, max_tokens=None):
        try:
            kwargs = dict(
                model=DEEPSEEK_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or DEEPSEEK_MAX_TOKENS,
            )
            # V4 Pro 支持 reasoning_effort 参数
            if DEEPSEEK_MODEL == "deepseek-v4-pro":
                kwargs["extra_body"] = {"reasoning_effort": DEEPSEEK_REASONING}
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            return f"抱歉，AI服务暂时不可用，请稍后重试。错误信息：{str(e)}"

app = Flask(__name__,
            template_folder=os.path.join(base_dir, 'templates'),
            static_folder=os.path.join(base_dir, 'static'))
app.secret_key = SECRET_KEY


# ===== 范文库（按年级标注 · 符合字数要求） =====
SAMPLE_ESSAYS = [
    # ===== 三年级（≥300字） =====
    {
        "title": "我家的小金鱼",
        "author": "三年级学生作品",
        "grade": "三年级",
        "word_count": "约320字",
        "content": (
            '我家有一条可爱的小金鱼，名叫\u201c泡泡\u201d。它是我去年生日时妈妈送给我的礼物。\n\n'
            '泡泡的身体是金红色的，像穿着一件闪闪发光的外衣。它的眼睛大大的、圆圆的，'
            '总是好奇地东张西望。最漂亮的是它的尾巴，像一把透明的小扇子，'
            '在水中轻轻摆动的时候，就像跳舞一样优美。\n\n'
            '泡泡最喜欢在鱼缸里游来游去。每当我去喂它的时候，它就会飞快地游到水面，'
            '小嘴巴一张一合地等着。我把鱼食撒下去，它就一口一个，吃得可快了。'
            '有一次，我故意把手指放在鱼缸外面，泡泡以为有吃的，'
            '就游过来用嘴巴碰了碰玻璃，好像在说：\u201c快给我吃的呀！\u201d真是有趣极了。\n\n'
            '我喜欢我的小金鱼泡泡，它给我的生活带来了许多快乐。'
            '每当我写作业累了，看看它在水里自由自在地游着，心情就会好起来。'
            '有一次我考试考得不好，回到家闷闷不乐。泡泡好像看出了我的心思，'
            '就在鱼缸里转着圈游来游去，还吐出一串小泡泡，好像在逗我开心。'
            '看着它无忧无虑的样子，我的烦恼一下子就没有了。'
        ),
        "tags": "三年级,金鱼,宠物,写话"
    },
    {
        "title": "可爱的小白兔",
        "author": "三年级学生作品",
        "grade": "三年级",
        "word_count": "约340字",
        "content": (
            '我最喜欢的小动物是小白兔。去年暑假，奶奶从乡下给我带回来一只，我高兴极了。\n\n'
            '小白兔全身雪白雪白的，摸上去毛茸茸的，像一团棉花。它的脑袋圆圆的，'
            '头顶上竖着两只长长的耳朵，只要有一点声音，就会立刻竖起来，可机灵了。'
            '它有一双红宝石般的眼睛，一闪一闪的，特别好看。它的嘴巴是三瓣嘴，'
            '吃东西的时候一动一动的，非常可爱。身体后面有一个又短又圆的小尾巴，'
            '像一个白色的小毛球。\n\n'
            '小白兔最爱吃胡萝卜和青菜叶。每次我拿着胡萝卜走过去，'
            '它就会用后腿站起来，前爪扒着笼子，好像在说：\u201c快给我！快给我！\u201d'
            '我把胡萝卜放进笼子里，它就抱着胡萝卜津津有味地啃起来，'
            '三瓣嘴一动一动的，看得我都饿了。\n\n'
            '小白兔是我的好朋友，每天放学回家我都要先去看看它，'
            '给它喂食、换水。它给我带来了无数欢乐。'
            '有一次我给它喂了一根胡萝卜，它吃得太急了，'
            '不小心咬到了我的手。虽然有点疼，但我知道它不是故意的，'
            '我还是很喜欢它。我希望小白兔能一直健康快乐地陪着我。'
        ),
        "tags": "三年级,小白兔,宠物,观察"
    },

    # ===== 四年级（≥400字） =====
    {
        "title": "我的动物朋友\u2014\u2014小狗乐乐",
        "author": "四年级学生作品",
        "grade": "四年级",
        "word_count": "约450字",
        "content": (
            '我有这样一个动物朋友，它不是什么珍稀动物，而是一只普普通通的小狗，'
            '名叫\u201c乐乐\u201d。它是我十岁生日时，爸爸从宠物店买回来的。\n\n'
            '乐乐长得胖乎乎的，一身棕黄色的毛油光发亮，像穿了一件绸缎大衣。'
            '它的脑袋圆溜溜的，两只耳朵像小扇子一样耷拉着。一双黑葡萄似的大眼睛，'
            '总是水汪汪地看着我，好像在说：\u201c陪我玩一会儿吧！\u201d'
            '它的鼻子黑黑的、湿湿的，嗅觉可灵敏了。一条毛茸茸的尾巴，'
            '见到我就摇个不停，像一把小扫帚。\n\n'
            '乐乐是个十足的小吃货。每次我吃饭的时候，它就蹲在我脚边，'
            '眼巴巴地望着我，口水都要流出来了。有一次我故意把一块骨头举得高高的，'
            '乐乐就站起来用两条后腿走路，像个杂技演员一样，逗得全家哈哈大笑。'
            '它不仅贪吃，还特别聪明。我教它\u201c握手\u201d的动作，'
            '它很快就学会了。现在只要我一伸手说\u201c握手\u201d，'
            '它就会把一只前爪放在我的手心里。\n\n'
            '乐乐是我最好的朋友。每当我心情不好的时候，它就会蹭蹭我的腿，'
            '用舌头舔舔我的手，好像在安慰我。有了乐乐的陪伴，我的生活变得更加丰富多彩。'
            '我希望乐乐能一直健康快乐地陪在我身边。'
            '记得有一次我发烧了，乐乐就趴在我的床边守了一整夜，'
            '一步都不肯离开。第二天妈妈告诉我，乐乐一晚上都没睡好，'
            '时不时抬头看看我有没有醒。听了这话，我的眼眶湿润了。'
        ),
        "tags": "四年级,小狗,动物朋友,叙事"
    },
    {
        "title": "奶奶家的大公鸡",
        "author": "四年级学生作品",
        "grade": "四年级",
        "word_count": "约420字",
        "content": (
            '奶奶家有一只威武的大公鸡，我给它取名叫\u201c大红\u201d。'
            '每次去奶奶家，我总是先跑去看它。\n\n'
            '大红长得可神气了。它全身披着金红色的羽毛，在阳光下闪闪发光，'
            '像一位穿着铠甲的将军。头上顶着一个鲜红的鸡冠，像一顶王冠。'
            '一双圆溜溜的小眼睛，炯炯有神。最引人注目的是它那条长长的尾巴，'
            '由黑绿相间的羽毛组成，高高翘起，走起路来一摇一摆的，威风极了。\n\n'
            '大红每天早上天还没亮就开始打鸣。那响亮的声音\u201c喔喔喔\u201d地叫着，'
            '好像在说：\u201c快起床啦！太阳晒屁股啦！\u201d'
            '它吃东西的时候特别有趣。我把玉米粒撒在地上，它就低下头，'
            '用小嘴飞快地啄着，一边吃一边发出\u201c咯咯咯\u201d的声音，好像很满意似的。'
            '有一次邻居家的小狗跑过来想抢它的食物，大红毫不示弱，'
            '张开翅膀冲了过去，吓得小狗赶紧逃走了。\n\n'
            '大公鸡大红不仅是奶奶家的\u201c闹钟\u201d，还是奶奶家的\u201c小卫士\u201d。'
            '我很喜欢它，每次离开时都要跟它说再见。'
            '有一回邻居家的猫想来偷鸡蛋吃，大红发现了，'
            '立刻竖起羽毛冲了过去，一边叫一边用嘴啄那只猫。'
            '那只猫被啄得狼狈地逃走了。奶奶笑着说：\u201c有大红在，什么都不用怕。\u201d'
            '从那以后，我对大红更加敬佩了，它不仅是只会打鸣的公鸡，'
            '还是一个勇敢的小卫士呢！'
        ),
        "tags": "四年级,大公鸡,动物,观察日记"
    },

    # ===== 五年级（≥500字） =====
    {
        "title": "我和小猫\u201c雪球\u201d的故事",
        "author": "五年级学生作品",
        "grade": "五年级",
        "word_count": "约550字",
        "content": (
            '去年冬天的一个雪夜，我在回家的路上捡到了一只流浪猫。'
            '它浑身雪白，蜷缩在墙角瑟瑟发抖，一双蓝宝石般的眼睛可怜巴巴地望着我。'
            '我心一软，就把它抱回了家。因为它是在雪天捡到的，我给它取名\u201c雪球\u201d。\n\n'
            '雪球是一只漂亮的波斯猫。它的毛又长又软，像冬天的雪花一样洁白。'
            '两只尖尖的小耳朵警惕地竖着，一有动静就会轻轻抖动。'
            '最迷人的是它那双蓝宝石般的大眼睛，白天瞳孔缩成一条线，'
            '到了晚上就会变得又圆又大，发出幽幽的蓝光。它走起路来悄无声息，'
            '身后拖着一条蓬松的大尾巴，优雅得像一位公主。\n\n'
            '雪球的到来给我家带来了许多欢乐，也闹出了不少笑话。'
            '有一次妈妈织毛衣，把毛线球放在沙发上。雪球以为是新玩具，'
            '扑上去就用爪子拨弄起来。结果毛线滚了一地，它自己被缠得团团转，'
            '像一个小雪人似的滚来滚去，把我和妈妈笑得直不起腰。'
            '还有一次，我写作业时把它放在书桌上，它倒好，'
            '直接趴在我的作业本上呼呼大睡，还打起了小呼噜，'
            '好像在说：\u201c别写了，陪我睡觉吧。\u201d\n\n'
            '雪球虽然有时候很调皮，但它也非常贴心。每当我生病不舒服的时候，'
            '它就会安静地趴在我的枕头边，用温热的身体给我取暖。'
            '我难过的时候，它会用头蹭蹭我的手，好像在安慰我。'
            '渐渐地，雪球已经不再是一只流浪猫，而是我们家庭中不可或缺的一员。\n\n'
            '从捡到雪球到现在已经一年了。看着它从瘦弱的小猫变成现在圆滚滚的模样，'
            '我深深感受到：每一个小生命都值得被温柔以待。'
            '雪球给了我快乐和陪伴，我也会一直好好照顾它。'
        ),
        "tags": "五年级,小猫,故事,情感"
    },

    # ===== 惠州特色范文 =====
    {
        "title": "惠州西湖的白鹭",
        "author": "四年级学生作品 \u00b7 惠州特色",
        "grade": "四年级",
        "word_count": "约430字",
        "content": (
            '我的家乡在惠州，这里有美丽的西湖。每到周末，爸爸都会带我去西湖边散步，'
            '我最喜欢看湖面上的白鹭。\n\n'
            '白鹭全身披着雪白的羽毛，像一位穿着白纱裙的仙子。它的脖子又细又长，'
            '常常弯成优雅的S形。一双细长的腿站在浅水中，一动不动地等待着猎物。'
            '正如课本中《白鹭》一文所写：\u201c那雪白的蓑毛，那全身的流线型结构，那铁色的长喙，'
            '那青色的脚\u201d，真是美极了。\n\n'
            '有一次，我看见一只白鹭静静地站在水边，眼睛紧紧盯着水面。'
            '突然，它闪电般地把长嘴伸进水里，叼起一条小鱼，仰起头吞了下去。'
            '那动作快得我差点没看清！吃饱后，它张开宽大的翅膀，在湖面上低低地飞着，'
            '翅膀轻轻扇动，像一朵白云在飘动。\n\n'
            '惠州西湖因为有了这些白鹭，变得更加生动美丽。'
            '我为家乡有如此美丽的景色感到骄傲。'
        ),
        "tags": "惠州,白鹭,西湖,课本关联"
    },
    {
        "title": "罗浮山的小松鼠",
        "author": "三年级学生作品 \u00b7 惠州特色",
        "grade": "三年级",
        "word_count": "约350字",
        "content": (
            '周末，爸爸妈妈带我去惠州的罗浮山玩。罗浮山可高可美了，山上长满了大树。'
            '在树林里，我看见了一只可爱的小松鼠。\n\n'
            '小松鼠的身体小小的，披着一身灰褐色的毛，油亮亮的。它有一条毛茸茸的大尾巴，'
            '翘得高高的，像一把小伞。它的眼睛黑溜溜的，像两颗小黑豆，'
            '总是警惕地东张西望。它的两只前爪小小的，特别灵活，'
            '捧着松果的样子就像我们捧着零食一样可爱。\n\n'
            '小松鼠在树枝间跳来跳去，动作可敏捷了。'
            '这时我想起课文里学过的\u201c松鼠是一种美丽的小动物，乖巧，驯良\u201d'
            '（六年级上册《跑进家来的松鼠》），简直和眼前这只一模一样！\n\n'
            '罗浮山的小松鼠给我们的旅行带来了许多快乐。'
            '我把一片红叶带回家夹在书里，每次看到它就会想起那只可爱的松鼠。'
        ),
        "tags": "惠州,罗浮山,松鼠,课本关联"
    }
]

# ===== 课本好句库（部编版） =====
TEXTBOOK_SENTENCES = [
    {
        "source": "\u300a白鹭\u300b",
        "grade": "五年级上册",
        "sentence": '\u201c那雪白的蓑毛，那全身的流线型结构，那铁色的长喙，那青色的脚，增之一分则嫌长，减之一分则嫌短，素之一忽则嫌白，黛之一忽则嫌黑。\u201d',
        "usage": "用排比句从多个角度描写外形，突出动物体态的完美。"
    },
    {
        "source": "\u300a搭船的鸟\u300b",
        "grade": "三年级上册",
        "sentence": '\u201c它的羽毛是翠绿的，翅膀带着一些蓝色，比鹦鹉还漂亮。它还有一张红色的长嘴。\u201d',
        "usage": "按羽毛\u2192翅膀\u2192嘴巴的顺序写颜色，层次分明。"
    },
    {
        "source": "\u300a猫\u300b",
        "grade": "四年级下册",
        "sentence": '\u201c它要是高兴，能比谁都温柔可亲：用身子蹭你的腿，把脖子伸出来让你给它抓痒，或是在你写作的时候，跳上桌来，在稿纸上踩印几朵小梅花。\u201d',
        "usage": "用具体动作来表现性格，比直接说\u201c它很温顺\u201d生动得多。"
    },
    {
        "source": "\u300a母鸡\u300b",
        "grade": "四年级下册",
        "sentence": '\u201c它负责、慈爱、勇敢、辛苦，因为它有了一群鸡雏。它伟大，因为它是鸡母亲。一个母亲必定就是一位英雄。\u201d',
        "usage": "先写具体表现，最后用一句话升华情感。"
    },
    {
        "source": "\u300a白鹅\u300b",
        "grade": "四年级下册",
        "sentence": '\u201c鹅的步态，更是傲慢了。大体上与鸭相似，但鸭的步调急速，有局促不安之相；鹅的步调从容，大模大样的，颇像京剧里的净角出场。\u201d',
        "usage": "用对比突出特点，动物和动物比，一下子就鲜明了。"
    },
    {
        "source": "\u300a珍珠鸟\u300b",
        "grade": "五年级上册",
        "sentence": '\u201c它先是离我较远，见我不去伤害它，便一点点挨近，然后蹦到我的杯子上，俯下头来喝茶，再偏过脸瞧瞧我的反应。\u201d',
        "usage": "用\u201c先\u2026\u2026然后\u2026\u2026再\u2026\u2026\u201d的递进顺序，把过程写活。"
    },
    {
        "source": "\u300a燕子\u300b",
        "grade": "三年级下册",
        "sentence": '\u201c一身乌黑的羽毛，一对轻快有力的翅膀，加上剪刀似的尾巴，凑成了那样可爱的活泼的小燕子。\u201d',
        "usage": "三个短句写三个部位，最后用长句总结，简洁有力。"
    },
    {
        "source": "\u300a跑进家来的松鼠\u300b",
        "grade": "六年级上册",
        "sentence": '\u201c松鼠是一种美丽的小动物，乖巧，驯良，很讨人喜欢。它面容清秀，眼睛闪闪发光，身体矫健，四肢轻快，非常敏捷，非常机警。\u201d',
        "usage": "先用概括句写整体印象，再用具体描写展开，经典开头方式。"
    }
]

# ===== 惠州特色好词 =====
HUIZHOU_WORDS = [
    {"word": "惠州西湖", "example": "惠州西湖的湖水碧波荡漾，像一面镜子。"},
    {"word": "罗浮山", "example": "罗浮山上云雾缭绕，像仙境一样美。"},
    {"word": "白鹭", "example": "西湖边的白鹭像一位白衣仙子，优雅地站在水中。"},
    {"word": "苏东坡", "example": "苏东坡在惠州写下\u201c日啖荔枝三百颗\u201d的名句。"},
    {"word": "荔枝", "example": "惠州荔枝又大又甜，像一颗颗红宝石挂在枝头。"},
    {"word": "东江", "example": "东江水清清的，缓缓地流过惠州城。"},
]


# ===== 路由 =====

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/write-guide", methods=["POST"])
def write_guide():
    """写作指导"""
    data = request.get_json()
    animal = data.get("animal", "").strip()
    detail = data.get("detail", "").strip()

    if USE_MOCK:
        result = get_write_guide(animal, detail)
    else:
        from config import SYSTEM_PROMPTS
        user_content = f"我想写一篇关于【{animal}】的作文。"
        if detail:
            user_content += f" 具体要求：{detail}"
        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS["write_guide"]},
            {"role": "user", "content": user_content}
        ]
        result = call_deepseek(messages)

    return jsonify({"result": result})


@app.route("/api/review", methods=["POST"])
def review_essay():
    """作文批改"""
    data = request.get_json()
    essay = data.get("essay", "").strip()

    if len(essay) < 10:
        return jsonify({"result": "作文内容太短了，请至少写50个字以上再来批改哦！"})

    if USE_MOCK:
        result = get_review(essay)
    else:
        from config import SYSTEM_PROMPTS
        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS["essay_review"]},
            {"role": "user", "content": f"请批改这篇四年级学生的动物习作：\n\n{essay}"}
        ]
        result = call_deepseek(messages)

    return jsonify({"result": result})


@app.route("/api/qa", methods=["POST"])
def qa():
    """互动问答"""
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"result": "请先输入你的问题。"})

    history = data.get("history", [])

    if USE_MOCK:
        result = get_qa_response(question, history)
    else:
        from config import SYSTEM_PROMPTS
        messages = [{"role": "system", "content": SYSTEM_PROMPTS["qa"]}]
        for msg in history[-6:]:
            messages.append(msg)
        messages.append({"role": "user", "content": question})
        result = call_deepseek(messages, max_tokens=1024)

    return jsonify({"result": result})


@app.route("/api/samples", methods=["GET"])
def get_samples():
    """获取范文列表"""
    return jsonify({"samples": SAMPLE_ESSAYS})


# ===== 互动增强模块路由 =====

@app.route("/api/writing-steps", methods=["GET"])
def writing_steps():
    """获取写作闯关步骤"""
    return jsonify({"steps": get_writing_steps()})


@app.route("/api/challenge-step", methods=["POST"])
def challenge_step():
    """获取指定步骤的AI提示"""
    data = request.get_json()
    animal = data.get("animal", "").strip()
    step = data.get("step", 1)
    result = get_challenge_step(animal, step)
    return jsonify({"result": result, "step": step})


@app.route("/api/textbook-sentences", methods=["GET"])
def textbook_sentences():
    """获取课本好句库"""
    return jsonify({"sentences": TEXTBOOK_SENTENCES})


@app.route("/api/huizhou-words", methods=["GET"])
def huizhou_words():
    """获取惠州特色好词"""
    return jsonify({"words": HUIZHOU_WORDS})


@app.route("/api/word-bank", methods=["GET"])
def word_bank():
    """获取好词好句分类库"""
    return jsonify(get_word_bank())


@app.route("/api/writing-tips", methods=["GET"])
def writing_tips():
    """获取写作小贴士"""
    return jsonify({"tips": get_writing_tips()})


@app.route("/api/checklist", methods=["GET"])
def checklist():
    """获取自查清单"""
    return jsonify({"checklist": get_checklist()})


if __name__ == "__main__":
    mode_str = "模拟模式（演示用）" if USE_MOCK else "真实API模式"
    print(f"《动物习作AI智能助教》启动中...")
    print(f"当前模式：{mode_str}")
    print(f"请在浏览器中访问: http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
