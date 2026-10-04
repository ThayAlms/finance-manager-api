const API = "/api/v1";
const state = {
  token: localStorage.getItem("caixalivre_token"),
  user: null,
  accounts: [],
  categories: [],
  goals: [],
  importPreview: null,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const formatMoney = (value) => money.format(Number(value || 0));
const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);

function toast(message, error = false) {
  const element = $("#toast");
  element.textContent = message;
  element.className = `toast show${error ? " error" : ""}`;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => (element.className = "toast"), 3500);
}

async function request(path, options = {}) {
  const headers = { ...(options.body ? { "Content-Type": "application/json" } : {}), ...options.headers };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(`${API}${path}`, { ...options, headers });
  if (response.status === 401 && state.token) logout();
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.message || "Não foi possível concluir a operação.");
  }
  return response.status === 204 ? null : response.json();
}

function monthPeriod() {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), 1);
  const local = (date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
  return { start: local(start), end: local(now) };
}

function periodQuery() {
  return new URLSearchParams({ inicio: $("#period-start").value, fim: $("#period-end").value }).toString();
}

function logout() {
  state.token = null;
  state.user = null;
  localStorage.removeItem("caixalivre_token");
  $("#app-view").classList.add("hidden");
  $("#auth-view").classList.remove("hidden");
}

async function enterApp(token) {
  state.token = token;
  localStorage.setItem("caixalivre_token", token);
  try {
    state.user = await request("/usuarios/me");
    $("#user-name").textContent = state.user.nome;
    $("#user-email").textContent = state.user.email;
    $("#avatar").textContent = state.user.nome.split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
    $("#auth-view").classList.add("hidden");
    $("#app-view").classList.remove("hidden");
    await loadDashboard();
  } catch (error) {
    logout();
    toast(error.message, true);
  }
}

async function loadBaseData() {
  const [accounts, categories, goals] = await Promise.all([
    request("/contas"), request("/categorias"), request("/metas"),
  ]);
  Object.assign(state, { accounts, categories, goals });
}

async function loadDashboard() {
  try {
    const summary = await request(`/resumo?${periodQuery()}`);
    $("#metric-balance").textContent = formatMoney(summary.saldo_total);
    $("#metric-income").textContent = formatMoney(summary.receitas);
    $("#metric-expense").textContent = formatMoney(summary.despesas);
    $("#metric-saving").textContent = `${Number(summary.taxa_economia).toFixed(1).replace(".", ",")}%`;
    renderMonthly(summary.evolucao_mensal);
    renderNature(summary.por_natureza);
    renderCategoriesChart(summary.por_categoria.filter((item) => item.tipo === "DESPESA"));
  } catch (error) {
    toast(error.message, true);
  }
}

function renderMonthly(items) {
  const root = $("#monthly-chart");
  if (!items.length) {
    root.className = "chart empty-state";
    root.textContent = "Sem dados no período";
    return;
  }
  const max = Math.max(...items.flatMap((item) => [Number(item.receitas), Number(item.despesas)]), 1);
  root.className = "chart";
  root.innerHTML = items.map((item) => `
    <div class="chart-group" title="${escapeHtml(item.mes)} — receitas ${formatMoney(item.receitas)}, despesas ${formatMoney(item.despesas)}">
      <div class="chart-bars">
        <span class="chart-bar" style="height:${Math.max(2, (Number(item.receitas) / max) * 160)}px"></span>
        <span class="chart-bar expense" style="height:${Math.max(2, (Number(item.despesas) / max) * 160)}px"></span>
      </div>
      <span class="chart-label">${escapeHtml(item.mes.slice(5))}/${escapeHtml(item.mes.slice(2, 4))}</span>
    </div>`).join("");
}

function renderNature(items) {
  $("#nature-summary").innerHTML = items.map((item) => `
    <div class="nature-item">
      <div class="nature-title"><span>${item.natureza === "NEGOCIO" ? "Negócio" : "Pessoal"}</span><span class="${Number(item.resultado) >= 0 ? "positive" : "negative"}">${formatMoney(item.resultado)}</span></div>
      <div class="nature-numbers"><span>Receitas<strong>${formatMoney(item.receitas)}</strong></span><span>Despesas<strong>${formatMoney(item.despesas)}</strong></span></div>
    </div>`).join("");
}

