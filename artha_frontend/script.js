// ============================================================
// ARTHA AI – Frontend ↔ FastAPI Backend Connector
// ============================================================
const BACKEND_URL =
  (window.ARTHA_CONFIG && window.ARTHA_CONFIG.BACKEND_URL) || "http://localhost:8000";
const IS_LOCAL_BACKEND = /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(BACKEND_URL);

function backendConnectionHelp() {
  if (IS_LOCAL_BACKEND) {
    return (
      "⚠️ I couldn't connect to the backend. Start the API locally:\n" +
      "`cd artha_backend && uvicorn main:app --port 8000`"
    );
  }
  return (
    `⚠️ I couldn't reach the API at **${BACKEND_URL}**.\n` +
    "Check that the API is running and `ALLOWED_ORIGINS` on the backend includes this site's URL."
  );
}

function backendOfflineStatus() {
  return IS_LOCAL_BACKEND ? "Backend offline — start uvicorn on port 8000" : `API offline — ${BACKEND_URL}`;
}
function startRenderKeepAlive() {
  if (IS_LOCAL_BACKEND) return;
  const ping = async () => {
    try {
      await fetch(`${BACKEND_URL}/v1/demo/hello`, { method: "GET", cache: "no-store" });
    } catch (_) {}
  };
  ping();
  window.setInterval(ping, 50000);
}

let DEMO_TOKEN = "demo-token";
let notifications = [];

let sessionId = null;
let isRecording = false;
let currentVoiceAudio = null;
let visemeTimeouts = [];
let customerSnapshot = null;
let lastPlanData = null;
let messageMode = "auto";
let speechRecognition = null;
let demoCustomers = [];

let browserVoices = [];
if (typeof speechSynthesis !== "undefined" && speechSynthesis.onvoiceschanged !== undefined) {
  speechSynthesis.onvoiceschanged = () => {
    browserVoices = speechSynthesis.getVoices();
  };
}

if (typeof window !== "undefined") {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SR) {
    speechRecognition = new SR();
    speechRecognition.lang = "en-IN";
    speechRecognition.interimResults = false;
    speechRecognition.maxAlternatives = 1;
    speechRecognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      stopVoice(transcript);
    };
    speechRecognition.onerror = () => stopVoice(null);
    speechRecognition.onend = () => {
      if (isRecording) stopVoice(null);
    };
  }
}

// ---- Utility -----------------------------------------------
function now() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function timeGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

async function apiPost(path, body, retryOnSession = true) {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${DEMO_TOKEN}`,
    },
    body: JSON.stringify(body),
  });
  if (res.status === 403 && retryOnSession && path === "/v1/conversation/message") {
    const err = await res.json().catch(() => ({}));
    if (String(err.detail || "").toLowerCase().includes("session")) {
      sessionId = null;
      await startSession(false);
      return apiPost(path, { ...body, session_id: sessionId }, false);
    }
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

function getCustomerName(snapshot = customerSnapshot) {
  return (snapshot || customerSnapshot || {}).name || "Guest";
}

function getCustomerFirstName(snapshot = customerSnapshot) {
  const first = getCustomerName(snapshot).split(/\s+/).filter(Boolean)[0];
  return first || "there";
}

function getCustomerInitials(snapshot = customerSnapshot) {
  return getCustomerName(snapshot)
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0])
    .join("")
    .toUpperCase() || "??";
}

function monthLabel(monthKey) {
  if (!monthKey || monthKey.length < 7) return "This month";
  const [year, month] = monthKey.split("-");
  const d = new Date(Number(year), Number(month) - 1, 1);
  return d.toLocaleString("en-IN", { month: "long", year: "numeric" });
}

function getLatestMonthWithIncome(transactions) {
  const monthly = {};
  (transactions || []).forEach((tx) => {
    const amount = parseFloat(tx.amount) || 0;
    const month = (tx.date || "").substring(0, 7);
    if (!month) return;
    if (!monthly[month]) monthly[month] = { income: 0, expenses: 0 };
    if (amount > 0) monthly[month].income += amount;
    else if (tx.category !== "Investment") monthly[month].expenses += Math.abs(amount);
  });
  const months = Object.keys(monthly).filter((m) => monthly[m].income > 0).sort();
  if (!months.length) return { month: null, rate: 0.22, avgRate: 0.18 };
  const rates = months.map((m) => {
    const { income, expenses } = monthly[m];
    return income > 0 ? (income - expenses) / income : 0;
  });
  return {
    month: months[months.length - 1],
    rate: rates[rates.length - 1],
    avgRate: rates.reduce((a, b) => a + b, 0) / rates.length,
  };
}

function computeHealthScore(snapshot) {
  const { rate } = getLatestMonthWithIncome(snapshot.transactions || []);
  let score = 55 + Math.round(rate * 100 * 0.35);
  const liabilities = Number(snapshot.debts || 0);
  const totalAssets = (snapshot.accounts || []).reduce((s, a) => s + (a.balance || 0), 0);
  if (liabilities > 0 && totalAssets > 0) {
    score -= Math.min(12, Math.round((liabilities / totalAssets) * 100 * 0.15));
  }
  const goals = snapshot.goals || [];
  goals.forEach((g) => {
    const pct = (g.currentAmount || 0) / (g.targetAmount || 1);
    if (pct < 0.35) score -= 4;
  });
  return Math.max(0, Math.min(100, score));
}

function healthLabel(score) {
  if (score >= 80) return "Excellent";
  if (score >= 65) return "Good";
  if (score >= 50) return "Fair";
  return "Needs attention";
}

function renderCustomerIdentity(snapshot = customerSnapshot) {
  const fullName = getCustomerName(snapshot);
  const firstName = getCustomerFirstName(snapshot);
  const initials = getCustomerInitials(snapshot);
  const risk = snapshot.riskProfile || "Moderate";

  const greeting = document.getElementById("dashboard-greeting");
  if (greeting) greeting.textContent = `${timeGreeting()}, ${firstName}! 👋`;

  const heroKicker = document.getElementById("hero-kicker");
  if (heroKicker) heroKicker.textContent = `Hi ${firstName}! I'm Artha AI`;

  const topbarName = document.getElementById("topbar-name");
  if (topbarName) topbarName.textContent = fullName;

  const topbarAvatar = document.getElementById("topbar-avatar");
  if (topbarAvatar) topbarAvatar.textContent = initials;

  const sidebarName = document.getElementById("persona-name");
  if (sidebarName) sidebarName.textContent = fullName;

  const sidebarAvatar = document.getElementById("sidebar-avatar");
  if (sidebarAvatar) sidebarAvatar.textContent = initials.charAt(0);

  const personaTag = document.getElementById("persona-tag");
  if (personaTag) {
    const match = demoCustomers.find((c) => c.token === DEMO_TOKEN);
    personaTag.textContent = match?.persona || `${risk} Risk`;
  }
}

