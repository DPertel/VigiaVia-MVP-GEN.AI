const $ = (id) => document.getElementById(id);
const messages = $("messages");
let busy = false;
let currentFlow = "qa";
let reportState = {};

function setStatus(ok, model) {
  ["side-dot", "top-dot"].forEach(id => $(id).className = "status-dot " + (ok ? "ok" : "bad"));
  $("side-status").textContent = ok ? "API conectada" : "API indisponível";
  $("top-status").textContent = ok ? "Sistema operacional" : "Sem conexão com a API";
  if (model) $("model-name").textContent = model;
}

async function checkHealth() {
  try {
    const r = await fetch("/health");
    if (!r.ok) throw new Error();
    const data = await r.json();
    setStatus(true, data.model || "Modelo local");
  } catch {
    setStatus(false);
    $("model-name").textContent = "Não foi possível consultar o modelo.";
  }
}

function addMessage(role, text, data = null) {
  $("welcome").style.display = "none";
  const wrap = document.createElement("div");
  wrap.className = "message " + role;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "V" : "\u2014";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  const who = document.createElement("div");
  who.className = "who";
  who.textContent = role === "user" ? "VOCÊ" : "VIGIAIA";
  const p = document.createElement("p");
  p.textContent = text;
  bubble.append(who, p);

  if (data) {
    const meta = document.createElement("div");
    meta.className = "answer-meta";
    const mode = document.createElement("span");
    mode.className = "tag";
    mode.textContent = "Modo: " + modeName(data.mode);
    const status = document.createElement("span");
    status.className = "tag " + ((data.fallback || data.abstained) ? "warn" : "good");
    status.textContent = data.fallback
      ? "Conhecimento geral (n\u00e3o verificado)"
      : data.abstained
        ? "Sem evidência suficiente"
        : "Resposta fundamentada";
    meta.append(mode, status);
    bubble.append(meta);

    if (Array.isArray(data.citations) && data.citations.length) {
      const sources = document.createElement("div");
      sources.className = "sources";
      const heading = document.createElement("strong");
      heading.textContent = "REFERÊNCIAS UTILIZADAS";
      sources.append(heading);
      data.citations.forEach(c => {
        const chip = document.createElement("span");
        chip.className = "source-chip";
        chip.textContent = (c.source_id || "Fonte") + (c.chunk_id ? " \u00b7 " + c.chunk_id : "");
        sources.append(chip);
      });
      bubble.append(sources);
    }
    if (data.rationale) {
      const rationale = document.createElement("div");
      rationale.className = "rationale";
      rationale.textContent = data.rationale;
      bubble.append(rationale);
    }
    if (Array.isArray(data.retrieved) && data.retrieved.length) {
      const details = document.createElement("div");
      details.className = "rationale";
      const scores = data.retrieved.map(x => `${x.source_id || "fonte"}: ${Number(x.score || 0).toFixed(3)}`);
      details.textContent = "Trechos recuperados (pontuação): " + scores.join(" \u00b7 ");
      bubble.append(details);
    }
  }

  wrap.append(avatar, bubble);
  messages.append(wrap);
  wrap.scrollIntoView({behavior:"smooth", block:"nearest"});
}

function modeName(mode) {
  return ({base:"Base", rag:"RAG", agent_rag:"Agent + RAG"})[mode] || mode;
}

async function ask(question) {
  if (busy || !question.trim()) return;
  busy = true;
  $("send").disabled = true;
  addMessage("user", question.trim());
  const loading = document.createElement("div");
  loading.className = "message assistant";
  loading.innerHTML = '<div class="avatar">✦</div><div class="bubble"><div class="who">VIGIAIA</div><p>Consultando o modelo local...</p></div>';
  messages.append(loading);
  const started = performance.now();

  try {
    const response = await fetch("/chat-ask", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({question:question.trim(), mode:$("mode").value})
    });
    const data = await response.json();
    loading.remove();
    if (!response.ok) throw new Error(data.detail || "Erro ao consultar a API.");
    addMessage("assistant", data.answer || "O modelo n?o retornou uma resposta.", data);
    const elapsed = ((performance.now() - started) / 1000).toFixed(2);
    const last = messages.lastElementChild?.querySelector(".rationale");
    if (last) last.textContent += ` \u00b7 Tempo nesta interface: ${elapsed}s`;
  } catch (err) {
    loading.remove();
    addMessage("assistant", "Não foi possível concluir a consulta: " + err.message);
  } finally {
    busy = false;
    $("send").disabled = false;
    $("question").focus();
  }
}