function renderCategoriesChart(items) {
  const root = $("#category-chart");
  if (!items.length) {
    root.className = "bar-list empty-state";
    root.textContent = "Sem despesas no período";
    return;
  }
  const max = Math.max(...items.map((item) => Number(item.total)), 1);
  root.className = "bar-list";
  root.innerHTML = items.slice(0, 6).map((item) => `
    <div class="bar-row"><span>${escapeHtml(item.categoria_nome)}</span><div class="bar-track"><div class="bar-fill" style="width:${(Number(item.total) / max) * 100}%"></div></div><strong>${formatMoney(item.total)}</strong></div>`).join("");
}

const pageMeta = {
  dashboard: ["Seu mês em números", "Visão geral"],
  transactions: ["Movimentações", "Transações"],
  accounts: ["Seu dinheiro", "Contas"],
  categories: ["Organização", "Categorias"],
  goals: ["Planos para o futuro", "Metas"],
};

async function showPage(page) {
  $$(".page").forEach((element) => element.classList.add("hidden"));
  $(`#${page}-page`).classList.remove("hidden");
  $$(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.page === page));
  $("#page-eyebrow").textContent = pageMeta[page][0];
  $("#page-title").textContent = pageMeta[page][1];
  try {
    if (page === "dashboard") await loadDashboard();
    else {
      await loadBaseData();
      if (page === "accounts") renderAccounts();
      if (page === "categories") renderCategories();
      if (page === "goals") renderGoals();
      if (page === "transactions") await renderTransactions();
    }
  } catch (error) { toast(error.message, true); }
}

function renderAccounts() {
  $("#accounts-page").innerHTML = `
    <form id="account-form" class="inline-form">
      <label class="wide">Nome<input name="nome" required maxlength="80" placeholder="Ex.: Conta PJ" /></label>
      <label>Tipo<select name="tipo"><option>CORRENTE</option><option>POUPANCA</option><option>CARTEIRA</option></select></label>
      <label>Natureza<select name="natureza"><option>PESSOAL</option><option>NEGOCIO</option></select></label>
      <label>Saldo inicial<input name="saldo_inicial" type="number" step="0.01" value="0.00" /></label>
      <button class="button primary" type="submit">Adicionar conta</button>
    </form>
    <div class="resource-grid">${state.accounts.map((item) => `
      <article class="resource-card"><span class="tag">${item.natureza === "NEGOCIO" ? "NEGÓCIO" : "PESSOAL"}</span><h3>${escapeHtml(item.nome)}</h3><small class="muted">${escapeHtml(item.tipo)}</small><strong class="amount">${formatMoney(item.saldo_atual)}</strong><small class="muted">Saldo atual</small></article>`).join("") || '<div class="empty-state">Nenhuma conta cadastrada.</div>'}</div>`;
  $("#account-form").addEventListener("submit", createAccount);
}

async function createAccount(event) {
  event.preventDefault();
  const body = Object.fromEntries(new FormData(event.currentTarget));
  try {
    await request("/contas", { method: "POST", body: JSON.stringify(body) });
    toast("Conta criada com sucesso.");
    await showPage("accounts");
  } catch (error) { toast(error.message, true); }
}

function renderCategories() {
  $("#categories-page").innerHTML = `
    <form id="category-form" class="inline-form">
      <label class="wide">Nome<input name="nome" required maxlength="60" placeholder="Ex.: Marketing" /></label>
      <label>Tipo<select name="tipo"><option>DESPESA</option><option>RECEITA</option></select></label>
      <button class="button primary" type="submit">Adicionar categoria</button>
    </form>
    <div class="resource-grid">${state.categories.map((item) => `
      <article class="resource-card"><span class="tag">${item.sistema ? "PADRÃO" : "PERSONALIZADA"}</span><h3>${escapeHtml(item.nome)}</h3><small class="muted">${item.tipo}</small></article>`).join("")}</div>`;
  $("#category-form").addEventListener("submit", createCategory);
}