function buildWelcomeMessage(snapshot) {
  const firstName = getCustomerFirstName(snapshot);
  const { rate, avgRate } = getLatestMonthWithIncome(snapshot.transactions || []);
  const pct = Math.round(rate * 100);
  const avgPct = Math.round(avgRate * 100);
  const comparison = pct >= avgPct ? "above" : "below";
  return (
    `👋 ${timeGreeting()}, ${firstName}! I'm Artha, your personal wealth advisor. ` +
    `You saved **${pct}%** of your income this month — ${comparison} your usual ${avgPct}%. ` +
    `Want a quick update or the full breakdown?`
  );
}

// ---- Session -----------------------------------------------
async function startSession(showWelcome = true) {
  setStatus("Connecting…", false);
  try {
    const data = await apiPost("/v1/session/start", { language: "en" });
    sessionId = data.session_id;
    setStatus(`Connected · ${data.customer_id}`, true);
    await loadCustomerDashboard();

    if (showWelcome) {
      const welcome = buildWelcomeMessage(customerSnapshot);
      appendBotMessage(welcome, null);
      playVoiceAndAnimate(welcome.replace(/\*\*/g, ""), "en");
    }
  } catch (e) {
    setStatus(backendOfflineStatus(), false);
    appendBotMessage(backendConnectionHelp(), null);
  }
}

function setStatus(text, ok) {
  document.getElementById("status-text").textContent = text;
  const dot = document.getElementById("backend-status");
  dot.className = "status-dot-small " + (ok ? "connected" : "disconnected");
}

function switchTab(name) {
  document.querySelectorAll(".nav-item").forEach((el) => el.classList.remove("active"));
  const nav = document.getElementById("nav-" + name);
  if (nav) nav.classList.add("active");

  const target = document.getElementById("tab-" + name);
  if (!target) return;

  if (name === "chat") {
    target.scrollIntoView({ behavior: "smooth", block: "nearest" });
    return;
  }

  const workspace = document.querySelector(".workspace-left");
  if (workspace) {
    const top = target.getBoundingClientRect().top - workspace.getBoundingClientRect().top + workspace.scrollTop;
    workspace.scrollTo({ top: top - 12, behavior: "smooth" });
  }
}

function clearChat() {
  if (currentVoiceAudio) {
    currentVoiceAudio.pause();
    currentVoiceAudio = null;
  }
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  visemeTimeouts.forEach(clearTimeout);
  visemeTimeouts = [];
  applyMouthShape(document.getElementById("avatar-mouth"), "closed");

  clearElement(document.getElementById("chat-messages"));
  document.getElementById("chat-suggestions").style.display = "flex";
  sessionId = null;
  startSession(true);
}

function toggleSidebar() {
  const sb = document.getElementById("sidebar");
  sb.style.display = sb.style.display === "none" ? "flex" : "none";
}

