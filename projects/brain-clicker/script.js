// === Состояние игры ===
let state = {
    brains: 10,
    totalClicks: 0,
    brainsPerClick: 1,
    brainsPerSec: 0,
    clickLevel: 1,
    passiveLevel: 0,
    implantLevel: 0,
    lang: 'ru',
    lastSeen: Date.now(),
    shadowSightings: 0,
    shadowDrops: 0,
    shadowFiguresSeen: {}
};

// === Языки ===
const translations = {
    ru: {
        scoreLabel: 'мозгов', clicksLabel: 'Кликов:', psecLabel: 'Мозгов/сек:',
        shopLabel: 'Магазин', shopHint: 'Магазин откроется позже', resetLabel: 'Сбросить прогресс',
        resetConfirm: 'Точно сбросить весь прогресс?', resetDone: 'Прогресс сброшен',
        offlineHint: 'Если уйдёте — я поработаю за вас! 🧠',
        offlineNotif: 'Привет! Тебя не было {time}. Я поработал вместо тебя!', offlineEarned: '+{brains} 🧠'
    },
    en: {
        scoreLabel: 'brains', clicksLabel: 'Clicks:', psecLabel: 'Brains/sec:',
        shopLabel: 'Shop', shopHint: 'Shop will open later', resetLabel: 'Reset progress',
        resetConfirm: 'Really reset all progress?', resetDone: 'Progress reset',
        offlineHint: "If you leave — I'll work for you! 🧠",
        offlineNotif: "Hey! You were away {time}. I worked for you!", offlineEarned: '+{brains} 🧠'
    }
};

// === Фразы-пасхалки ===
const teaserPhrases = {
    ru: ["Закрыто!", "Магазин спит 🧠", "Перестань нажимать!", "Скоро откроемся...", "Тук-тук! Кто там? Никого.", "Не сейчас, дружище!", "Мозги закончились на складе 🧠", "Может, лучше кликнешь?", "Магазин на обеде", "Продавец ушёл за кофе ☕", "Ещё не время...", "Терпение, юный нейроучёный", "Дверь закрыта 🔒", "Сначала заработай мозгов!", "Кликай дальше — откроемся", "Инвентарь пуст (пока что)", "Может, чай?", "Не тыкай — я живой!", "Купил бы... да нечего", "СКОРО™"],
    en: ["Closed!", "Shop is sleeping 🧠", "Stop clicking!", "We'll open soon...", "Knock-knock! Who's there? No one.", "Not now, buddy!", "Out of brains in stock 🧠", "Maybe just click instead?", "Shop is on lunch break", "The seller went for coffee ☕", "Not yet...", "Patience, young neuroscientist", "Door is locked 🔒", "Earn some brains first!", "Keep clicking — we'll open", "Inventory is empty (for now)", "Maybe some tea?", "Don't poke me — I'm alive!", "Would buy... but nothing here", "SOON™"]
};

