// === Состояние игры ===
let state = {
    brains: 0,
    totalClicks: 0,
    brainsPerClick: 1,
    brainsPerSec: 0,
    lang: 'ru',
    lastSeen: Date.now(),
    shadowSightings: 0,
    shadowDrops: 0,
    shadowFiguresSeen: {} // сколько раз встречал каждую фигуру
};

// === Языки ===
const translations = {
    ru: {
        scoreLabel: 'мозгов',
        clicksLabel: 'Кликов:',
        psecLabel: 'Мозгов/сек:',
        shopLabel: 'Магазин',
        shopHint: 'Магазин откроется позже',
        resetLabel: 'Сбросить прогресс',
        resetConfirm: 'Точно сбросить весь прогресс?',
        resetDone: 'Прогресс сброшен',
        offlineHint: 'Если уйдёте — я поработаю за вас! 🧠',
        offlineNotif: 'Привет! Тебя не было {time}. Я поработал вместо тебя!',
        offlineEarned: '+{brains} 🧠'
    },
    en: {
        scoreLabel: 'brains',
        clicksLabel: 'Clicks:',
        psecLabel: 'Brains/sec:',
        shopLabel: 'Shop',
        shopHint: 'Shop will open later',
        resetLabel: 'Reset progress',
        resetConfirm: 'Really reset all progress?',
        resetDone: 'Progress reset',
        offlineHint: "If you leave — I'll work for you! 🧠",
        offlineNotif: "Hey! You were away {time}. I worked for you!",
        offlineEarned: '+{brains} 🧠'
    }
};

// === Фразы-пасхалки ===
const teaserPhrases = {
    ru: [
        "Закрыто!", "Магазин спит 🧠", "Перестань нажимать!",
        "Скоро откроемся...", "Тук-тук! Кто там? Никого.",
        "Не сейчас, дружище!", "Мозги закончились на складе 🧠",
        "Может, лучше кликнешь?", "Магазин на обеде",
        "Продавец ушёл за кофе ☕", "Ещё не время...",
        "Терпение, юный нейроучёный", "Дверь закрыта 🔒",
        "Сначала заработай мозгов!", "Кликай дальше — откроемся",
        "Инвентарь пуст (пока что)", "Может, чай?",
        "Не тыкай — я живой!", "Купил бы... да нечего", "СКОРО™"
    ],
    en: [
        "Closed!", "Shop is sleeping 🧠", "Stop clicking!",
        "We'll open soon...", "Knock-knock! Who's there? No one.",
        "Not now, buddy!", "Out of brains in stock 🧠",
        "Maybe just click instead?", "Shop is on lunch break",
        "The seller went for coffee ☕", "Not yet...",
        "Patience, young neuroscientist", "Door is locked 🔒",
        "Earn some brains first!", "Keep clicking — we'll open",
        "Inventory is empty (for now)", "Maybe some tea?",
        "Don't poke me — I'm alive!", "Would buy... but nothing here", "SOON™"
    ]
};

// === ФИГУРЫ ТЕНИ ===
const shadowFigures = [
    {
        id: 'man-tall',
        label: 'Мужчина высокий',
        width: 55,
        height: 110,
        clip: `polygon(
            50% 0%, 60% 3%, 65% 12%, 60% 22%, 75% 32%,
            85% 50%, 82% 65%, 72% 60%, 68% 100%,
            58% 100%, 52% 70%, 48% 70%, 42% 100%,
            32% 100%, 28% 60%, 18% 65%, 15% 50%,
            25% 32%, 40% 22%, 35% 12%, 40% 3%
        )`,
        drops: [
            { id: 'muscle', emoji: '💪', type: 'brains', minMult: 8, maxMult: 15 },
            { id: 'stone', emoji: '🪨', type: 'boost', duration: 60000, multiplier: 2, flatBrains: 500 },
            { id: 'hammer', emoji: '⚒', type: 'brains', minMult: 15, maxMult: 25 },
            { id: 'shield', emoji: '🛡', type: 'brains', minMult: 5, maxMult: 10 }
        ]
    },
    {
        id: 'woman-mid',
        label: 'Женщина средняя',
        width: 42,
        height: 95,
        clip: `polygon(
            50% 0%, 62% 4%, 68% 14%, 62% 24%, 64% 32%,
            56% 34%, 58% 42%, 62% 58%, 56% 62%,
            52% 100%, 48% 100%, 44% 62%, 38% 58%,
            42% 42%, 44% 34%, 36% 32%, 38% 24%,
            32% 14%, 38% 4%
        )`,
        drops: [
            { id: 'crystal', emoji: '💎', type: 'brains', minMult: 10, maxMult: 20 },
            { id: 'scroll', emoji: '📜', type: 'permanent', bonus: 5 },
            { id: 'flower', emoji: '🌸', type: 'boost', duration: 30000, multiplier: 3, flatBrains: 300 },
            { id: 'amulet', emoji: '🔮', type: 'brains', minMult: 8, maxMult: 18 }
        ]
    },
    {
        id: 'child',
        label: 'Ребёнок',
        width: 35,
        height: 70,
        clip: `polygon(
            50% 0%, 65% 5%, 70% 18%, 65% 28%, 75% 38%,
            82% 55%, 78% 70%, 65% 65%, 60% 100%,
            55% 100%, 52% 72%, 48% 72%, 45% 100%,
            40% 100%, 35% 65%, 22% 70%, 18% 55%,
            25% 38%, 35% 28%, 30% 18%, 35% 5%
        )`,
        drops: [
            { id: 'candy', emoji: '🍬', type: 'brains', minMult: 1, maxMult: 3 },
            { id: 'toy', emoji: '🧸', type: 'brains', minMult: 2, maxMult: 5 },
            { id: 'balloon', emoji: '🎈', type: 'boost', duration: 30000, multiplier: 1.5, flatBrains: 100 },
            { id: 'lollipop', emoji: '🍭', type: 'brains', minMult: 1, maxMult: 4 }
        ],
        // Сюрприз — 1% шанс на легендарку
        surpriseDrop: {
            chance: 0.01,
            emoji: '🏆',
            type: 'legendary',
            bonus: 10
        }
    }
];