async function createCategory(event) {
  event.preventDefault();
  try {
    await request("/categorias", { method: "POST", body: JSON.stringify(Object.fromEntries(new FormData(event.currentTarget))) });
    toast("Categoria criada com sucesso.");
    await showPage("categories");
  } catch (error) { toast(error.message, true); }
}

function renderGoals() {
  $("#goals-page").innerHTML = `
    <form id="goal-form" class="inline-form">
      <label class="wide">Nome<input name="nome" required maxlength="80" placeholder="Ex.: Reserva de emergência" /></label>
      <label>Valor alvo<input name="valor_meta" type="number" min="0.01" step="0.01" required /></label>
      <label>Valor atual<input name="valor_atual" type="number" min="0" step="0.01" value="0.00" /></label>
      <label>Prazo<input name="prazo" type="date" /></label>
      <button class="button primary" type="submit">Adicionar meta</button>
    </form>
    <div class="resource-grid">${state.goals.map((item) => `
      <article class="resource-card"><span class="tag">${item.atingida ? "CONCLUÍDA" : "EM ANDAMENTO"}</span><h3>${escapeHtml(item.nome)}</h3><strong class="amount">${formatMoney(item.valor_atual)} <small class="muted">de ${formatMoney(item.valor_meta)}</small></strong><div class="progress"><span style="width:${item.progresso_percentual}%"></span></div><small class="muted">${Number(item.progresso_percentual).toFixed(0)}% concluído</small></article>`).join("") || '<div class="empty-state">Nenhuma meta cadastrada.</div>'}</div>`;
  $("#goal-form").addEventListener("submit", createGoal);
}

async function createGoal(event) {
  event.preventDefault();
  const body = Object.fromEntries(new FormData(event.currentTarget));
  if (!body.prazo) body.prazo = null;
  try {
    await request("/metas", { method: "POST", body: JSON.stringify(body) });
    toast("Meta criada com sucesso.");
    await showPage("goals");
  } catch (error) { toast(error.message, true); }
}

async function renderTransactions() {
  const transactions = await request(`/transacoes?${periodQuery()}&limit=100`);
  const accountOptions = state.accounts.map((item) => `<option value="${item.id}">${escapeHtml(item.nome)}</option>`).join("");
  const categoryOptions = state.categories.map((item) => `<option value="${item.id}" data-type="${item.tipo}">${escapeHtml(item.nome)} — ${item.tipo}</option>`).join("");
  $("#transactions-page").innerHTML = `
    <article class="panel import-panel">
      <div class="panel-head"><div><p class="eyebrow green">Importação inteligente</p><h2>Importar extrato bancário</h2><p class="muted">Envie CSV ou OFX. A IA sugere categoria e separa pessoa física de negócio antes de gravar.</p></div></div>
      <form id="statement-form" class="inline-form import-form">
        <label class="wide">Arquivo CSV ou OFX<input name="arquivo" type="file" accept=".csv,.ofx,.qfx,text/csv" required /></label>
        <label>Nome da conta<input name="conta_nome" required maxlength="80" placeholder="Ex.: Banco Principal" /></label>
        <label>Tipo<select name="tipo_conta"><option>CORRENTE</option><option>POUPANCA</option><option>CARTEIRA</option></select></label>
        <label>Natureza padrão<select name="natureza_padrao"><option>PESSOAL</option><option>NEGOCIO</option></select></label>
        <button class="button primary" type="submit">Analisar extrato</button>
      </form>
      <div id="import-preview"></div>
    </article>
    <form id="transaction-form" class="inline-form">
      <label>Conta<select name="conta_id" required>${accountOptions}</select></label>
      <label>Categoria<select name="categoria_id" required>${categoryOptions}</select></label>
      <label class="wide">Descrição<input name="descricao" required maxlength="160" placeholder="Ex.: Pagamento de cliente" /></label>
      <label>Valor<input name="valor" type="number" min="0.01" step="0.01" required /></label>
      <label>Data<input name="data" type="date" max="${new Date().toISOString().slice(0, 10)}" value="${new Date().toISOString().slice(0, 10)}" required /></label>
      <label>Natureza<select name="natureza"><option value="">Herdar da conta</option><option>PESSOAL</option><option>NEGOCIO</option></select></label>
      <button class="button primary" type="submit" ${state.accounts.length && state.categories.length ? "" : "disabled"}>Adicionar transação</button>
    </form>
    <div class="table-wrap"><table><thead><tr><th>Data</th><th>Descrição</th><th>Conta</th><th>Categoria</th><th>Natureza</th><th>Valor</th></tr></thead><tbody>
      ${transactions.map((item) => `<tr><td>${new Date(`${item.data}T12:00:00`).toLocaleDateString("pt-BR")}</td><td>${escapeHtml(item.descricao)}</td><td>${escapeHtml(item.conta_nome)}</td><td>${escapeHtml(item.categoria_nome)}</td><td><span class="tag">${item.natureza === "NEGOCIO" ? "NEGÓCIO" : "PESSOAL"}</span></td><td class="${item.tipo === "RECEITA" ? "positive" : "negative"}">${item.tipo === "RECEITA" ? "+" : "−"} ${formatMoney(item.valor)}</td></tr>`).join("") || '<tr><td colspan="6" class="empty-state">Nenhuma transação no período.</td></tr>'}
    </tbody></table></div>`;
  $("#transaction-form").addEventListener("submit", createTransaction);
  $("#statement-form").addEventListener("submit", analyzeStatement);
  if (state.importPreview) renderImportPreview();
}

