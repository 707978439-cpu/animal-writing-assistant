/* ===== 《动物习作AI智能助教》前端交互 ===== */

document.addEventListener("DOMContentLoaded", function () {

    // ===== 标签切换 =====
    const tabBtns = document.querySelectorAll(".tab-btn");
    const panels = {};
    document.querySelectorAll(".tab-panel").forEach(function (p) {
        panels[p.id.replace("tab-", "")] = p;
    });

    tabBtns.forEach(function (btn) {
        btn.addEventListener("click", function () {
            tabBtns.forEach(function (b) { b.classList.remove("active"); });
            Object.values(panels).forEach(function (p) { p.classList.remove("active"); });
            btn.classList.add("active");
            var tab = btn.getAttribute("data-tab");
            if (panels[tab]) panels[tab].classList.add("active");
            if (tab === "word-wall" && !window._wordsLoaded) loadWordBank();
            if (tab === "samples" && !window._samplesLoaded) loadSamples();
        });
    });

    // ===== 加载浮层 =====
    var loadingOverlay = document.getElementById("loading-overlay");
    function showLoading() { loadingOverlay.classList.remove("hidden"); }
    function hideLoading() { loadingOverlay.classList.add("hidden"); }

    // ===== 通用API =====
    async function apiGet(url) {
        showLoading();
        try { var r = await fetch(url); var j = await r.json(); return j; }
        catch (e) { return null; }
        finally { hideLoading(); }
    }
    async function apiPost(url, data) {
        showLoading();
        try {
            var r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
            var j = await r.json(); return j;
        } catch (e) { return { result: "网络出错了。" }; }
        finally { hideLoading(); }
    }
    function escapeHtml(t) {
        var d = document.createElement("div");
        d.textContent = t;
        return d.innerHTML.replace(/\n/g, "<br>");
    }

    // ===== 写作小贴士 =====
    var tipsData = [];
    var tipsIdx = 0;
    var tipsTimer = null;

    fetch("/api/writing-tips").then(function (r) { return r.json(); }).then(function (j) {
        tipsData = j.tips || [];
        if (tipsData.length > 0) showTip(0);
    });

    function showTip(idx) {
        var t = tipsData[idx];
        if (!t) return;
        document.getElementById("tipsIcon").textContent = t.icon;
        document.getElementById("tipsText").textContent = t.tip;
        tipsIdx = idx;
        restartTipTimer();
    }

    function restartTipTimer() {
        if (tipsTimer) clearInterval(tipsTimer);
        tipsTimer = setInterval(function () {
            tipsIdx = (tipsIdx + 1) % tipsData.length;
            showTip(tipsIdx);
        }, 25000);
    }

    document.getElementById("tipsPrev").addEventListener("click", function () {
        tipsIdx = (tipsIdx - 1 + tipsData.length) % tipsData.length;
        showTip(tipsIdx);
    });
    document.getElementById("tipsNext").addEventListener("click", function () {
        tipsIdx = (tipsIdx + 1) % tipsData.length;
        showTip(tipsIdx);
    });

    // ===== 写作闯关 =====
    var stepsData = [];
    var currentStep = 1;
    var challengeAnimal = "";

    fetch("/api/writing-steps").then(function (r) { return r.json(); }).then(function (j) {
        stepsData = j.steps || [];
        if (stepsData.length > 0) renderStep(1);
    });

    function renderStep(stepNum) {
        var s = stepsData[stepNum - 1];
        if (!s) return;
        currentStep = stepNum;

        // 更新进度
        var pct = ((stepNum - 1) / stepsData.length) * 100;
        if (stepNum === stepsData.length) pct = 100;
        document.getElementById("progressFill").style.width = pct + "%";

        var steps = document.querySelectorAll(".p-step");
        steps.forEach(function (sp, i) {
            sp.classList.remove("active", "done");
            if (i + 1 === stepNum) sp.classList.add("active");
            else if (i + 1 < stepNum) sp.classList.add("done");
        });

        // 更新卡片
        document.getElementById("stepBadge").textContent = "第" + stepNum + "步";
        document.getElementById("stepTitle").textContent = s.title;
        document.getElementById("stepTask").textContent = s.task;
        document.getElementById("stepTipText").textContent = s.tips;

        // 引导问题
        var qDiv = document.getElementById("stepQuestions");
        qDiv.innerHTML = "";
        (s.guiding_questions || []).forEach(function (q) {
            var d = document.createElement("div");
            d.className = "q-item";
            d.textContent = "❓ " + q;
            qDiv.appendChild(d);
        });

        // 推荐词语
        var wDiv = document.getElementById("stepWords");
        wDiv.innerHTML = "";
        (s.sample_words || []).forEach(function (w) {
            var chip = document.createElement("span");
            chip.className = "word-chip";
            chip.textContent = w;
            chip.addEventListener("click", function () {
                // 点击词语加入好词墙
                addToWordWall(w, stepsData.length > 0 ? "" : "外形");
            });
            wDiv.appendChild(chip);
        });

        // 按钮状态
        document.getElementById("challengePrev").disabled = (stepNum <= 1);
        var nextBtn = document.getElementById("challengeNext");
        if (stepNum >= stepsData.length) {
            nextBtn.textContent = "完成 ✅";
        } else {
            nextBtn.textContent = "下一步 →";
        }

        // 重置动物输入
        var animalInput = document.getElementById("challenge-animal");
        if (stepNum === 1) {
            document.getElementById("challengeInputArea").style.display = "block";
        } else {
            document.getElementById("challengeInputArea").style.display = "none";
        }
    }

    document.getElementById("challengeNext").addEventListener("click", function () {
        if (currentStep === 1) {
            var animal = document.getElementById("challenge-animal").value.trim();
            if (!animal) { alert("请先输入你想写的动物名称！"); return; }
            challengeAnimal = animal;
        }
        if (currentStep >= stepsData.length) {
            // 完成闯关
            showAchievement();
            return;
        }
        renderStep(currentStep + 1);
    });

    document.getElementById("challengePrev").addEventListener("click", function () {
        if (currentStep > 1) renderStep(currentStep - 1);
    });

    // 回车键推进
    document.getElementById("challenge-animal").addEventListener("keydown", function (e) {
        if (e.key === "Enter") document.getElementById("challengeNext").click();
    });

    function showAchievement() {
        document.getElementById("achievementOverlay").classList.remove("hidden");
        var msgs = [
            "你已经完成了所有步骤，可以开始动笔写啦！",
            "太棒了！素材都准备好了，快开始写作文吧！",
            "恭喜你闯关成功！每个步骤的提示都是你的写作宝藏！",
            "你真厉害！所有的写作素材都收集齐了，加油写！"
        ];
        document.getElementById("achievementText").textContent = msgs[Math.floor(Math.random() * msgs.length)];
        document.getElementById("achievementTitle").textContent = ["太棒了！", "真厉害！", "恭喜你！", "好样的！"][Math.floor(Math.random() * 4)];
    }

    document.getElementById("achievementBtn").addEventListener("click", function () {
        document.getElementById("achievementOverlay").classList.add("hidden");
    });

    // ===== 好词好句墙 =====
    var wordBankData = {};
    var currentCategory = "外形";
    var wallWords = [];
    window._wordsLoaded = false;

    async function loadWordBank() {
        var j = await apiGet("/api/word-bank");
        if (!j) return;
        wordBankData = j;
        window._wordsLoaded = true;
        renderWordWall();
    }

    function renderWordWall() {
        var wall = document.getElementById("wordWall");
        wall.innerHTML = "";

        var words = wordBankData[currentCategory];
        if (!words || !words.words) return;

        words.words.forEach(function (item) {
            addWordCard(item.word, item.example);
        });
    }

    function addWordCard(word, example) {
        var wall = document.getElementById("wordWall");
        var card = document.createElement("div");
        card.className = "word-card";
        card.innerHTML = '<span>' + escapeHtml(word) + '</span><div class="word-example">📖 ' + escapeHtml(example || "") + '</div>';
        card.addEventListener("click", function () {
            card.classList.toggle("expanded");
        });
        wall.appendChild(card);
    }

    function addToWordWall(word, category) {
        if (!word) return;
        var wall = document.getElementById("wordWall");
        // 去重
        var existing = wall.querySelectorAll(".word-card span");
        for (var i = 0; i < existing.length; i++) {
            if (existing[i].textContent.trim() === word) return;
        }
        addWordCard(word, "（课堂收集）");
    }

    // 分类切换
    document.querySelectorAll(".cat-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            document.querySelectorAll(".cat-btn").forEach(function (b) { b.classList.remove("active"); });
            btn.classList.add("active");
            currentCategory = btn.getAttribute("data-cat");
            renderWordWall();
        });
    });

    // 添加课堂好词
    document.getElementById("addWordBtn").addEventListener("click", function () {
        var input = document.getElementById("classWordInput");
        var word = input.value.trim();
        var cat = document.getElementById("classWordCategory").value;
        if (!word) return;
        addToWordWall(word, cat);
        input.value = "";
        // 鼓励效果
        input.placeholder = "✓ 已添加！继续收集吧……";
        setTimeout(function () {
            input.placeholder = '学生说的好词，比如"毛茸茸"……';
        }, 2000);
    });

    document.getElementById("classWordInput").addEventListener("keydown", function (e) {
        if (e.key === "Enter") document.getElementById("addWordBtn").click();
    });

    // ===== 自查清单 =====
    fetch("/api/checklist").then(function (r) { return r.json(); }).then(function (j) {
        var grid = document.getElementById("checklistGrid");
        grid.innerHTML = "";
        (j.checklist || []).forEach(function (item) {
            var div = document.createElement("div");
            div.className = "check-item";
            div.innerHTML = '<span class="check-box"></span><span class="check-icon">' + item.icon + '</span><span>' + item.label + '</span>';
            div.addEventListener("click", function () {
                div.classList.toggle("checked");
            });
            grid.appendChild(div);
        });
    });

    // ===== 写作分析 =====
    var btnReview = document.getElementById("btn-review");
    var reviewResult = document.getElementById("review-result");

    btnReview.addEventListener("click", async function () {
        var essay = document.getElementById("essay-input").value.trim();
        if (!essay || essay.length < 10) {
            reviewResult.textContent = "作文内容太短了，请至少写50个字以上再来分析哦！";
            reviewResult.classList.add("show");
            return;
        }
        var json = await apiPost("/api/review", { essay: essay });
        reviewResult.innerHTML = "";
        reviewResult.classList.add("show");

        // 卡片化展示
        var text = json.result;
        var sections = text.split("【");
        var cardsDiv = document.getElementById("resultCards");
        cardsDiv.innerHTML = "";

        for (var i = 0; i < sections.length; i++) {
            var s = sections[i].trim();
            if (!s) continue;
            var parts = s.split("】");
            var label = parts[0] || "";
            var content = parts.slice(1).join("】") || "";
            if (!content) content = label;

            var card = document.createElement("div");
            card.className = "result-card";
            card.innerHTML = '<div class="card-label">' + label + '</div><div class="card-content">' + escapeHtml(content) + '</div>';
            cardsDiv.appendChild(card);
        }

        // 显示教师批注区
        document.getElementById("teacherNoteArea").style.display = "block";
    });

    // 教师批注
    document.getElementById("saveTeacherNote").addEventListener("click", function () {
        var note = document.getElementById("teacherNoteInput").value.trim();
        if (!note) { alert("请输入批注内容"); return; }
        var card = document.createElement("div");
        card.className = "result-card";
        card.style.borderLeftColor = "#9a8a7a";
        card.innerHTML = '<div class="card-label">👩‍🏫 教师批注</div><div class="card-content">' + escapeHtml(note) + '</div>';
        document.getElementById("resultCards").appendChild(card);
        document.getElementById("teacherNoteInput").value = "";
    });

    // ===== 互动问答 =====
    var btnQaSend = document.getElementById("btn-qa-send");
    var qaInput = document.getElementById("qa-input");
    var qaChat = document.getElementById("qa-chat");
    var qaHistory = [];

    function addChatMessage(text, isUser) {
        var div = document.createElement("div");
        div.className = "chat-msg" + (isUser ? " user-msg" : " ai-msg");
        if (isUser) {
            div.innerHTML = '<div class="msg-bubble">' + escapeHtml(text) + '</div><div class="msg-avatar">🧑</div>';
        } else {
            div.innerHTML = '<div class="msg-avatar">🤖</div><div class="msg-bubble">' + escapeHtml(text) + '</div>';
        }
        qaChat.appendChild(div);
        qaChat.scrollTop = qaChat.scrollHeight;
    }

    btnQaSend.addEventListener("click", async function () {
        var question = qaInput.value.trim();
        if (!question) return;
        qaInput.value = "";
        addChatMessage(question, true);
        qaHistory.push({ role: "user", content: question });
        var json = await apiPost("/api/qa", { question: question, history: qaHistory });
        addChatMessage(json.result, false);
        qaHistory.push({ role: "assistant", content: json.result });
        if (qaHistory.length > 20) qaHistory = qaHistory.slice(-10);
    });

    qaInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); btnQaSend.click(); }
    });

    // ===== 范文展示 =====
    window._samplesLoaded = false;

    async function loadSamples() {
        if (window._samplesLoaded) return;
        var json = await apiGet("/api/samples");
        if (!json) return;
        var list = document.getElementById("samples-list");
        list.innerHTML = "";
        json.samples.forEach(function (sample) {
            var card = document.createElement("div");
            card.className = "sample-card";
            card.innerHTML =
                '<h3>' + escapeHtml(sample.title) + '</h3>' +
                '<div class="sample-author">作者：' + escapeHtml(sample.author) + '</div>' +
                '<div class="sample-body">' + escapeHtml(sample.content) + '</div>' +
                '<div class="sample-tags">' +
                    sample.tags.split(",").map(function (t) {
                        return '<span class="tag">#' + escapeHtml(t.trim()) + '</span>';
                    }).join("") +
                '</div>';
            card.addEventListener("click", function () { card.classList.toggle("expanded"); });
            list.appendChild(card);
        });
        window._samplesLoaded = true;
    }

});