// ---- Chat rendering ----------------------------------------
function appendBotMessage(text, recommendation) {
  hideSuggestions();
  const row = document.createElement("div");
  row.className = "msg-row bot";

  const avatar = createTextElement("div", "msg-avatar bot", "₳");
  const bubble = document.createElement("div");
  bubble.className = "msg-bubble bot";

  text.split(/(\*\*.*?\*\*)/g).forEach((part) => {
    if (part.startsWith("**") && part.endsWith("**") && part.length >= 4) {
      const strong = document.createElement("strong");
      strong.textContent = part.slice(2, -2);
      bubble.appendChild(strong);
    } else if (part.length > 0) {
      bubble.appendChild(document.createTextNode(part));
    }
  });

  bubble.appendChild(createTextElement("div", "msg-time", now()));
  if (recommendation) bubble.appendChild(buildRecCard(recommendation));

  row.appendChild(avatar);
  row.appendChild(bubble);
  document.getElementById("chat-messages").appendChild(row);
  scrollChat();
}

function appendUserMessage(text) {
  hideSuggestions();
  const row = document.createElement("div");
  row.className = "msg-row user";

  const avatar = createTextElement("div", "msg-avatar user", getCustomerInitials());
  const bubble = createTextElement("div", "msg-bubble user", text);
  bubble.appendChild(createTextElement("div", "msg-time", now()));

  row.appendChild(avatar);
  row.appendChild(bubble);
  document.getElementById("chat-messages").appendChild(row);
  scrollChat();
}

function showTyping() {
  const row = document.createElement("div");
  row.className = "msg-row bot";
  row.id = "typing-row";
  const avatar = createTextElement("div", "msg-avatar bot", "₳");
  const bubble = document.createElement("div");
  bubble.className = "msg-bubble bot typing-indicator";
  [1, 2, 3].forEach(() => bubble.appendChild(createTextElement("div", "dot")));
  row.appendChild(avatar);
  row.appendChild(bubble);
  document.getElementById("chat-messages").appendChild(row);
  scrollChat();
}

function hideTyping() {
  const row = document.getElementById("typing-row");
  if (row) row.remove();
}

async function requestRmHandoff(reason) {
  try {
    await apiPost("/v1/handoff/rm", { reason });
    addNotification("RM handoff requested — your advisor will reach out shortly.");
  } catch (e) {
    console.warn("RM handoff failed:", e);
  }
}

function buildRecCard(rec) {
  const card = document.createElement("div");
  card.className = "rec-card";
  card.appendChild(createTextElement("div", "rec-card-header", `Recommendation · ${rec.reasonCode || "ADVISORY"}`));

  const facts = document.createElement("div");
  facts.className = "rec-facts";
  Object.entries(rec.facts || {}).forEach(([k, v]) => {
    const fact = document.createElement("div");
    fact.className = "rec-fact";
    fact.appendChild(document.createTextNode(`${k}: `));
    fact.appendChild(createTextElement("span", null, v));
    facts.appendChild(fact);
  });
  card.appendChild(facts);

  const actions = document.createElement("div");
  actions.className = "rec-actions";

  const tellMeMore = createTextElement("button", "rec-btn primary", "Tell me more");
  tellMeMore.type = "button";
  tellMeMore.addEventListener("click", () => sendSuggestion("Tell me more about this recommendation"));

  const talkToRm = createTextElement("button", "rec-btn", "Talk to RM");
  talkToRm.type = "button";
  talkToRm.addEventListener("click", async () => {
    await requestRmHandoff("Customer requested RM from recommendation card");
    sendSuggestion("Connect me to my RM");
  });

  const dismiss = createTextElement("button", "rec-btn", "Dismiss");
  dismiss.type = "button";
  dismiss.addEventListener("click", async () => {
    if (rec.recommendation_id) {
      try {
        await apiPost(`/v1/recommendations/${rec.recommendation_id}/feedback`, { feedback: "dismiss" });
      } catch (_) {}
    }
    card.remove();
  });

  actions.append(tellMeMore, talkToRm, dismiss);
  card.appendChild(actions);
  return card;
}

function hideSuggestions() {
  document.getElementById("chat-suggestions").style.display = "none";
}

function scrollChat() {
  const el = document.getElementById("chat-messages");
  el.scrollTop = el.scrollHeight;
}

function clearElement(element) {
  if (element) element.replaceChildren();
}

function createTextElement(tagName, className, text) {
  const el = document.createElement(tagName);
  if (className) el.className = className;
  if (text !== undefined && text !== null) el.textContent = String(text);
  return el;
}