async function analyzeStatement(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const file = form.elements.arquivo.files[0];
  if (!file) return;
  const button = form.querySelector("button");
  button.disabled = true;
  button.textContent = "Analisando…";
  try {
    const body = {
      arquivo_nome: file.name,
      conteudo: await file.text(),
      conta_nome: form.elements.conta_nome.value,
      tipo_conta: form.elements.tipo_conta.value,
      natureza_padrao: form.elements.natureza_padrao.value,
    };
    state.importPreview = await request("/extratos/preview", {
      method: "POST", body: JSON.stringify(body),
    });
    renderImportPreview();
    toast(`${state.importPreview.total_linhas} lançamentos encontrados. Revise antes de confirmar.`);
  } catch (error) { toast(error.message, true); }
  finally { button.disabled = false; button.textContent = "Analisar extrato"; }
}

function renderImportPreview() {
  const preview = state.importPreview;
  if (!preview || !$("#import-preview")) return;
  const categoryOptions = (item) => state.categories
    .filter((category) => category.tipo === item.tipo)
    .map((category) => `<option value="${category.id}" ${category.id === item.categoria_id ? "selected" : ""}>${escapeHtml(category.nome)}</option>`)
    .join("");
  $("#import-preview").innerHTML = `
    <div class="import-summary">
      <span><strong>${preview.total_linhas}</strong> lançamentos</span>
      <span><strong class="positive">${formatMoney(preview.total_creditos)}</strong> créditos</span>
      <span><strong class="negative">${formatMoney(preview.total_debitos)}</strong> débitos</span>
      <span class="tag">${preview.classificado_por_ia ? `IA: ${escapeHtml(preview.modelo)}` : "Regras locais"}</span>
    </div>
    ${preview.aviso ? `<p class="form-warning">${escapeHtml(preview.aviso)}</p>` : ""}
    <div class="table-wrap"><table><thead><tr><th>Importar</th><th>Data</th><th>Descrição</th><th>Tipo</th><th>Valor</th><th>PF/PJ</th><th>Categoria</th><th>Confiança</th></tr></thead><tbody>
      ${preview.lancamentos.map((item) => `<tr data-import-line="${item.linha}">
        <td><input class="import-check" type="checkbox" ${item.duplicada ? "disabled" : "checked"} title="${item.duplicada ? "Já importada" : "Importar"}" /></td>
        <td>${new Date(`${item.data}T12:00:00`).toLocaleDateString("pt-BR")}</td>
        <td title="${escapeHtml(item.justificativa)}">${escapeHtml(item.descricao)}${item.duplicada ? ' <span class="tag">DUPLICADA</span>' : ""}</td>
        <td>${item.tipo}</td><td>${formatMoney(item.valor)}</td>
        <td><select class="import-nature"><option ${item.natureza === "PESSOAL" ? "selected" : ""}>PESSOAL</option><option ${item.natureza === "NEGOCIO" ? "selected" : ""}>NEGOCIO</option></select></td>
        <td><select class="import-category">${categoryOptions(item)}</select></td>
        <td>${Math.round(Number(item.confianca) * 100)}%</td>
      </tr>`).join("")}
    </tbody></table></div>
    <div class="confirm-row"><p class="muted">Revise as sugestões. Nenhum dado foi gravado ainda.</p><button id="confirm-import" class="button primary">Confirmar importação</button></div>`;
  $("#confirm-import").addEventListener("click", confirmStatement);
}

