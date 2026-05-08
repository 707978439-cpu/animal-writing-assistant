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
from flask import Flask, render_template, request, jsonify
from config import SECRET_KEY, DEBUG, HOST, PORT

# ===== 模式切换 =====
# True = 使用模拟回复（无需API Key，适合演示和开发报告截图）
# False = 使用DeepSeek真实API（需在config.py中配置有效API Key）
USE_MOCK = False

if USE_MOCK:
    from mock_responses import (
    get_write_guide, get_review, get_qa_response,
    get_writing_steps, get_word_bank, get_writing_tips,
    get_checklist, get_challenge_step
)
else:
    from openai import OpenAI
    from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

    def call_deepseek(messages, temperature=0.7, max_tokens=2048):
        try:
            response = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"抱歉，AI服务暂时不可用，请稍后重试。错误信息：{str(e)}"

app = Flask(__name__)
app.secret_key = SECRET_KEY


# ===== 范文库 =====
SAMPLE_ESSAYS = [
    {
        "title": "我家的小狗",
        "author": "四年级学生作品",
        "content": (
            '\u201c我家有一只可爱的小狗，名叫\u201c豆豆\u201d。它全身长满了金黄色的毛，摸起来软软的，'
            '像一团毛绒绒的小球。豆豆有一双圆溜溜的大眼睛，黑黑的鼻子总是湿漉漉的。'
            '每次我放学回家，它都会摇着尾巴向我扑来，好像在说：\u201c主人，你终于回来啦！\u201d\n\n'
            '豆豆特别聪明。有一次我教它\u201c坐下\u201d的口令，它只学了三遍就记住了。它吃东西的'
            "样子很有趣，总是先把食物闻一闻，确认合自己口味后，才会慢慢品尝。\n\n"
            "我非常喜欢我的小狗豆豆，它是我最好的朋友！"
        ),
        "tags": "小狗,动物,陪伴"
    },
    {
        "title": "可爱的大熊猫",
        "author": "四年级学生作品",
        "content": (
            "大熊猫是我们的国宝，也是我最喜欢的动物。\n\n"
            "大熊猫长得胖乎乎的，身上的毛黑白分明。它的脑袋圆圆的，两只耳朵也是圆的，"
            '像两个黑色的小绒球。最有趣的是它那一对\u201c黑眼圈\u201d，看起来好像戴了一副墨镜，'
            "酷极了！\n\n"
            "大熊猫最喜欢吃竹子。它吃竹子的时候会用前爪抓住竹子，像我们吃甘蔗一样，"
            "一口一口地啃着，样子憨态可掬。大熊猫走起路来慢悠悠的，一摇一摆，"
            "特别可爱。\n\n"
            "我希望大家都能保护大熊猫，保护它们生活的家园。"
        ),
        "tags": "大熊猫,国宝,保护动物"
    },
    {
        "title": "勤劳的小蜜蜂",
        "author": "四年级学生作品",
        "content": (
            "春暖花开的时候，我总能看到许多小蜜蜂在花丛中忙碌着。\n\n"
            '小蜜蜂的身体是黄黑相间的，有一对透明的翅膀，飞行时会发出\u201c嗡嗡嗡\u201d的声音。'
            '它的后腿上有一个小小的\u201c花粉篮\u201d，采蜜的时候会把花粉装在里面带回家。\n\n'
            "蜜蜂非常勤劳。它们每天天一亮就出去采蜜，一直工作到太阳下山。一只蜜蜂"
            "要采上千朵花，才能酿出一滴蜂蜜。它们团结协作的精神真值得我们学习！\n\n"
            "我喜欢小蜜蜂，它们是最勤劳的小动物。"
        ),
        "tags": "蜜蜂,勤劳,昆虫"
    }
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