// ---- Voice / lipsync ---------------------------------------
function playVoiceAndAnimate(text, language) {
  if (currentVoiceAudio) {
    try { currentVoiceAudio.pause(); } catch (_) {}
    currentVoiceAudio = null;
  }
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  visemeTimeouts.forEach(clearTimeout);
  visemeTimeouts = [];

  const mouth = document.getElementById("avatar-mouth");
  applyMouthShape(mouth, "closed");

  apiPost("/v1/voice/synthesize", { text, language })
    .then((data) => {
      if (!window.speechSynthesis) {
        currentVoiceAudio = new Audio(data.audio_url);
        currentVoiceAudio.play().catch(() => {});
        data.viseme_cues.forEach((cue) => {
          visemeTimeouts.push(setTimeout(() => applyMouthShape(mouth, cue.shape), cue.atMs));
        });
        return;
      }

      const utterance = new SpeechSynthesisUtterance(text);
      if (browserVoices.length === 0) browserVoices = window.speechSynthesis.getVoices();
      const voice = browserVoices.find((v) =>
        language === "hi" ? v.lang.includes("hi") : v.lang.includes("en")
      );
      if (voice) utterance.voice = voice;
      utterance.rate = 0.95;
      utterance.onstart = () => {
        data.viseme_cues.forEach((cue) => {
          visemeTimeouts.push(setTimeout(() => applyMouthShape(mouth, cue.shape), cue.atMs));
        });
      };
      utterance.onend = () => applyMouthShape(mouth, "closed");
      utterance.onerror = () => applyMouthShape(mouth, "closed");
      window.speechSynthesis.speak(utterance);
    })
    .catch((err) => console.warn("Voice synthesis failed:", err));
}

function applyMouthShape(mouth, shape) {
  if (!mouth) return;
  mouth.style.transition = "all 0.1s ease-in-out";
  const shapes = {
    closed: { height: "2px", borderRadius: "0", width: "14px", borderBottom: "2px solid rgba(255,255,255,0.6)" },
    open_wide: { height: "10px", borderRadius: "50%", width: "12px", borderBottom: "3px solid var(--accent-light)" },
    narrow: { height: "5px", borderRadius: "50%", width: "6px", borderBottom: "3px solid var(--accent-light)" },
    open_mild: { height: "5px", borderRadius: "40%", width: "14px", borderBottom: "3px solid var(--accent-light)" },
    wide_smile: { height: "3px", borderRadius: "0 0 10px 10px", width: "16px", borderBottom: "3px solid var(--accent-light)" },
  };
  const s = shapes[shape] || shapes.closed;
  Object.assign(mouth.style, s);
}

function showChainProgress(activeStep) {
  const el = document.getElementById("chain-progress");
  if (!el) return;
  el.classList.remove("hidden");
  document.querySelectorAll(".chain-step").forEach((step) => {
    const n = parseInt(step.dataset.step, 10);
    step.classList.toggle("done", n < activeStep);
    step.classList.toggle("active", n === activeStep);
  });
}

function hideChainProgress() {
  const el = document.getElementById("chain-progress");
  if (el) el.classList.add("hidden");
}

function showAuditBadge(meta) {
  const badge = document.getElementById("audit-badge");
  if (!badge || !meta || meta.path !== "deep") {
    if (badge) badge.classList.add("hidden");
    return;
  }
  const approved = meta.decision === "approve";
  badge.classList.remove("hidden");
  badge.className = "audit-badge " + (approved ? "approved" : "warning");
  badge.textContent = approved
    ? `Audited · ${Math.round(meta.confidence)}% confidence · Chief Wealth Officer`
    : `${meta.decision} · ${Math.round(meta.confidence)}% confidence`;
}

function renderWealthPlan(plan) {
  const container = document.getElementById("wealth-plan-content");
  if (!container || !plan) return;

  const createSection = (title) => {
    const section = document.createElement("div");
    section.className = "plan-section";
    section.appendChild(createTextElement("h3", null, title));
    return section;
  };

  const s2 = plan.step2 || {};
  const s3 = plan.step3 || {};
  const s4 = plan.step4 || {};
  const s5 = plan.step5 || {};

  const goalsSection = createSection("Goals");
  (s2.goals || []).forEach((g) => {
    const row = document.createElement("div");
    row.className = "plan-goal";
    row.appendChild(createTextElement("strong", null, g.name || "Goal"));
    row.appendChild(
      document.createTextNode(
        ` — ${Math.round(Number(g.feasibility_score || 0))}% feasible — SIP ₹${Math.round(Number(g.monthly_sip_required || 0))}/mo`
      )
    );
    goalsSection.appendChild(row);
  });
  if (!(s2.goals || []).length) goalsSection.appendChild(createTextElement("p", null, "No goals"));

  const allocSection = createSection("Allocation");
  (s3.allocations || []).forEach((a) => {
    const row = document.createElement("div");
    row.className = "plan-alloc";
    row.appendChild(createTextElement("span", null, a.product_name || "Product"));
    row.appendChild(createTextElement("span", null, `${Number(a.allocation_pct || 0)}%`));
    allocSection.appendChild(row);
  });
  if (!(s3.allocations || []).length) allocSection.appendChild(createTextElement("p", null, "No allocations"));

  const risksSection = createSection("Red Team Risks");
  const riskList = document.createElement("ul");
  (s4.risks || []).forEach((r) => riskList.appendChild(createTextElement("li", null, r)));
  if ((s4.risks || []).length) risksSection.appendChild(riskList);
  else risksSection.appendChild(createTextElement("p", null, "No risks"));

  const nudgesSection = createSection("Blue Team Nudges");
  const nudgeList = document.createElement("ul");
  (s5.nudges || []).forEach((n) => nudgeList.appendChild(createTextElement("li", null, n.message || "")));
  if ((s5.nudges || []).length) nudgesSection.appendChild(nudgeList);
  else nudgesSection.appendChild(createTextElement("p", null, "No nudges"));

  clearElement(container);
  container.append(goalsSection, allocSection, risksSection, nudgesSection);
  switchTab("plan");
}