async function confirmStatement() {
  const preview = state.importPreview;
  const rows = $$('[data-import-line]');
  const selected = rows.filter((row) => row.querySelector('.import-check').checked);
  if (!selected.length) return toast("Selecione ao menos um lançamento.", true);
  const items = selected.map((row) => {
    const source = preview.lancamentos.find((item) => item.linha === Number(row.dataset.importLine));
    const categoryId = Number(row.querySelector('.import-category').value);
    const category = state.categories.find((item) => item.id === categoryId);
    return {
      ...source,
      natureza: row.querySelector('.import-nature').value,
      categoria_id: categoryId,
      categoria_nome: category.nome,
      duplicada: false,
    };
  });
  const button = $("#confirm-import");
  button.disabled = true;
  button.textContent = "Importando…";
  try {
    const result = await request("/extratos/confirmar", {
      method: "POST",
      body: JSON.stringify({
        conta_id: preview.conta_existente_id,
        conta_nome: preview.conta_nome,
        tipo_conta: preview.tipo_conta,
        natureza: preview.natureza_padrao,
        saldo_inicial: "0.00",
        lancamentos: items,
      }),
    });
    state.importPreview = null;
    toast(`${result.importadas} transações importadas; ${result.ignoradas_duplicadas} duplicadas ignoradas.`);
    await showPage("transactions");
  } catch (error) {
    button.disabled = false;
    button.textContent = "Confirmar importação";
    toast(error.message, true);
  }
}

async function createTransaction(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const body = Object.fromEntries(new FormData(form));
  body.conta_id = Number(body.conta_id);
  body.categoria_id = Number(body.categoria_id);
  body.tipo = form.elements.categoria_id.selectedOptions[0].dataset.type;
  if (!body.natureza) body.natureza = null;
  try {
    await request("/transacoes", { method: "POST", body: JSON.stringify(body) });
    toast("Transação adicionada com sucesso.");
    await showPage("transactions");
  } catch (error) { toast(error.message, true); }
}

$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const result = await request("/auth/login", { method: "POST", body: JSON.stringify(Object.fromEntries(new FormData(event.currentTarget))) });
    await enterApp(result.access_token);
  } catch (error) { toast(error.message, true); }
});

$("#register-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const body = Object.fromEntries(new FormData(event.currentTarget));
  try {
    await request("/usuarios", { method: "POST", body: JSON.stringify(body) });
    const result = await request("/auth/login", { method: "POST", body: JSON.stringify({ email: body.email, senha: body.senha }) });
    await enterApp(result.access_token);
  } catch (error) { toast(error.message, true); }
});

$$('[data-auth-mode]').forEach((button) => button.addEventListener("click", () => {
  $("#login-form").classList.toggle("hidden", button.dataset.authMode === "register");
  $("#register-form").classList.toggle("hidden", button.dataset.authMode !== "register");
}));
$$('.nav-item').forEach((button) => button.addEventListener("click", () => showPage(button.dataset.page)));
$("#refresh").addEventListener("click", () => showPage($(".nav-item.active").dataset.page));
$("#logout").addEventListener("click", logout);
$("#generate-insight").addEventListener("click", async () => {
  const button = $("#generate-insight");
  button.disabled = true;
  button.textContent = "Analisando…";
  try {
    const result = await request(`/insights?${periodQuery()}`, { method: "POST" });
    $("#insight-text").textContent = result.insight;
    $("#insight-warning").textContent = result.aviso || `Gerado por ${result.modelo}`;
  } catch (error) { toast(error.message, true); }
  finally { button.disabled = false; button.textContent = "Gerar análise"; }
});

const period = monthPeriod();
$("#period-start").value = period.start;
$("#period-end").value = period.end;
if (state.token) enterApp(state.token);