function setFlow(flow) {
  if (busy) return;

  currentFlow = flow;
  reportState = {};
  messages.replaceChildren();


document.querySelectorAll("#qa-suggestions .suggestion").forEach(button => {
  button.addEventListener("click", () => {
    if (busy) return;
    $("question").value = button.dataset.question;
    $("ask-form").requestSubmit();
  });
});

document.querySelectorAll(".flow-option").forEach(button => {
    button.classList.toggle("active", button.dataset.flow === flow);
  });

  const reportMode = flow === "report";
  $("welcome").style.display = reportMode ? "none" : "";
  $("qa-suggestions").hidden = reportMode;
  $("report-toolbar").hidden = !reportMode;
  document.querySelector(".mode-row").style.display = reportMode ? "none" : "";
  document.querySelector(".composer-note").textContent = reportMode
    ? "Informe os dados aos poucos. O relato será gerado para sua revisão, sem envio automático."
    : "O VigiaIA utiliza um modelo local. As respostas podem exigir validação documental.";

  $("question").placeholder = reportMode
    ? "Descreva o problema encontrado..."
    : "Pergunte algo sobre o VigiaVia...";

  if (reportMode) {
    addMessage(
      "assistant",
      "Vamos montar seu relato viário. Conte o que você encontrou: pode ser um buraco, asfalto danificado, sinalização quebrada ou uma obstrução na via."
    );
  }
}

async function sendReportMessage(message) {
  if (busy || !message.trim()) return;

  busy = true;
  $("send").disabled = true;
  addMessage("user", message.trim());

  const loading = document.createElement("div");
  loading.className = "message assistant";
  loading.innerHTML = '<div class="avatar">?</div><div class="bubble"><div class="who">VIGIAIA</div><p>Organizando seu relato...</p></div>';
  messages.append(loading);

  try {
    const response = await fetch("/report-chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        message: message.trim(),
        report: reportState
      })
    });

    const data = await response.json();
    loading.remove();

    if (!response.ok) {
      throw new Error(data.detail || "Erro ao processar o relato.");
    }

    reportState = data.report || reportState;
    addMessage("assistant", data.answer || "Não foi possível continuar o relato.");

    if (data.completed) {
      const note = document.createElement("div");
      note.className = "report-result";
      note.textContent = "Relato organizado com sucesso. Revise as informações antes de encaminhá-las ao órgão responsável. O VigiaIA não realizou o envio à prefeitura.";
      const restart = document.createElement("button");
      restart.type = "button";
      restart.className = "suggestion";
      restart.textContent = "Montar outro relato";
      restart.addEventListener("click", () => setFlow("report"));
      note.append(document.createElement("br"), restart);
      messages.append(note);
    }
  } catch (err) {
    loading.remove();
    addMessage("assistant", "Não foi possível processar seu relato: " + err.message);
  } finally {
    busy = false;
    $("send").disabled = false;
    $("question").focus();
  }
}

document.querySelectorAll(".flow-option").forEach(button => {
  button.addEventListener("click", () => setFlow(button.dataset.flow));
});

$("new-report").addEventListener("click", () => setFlow("report"));

$("ask-form").addEventListener("submit", e => {
  e.preventDefault();
  const q = $("question").value;
  $("question").value = "";
  if (currentFlow === "report") {
    sendReportMessage(q);
  } else {
    ask(q);
  }
});
$("question").addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    $("ask-form").requestSubmit();
  }
});
document.querySelectorAll(".suggestion").forEach(btn => {
  btn.addEventListener("click", () => ask(btn.dataset.question));
});

document.querySelectorAll(".nav-item").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach(x => x.classList.remove("active"));
    btn.classList.add("active");
    const evaluation = btn.dataset.page === "evaluation";
    $("chat-page").classList.toggle("active", !evaluation);
    $("evaluation-page").classList.toggle("active", evaluation);
    $("page-title").textContent = evaluation ? "Avaliação experimental" : "Assistente inteligente";
    if (evaluation) loadEvaluation();
  });
});