async function requestFullPlan() {
  messageMode = "deep";
  document.getElementById("user_input").value = "Generate my full wealth plan";
  await sendMessage();
  messageMode = "auto";
}

async function sendMessage() {
  const input = document.getElementById("user_input");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";

  appendUserMessage(text);
  showTyping();

  const isDeep = messageMode === "deep" || /\b(full wealth plan|wealth plan|portfolio strategy)\b/i.test(text);
  const progressPromise = isDeep ? animateChainProgress() : Promise.resolve();

  const lang = detectLang(text);
  document.getElementById("lang-chip").textContent = lang === "hi" ? "HI" : "EN";

  try {
    if (!sessionId) await startSession(false);

    const [data] = await Promise.all([
      apiPost("/v1/conversation/message", {
        session_id: sessionId,
        message_text: text,
        mode: messageMode,
      }),
      progressPromise,
    ]);

    hideTyping();
    hideChainProgress();

    const voiceText = (data.avatar_script || data.reply_text).replace(/\*\*/g, "");
    appendBotMessage(data.reply_text, data.recommendation);
    showAuditBadge(data.chain_metadata);

    if (data.chain_metadata?.plan_id && data.chain_metadata.path === "deep") {
      try {
        const planRes = await fetch(`${BACKEND_URL}/v1/wealth/plan/${data.chain_metadata.plan_id}`, {
          headers: { Authorization: `Bearer ${DEMO_TOKEN}` },
        });
        if (planRes.ok) {
          const planPayload = await planRes.json();
          lastPlanData = planPayload.steps;
          renderWealthPlan(lastPlanData);
        }
      } catch (_) {}
    }

    await loadCustomerDashboard();
    playVoiceAndAnimate(voiceText, lang);
  } catch (e) {
    hideTyping();
    hideChainProgress();
    const msg = e && e.message ? String(e.message) : "Unknown error";
    if (msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
      appendBotMessage(
        IS_LOCAL_BACKEND
          ? "❌ Couldn't reach the backend. Start the API: `cd artha_backend && uvicorn main:app --port 8000`"
          : `❌ Couldn't reach the API at ${BACKEND_URL}. Verify the server is up and CORS allows this domain.`,
        null
      );
    } else {
      appendBotMessage(`❌ ${msg}`, null);
    }
  }
}

async function animateChainProgress() {
  for (let i = 1; i <= 7; i++) {
    showChainProgress(i);
    await new Promise((r) => setTimeout(r, 350));
  }
}

function sendSuggestion(text) {
  document.getElementById("user_input").value = text;
  sendMessage();
}

function detectLang(text) {
  if (/[\u0900-\u097F]/.test(text)) return "hi";
  const lower = text.toLowerCase();
  const hindiKeywords = ["theek", "kya", "aap", "nahi", "hai", "hoon", "acha", "bol", "batao", "samjhao"];
  if (hindiKeywords.some((w) => new RegExp(`\\b${w}\\b`, "i").test(lower))) return "hi";
  if (/\bmain\b/i.test(lower)) {
    const englishContext = ["account", "balance", "fund", "goal", "portfolio", "rate", "salary"];
    if (!englishContext.some((w) => new RegExp(`\\b${w}\\b`, "i").test(lower))) return "hi";
  }
  return "en";
}

function toggleVoice() {
  const btn = document.getElementById("mic-btn");
  if (!isRecording) {
    isRecording = true;
    btn.classList.add("recording");
    btn.textContent = "⏹";
    document.getElementById("user_input").placeholder = "Listening…";
    if (speechRecognition) {
      try { speechRecognition.start(); } catch (_) { stopVoice("How am I doing this month?"); }
    } else {
      setTimeout(() => stopVoice("How am I doing this month?"), 2000);
    }
  } else {
    stopVoice(null);
  }
}

function stopVoice(transcript) {
  isRecording = false;
  if (speechRecognition) {
    try { speechRecognition.stop(); } catch (_) {}
  }
  const btn = document.getElementById("mic-btn");
  btn.classList.remove("recording");
  btn.textContent = "🎤";
  document.getElementById("user_input").placeholder = "Ask Artha anything about your finances…";
  if (transcript) {
    document.getElementById("user_input").value = transcript;
    sendMessage();
  }
}

// ---- Dashboard ---------------------------------------------
async function loadCustomerDashboard() {
  try {
    const res = await fetch(`${BACKEND_URL}/v1/customer/snapshot`, {
      headers: { Authorization: `Bearer ${DEMO_TOKEN}` },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    customerSnapshot = await res.json();
    renderCustomerIdentity(customerSnapshot);
    renderPortfolio(customerSnapshot);
    renderGoals(customerSnapshot);
    renderInsights(customerSnapshot);
    renderInsightStrip(customerSnapshot);
    renderRecommendationsStrip(customerSnapshot);
    renderHealthScore(customerSnapshot);
  } catch (e) {
    console.warn("Failed to load customer snapshot:", e);
  }
}

function formatCurrency(amount) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);
}

