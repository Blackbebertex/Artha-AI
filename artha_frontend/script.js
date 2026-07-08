// ============================================================
// ARTHA AI – Frontend ↔ FastAPI Backend Connector
// ============================================================
const BACKEND_URL = "http://localhost:8000";
const DEMO_TOKEN  = "demo-token";

let sessionId = null;
let isRecording = false;
let currentVoiceAudio = null;
let visemeTimeouts = [];
let customerSnapshot = null;
let lastPlanData = null;
let messageMode = "auto";

// Browser voice initialization
let browserVoices = [];
if (typeof speechSynthesis !== 'undefined' && speechSynthesis.onvoiceschanged !== undefined) {
  speechSynthesis.onvoiceschanged = () => {
    browserVoices = speechSynthesis.getVoices();
  };
}

// ---- Utility -----------------------------------------------
function now() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

async function apiPost(path, body) {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${DEMO_TOKEN}`,
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ---- Session -----------------------------------------------
async function startSession() {
  setStatus("Connecting…", false);
  try {
    const data = await apiPost("/v1/session/start", { language: "en" });
    sessionId = data.session_id;
    setStatus("Connected · Session " + sessionId, true);
    
    // Dynamically fetch customer snapshot to populate dashboard
    await loadCustomerDashboard();
    
    // Initial welcome message from backend
    appendBotMessage(
      "👋 Good morning, Riya! I'm Artha, your personal wealth advisor. You saved **22%** of your income this month — above your usual 18%! Want a quick update or the full breakdown?",
      null
    );
    // Play voice for the initial welcome
    playVoiceAndAnimate("Good morning, Riya! I'm Artha, your personal wealth advisor. You saved 22% of your income this month — above your usual 18%! Want a quick update or the full breakdown?", "en");
  } catch (e) {
    setStatus("Backend offline – check uvicorn is running on port 8000", false);
    appendBotMessage("⚠️ I couldn't connect to the backend. Please make sure the FastAPI server is running on http://localhost:8000", null);
  }
}

// ---- Status bar --------------------------------------------
function setStatus(text, ok) {
  document.getElementById("status-text").textContent = text;
  const dot = document.getElementById("backend-status");
  dot.className = "status-dot-small " + (ok ? "connected" : "disconnected");
}

// ---- Tab switching -----------------------------------------
function switchTab(name) {
  document.querySelectorAll(".tab-panel").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
  document.getElementById("tab-" + name).classList.add("active");
  document.getElementById("nav-" + name).classList.add("active");
}

// ---- Clear chat --------------------------------------------
function clearChat() {
  // Stop active voice / animations
  if (currentVoiceAudio) {
    currentVoiceAudio.pause();
    currentVoiceAudio = null;
  }
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
  visemeTimeouts.forEach(clearTimeout);
  visemeTimeouts = [];
  applyMouthShape(document.getElementById("avatar-mouth"), "closed");

  document.getElementById("chat-messages").innerHTML = "";
  document.getElementById("chat-suggestions").style.display = "flex";
  startSession();
}

// ---- Sidebar toggle (mobile) --------------------------------
function toggleSidebar() {
  const sb = document.getElementById("sidebar");
  sb.style.display = sb.style.display === "none" ? "flex" : "none";
}

// ---- Chat rendering ----------------------------------------
function appendBotMessage(text, recommendation) {
  hideSuggestions();
  const row = document.createElement("div");
  row.className = "msg-row bot";

  const avatar = document.createElement("div");
  avatar.className = "msg-avatar bot";
  avatar.textContent = "₳";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble bot";

  // Safely parse **bold** markdown to avoid XSS
  const parts = text.split(/(\*\*.*?\*\*)/g);
  parts.forEach(part => {
    if (part.startsWith("**") && part.endsWith("**") && part.length >= 4) {
      const strong = document.createElement("strong");
      strong.textContent = part.slice(2, -2);
      bubble.appendChild(strong);
    } else if (part.length > 0) {
      bubble.appendChild(document.createTextNode(part));
    }
  });

  const timeEl = document.createElement("div");
  timeEl.className = "msg-time";
  timeEl.textContent = now();
  bubble.appendChild(timeEl);

  if (recommendation) {
    bubble.appendChild(buildRecCard(recommendation));
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  document.getElementById("chat-messages").appendChild(row);
  scrollChat();
}

function appendUserMessage(text) {
  hideSuggestions();
  const row = document.createElement("div");
  row.className = "msg-row user";

  const avatar = document.createElement("div");
  avatar.className = "msg-avatar user";
  avatar.textContent = "R";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble user";
  bubble.textContent = text;

  const timeEl = document.createElement("div");
  timeEl.className = "msg-time";
  timeEl.textContent = now();
  bubble.appendChild(timeEl);

  row.appendChild(avatar);
  row.appendChild(bubble);
  document.getElementById("chat-messages").appendChild(row);
  scrollChat();
}

function showTyping() {
  const row = document.createElement("div");
  row.className = "msg-row bot";
  row.id = "typing-row";

  const avatar = document.createElement("div");
  avatar.className = "msg-avatar bot";
  avatar.textContent = "₳";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble bot typing-indicator";
  bubble.innerHTML = "<div class='dot'></div><div class='dot'></div><div class='dot'></div>";

  row.appendChild(avatar);
  row.appendChild(bubble);
  document.getElementById("chat-messages").appendChild(row);
  scrollChat();
}

function hideTyping() {
  const row = document.getElementById("typing-row");
  if (row) row.remove();
}

function buildRecCard(rec) {
  const card = document.createElement("div");
  card.className = "rec-card";
  card.innerHTML = `
    <div class="rec-card-header">💡 Recommendation · ${rec.reasonCode || "ADVISORY"}</div>
    <div class="rec-facts">
      ${Object.entries(rec.facts || {}).map(([k,v]) => `<div class="rec-fact">${k}: <span>${v}</span></div>`).join("")}
    </div>
    <div class="rec-actions">
      <button class="rec-btn primary" onclick="sendSuggestion('Tell me more about this recommendation')">Tell me more</button>
      <button class="rec-btn" onclick="sendSuggestion('Connect me to my RM')">Talk to RM</button>
      <button class="rec-btn" onclick="this.closest('.rec-card').remove()">Dismiss</button>
    </div>
  `;
  return card;
}

function hideSuggestions() {
  document.getElementById("chat-suggestions").style.display = "none";
}

function scrollChat() {
  const el = document.getElementById("chat-messages");
  el.scrollTop = el.scrollHeight;
}

// ---- Lipsync Avatar Viseme Controller ----------------------
function playVoiceAndAnimate(text, language) {
  // Clear running instances
  if (currentVoiceAudio) {
    try { currentVoiceAudio.pause(); } catch(e){}
    currentVoiceAudio = null;
  }
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
  visemeTimeouts.forEach(clearTimeout);
  visemeTimeouts = [];
  
  const mouth = document.getElementById("avatar-mouth");
  applyMouthShape(mouth, "closed");
  
  // Call backend voice synthesize API
  apiPost("/v1/voice/synthesize", { text: text, language: language })
    .then(data => {
      if (!window.speechSynthesis) {
        // Fallback to static audio file if SpeechSynthesis is not supported
        currentVoiceAudio = new Audio(data.audio_url);
        currentVoiceAudio.play().catch(e => console.log("Audio playback blocked/failed:", e));
        
        data.viseme_cues.forEach(cue => {
          const timer = setTimeout(() => {
            applyMouthShape(mouth, cue.shape);
          }, cue.atMs);
          visemeTimeouts.push(timer);
        });
        return;
      }
      
      // Use browser SpeechSynthesis for real voice response
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Load current voices list
      if (browserVoices.length === 0) {
        browserVoices = window.speechSynthesis.getVoices();
      }
      
      // Select appropriate voice based on language
      let selectedVoice = null;
      if (language === "hi") {
        selectedVoice = browserVoices.find(v => v.lang.includes("hi-IN") || v.lang.includes("hi"));
      } else {
        selectedVoice = browserVoices.find(v => v.lang.includes("en-IN") || v.lang.includes("en-US") || v.lang.includes("en"));
      }
      if (selectedVoice) utterance.voice = selectedVoice;
      
      utterance.rate = 0.95; // Slightly slower for natural pacing
      
      // Synchronize viseme mouth shapes starting exactly when speech starts
      utterance.onstart = () => {
        data.viseme_cues.forEach(cue => {
          const timer = setTimeout(() => {
            applyMouthShape(mouth, cue.shape);
          }, cue.atMs);
          visemeTimeouts.push(timer);
        });
      };
      
      utterance.onend = () => {
        applyMouthShape(mouth, "closed");
      };
      
      utterance.onerror = () => {
        applyMouthShape(mouth, "closed");
      };
      
      window.speechSynthesis.speak(utterance);
    })
    .catch(err => {
      console.warn("Could not load lipsync voice stream:", err);
    });
}

function applyMouthShape(mouth, shape) {
  if (!mouth) return;
  mouth.style.transition = "all 0.1s ease-in-out";
  
  if (shape === "closed") {
    mouth.style.height = "2px";
    mouth.style.borderRadius = "0";
    mouth.style.width = "14px";
    mouth.style.borderBottom = "2px solid rgba(255,255,255,0.6)";
  } else if (shape === "open_wide") {
    mouth.style.height = "10px";
    mouth.style.borderRadius = "50%";
    mouth.style.width = "12px";
    mouth.style.borderBottom = "3px solid var(--accent-light)";
  } else if (shape === "narrow") {
    mouth.style.height = "5px";
    mouth.style.borderRadius = "50%";
    mouth.style.width = "6px";
    mouth.style.borderBottom = "3px solid var(--accent-light)";
  } else if (shape === "open_mild") {
    mouth.style.height = "5px";
    mouth.style.borderRadius = "40%";
    mouth.style.width = "14px";
    mouth.style.borderBottom = "3px solid var(--accent-light)";
  } else if (shape === "wide_smile") {
    mouth.style.height = "3px";
    mouth.style.borderRadius = "0 0 10px 10px";
    mouth.style.width = "16px";
    mouth.style.borderBottom = "3px solid var(--accent-light)";
  }
}

// ---- Chain progress UI -------------------------------------
function showChainProgress(activeStep) {
  const el = document.getElementById("chain-progress");
  if (!el) return;
  el.classList.remove("hidden");
  document.querySelectorAll(".chain-step").forEach(step => {
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
  if (!badge || !meta) return;
  if (meta.path !== "deep") {
    badge.classList.add("hidden");
    return;
  }
  const approved = meta.decision === "approve";
  badge.classList.remove("hidden");
  badge.innerHTML = approved
    ? `✓ Audited · ${Math.round(meta.confidence)}% confidence · Chief Wealth Officer`
  : `⚠ ${meta.decision} · ${Math.round(meta.confidence)}% confidence`;
  badge.className = "audit-badge " + (approved ? "approved" : "warning");
}

async function animateChainProgress() {
  for (let i = 1; i <= 7; i++) {
    showChainProgress(i);
    await new Promise(r => setTimeout(r, 400));
  }
}

function renderWealthPlan(plan) {
  const container = document.getElementById("wealth-plan-content");
  if (!container || !plan) return;
  const s2 = plan.step2 || {};
  const s3 = plan.step3 || {};
  const s4 = plan.step4 || {};
  const s5 = plan.step5 || {};
  const goals = (s2.goals || []).map(g =>
    `<div class="plan-goal"><strong>${g.name}</strong> — ${g.feasibility_score}% feasible · SIP ₹${Math.round(g.monthly_sip_required || 0)}/mo</div>`
  ).join("");
  const allocs = (s3.allocations || []).map(a =>
    `<div class="plan-alloc"><span>${a.product_name}</span><span>${a.allocation_pct}%</span></div>`
  ).join("");
  const risks = (s4.risks || []).map(r => `<li>${r}</li>`).join("");
  const nudges = (s5.nudges || []).map(n => `<li>${n.message}</li>`).join("");
  container.innerHTML = `
    <div class="plan-section"><h3>Goals</h3>${goals || "<p>No goals</p>"}</div>
    <div class="plan-section"><h3>Allocation</h3>${allocs || "<p>No allocations</p>"}</div>
    <div class="plan-section"><h3>Red Team Risks</h3><ul>${risks}</ul></div>
    <div class="plan-section"><h3>Blue Team Nudges</h3><ul>${nudges}</ul></div>
  `;
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
  if (isDeep) {
    animateChainProgress();
  }

  const lang = detectLang(text);
  document.getElementById("lang-chip").textContent = lang === "hi" ? "HI" : "EN";

  try {
    if (!sessionId) await startSession();

    const data = await apiPost("/v1/conversation/message", {
      session_id: sessionId,
      message_text: text,
      mode: messageMode,
    });

    hideTyping();
    hideChainProgress();

    const replyText = data.reply_text;
    const rec = data.recommendation;
    const meta = data.chain_metadata;
    const voiceText = (data.avatar_script || replyText).replace(/\*\*|👋|📊|🎯|💡|📋|❌|⚠️|💰|🎉/g, "");

    appendBotMessage(replyText, rec);
    showAuditBadge(meta);

    if (meta && meta.plan_id && meta.path === "deep") {
      try {
        const planRes = await fetch(`${BACKEND_URL}/v1/wealth/plan/${meta.plan_id}`, {
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
    appendBotMessage("❌ Couldn't reach the backend. Is the FastAPI server running? (`uvicorn main:app --port 8000`)", null);
  }
}

function sendSuggestion(text) {
  document.getElementById("user_input").value = text;
  sendMessage();
}

// ---- Language detection ------------------------------------
function detectLang(text) {
  const lower = text.toLowerCase();
  
  // Devanagari script check
  if (/[\u0900-\u097F]/.test(text)) {
    return "hi";
  }
  
  // Common Hindi structural words
  const hindiKeywords = ["theek", "kya", "aap", "nahi", "hai", "hoon", "acha", "bol", "batao", "samjhao"];
  const matchesHindi = hindiKeywords.some(word => new RegExp(`\\b${word}\\b`, 'i').test(lower));
  if (matchesHindi) {
    return "hi";
  }
  
  // Roman Hindi "main" (I) vs English "main" context detection
  if (/\bmain\b/i.test(lower)) {
    const englishContext = ["account", "balance", "fund", "goal", "is", "my", "the", "portfolio", "card", "rate", "interest", "salary", "expense", "saving"];
    const matchesEnglish = englishContext.some(word => new RegExp(`\\b${word}\\b`, 'i').test(lower));
    if (!matchesEnglish) {
      return "hi"; // Roman Hindi context
    }
  }
  
  return "en";
}

// ---- Voice (mock – shows recording state) ------------------
function toggleVoice() {
  const btn = document.getElementById("mic-btn");
  if (!isRecording) {
    isRecording = true;
    btn.classList.add("recording");
    btn.textContent = "⏹️";
    document.getElementById("user_input").placeholder = "Listening…";
    // Simulate voice transcript after 2 seconds
    setTimeout(() => stopVoice("How am I doing this month?"), 2000);
  } else {
    stopVoice(null);
  }
}

// ---- Dynamic Dashboard Data Binding -----------------------
async function loadCustomerDashboard() {
  try {
    const res = await fetch(`${BACKEND_URL}/v1/customer/snapshot`, {
      headers: {
        Authorization: `Bearer ${DEMO_TOKEN}`,
      }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    customerSnapshot = await res.json();
    
    renderPortfolio(customerSnapshot);
    renderGoals(customerSnapshot);
    renderInsights(customerSnapshot);
  } catch (e) {
    console.warn("Failed to load customer snapshot for dashboard:", e);
  }
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount);
}

function renderPortfolio(snapshot) {
  const accounts = snapshot.accounts || [];
  let savings = 0;
  let fd = 0;
  let mf = 0;
  
  accounts.forEach(acc => {
    if (acc.type === "SAVINGS") savings += acc.balance || 0;
    else if (acc.type === "FD") fd += acc.balance || 0;
    else if (acc.type === "MF_SIP") mf += acc.balance || 0;
  });
  
  const total = savings + fd + mf;
  
  document.getElementById("portfolio-net-worth").textContent = formatCurrency(total);
  document.getElementById("portfolio-mf").textContent = formatCurrency(mf);
  document.getElementById("portfolio-fd").textContent = formatCurrency(fd);
  document.getElementById("portfolio-savings").textContent = formatCurrency(savings);
  
  const fdPct = total > 0 ? (fd / total) * 100 : 0;
  const mfPct = total > 0 ? (mf / total) * 100 : 0;
  const savPct = total > 0 ? (savings / total) * 100 : 0;
  
  const fdEl = document.getElementById("alloc-fd");
  const mfEl = document.getElementById("alloc-mf");
  const savEl = document.getElementById("alloc-savings");
  const otherEl = document.getElementById("alloc-other");
  
  if (fdEl) {
    fdEl.style.width = `${fdPct}%`;
    fdEl.textContent = `FD ${Math.round(fdPct)}%`;
    fdEl.title = `FD – ${Math.round(fdPct)}%`;
  }
  if (mfEl) {
    mfEl.style.width = `${mfPct}%`;
    mfEl.textContent = `MF ${Math.round(mfPct)}%`;
    mfEl.title = `MF – ${Math.round(mfPct)}%`;
  }
  if (savEl) {
    savEl.style.width = `${savPct}%`;
    savEl.textContent = `SAV ${Math.round(savPct)}%`;
    savEl.title = `Savings – ${Math.round(savPct)}%`;
  }
  if (otherEl) {
    otherEl.style.width = `0%`;
    otherEl.style.display = "none";
  }
}

function renderGoals(snapshot) {
  const goalsList = document.getElementById("goals-list");
  if (!goalsList) return;
  
  goalsList.innerHTML = "";
  const goals = snapshot.goals || [];
  
  goals.forEach(goal => {
    const target = goal.targetAmount || 1;
    const current = goal.currentAmount || 0;
    const pct = Math.min(100, Math.round((current / target) * 100));
    
    let isAtRisk = false;
    let statusText = "On Track";
    let statusClass = "on-track";
    
    if (goal.name === "Europe Vacation" && pct < 40) {
      isAtRisk = true;
      statusText = "At Risk";
      statusClass = "at-risk";
    }
    
    const card = document.createElement("div");
    card.className = "goal-card";
    
    let icon = "🎯";
    if (goal.name.includes("Car")) icon = "🚗";
    else if (goal.name.includes("Emergency")) icon = "🛡️";
    else if (goal.name.includes("Vacation") || goal.name.includes("Europe")) icon = "✈️";
    
    card.innerHTML = `
      <div class="goal-icon">${icon}</div>
      <div class="goal-info">
        <div class="goal-name">${goal.name}</div>
        <div class="goal-meta">Target: ${formatCurrency(target)} · Due: ${goal.targetDate || "N/A"}</div>
        <div class="goal-progress-bar">
          <div class="goal-progress-fill ${isAtRisk ? 'warning' : ''}" style="width: ${pct}%"></div>
        </div>
        <div class="goal-pct">${pct}% funded</div>
      </div>
      <div class="goal-status ${statusClass}">${statusText}</div>
    `;
    goalsList.appendChild(card);
  });
}

function renderInsights(snapshot) {
  const grid = document.getElementById("insights-grid");
  if (!grid) return;
  
  const transactions = snapshot.transactions || [];
  const spendsByMonthCat = {};
  
  transactions.forEach(tx => {
    const amount = parseFloat(tx.amount) || 0;
    const category = tx.category || "Other";
    const date = tx.date || "";
    if (amount < 0 && category !== "Investment") {
      const month = date.substring(0, 7);
      if (month) {
        if (!spendsByMonthCat[month]) spendsByMonthCat[month] = {};
        spendsByMonthCat[month][category] = (spendsByMonthCat[month][category] || 0) + Math.abs(amount);
      }
    }
  });
  
  const juneSpends = spendsByMonthCat["2026-06"] || {};
  const maySpends = spendsByMonthCat["2026-05"] || {};
  
  grid.innerHTML = "";
  
  // Render Dining Out Card
  const diningJune = juneSpends["Dining"] || 0;
  const diningMay = maySpends["Dining"] || 0;
  const diningDelta = Math.max(0, diningJune - diningMay);
  
  const diningCard = document.createElement("div");
  diningCard.className = "insight-card";
  diningCard.innerHTML = `
    <div class="insight-cat">🍽️ Dining Out (June)</div>
    <div class="insight-amount">${formatCurrency(diningJune)}</div>
    <div class="insight-change ${diningDelta > 0 ? 'up' : 'neutral'}">+${formatCurrency(diningDelta)} vs avg</div>
    <div class="insight-note">Mostly weekday lunches near office. 3rd week in a row.</div>
  `;
  grid.appendChild(diningCard);
  
  // Render Groceries Card
  const grocJune = juneSpends["Groceries"] || 0;
  const grocCard = document.createElement("div");
  grocCard.className = "insight-card";
  grocCard.innerHTML = `
    <div class="insight-cat">🛒 Groceries (June)</div>
    <div class="insight-amount">${formatCurrency(grocJune)}</div>
    <div class="insight-change neutral">On par with avg</div>
    <div class="insight-note">Consistent spending pattern. No action needed.</div>
  `;
  grid.appendChild(grocCard);
  
  // Render Utilities Card
  const utilJune = juneSpends["Utilities"] || 0;
  const utilCard = document.createElement("div");
  utilCard.className = "insight-card";
  utilCard.innerHTML = `
    <div class="insight-cat">🔌 Utilities (June)</div>
    <div class="insight-amount">${formatCurrency(utilJune)}</div>
    <div class="insight-change neutral">Consistent</div>
    <div class="insight-note">Routine household bill payments.</div>
  `;
  grid.appendChild(utilCard);
  
  // Render Transport Card
  const transJune = juneSpends["Transport"] || 0;
  const transMay = maySpends["Transport"] || 0;
  const transDelta = transMay - transJune;
  const transCard = document.createElement("div");
  transCard.className = "insight-card";
  transCard.innerHTML = `
    <div class="insight-cat">🚕 Transport (June)</div>
    <div class="insight-amount">${formatCurrency(transJune)}</div>
    <div class="insight-change ${transDelta > 0 ? 'down' : 'neutral'}">${transDelta > 0 ? '-' : ''}${formatCurrency(Math.abs(transDelta))} vs avg</div>
    <div class="insight-note">Good – possible savings from WFH days.</div>
  `;
  grid.appendChild(transCard);
  
  // Update savings rate panel dynamically
  let juneIncome = 0;
  let juneExpenses = 0;
  
  transactions.forEach(tx => {
    const amount = parseFloat(tx.amount) || 0;
    const date = tx.date || "";
    if (date.startsWith("2026-06")) {
      if (amount > 0) juneIncome += amount;
      else if (tx.category !== "Investment") juneExpenses += Math.abs(amount);
    }
  });
  
  if (juneIncome === 0) juneIncome = 58000;
  
  const savingsRate = juneIncome > 0 ? ((juneIncome - juneExpenses) / juneIncome) : 0.22;
  const savingsPct = Math.round(savingsRate * 100);
  
  const fill = document.getElementById("savings-rate-fill");
  const label = document.getElementById("savings-rate-label");
  if (fill) fill.style.width = `${savingsPct}%`;
  if (label) {
    label.innerHTML = `${savingsPct}% this month &nbsp;·&nbsp; avg 18% &nbsp;·&nbsp; <span style="color:var(--green)">↑ Good job!</span>`;
  }
}

function stopVoice(transcript) {
  isRecording = false;
  const btn = document.getElementById("mic-btn");
  btn.classList.remove("recording");
  btn.textContent = "🎤";
  document.getElementById("user_input").placeholder = "Ask Artha anything about your finances…";
  if (transcript) {
    document.getElementById("user_input").value = transcript;
    sendMessage();
  }
}

// ---- Enter key sends message --------------------------------
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("user_input").addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
  });
  startSession();
});