// === ФИГУРЫ ТЕНИ ===
const shadowFigures = [
    { id: 'man-tall', label: 'Мужчина высокий', width: 55, height: 110, clip: `polygon(50% 0%, 60% 3%, 65% 12%, 60% 22%, 75% 32%, 85% 50%, 82% 65%, 72% 60%, 68% 100%, 58% 100%, 52% 70%, 48% 70%, 42% 100%, 32% 100%, 28% 60%, 18% 65%, 15% 50%, 25% 32%, 40% 22%, 35% 12%, 40% 3%)`, drops: [{ id: 'muscle', emoji: '💪', type: 'brains', minMult: 8, maxMult: 15 }, { id: 'stone', emoji: '🪨', type: 'boost', duration: 60000, multiplier: 2, flatBrains: 500 }, { id: 'hammer', emoji: '⚒', type: 'brains', minMult: 15, maxMult: 25 }, { id: 'shield', emoji: '🛡', type: 'brains', minMult: 5, maxMult: 10 }] },
    { id: 'woman-mid', label: 'Женщина средняя', width: 42, height: 95, clip: `polygon(50% 0%, 62% 4%, 68% 14%, 62% 24%, 64% 32%, 56% 34%, 58% 42%, 62% 58%, 56% 62%, 52% 100%, 48% 100%, 44% 62%, 38% 58%, 42% 42%, 44% 34%, 36% 32%, 38% 24%, 32% 14%, 38% 4%)`, drops: [{ id: 'crystal', emoji: '💎', type: 'brains', minMult: 10, maxMult: 20 }, { id: 'scroll', emoji: '📜', type: 'permanent', bonus: 5 }, { id: 'flower', emoji: '🌸', type: 'boost', duration: 30000, multiplier: 3, flatBrains: 300 }, { id: 'amulet', emoji: '🔮', type: 'brains', minMult: 8, maxMult: 18 }] },
    { id: 'child', label: 'Ребёнок', width: 35, height: 70, clip: `polygon(50% 0%, 65% 5%, 70% 18%, 65% 28%, 75% 38%, 82% 55%, 78% 70%, 65% 65%, 60% 100%, 55% 100%, 52% 72%, 48% 72%, 45% 100%, 40% 100%, 35% 65%, 22% 70%, 18% 55%, 25% 38%, 35% 28%, 30% 18%, 35% 5%)`, drops: [{ id: 'candy', emoji: '🍬', type: 'brains', minMult: 1, maxMult: 3 }, { id: 'toy', emoji: '🧸', type: 'brains', minMult: 2, maxMult: 5 }, { id: 'balloon', emoji: '🎈', type: 'boost', duration: 30000, multiplier: 1.5, flatBrains: 100 }, { id: 'lollipop', emoji: '🍭', type: 'brains', minMult: 1, maxMult: 4 }], surpriseDrop: { chance: 0.01, emoji: '🏆', type: 'legendary', bonus: 10 } }
];

const shadowPositions = [
    { id: 'top-left', x: 40, y: 40 }, { id: 'top-right', x: -100, y: 40 },
    { id: 'bottom-left', x: 40, y: -140 }, { id: 'bottom-right', x: -100, y: -140 },
    { id: 'left-middle', x: 40, y: 'middle' }, { id: 'right-middle', x: -100, y: 'middle' },
    { id: 'top-center', x: 'center', y: 40 }, { id: 'bottom-center', x: 'center', y: -140 }
];

let lastPhraseIndex = -1, lastShadowPosition = null, recentShadowPositions = [], recentShadowFigures = [], lastShadowSpawn = Date.now(), currentShadow = null;

// === Функция пересчета статов (Синергия) ===
function recalculateStats() {
    const mult = 1 + (state.implantLevel * 0.1);
    state.brainsPerClick = Math.floor((1 + state.clickLevel) * mult);
    state.brainsPerSec = (state.brainsPerClick * 0.5) * state.passiveLevel * mult;
}

// === Функции (Загрузка, Сохранение, UI) ===
function loadGame() {
    const saved = localStorage.getItem('brainClicker');
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            state = { ...state, ...parsed };
            if (!state.shadowFiguresSeen) state.shadowFiguresSeen = {};
        } catch (e) { console.error('Ошибка загрузки:', e); }
    }
    recalculateStats();

    let offlineEarned = 0, offlineSecCapped = 0;
    if (state.lastSeen && state.brainsPerSec > 0) {
        const now = Date.now();
        const offlineSec = Math.floor((now - state.lastSeen) / 1000);
        const cappedSec = Math.min(offlineSec, 18000);
        const earned = Math.floor(state.brainsPerSec * cappedSec * 1.1);
        if (earned > 0 && cappedSec > 30) { state.brains += earned; offlineEarned = earned; offlineSecCapped = cappedSec; }
    }
    applyLanguage(state.lang);
    updateUI();
    if (offlineEarned > 0) setTimeout(() => showOfflineNotification(offlineSecCapped, offlineEarned), 500);
    state.lastSeen = Date.now();
    saveGame();
}

function saveGame() { state.lastSeen = Date.now(); localStorage.setItem('brainClicker', JSON.stringify(state)); }

function updateUI() {
    document.getElementById('score').textContent = formatNumber(state.brains);
    document.getElementById('clicks').textContent = formatNumber(state.totalClicks);
    document.getElementById('per-sec').textContent = formatNumber(state.brainsPerSec);
}

function formatNumber(num) {
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return Math.floor(num);
}

function clickBrain(e) {
    state.brains += state.brainsPerClick;
    state.totalClicks += 1;
    updateUI(); saveGame();
    const scoreEl = document.getElementById('score');
    scoreEl.classList.add('bump');
    setTimeout(() => scoreEl.classList.remove('bump'), 100);
    spawnFloatingNumber(e, '+' + state.brainsPerClick);
}