function renderHealthScore(snapshot) {
  const score = computeHealthScore(snapshot);
  const label = healthLabel(score);

  const mainScore = document.getElementById("main-health-score");
  const mainCopy = document.getElementById("main-health-copy");
  const scoreLabel = document.getElementById("score-card-label");
  const sidebarFill = document.getElementById("sidebar-health-fill");
  const sidebarNumber = document.getElementById("sidebar-health-number");

  if (mainScore) mainScore.textContent = String(score);
  if (scoreLabel) scoreLabel.textContent = label;
  if (sidebarFill) sidebarFill.style.width = `${score}%`;
  if (sidebarNumber) sidebarNumber.textContent = `${score} / 100`;
  if (mainCopy) {
    mainCopy.textContent =
      score >= 65
        ? "You are doing great. Keep investing and monitor your expenses."
        : "Focus on savings rate and goal funding to improve your score.";
  }
}

function renderPortfolio(snapshot) {
  const accounts = snapshot.accounts || [];
  let savingsBal = 0;
  let fd = 0;
  let mf = 0;
  const liabilities = Number(snapshot.debts || 0);

  accounts.forEach((acc) => {
    if (acc.type === "SAVINGS") savingsBal += acc.balance || 0;
    else if (acc.type === "FD") fd += acc.balance || 0;
    else if (acc.type === "MF_SIP") mf += acc.balance || 0;
  });

  const totalAssets = savingsBal + fd + mf;
  const netWorth = Math.max(0, totalAssets - liabilities);
  const investments = mf + fd;

  const set = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  set("portfolio-net-worth", formatCurrency(netWorth));
  set("portfolio-mf", formatCurrency(mf));
  set("portfolio-fd", formatCurrency(fd));
  set("portfolio-savings", formatCurrency(savingsBal));
  set("main-net-worth", formatCurrency(netWorth));
  set("main-investments", formatCurrency(investments));
  set("main-savings", formatCurrency(savingsBal));
  set("main-liabilities", formatCurrency(liabilities));

  const fdPct = totalAssets > 0 ? (fd / totalAssets) * 100 : 0;
  const mfPct = totalAssets > 0 ? (mf / totalAssets) * 100 : 0;
  const savPct = totalAssets > 0 ? (savingsBal / totalAssets) * 100 : 0;

  const fdEl = document.getElementById("alloc-fd");
  const mfEl = document.getElementById("alloc-mf");
  const savEl = document.getElementById("alloc-savings");
  const otherEl = document.getElementById("alloc-other");

  if (fdEl) { fdEl.style.width = `${fdPct}%`; fdEl.textContent = `FD ${Math.round(fdPct)}%`; }
  if (mfEl) { mfEl.style.width = `${mfPct}%`; mfEl.textContent = `MF ${Math.round(mfPct)}%`; }
  if (savEl) { savEl.style.width = `${savPct}%`; savEl.textContent = `SAV ${Math.round(savPct)}%`; }
  if (otherEl) otherEl.style.display = "none";
}

function renderGoals(snapshot) {
  const goalsList = document.getElementById("goals-list");
  if (!goalsList) return;
  clearElement(goalsList);

  (snapshot.goals || []).forEach((goal) => {
    const target = goal.targetAmount || 1;
    const current = goal.currentAmount || 0;
    const pct = Math.min(100, Math.round((current / target) * 100));
    const atRisk = pct < 35;
    const statusText = atRisk ? "At Risk" : "On Track";
    const statusClass = atRisk ? "at-risk" : "on-track";

    const card = document.createElement("div");
    card.className = "goal-card";
    const icon = goal.name?.includes("Car") ? "🚗" : goal.name?.includes("House") ? "🏠" : goal.name?.includes("Vacation") ? "✈️" : "🎯";

    const info = document.createElement("div");
    info.className = "goal-info";
    info.appendChild(createTextElement("div", "goal-name", goal.name || "Goal"));
    info.appendChild(createTextElement("div", "goal-meta", `Target: ${formatCurrency(target)} · Due: ${goal.targetDate || "N/A"}`));

    const progressBar = document.createElement("div");
    progressBar.className = "goal-progress-bar";
    const fill = document.createElement("div");
    fill.className = "goal-progress-fill" + (atRisk ? " warning" : "");
    fill.style.width = `${pct}%`;
    progressBar.appendChild(fill);
    info.append(progressBar, createTextElement("div", "goal-pct", `${pct}% funded`));

    card.append(createTextElement("div", "goal-icon", icon), info, createTextElement("div", `goal-status ${statusClass}`, statusText));
    goalsList.appendChild(card);
  });
}