function percent(value) {
  return typeof value === "number" ? (value * 100).toFixed(1) + "%" : "\u2014";
}
function metricValue(obj, path) {
  return path.split(".").reduce((v,k) => v == null ? undefined : v[k], obj);
}
function makeComparison(name, data) {
  const card = document.createElement("div");
  card.className = "comparison-card";
  const title = document.createElement("h4");
  title.textContent = name;
  const score = document.createElement("div");
  score.className = "big-number";
  score.textContent = percent(data.expected_terms_complete_rate);
  const sub = document.createElement("div");
  sub.className = "sub";
  sub.textContent = "Completude dos termos esperados";
  const bar = document.createElement("div");
  bar.className = "bar";
  const fill = document.createElement("span");
  fill.style.width = Math.max(0, Math.min(100, (data.expected_terms_complete_rate || 0)*100)) + "%";
  bar.append(fill);
  card.append(title, score, sub, bar);
  const stats = [
    ["Respostas bem-sucedidas", `${data.successful_cases ?? "\u2014"} / ${data.total_cases ?? "\u2014"}`],
    ["Erros de execução", data.execution_errors ?? "\u2014"],
    ["Schema válido", percent(data.schema_valid_rate)],
    ["Abstenção correta", percent(data.correct_abstention_rate)],
    ["Latência média", data.latency?.avg_seconds != null ? data.latency.avg_seconds.toFixed(2) + " s" : "\u2014"]
  ];
  stats.forEach(([label,value]) => {
    const row = document.createElement("div");
    row.className = "mini-stat";
    const a = document.createElement("span"); a.textContent = label;
    const b = document.createElement("b"); b.textContent = value;
    row.append(a,b); card.append(row);
  });
  return card;
}

async function loadEvaluation() {
  try {
    const r = await fetch("/evaluation/latest");
    if (!r.ok) throw new Error("Não foi possível carregar a avaliação.");
    const payload = await r.json();
    const data = payload.data;
    const retrieval = data.retrieval || {};
    const runs = data.response_metrics || {};
    $("eval-file").textContent = "Arquivo: " + payload.filename;
    $("recall1").textContent = percent(retrieval.recall_at_1);
    $("recall3").textContent = percent(retrieval.recall_at_3);
    $("eligible").textContent = retrieval.eligible_cases ?? "\u2014";

    const configs = [
      ["Base", runs.base || {}],
      ["RAG", runs.rag || {}],
      ["Agent + RAG", runs.agent_rag || {}]
    ];
    const comparison = $("comparison");
    comparison.replaceChildren(...configs.map(([n,d]) => makeComparison(n,d)));

    const rows = [
      ["Casos bem-sucedidos", "successful_cases", v => v ?? "\u2014"],
      ["Erros de execução", "execution_errors", v => v ?? "\u2014"],
      ["Schema válido", "schema_valid_rate", percent],
      ["Abstenção correta", "correct_abstention_rate", percent],
      ["Termos esperados completos", "expected_terms_complete_rate", percent],
      ["Latência média (s)", "latency.avg_seconds", v => v == null ? "\u2014" : v.toFixed(2)],
      ["Latência mediana (s)", "latency.median_seconds", v => v == null ? "\u2014" : v.toFixed(2)]
    ];
    const tbody = $("metrics-table");
    tbody.replaceChildren();
    rows.forEach(([label,path,format]) => {
      const tr = document.createElement("tr");
      const th = document.createElement("td"); th.textContent = label; tr.append(th);
      configs.forEach(([,d]) => {
        const td = document.createElement("td");
        td.textContent = format(metricValue(d,path));
        tr.append(td);
      });
      tbody.append(tr);
    });
  } catch (err) {
    $("eval-file").textContent = err.message;
    $("comparison").textContent = "Resultados de avaliação indisponíveis.";
    $("metrics-table").textContent = "Execute a avaliação do projeto para gerar um arquivo de resultados.";
  }
}

checkHealth();
setInterval(checkHealth, 30000);