// === Позиции тени ===
const shadowPositions = [
    { id: 'top-left', x: 40, y: 40 },
    { id: 'top-right', x: -100, y: 40 },
    { id: 'bottom-left', x: 40, y: -140 },
    { id: 'bottom-right', x: -100, y: -140 },
    { id: 'left-middle', x: 40, y: 'middle' },
    { id: 'right-middle', x: -100, y: 'middle' },
    { id: 'top-center', x: 'center', y: 40 },
    { id: 'bottom-center', x: 'center', y: -140 }
];

// === Состояние фраз и тени ===
let lastPhraseIndex = -1;
let lastShadowPosition = null;
let recentShadowPositions = [];
let recentShadowFigures = [];
let lastShadowSpawn = Date.now();
let currentShadow = null;

// === Загрузка из localStorage ===
function loadGame() {
    const saved = localStorage.getItem('brainClicker');
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            state = { ...state, ...parsed };
            // Миграция для старых сейвов
            if (!state.shadowFiguresSeen) state.shadowFiguresSeen = {};
        } catch (e) {
            console.error('Ошибка загрузки:', e);
        }
    }

    // === Считаем оффлайн-доход ===
    let offlineEarned = 0;
    let offlineSecCapped = 0;

    if (state.lastSeen && state.brainsPerSec > 0) {
        const now = Date.now();
        const offlineSec = Math.floor((now - state.lastSeen) / 1000);
        const cappedSec = Math.min(offlineSec, 18000); // макс 5 часов
        const earned = Math.floor(state.brainsPerSec * cappedSec * 1.1); // x1.1 подкрутка

        if (earned > 0 && cappedSec > 30) {
            state.brains += earned;
            offlineEarned = earned;
            offlineSecCapped = cappedSec;
        }
    }

    applyLanguage(state.lang);
    updateUI();

    // Показываем уведомление оффлайна
    if (offlineEarned > 0) {
        setTimeout(() => {
            showOfflineNotification(offlineSecCapped, offlineEarned);
        }, 500);
    }

    // Сброс lastSeen
    state.lastSeen = Date.now();
    saveGame();
}

// === Сохранение ===
function saveGame() {
    state.lastSeen = Date.now();
    localStorage.setItem('brainClicker', JSON.stringify(state));
}

// === Обновление интерфейса ===
function updateUI() {
    document.getElementById('score').textContent = formatNumber(state.brains);
    document.getElementById('clicks').textContent = formatNumber(state.totalClicks);
    document.getElementById('per-sec').textContent = formatNumber(state.brainsPerSec);
}

// === Форматирование чисел ===
function formatNumber(num) {
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return Math.floor(num);
}

// === Клик по мозгу ===
function clickBrain(e) {
    state.brains += state.brainsPerClick;
    state.totalClicks += 1;
    updateUI();
    saveGame();

    const scoreEl = document.getElementById('score');
    scoreEl.classList.add('bump');
    setTimeout(() => scoreEl.classList.remove('bump'), 100);

    spawnFloatingNumber(e, '+' + state.brainsPerClick);
}