function spawnFloatingNumber(e, text) {
    const container = document.querySelector('.brain-container');
    const rect = container.getBoundingClientRect();
    const el = document.createElement('div');
    el.className = 'floating-number'; el.textContent = text;
    let x = e && e.clientX ? e.clientX - rect.left : rect.width / 2;
    let y = e && e.clientY ? e.clientY - rect.top : rect.height / 2;
    x += (Math.random() - 0.5) * 40;
    el.style.left = x + 'px'; el.style.top = y + 'px';
    container.appendChild(el);
    setTimeout(() => el.remove(), 1000);
}

function showTeaser() {
    const phrases = teaserPhrases[state.lang];
    let index;
    do { index = Math.floor(Math.random() * phrases.length); } while (index === lastPhraseIndex && phrases.length > 1);
    lastPhraseIndex = index;
    const container = document.getElementById('teaser-container');
    const existing = container.querySelectorAll('.teaser-phrase');
    existing.forEach(el => { el.classList.add('floating-away'); setTimeout(() => el.remove(), 600); });
    const newPhrase = document.createElement('div');
    newPhrase.className = 'teaser-phrase'; newPhrase.textContent = phrases[index];
    container.appendChild(newPhrase);
    setTimeout(() => { if (newPhrase.parentElement) { newPhrase.classList.add('floating-away'); setTimeout(() => newPhrase.remove(), 600); } }, 2500);
}

function pickNewShadowPosition() {
    const available = shadowPositions.filter(pos => !recentShadowPositions.includes(pos.id));
    if (available.length < 2) { recentShadowPositions = []; return pickNewShadowPosition(); }
    const picked = available[Math.floor(Math.random() * available.length)];
    lastShadowPosition = picked; recentShadowPositions.push(picked.id);
    if (recentShadowPositions.length > 3) recentShadowPositions.shift();
    return picked;
}

function pickNewShadowFigure() {
    const available = shadowFigures.filter(fig => !recentShadowFigures.includes(fig.id));
    const pool = available.length > 0 ? available : shadowFigures;
    const picked = pool[Math.floor(Math.random() * pool.length)];
    recentShadowFigures.push(picked.id);
    if (recentShadowFigures.length > 1) recentShadowFigures.shift();
    return picked;
}

function spawnShadow() {
    if (currentShadow) { currentShadow.remove(); currentShadow = null; }
    const layer = document.getElementById('shadow-layer');
    const fig = document.createElement('div'); fig.className = 'shadow-figure';
    const pos = pickNewShadowPosition(); const figure = pickNewShadowFigure();
    state.shadowFiguresSeen[figure.id] = (state.shadowFiguresSeen[figure.id] || 0) + 1;
    fig.style.width = figure.width + 'px'; fig.style.height = figure.height + 'px';
    fig.style.clipPath = figure.clip; fig.style.webkitClipPath = figure.clip;
    const W = window.innerWidth, H = window.innerHeight;
    let left = pos.x === 'center' ? W / 2 - figure.width / 2 : (pos.x < 0 ? W + pos.x : pos.x);
    let top = pos.y === 'middle' ? H / 2 - figure.height / 2 : (pos.y < 0 ? H + pos.y : pos.y);
    fig.style.left = left + 'px'; fig.style.top = top + 'px'; fig.dataset.figureId = figure.id;
    layer.appendChild(fig); currentShadow = fig;
    setTimeout(() => fig.classList.add('visible'), 50);
    const hideTimeout = setTimeout(() => { if (fig.parentElement) { fig.classList.remove('visible'); setTimeout(() => fig.remove(), 800); currentShadow = null; } }, 30 * 60 * 1000);
    fig.addEventListener('click', () => { clearTimeout(hideTimeout); onShadowClick(fig, figure); });
}

function onShadowClick(fig, figure) {
    state.shadowSightings = (state.shadowSightings || 0) + 1; state.shadowDrops = (state.shadowDrops || 0) + 1;
    const drop = rollShadowDrop(figure);
    showDropAnimation(fig, drop); applyDrop(drop, figure);
    fig.classList.remove('visible'); setTimeout(() => fig.remove(), 600); currentShadow = null;
    saveGame();
}