function renderInsights(snapshot) {
  const grid = document.getElementById("insights-grid");
  if (!grid) return;

  const transactions = snapshot.transactions || [];
  const spendsByMonthCat = {};
  transactions.forEach((tx) => {
    const amount = parseFloat(tx.amount) || 0;
    const category = tx.category || "Other";
    const month = (tx.date || "").substring(0, 7);
    if (amount < 0 && category !== "Investment" && month) {
      if (!spendsByMonthCat[month]) spendsByMonthCat[month] = {};
      spendsByMonthCat[month][category] = (spendsByMonthCat[month][category] || 0) + Math.abs(amount);
    }
  });

  const months = Object.keys(spendsByMonthCat).sort();
  const currentMonth = months[months.length - 1] || null;
  const prevMonth = months.length >= 2 ? months[months.length - 2] : null;
  const currentSpends = currentMonth ? spendsByMonthCat[currentMonth] : {};
  const prevSpends = prevMonth ? spendsByMonthCat[prevMonth] : {};
  const monthName = currentMonth ? monthLabel(currentMonth) : "This month";

  const createInsightCard = (category, amount, changeText, changeClass, note) => {
    const card = document.createElement("div");
    card.className = "insight-card";
    card.append(
      createTextElement("div", "insight-cat", category),
      createTextElement("div", "insight-amount", amount),
      createTextElement("div", `insight-change ${changeClass}`, changeText),
      createTextElement("div", "insight-note", note)
    );
    return card;
  };

  clearElement(grid);

  const categories = ["Dining", "Groceries", "Utilities", "Transport"];
  categories.forEach((cat) => {
    const cur = currentSpends[cat] || 0;
    const prev = prevSpends[cat] || 0;
    const delta = cur - prev;
    let changeText = "On par with last month";
    let changeClass = "neutral";
    if (delta > 0) { changeText = `+${formatCurrency(delta)} vs last month`; changeClass = "up"; }
    else if (delta < 0) { changeText = `-${formatCurrency(Math.abs(delta))} vs last month`; changeClass = "down"; }
    grid.appendChild(createInsightCard(`${cat} (${monthName})`, formatCurrency(cur), changeText, changeClass, ""));
  });

  const { rate, avgRate } = getLatestMonthWithIncome(transactions);
  const savingsPct = Math.round(rate * 100);
  const avgPct = Math.round(avgRate * 100);

  const fill = document.getElementById("savings-rate-fill");
  const label = document.getElementById("savings-rate-label");
  if (fill) fill.style.width = `${Math.min(100, savingsPct)}%`;
  if (label) {
    clearElement(label);
    label.appendChild(document.createTextNode(`${savingsPct}% this month · avg ${avgPct}% · `));
    const span = createTextElement("span", null, savingsPct >= avgPct ? "Good job!" : "Room to improve");
    span.style.color = savingsPct >= avgPct ? "var(--green)" : "var(--amber)";
    label.appendChild(span);
  }
}

function renderRecommendationsStrip(snapshot) {
  const list = document.getElementById("recommendation-strip-list");
  if (!list) return;
  clearElement(list);

  const rec = snapshot.active_recommendation || {};
  const items = [];

  if (rec.reasonCode === "DORMANT_FD_REALLOCATION") {
    items.push({
      title: "Review dormant Fixed Deposit",
      detail: "Your FD may be better aligned with an upcoming goal.",
    });
  } else if (rec.reasonCode === "INSUFFICIENT_EMERGENCY_FUND") {
    items.push({
      title: "Build emergency fund",
      detail: rec.facts?.["Shortfall"]
        ? `Close the ${rec.facts["Shortfall"]} gap to reach a 3-month buffer.`
        : "Strengthen your cash buffer for unforeseen expenses.",
    });
  }

  const sip = (snapshot.accounts || []).find((a) => a.type === "MF_SIP");
  if (sip) {
    items.push({
      title: `Continue SIP — ${sip.fundName || "Mutual Fund"}`,
      detail: `₹${Number(sip.sipAmount || 0).toLocaleString("en-IN")}/month keeps your goals on track.`,
    });
  }

  if (!items.length) {
    items.push(
      { title: "Tax Saving (Section 80C)", detail: "Save up to ₹46,800 with ELSS or PPF." },
      { title: "Emergency Fund", detail: "Aim for 3–6 months of expenses in liquid savings." }
    );
  }

  items.slice(0, 3).forEach(({ title, detail }) => {
    const li = document.createElement("li");
    li.appendChild(createTextElement("strong", null, title));
    li.appendChild(createTextElement("span", null, detail));
    list.appendChild(li);
  });
}