// === Всплывающее число ===
function spawnFloatingNumber(e, text) {
    const container = document.querySelector('.brain-container');
    const rect = container.getBoundingClientRect();

    const el = document.createElement('div');
    el.className = 'floating-number';
    el.textContent = text;

    let x, y;
    if (e && e.clientX) {
        x = e.clientX - rect.left;
        y = e.clientY - rect.top;
    } else {
        x = rect.width / 2;
        y = rect.height / 2;
    }
    x += (Math.random() - 0.5) * 40;

    el.style.left = x + 'px';
    el.style.top = y + 'px';

    container.appendChild(el);
    setTimeout(() => el.remove(), 1000);
}

// === Показ фразы-пасхалки ===
function showTeaser() {
    const phrases = teaserPhrases[state.lang];
    let index;
    do {
        index = Math.floor(Math.random() * phrases.length);
    } while (index === lastPhraseIndex && phrases.length > 1);

    lastPhraseIndex = index;
    const phrase = phrases[index];

    const container = document.getElementById('teaser-container');
    const existing = container.querySelectorAll('.teaser-phrase');
    existing.forEach(el => {
        el.classList.add('floating-away');
        setTimeout(() => el.remove(), 600);
    });

    const newPhrase = document.createElement('div');
    newPhrase.className = 'teaser-phrase';
    newPhrase.textContent = phrase;
    container.appendChild(newPhrase);

    setTimeout(() => {
        if (newPhrase.parentElement) {
            newPhrase.classList.add('floating-away');
            setTimeout(() => newPhrase.remove(), 600);
        }
    }, 2500);
}

// === Тень ===
function pickNewShadowPosition() {
    const available = shadowPositions.filter(pos => {
        if (recentShadowPositions.includes(pos.id)) return false;
        return true;
    });

    if (available.length < 2) {
        recentShadowPositions = [];
        return pickNewShadowPosition();
    }

    const picked = available[Math.floor(Math.random() * available.length)];
    lastShadowPosition = picked;
    recentShadowPositions.push(picked.id);
    if (recentShadowPositions.length > 3) {
        recentShadowPositions.shift();
    }
    return picked;
}

function pickNewShadowFigure() {
    // Не повторять последние 1-2 фигуры
    const available = shadowFigures.filter(fig => {
        if (recentShadowFigures.includes(fig.id)) return false;
        return true;
    });

    const pool = available.length > 0 ? available : shadowFigures;
    const picked = pool[Math.floor(Math.random() * pool.length)];

    recentShadowFigures.push(picked.id);
    if (recentShadowFigures.length > 1) {
        recentShadowFigures.shift();
    }
    return picked;
}

function spawnShadow() {
    if (currentShadow) {
        currentShadow.remove();
        currentShadow = null;
    }

    const layer = document.getElementById('shadow-layer');
    const fig = document.createElement('div');
    fig.className = 'shadow-figure';

    const pos = pickNewShadowPosition();
    const figure = pickNewShadowFigure();

    // Записываем фигуру в статистику
    state.shadowFiguresSeen[figure.id] = (state.shadowFiguresSeen[figure.id] || 0) + 1;

    // Размеры и форма
    fig.style.width = figure.width + 'px';
    fig.style.height = figure.height + 'px';
    fig.style.clipPath = figure.clip;
    fig.style.webkitClipPath = figure.clip; // Safari

    // Позиция
    const W = window.innerWidth;
    const H = window.innerHeight;

    let left, top;
    if (pos.x === 'center') left = W / 2 - figure.width / 2;
    else if (pos.x < 0) left = W + pos.x;
    else left = pos.x;

    if (pos.y === 'middle') top = H / 2 - figure.height / 2;
    else if (pos.y < 0) top = H + pos.y;
    else top = pos.y;

    fig.style.left = left + 'px';
    fig.style.top = top + 'px';
    fig.dataset.figureId = figure.id;

    layer.appendChild(fig);
    currentShadow = fig;

    setTimeout(() => fig.classList.add('visible'), 50);

    const hideTimeout = setTimeout(() => {
        if (fig.parentElement) {
            fig.classList.remove('visible');
            setTimeout(() => fig.remove(), 800);
            currentShadow = null;
        }
    }, 30 * 60 * 1000); // ждёт 30 минут

    fig.addEventListener('click', () => {
        clearTimeout(hideTimeout);
        onShadowClick(fig, figure);
    });
}

function onShadowClick(fig, figure) {
    state.shadowSightings = (state.shadowSightings || 0) + 1;
    state.shadowDrops = (state.shadowDrops || 0) + 1;

    const drop = rollShadowDrop(figure);
    showDropAnimation(fig, drop);
    applyDrop(drop, figure);

    fig.classList.remove('visible');
    setTimeout(() => fig.remove(), 600);
    currentShadow = null;

    saveGame();
}