function rollShadowDrop(figure) {
    if (figure.surpriseDrop && Math.random() < figure.surpriseDrop.chance) return { ...figure.surpriseDrop };
    const drop = { ...figure.drops[Math.floor(Math.random() * figure.drops.length)] };
    if (drop.type === 'brains') {
        const base = Math.max(50, state.brainsPerSec * 60 + state.brainsPerClick * 30);
        drop.brains = Math.floor(base * (drop.minMult + Math.random() * (drop.maxMult - drop.minMult)));
    }
    return drop;
}

function showDropAnimation(fig, drop) {
    const rect = fig.getBoundingClientRect(); const el = document.createElement('div');
    el.className = 'drop-item'; el.textContent = drop.emoji;
    el.style.left = (rect.left + rect.width / 2 - 24) + 'px'; el.style.top = (rect.top + rect.height / 2 - 24) + 'px';
    document.body.appendChild(el); setTimeout(() => el.remove(), 1500);
}

function applyDrop(drop, figure) {
    let message = '';
    if (drop.type === 'brains' && drop.brains) { state.brains += drop.brains; message = `${drop.emoji} +${formatNumber(drop.brains)} 🧠`; }
    else if (drop.type === 'boost') { if (drop.flatBrains) state.brains += drop.flatBrains; message = `${drop.emoji} x${drop.multiplier} на ${drop.duration / 1000} сек!`; }
    else if (drop.type === 'permanent') { state.brainsPerClick += drop.bonus; message = `${drop.emoji} +${drop.bonus} к клику навсегда!`; }
    else if (drop.type === 'legendary') { state.brainsPerClick += drop.bonus; message = `${drop.emoji} ЛЕГЕНДАРКА! +${drop.bonus} к клику навсегда!`; }
    updateUI(); showToast(message);
}

function showToast(text) {
    const toast = document.createElement('div'); toast.className = 'toast'; toast.textContent = text;
    document.body.appendChild(toast);
    setTimeout(() => { toast.classList.add('hiding'); setTimeout(() => toast.remove(), 500); }, 1800);
}

function showOfflineNotification(seconds, brains) {
    const mins = Math.floor(seconds / 60); const hrs = Math.floor(mins / 60);
    let timeStr = hrs > 0 ? `${hrs}ч ${mins % 60}м` : `${mins}м`;
    const t = translations[state.lang];
    const banner = document.createElement('div'); banner.className = 'offline-banner';
    banner.innerHTML = `<div class="offline-banner-main">🧠 ${t.offlineNotif.replace('{time}', timeStr)}</div><div class="offline-banner-earned">${t.offlineEarned.replace('{brains}', formatNumber(brains))}</div>`;
    document.body.appendChild(banner);
    setTimeout(() => { banner.classList.add('hiding'); setTimeout(() => banner.remove(), 500); }, 5000);
}

function applyLanguage(lang) {
    state.lang = lang; const t = translations[lang];
    document.getElementById('score-label').textContent = t.scoreLabel;
    document.getElementById('clicks-label').textContent = t.clicksLabel;
    document.getElementById('psec-label').textContent = t.psecLabel;
    document.getElementById('shop-label').textContent = t.shopLabel;
    if (document.getElementById('shop-hint')) document.getElementById('shop-hint').textContent = t.shopHint;
    document.getElementById('reset-label').textContent = t.resetLabel;
    document.getElementById('offline-hint-label').textContent = t.offlineHint;
    document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById('lang-' + lang).classList.add('active');
    saveGame();
}

function resetProgress() {
    const t = translations[state.lang];
    if (!confirm(t.resetConfirm)) return;
    state.brains = 10; state.totalClicks = 0; state.brainsPerClick = 1; state.brainsPerSec = 0;
    state.clickLevel = 1; state.passiveLevel = 0; state.implantLevel = 0;
    state.shadowSightings = 0; state.shadowDrops = 0; state.shadowFiguresSeen = {};
    recalculateStats();
    saveGame(); updateUI(); alert(t.resetDone);
}

// Привязка старых событий
document.getElementById('brain').addEventListener('click', clickBrain);
document.getElementById('reset').addEventListener('click', resetProgress);
document.getElementById('lang-ru').addEventListener('click', () => applyLanguage('ru'));
document.getElementById('lang-en').addEventListener('click', () => applyLanguage('en'));