function renderInsightStrip(snapshot) {
  const list = document.getElementById("insight-strip-list");
  if (!list) return;
  clearElement(list);

  const transactions = snapshot.transactions || [];
  const { rate } = getLatestMonthWithIncome(transactions);
  const signals = { dining_delta: 0 };
  const months = {};
  transactions.forEach((tx) => {
    const amount = parseFloat(tx.amount) || 0;
    const month = (tx.date || "").substring(0, 7);
    if (amount < 0 && tx.category === "Dining" && month) {
      months[month] = (months[month] || 0) + Math.abs(amount);
    }
  });
  const sorted = Object.keys(months).sort();
  if (sorted.length >= 2) {
    signals.dining_delta = Math.max(0, months[sorted[sorted.length - 1]] - months[sorted[sorted.length - 2]]);
  }

  const items = [
    signals.dining_delta > 0
      ? `Dining spend is up ${formatCurrency(signals.dining_delta)} vs last month — still saving ${Math.round(rate * 100)}% overall.`
      : `Your savings rate this month is ${Math.round(rate * 100)}% — keep up the momentum.`,
    "Review subscriptions and idle balances for quick wins.",
    "Build your emergency fund to cover at least 3 months of expenses.",
  ];

  items.forEach((text) => {
    const li = document.createElement("li");
    li.textContent = text;
    list.appendChild(li);
  });
}

// ---- Notifications -----------------------------------------
function addNotification(msg) {
  notifications.unshift({ text: msg, time: new Date() });
  const badge = document.getElementById("notif-badge");
  const list = document.getElementById("notification-list");
  if (!badge || !list) return;

  badge.style.display = "block";
  badge.textContent = String(notifications.length);
  clearElement(list);

  notifications.forEach((n) => {
    const item = document.createElement("div");
    item.style.cssText = "background:rgba(255,255,255,0.05);padding:10px;border-radius:8px;border-left:3px solid var(--accent);font-size:12px;";
    item.appendChild(createTextElement("div", null, n.text));
    const timeEl = createTextElement("div", null, n.time.toLocaleTimeString());
    timeEl.style.cssText = "font-size:10px;color:var(--text-secondary);margin-top:4px;";
    item.appendChild(timeEl);
    list.appendChild(item);
  });
}

// ---- Demo customers ----------------------------------------
async function loadDemoCustomers() {
  try {
    const res = await fetch(`${BACKEND_URL}/v1/demo/customers`);
    if (!res.ok) return;
    const data = await res.json();
    demoCustomers = data.customers || [];
    const select = document.getElementById("user-switch-select");
    if (!select || !demoCustomers.length) return;
    clearElement(select);
    demoCustomers.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c.token;
      opt.textContent = c.name;
      opt.style.background = "#111";
      if (c.token === DEMO_TOKEN) opt.selected = true;
      select.appendChild(opt);
    });
  } catch (e) {
    console.warn("Could not load demo customers:", e);
  }
}

// ---- Init --------------------------------------------------
document.addEventListener("DOMContentLoaded", async () => {
  startRenderKeepAlive();
  await loadDemoCustomers();

  document.getElementById("user_input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  document.getElementById("user-switch-select")?.addEventListener("change", (e) => {
    DEMO_TOKEN = e.target.value;
    sessionId = null;
    clearElement(document.getElementById("chat-messages"));
    document.getElementById("chat-suggestions").style.display = "flex";
    lastPlanData = null;
    const planContainer = document.getElementById("wealth-plan-content");
    if (planContainer) {
      clearElement(planContainer);
      planContainer.appendChild(
        createTextElement("p", "plan-empty", "Request a Full wealth plan from the chat to generate your audited plan.")
      );
    }
    addNotification(`Switched to ${e.target.selectedOptions[0]?.textContent || "profile"}.`);
    startSession(true);
  });

  document.getElementById("btn-notifications")?.addEventListener("click", () => {
    const panel = document.getElementById("notification-panel");
    panel.style.display = panel.style.display === "none" ? "block" : "none";
    document.getElementById("notif-badge").style.display = "none";
  });
  document.getElementById("close-notif")?.addEventListener("click", () => {
    document.getElementById("notification-panel").style.display = "none";
  });

  document.getElementById("btn-add-goal")?.addEventListener("click", () => {
    document.getElementById("add-goal-modal").style.display = "flex";
  });
  document.getElementById("btn-cancel-goal")?.addEventListener("click", () => {
    document.getElementById("add-goal-modal").style.display = "none";
  });
  document.getElementById("btn-save-goal")?.addEventListener("click", () => {
    const name = document.getElementById("new-goal-name").value.trim();
    const target = parseFloat(document.getElementById("new-goal-amount").value);
    if (name && target && customerSnapshot) {
      if (!customerSnapshot.goals) customerSnapshot.goals = [];
      customerSnapshot.goals.push({
        name,
        targetAmount: target,
        currentAmount: 0,
        targetDate: "2035-01-01",
      });
      renderGoals(customerSnapshot);
      renderHealthScore(customerSnapshot);
      addNotification(`Added new goal: ${name}`);
      document.getElementById("add-goal-modal").style.display = "none";
      document.getElementById("new-goal-name").value = "";
      document.getElementById("new-goal-amount").value = "";
    }
  });

  document.querySelectorAll('a[href="#tab-insights"]').forEach((a) => {
    a.addEventListener("click", (e) => { e.preventDefault(); switchTab("insights"); });
  });

  startSession(true);
});