function rollShadowDrop(figure) {
    // Проверяем сюрприз (для ребёнка)
    if (figure.surpriseDrop && Math.random() < figure.surpriseDrop.chance) {
        return { ...figure.surpriseDrop };
    }

    // Случайный дроп из списка
    const drop = { ...figure.drops[Math.floor(Math.random() * figure.drops.length)] };

    // Рассчитываем сумму для brain-дропов
    if (drop.type === 'brains') {
        const base = Math.max(50, state.brainsPerSec * 60 + state.brainsPerClick * 30);
        drop.brains = Math.floor(base * (drop.minMult + Math.random() * (drop.maxMult - drop.minMult)));
    }

    return drop;
}

function showDropAnimation(fig, drop) {
    const rect = fig.getBoundingClientRect();
    const el = document.createElement('div');
    el.className = 'drop-item';
    el.textContent = drop.emoji;

    el.style.left = (rect.left + rect.width / 2 - 24) + 'px';
    el.style.top = (rect.top + rect.height / 2 - 24) + 'px';

    document.body.appendChild(el);
    setTimeout(() => el.remove(), 1500);
}

function applyDrop(drop, figure) {
    let message = '';

    if (drop.type === 'brains' && drop.brains) {
        state.brains += drop.brains;
        message = `${drop.emoji} +${formatNumber(drop.brains)} 🧠`;
    } else if (drop.type === 'boost') {
        if (drop.flatBrains) state.brains += drop.flatBrains;
        message = `${drop.emoji} x${drop.multiplier} на ${drop.duration / 1000} сек!`;
    } else if (drop.type === 'permanent') {
        state.brainsPerClick += drop.bonus;
        message = `${drop.emoji} +${drop.bonus} к клику навсегда!`;
    } else if (drop.type === 'legendary') {
        state.brainsPerClick += drop.bonus;
        message = `${drop.emoji} ЛЕГЕНДАРКА! +${drop.bonus} к клику навсегда!`;
    }

    updateUI();
    showToast(message);
}

function showToast(text) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = text;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 500);
    }, 1800);
}

// === Уведомление об оффлайне ===
function showOfflineNotification(seconds, brains) {
    const mins = Math.floor(seconds / 60);
    const hrs = Math.floor(mins / 60);
    let timeStr;
    if (hrs > 0) {
        timeStr = `${hrs}ч ${mins % 60}м`;
    } else {
        timeStr = `${mins}м`;
    }

    const t = translations[state.lang];
    const mainText = t.offlineNotif.replace('{time}', timeStr);
    const earnedText = t.offlineEarned.replace('{brains}', formatNumber(brains));

    const banner = document.createElement('div');
    banner.className = 'offline-banner';
    banner.innerHTML = `
        <div class="offline-banner-main">🧠 ${mainText}</div>
        <div class="offline-banner-earned">${earnedText}</div>
    `;
    document.body.appendChild(banner);

    setTimeout(() => {
        banner.classList.add('hiding');
        setTimeout(() => banner.remove(), 500);
    }, 5000);
}

// === Применение языка ===
function applyLanguage(lang) {
    state.lang = lang;
    const t = translations[lang];

    document.getElementById('score-label').textContent = t.scoreLabel;
    document.getElementById('clicks-label').textContent = t.clicksLabel;
    document.getElementById('psec-label').textContent = t.psecLabel;
    document.getElementById('shop-label').textContent = t.shopLabel;
    document.getElementById('shop-hint').textContent = t.shopHint;
    document.getElementById('reset-label').textContent = t.resetLabel;
    document.getElementById('offline-hint-label').textContent = t.offlineHint;

    document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById('lang-' + lang).classList.add('active');

    saveGame();
}

// === Сброс прогресса ===
function resetProgress() {
    const t = translations[state.lang];
    if (!confirm(t.resetConfirm)) return;

    state.brains = 0;
    state.totalClicks = 0;
    state.brainsPerClick = 1;
    state.brainsPerSec = 0;
    state.shadowSightings = 0;
    state.shadowDrops = 0;
    state.shadowFiguresSeen = {};

    saveGame();
    updateUI();
    alert(t.resetDone);
}

// === Привязка событий ===
document.getElementById('brain').addEventListener('click', clickBrain);
document.getElementById('shop').addEventListener('click', showTeaser);
document.getElementById('reset').addEventListener('click', resetProgress);
document.getElementById('lang-ru').addEventListener('click', () => applyLanguage('ru'));
document.getElementById('lang-en').addEventListener('click', () => applyLanguage('en'));

// === Сохранение при уходе ===
window.addEventListener('beforeunload', () => {
    state.lastSeen = Date.now();
    saveGame();
});

// === Автосохранение ===
setInterval(saveGame, 10000);

// === Проверка тени (раз в 30 сек) ===
setInterval(() => {
    if (Date.now() - lastShadowSpawn > 30 * 60 * 1000) {
        lastShadowSpawn = Date.now();
        spawnShadow();
    }
}, 30000);

// === Запуск ===
loadGame();