window.addEventListener('beforeunload', () => { state.lastSeen = Date.now(); saveGame(); });
setInterval(saveGame, 10000);
setInterval(() => { if (Date.now() - lastShadowSpawn > 30 * 60 * 1000) { lastShadowSpawn = Date.now(); spawnShadow(); } }, 30000);

// === Тик пассивного дохода ===
setInterval(() => {
    if (state.brainsPerSec > 0) {
        state.brains += state.brainsPerSec;
        updateUI();
    }
}, 1000);

// === Запуск ===
loadGame();

// ==========================================
// МАГАЗИН И ПЕРЕТАСКИВАНИЕ
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    const shopWindow = document.getElementById('shop-window');
    const shopHeader = document.getElementById('shop-header');
    const shopClose = document.getElementById('shop-close');
    const openShopBtn = document.getElementById('open-shop-btn');

    if (!shopWindow || !shopHeader) return;

    // 1. Логика магазина
    const buyClickBtn = document.getElementById('buy-click');
    const clickLevelEl = document.getElementById('click-level');
    const buyPassiveBtn = document.getElementById('buy-passive');
    const passiveLevelEl = document.getElementById('passive-level');
    const buyImplantBtn = document.getElementById('buy-implant');
    const implantLevelEl = document.getElementById('implant-level');

    const MAX_CLICK_LEVEL = 50;
    const MAX_PASSIVE_LEVEL = 50;
    const MAX_IMPLANT_LEVEL = 20;

    function getClickCost(level) { return 10 + (level - 1) * 15; }
    function getPassiveCost(level) { return 100 + (level - 1) * 150; }
    function getImplantCost(level) { return 500 + (level * 1000); }

    function updateShopUI() {
        // Клик
        if (clickLevelEl && buyClickBtn) {
            const cost = getClickCost(state.clickLevel);
            if (state.clickLevel >= MAX_CLICK_LEVEL) {
                clickLevelEl.textContent = `МАКС (Ур. ${state.clickLevel})`;
                buyClickBtn.textContent = 'Максимум';
                buyClickBtn.disabled = true;
            } else {
                clickLevelEl.textContent = `Ур. ${state.clickLevel}`;
                buyClickBtn.textContent = `Купить (${formatNumber(cost)} 🧠)`;
                buyClickBtn.disabled = state.brains < cost;
            }
        }
        // Пассив (Нейро-сеть)
        if (passiveLevelEl && buyPassiveBtn) {
            const cost = getPassiveCost(state.passiveLevel);
            const perSec = (state.brainsPerClick * 0.5) * state.passiveLevel * (1 + state.implantLevel * 0.1);
            const perHour = Math.floor(perSec * 3600);

            if (state.passiveLevel >= MAX_PASSIVE_LEVEL) {
                passiveLevelEl.textContent = `МАКС (Ур. ${state.passiveLevel}) [${perHour}/ч]`;
                buyPassiveBtn.textContent = 'Максимум';
                buyPassiveBtn.disabled = true;
            } else {
                passiveLevelEl.textContent = `Ур. ${state.passiveLevel} (${formatNumber(perSec)}/сек)`;
                buyPassiveBtn.textContent = `Купить (${formatNumber(cost)} 🧠)`;
                buyPassiveBtn.disabled = state.brains < cost;
            }
        }
        // Имплант
        if (implantLevelEl && buyImplantBtn) {
            const cost = getImplantCost(state.implantLevel);
            const bonusPercent = state.implantLevel * 10;

            if (state.implantLevel >= MAX_IMPLANT_LEVEL) {
                implantLevelEl.textContent = `МАКС (Ур. ${state.implantLevel}) [+${bonusPercent}%]`;
                buyImplantBtn.textContent = 'Максимум';
                buyImplantBtn.disabled = true;
            } else {
                implantLevelEl.textContent = `Ур. ${state.implantLevel} (+${bonusPercent}%)`;
                buyImplantBtn.textContent = `Купить (${formatNumber(cost)} 🧠)`;
                buyImplantBtn.disabled = state.brains < cost;
            }
        }
    }

    setInterval(updateShopUI, 500);

    // --- ЛОГИКА ПОКУПОК ---
    if (buyClickBtn) {
        buyClickBtn.addEventListener('click', () => {
            const cost = getClickCost(state.clickLevel);
            if (state.brains >= cost && state.clickLevel < MAX_CLICK_LEVEL) {
                state.brains -= cost;
                state.clickLevel += 1;
                recalculateStats();
                updateUI(); saveGame(); updateShopUI();
            }
        });
    }

    if (buyPassiveBtn) {
        buyPassiveBtn.addEventListener('click', () => {
            const cost = getPassiveCost(state.passiveLevel);
            if (state.brains >= cost && state.passiveLevel < MAX_PASSIVE_LEVEL) {
                state.brains -= cost;
                state.passiveLevel += 1;
                recalculateStats();
                updateUI(); saveGame(); updateShopUI();
            }
        });
    }

    if (buyImplantBtn) {
        buyImplantBtn.addEventListener('click', () => {
            const cost = getImplantCost(state.implantLevel);
            if (state.brains >= cost && state.implantLevel < MAX_IMPLANT_LEVEL) {
                state.brains -= cost;
                state.implantLevel += 1;
                recalculateStats();
                updateUI(); saveGame(); updateShopUI();
            }
        });
    }

    // 2. Кнопка "Открыть магазин"
    if (openShopBtn) {
        openShopBtn.addEventListener('click', () => {
            shopWindow.style.display = 'flex';
            shopWindow.style.transform = 'translate(-50%, -50%)';
            shopWindow.style.left = '50%';
            shopWindow.style.top = '50%';
            localStorage.removeItem('shopLeft');
            localStorage.removeItem('shopTop');
        });
    }

    // 3. ФИЗИКА (УСИЛЕННАЯ + ДОЛГОЕ СКОЛЬЖЕНИЕ)
    let isDragging = false;
    let startX, startY, startLeft, startTop;
    let lastHitX = false, lastHitY = false;
    let velocityX = 0, velocityY = 0, lastMouseX = 0, lastMouseY = 0;
    let animationFrameId = null;
    let dragStartTime = 0;

    const friction = 0.975;
    const bounceForce = 0.95;

    const savedLeft = parseFloat(localStorage.getItem('shopLeft'));
    const savedTop = parseFloat(localStorage.getItem('shopTop'));

    shopWindow.style.display = 'flex';

    if (!isNaN(savedLeft) && !isNaN(savedTop)) {
        if (savedLeft >= 0 && savedLeft <= window.innerWidth - 100 && savedTop >= 0 && savedTop <= window.innerHeight - 100) {
            shopWindow.style.transform = 'none';
            shopWindow.style.left = savedLeft + 'px';
            shopWindow.style.top = savedTop + 'px';
        } else {
            localStorage.removeItem('shopLeft');
            localStorage.removeItem('shopTop');
        }
    }

    function triggerJelly(axis, x, y) {
        const animClass = axis === 'x' ? 'jelly-bounce-x' : 'jelly-bounce-y';
        shopWindow.classList.remove('jelly-bounce-x', 'jelly-bounce-y');
        void shopWindow.offsetWidth;
        shopWindow.classList.add(animClass);

        const texts = state.lang === 'en' ? ["Ouch!", "Hey!", "Oops!"] : ["Ай!", "Ой!", "Упс!"];
        const textEl = document.createElement('div');
        textEl.className = 'floating-text';
        textEl.textContent = texts[Math.floor(Math.random() * texts.length)];

        if (axis === 'x') {
            textEl.style.left = `${x + (x < window.innerWidth / 2 ? 60 : -60)}px`;
            textEl.style.top = `${y + 40}px`;
        } else {
            textEl.style.left = `${x + 60}px`;
            textEl.style.top = `${y + (y < window.innerHeight / 2 ? 60 : -60)}px`;
        }
        document.body.appendChild(textEl);
        setTimeout(() => textEl.remove(), 1000);
    }

    // --- ЗАКРЫТИЕ МАГАЗИНА (ЖЕСТКИЙ ФИКС) ---
    if (shopClose) {
        shopClose.addEventListener('mousedown', (e) => {
            e.preventDefault();
            e.stopPropagation();

            shopWindow.style.display = 'none';

            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
                animationFrameId = null;
            }
            velocityX = 0;
            velocityY = 0;
            isDragging = false;
        });
    }

    shopHeader.addEventListener('pointerdown', (e) => {
        if (e.button !== 0) return;

        // Если кликнули по крестику — не начинаем перетаскивание
        if (e.target.closest('#shop-close')) return;

        isDragging = true;
        dragStartTime = Date.now();

        if (animationFrameId) cancelAnimationFrame(animationFrameId);
        velocityX = 0; velocityY = 0; lastMouseX = e.clientX; lastMouseY = e.clientY;

        const rect = shopWindow.getBoundingClientRect();
        shopWindow.style.transform = 'none';
        shopWindow.style.left = rect.left + 'px'; shopWindow.style.top = rect.top + 'px';

        shopHeader.setPointerCapture(e.pointerId);
        startX = e.clientX; startY = e.clientY; startLeft = rect.left; startTop = rect.top;
        shopHeader.style.cursor = 'grabbing'; document.body.style.userSelect = 'none';
    });

    document.addEventListener('pointermove', (e) => {
        if (!isDragging) return;

        velocityX = (e.clientX - lastMouseX) * 1.8;
        velocityY = (e.clientY - lastMouseY) * 1.8;
        lastMouseX = e.clientX; lastMouseY = e.clientY;

        let dx = e.clientX - startX, dy = e.clientY - startY;
        let newLeft = startLeft + dx, newTop = startTop + dy;
        const windowWidth = shopWindow.offsetWidth, windowHeight = shopWindow.offsetHeight;
        const screenWidth = window.innerWidth, screenHeight = window.innerHeight;

        if (newLeft < 0) { newLeft = 0; if (!lastHitX) triggerJelly('x', 0, newTop); lastHitX = true; }
        else if (newLeft + windowWidth > screenWidth) { newLeft = screenWidth - windowWidth; if (!lastHitX) triggerJelly('x', newLeft, newTop); lastHitX = true; }
        else { lastHitX = false; }

        if (newTop < 0) { newTop = 0; if (!lastHitY) triggerJelly('y', newLeft, 0); lastHitY = true; }
        else if (newTop + windowHeight > screenHeight) { newTop = screenHeight - windowHeight; if (!lastHitY) triggerJelly('y', newLeft, newTop); lastHitY = true; }
        else { lastHitY = false; }

        shopWindow.style.left = `${newLeft}px`; shopWindow.style.top = `${newTop}px`;
    });

    document.addEventListener('pointerup', () => {
        if (!isDragging) return;
        isDragging = false;
        shopHeader.style.cursor = 'grab';
        document.body.style.userSelect = '';

        localStorage.setItem('shopLeft', parseFloat(shopWindow.style.left));
        localStorage.setItem('shopTop', parseFloat(shopWindow.style.top));

        const dragDuration = Date.now() - dragStartTime;

        if (dragDuration > 30 && (Math.abs(velocityX) > 0.5 || Math.abs(velocityY) > 0.5)) {
            animateInertia();
        } else {
            velocityX = 0; velocityY = 0;
        }
    });

    function animateInertia() {
        const windowWidth = shopWindow.offsetWidth, windowHeight = shopWindow.offsetHeight;
        const screenWidth = window.innerWidth, screenHeight = window.innerHeight;
        let currentLeft = parseFloat(shopWindow.style.left) || 0;
        let currentTop = parseFloat(shopWindow.style.top) || 0;

        velocityX *= friction;
        velocityY *= friction;

        currentLeft += velocityX; currentTop += velocityY;

        if (currentLeft < 0) { currentLeft = 0; velocityX *= -bounceForce; triggerJelly('x', 0, currentTop); }
        else if (currentLeft + windowWidth > screenWidth) { currentLeft = screenWidth - windowWidth; velocityX *= -bounceForce; triggerJelly('x', currentLeft, currentTop); }

        if (currentTop < 0) { currentTop = 0; velocityY *= -bounceForce; triggerJelly('y', currentLeft, 0); }
        else if (currentTop + windowHeight > screenHeight) { currentTop = screenHeight - windowHeight; velocityY *= -bounceForce; triggerJelly('y', currentLeft, currentTop); }

        shopWindow.style.left = `${currentLeft}px`; shopWindow.style.top = `${currentTop}px`;

        if (Math.abs(velocityX) > 0.02 || Math.abs(velocityY) > 0.02) {
            animationFrameId = requestAnimationFrame(animateInertia);
        } else {
            velocityX = 0; velocityY = 0;
            localStorage.setItem('shopLeft', parseFloat(shopWindow.style.left));
            localStorage.setItem('shopTop', parseFloat(shopWindow.style.top));
        }
    }
});