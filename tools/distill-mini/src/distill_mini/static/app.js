// The client intentionally stays framework-free to keep the local MVP small.
const stages = [
  { id: "inputs", title: "Inputs", description: "等待录入教师答案", badge: "待录入" },
  { id: "teacher", title: "Teacher", description: "教师答案已准备", badge: "教师就绪" },
  { id: "student", title: "Student", description: "学生输出已生成", badge: "学生就绪" },
  { id: "judged", title: "Judged", description: "评审已经完成", badge: "已评审" },
];

let snapshot = { items: [], counts: {} };
let selectedId = null;

const byId = (id) => document.getElementById(id);

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `请求失败：${response.status}`);
  }
  return response.json();
}

function showToast(message, error = false) {
  const toast = byId("toast");
  toast.textContent = message;
  toast.className = `toast${error ? " error" : ""}`;
  toast.hidden = false;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    toast.hidden = true;
  }, 3500);
}

function shortId(id) {
  return `#${id.slice(0, 6)}`;
}

function formatTime(value) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function escapeHtml(value) {
  const element = document.createElement("div");
  element.textContent = value || "";
  return element.innerHTML;
}

function renderBoard() {
  const board = byId("board");
  board.innerHTML = stages
    .map((stage) => {
      const items = snapshot.items.filter((item) => item.stage === stage.id);
      const cards = items.length
        ? items.map((item) => renderCard(item, stage)).join("")
        : `<div class="empty-column">当前没有项目</div>`;
      return `
        <section class="column">
          <div class="column-header">
            <h2 class="column-title">${stage.title}</h2>
            <span class="column-count">${items.length}</span>
          </div>
          <p class="column-description">${stage.description}</p>
          <div class="card-list">${cards}</div>
        </section>`;
    })
    .join("");
}

function renderCard(item, stage) {
  const comparison = item.comparison;
  const active = item.input.id === selectedId ? " active" : "";
  const score =
    comparison && comparison.score !== null ? ` · ${comparison.score.toFixed(2)}` : "";
  return `
    <button class="pipeline-card${active}" data-input-id="${item.input.id}">
      <span class="card-id">${shortId(item.input.id)}</span>
      <div class="card-question">${escapeHtml(item.input.question)}</div>
      <div class="card-footer">
        <span class="card-time">${formatTime(item.input.created_at)}</span>
        <span class="stage-badge badge-${stage.id}">${stage.badge}${score}</span>
      </div>
    </button>`;
}

function selectedItem() {
  return snapshot.items.find((item) => item.input.id === selectedId);
}

function renderDrawer() {
  const item = selectedItem();
  const drawer = byId("drawer");
  if (!item) {
    drawer.hidden = true;
    return;
  }

  drawer.hidden = false;
  byId("drawer-id").textContent = `${shortId(item.input.id)} · ${item.stage.toUpperCase()}`;
  byId("drawer-title").textContent = item.input.question;
  byId("question-copy").textContent = item.input.question;
  byId("teacher-output").value = item.teacher?.output || "";
  byId("student-output").textContent =
    item.student?.output || "运行 Student 后在这里查看输出。";
  byId("student-output").classList.toggle("empty", !item.student);
  byId("student-state").textContent = item.student ? "已生成" : "尚未生成";
  byId("judge-state").textContent = item.comparison ? "已评审" : "尚未对比";
  byId("judge-result").innerHTML = item.comparison
    ? `<div class="judge-summary"><span>${escapeHtml(item.comparison.winner)} 胜出</span><span>${item.comparison.score ?? "无评分"}</span></div><div>${escapeHtml(item.comparison.reason)}</div>`
    : "Teacher 和 Student 都准备好后即可运行对比。";
  byId("run-one-student").disabled = !item.teacher;
  byId("run-one-compare").disabled = !(item.teacher && item.student);
}

async function refresh() {
  snapshot = await request("/api/snapshot");
  const connection = byId("connection");
  connection.textContent = snapshot.openai_connected
    ? `已连接 OpenAI · ${snapshot.student_model}`
    : "OpenAI 未配置";
  connection.classList.toggle("connected", snapshot.openai_connected);
  renderBoard();
  renderDrawer();
}

async function withBusy(button, action) {
  const original = button.textContent;
  button.disabled = true;
  button.textContent = "处理中...";
  try {
    await action();
  } catch (error) {
    showToast(error.message, true);
  } finally {
    button.disabled = false;
    button.textContent = original;
  }
}

byId("board").addEventListener("click", (event) => {
  const card = event.target.closest("[data-input-id]");
  if (!card) return;
  selectedId = card.dataset.inputId;
  renderBoard();
  renderDrawer();
});

byId("add-toggle").addEventListener("click", () => {
  byId("composer").hidden = false;
  byId("new-question").focus();
});

byId("cancel-add").addEventListener("click", () => {
  byId("composer").hidden = true;
});

byId("save-question").addEventListener("click", (event) =>
  withBusy(event.currentTarget, async () => {
    const question = byId("new-question").value;
    const record = await request("/api/inputs", {
      method: "POST",
      body: JSON.stringify({ question }),
    });
    selectedId = record.id;
    byId("new-question").value = "";
    byId("composer").hidden = true;
    await refresh();
    showToast("问题已加入 Inputs。");
  }),
);

byId("close-drawer").addEventListener("click", () => {
  selectedId = null;
  renderBoard();
  renderDrawer();
});

byId("save-teacher").addEventListener("click", (event) =>
  withBusy(event.currentTarget, async () => {
    const item = selectedItem();
    await request(`/api/inputs/${item.input.id}/teacher`, {
      method: "PUT",
      body: JSON.stringify({ output: byId("teacher-output").value }),
    });
    await refresh();
    showToast("教师答案已保存，问题进入 Teacher 阶段。");
  }),
);

async function runBatch(kind, inputIds, message) {
  const result = await request(`/api/batch/${kind}`, {
    method: "POST",
    body: JSON.stringify({ input_ids: inputIds }),
  });
  await refresh();
  showToast(`${message}：处理 ${result.processed} 条。`);
}

byId("run-student").addEventListener("click", (event) =>
  withBusy(event.currentTarget, () => runBatch("student", [], "Student 批量运行完成")),
);

byId("run-compare").addEventListener("click", (event) =>
  withBusy(event.currentTarget, () => runBatch("compare", [], "批量对比完成")),
);

byId("export-sft").addEventListener("click", (event) =>
  withBusy(event.currentTarget, async () => {
    const result = await request("/api/export-sft", { method: "POST" });
    showToast(`已导出 ${result.exported} 条到 ${result.path}`);
  }),
);

byId("run-one-student").addEventListener("click", (event) =>
  withBusy(event.currentTarget, () =>
    runBatch("student", [selectedId], "当前 Student 运行完成"),
  ),
);

byId("run-one-compare").addEventListener("click", (event) =>
  withBusy(event.currentTarget, () =>
    runBatch("compare", [selectedId], "当前对比完成"),
  ),
);

refresh().catch((error) => showToast(error.message, true));
