/**
 * LoveRoutes - Romantic Travel App JavaScript
 * Full client-side functionality matching the React version
 */

// App State
let currentUser = null;
let currentCity = null;
let currentCityName = '';
let places = [];
let currentPlaceIndex = 0;
let isLoading = false;

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
    setupEventListeners();
});

// Event Listeners Setup
function setupEventListeners() {
    // Auth tab switching
    document.querySelectorAll('.auth-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            switchAuthTab(this.dataset.tab);
        });
    });

    // Form submissions
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);

    // Modal close events
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            hideAuth();
            hideInfo();
        }
    });

    // Keyboard events
    document.addEventListener('keydown', function(e) {
        if (getCurrentScreen() === 'swipeScreen') {
            if (e.key === 'ArrowLeft' || e.key === 'x') {
                skipPlace();
            } else if (e.key === 'ArrowRight' || e.key === ' ') {
                likePlace();
            } else if (e.key === 'i') {
                showPlaceInfo();
            }
        } else if (e.key === 'Escape') {
            hideAuth();
            hideInfo();
        }
    });
}

// Authentication Functions
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/current-user');
        if (response.ok) {
            const user = await response.json();
            currentUser = user;
            updateUserInfo();
            
            if (user.selectedCity) {
                currentCity = user.selectedCity;
                // Find city name
                const cityData = await fetch('/api/cities').then(r => r.json());
                const city = cityData.find(c => c.id === currentCity);
                currentCityName = city ? city.name : currentCity;
                
                showScreen('swipeScreen');
                loadPlaces();
            } else {
                showScreen('cityScreen');
            }
        } else {
            showScreen('landingScreen');
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        showScreen('landingScreen');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    if (isLoading) return;
    
    const formData = new FormData(e.target);
    const data = {
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    setLoading(true);
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            currentUser = result.user;
            updateUserInfo();
            hideAuth();
            
            if (result.user.selectedCity) {
                currentCity = result.user.selectedCity;
                // Find city name
                const cityData = await fetch('/api/cities').then(r => r.json());
                const city = cityData.find(c => c.id === currentCity);
                currentCityName = city ? city.name : currentCity;
                
                showScreen('swipeScreen');
                loadPlaces();
            } else {
                showScreen('cityScreen');
            }
        } else {
            alert(result.message || 'Ошибка входа');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Ошибка соединения');
    }
    setLoading(false);
}

async function handleRegister(e) {
    e.preventDefault();
    if (isLoading) return;
    
    const formData = new FormData(e.target);
    const data = {
        firstName: formData.get('firstName'),
        lastName: formData.get('lastName'),
        email: formData.get('email'),
        password: formData.get('password'),
        selectedCity: formData.get('selectedCity')
    };
    
    setLoading(true);
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            currentUser = result.user;
            currentCity = result.user.selectedCity;
            
            // Find city name
            const cityData = await fetch('/api/cities').then(r => r.json());
            const city = cityData.find(c => c.id === currentCity);
            currentCityName = city ? city.name : currentCity;
            
            updateUserInfo();
            hideAuth();
            showScreen('swipeScreen');
            loadPlaces();
        } else {
            alert(result.message || 'Ошибка регистрации');
        }
    } catch (error) {
        console.error('Register error:', error);
        alert('Ошибка соединения');
    }
    setLoading(false);
}

async function logout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        currentUser = null;
        currentCity = null;
        currentCityName = '';
        places = [];
        currentPlaceIndex = 0;
        
        updateUserInfo();
        showScreen('landingScreen');
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// City Selection
async function selectCity(cityId, cityName) {
    currentCity = cityId;
    currentCityName = cityName;
    showScreen('swipeScreen');
    loadPlaces();
}

// Places Loading
async function loadPlaces() {
    if (!currentCity) return;
    
    const cardStack = document.getElementById('cardStack');
    cardStack.innerHTML = '<div class="loading">Загружаем места...</div>';
    
    try {
        const response = await fetch(`/api/places?cityId=${currentCity}`);
        if (!response.ok) throw new Error('Failed to load places');
        
        places = await response.json();
        currentPlaceIndex = 0;
        
        updateCityInfo();
        displayCurrentPlace();
    } catch (error) {
        console.error('Failed to load places:', error);
        cardStack.innerHTML = '<div class="loading">Ошибка загрузки мест</div>';
    }
}

function updateCityInfo() {
    const cityNameEl = document.getElementById('currentCityName');
    const placeCounterEl = document.getElementById('placeCounter');
    
    if (cityNameEl) cityNameEl.textContent = `Романтические места • ${currentCityName}`;
    if (placeCounterEl) {
        placeCounterEl.textContent = `Место ${currentPlaceIndex + 1} из ${places.length}`;
    }
}

function displayCurrentPlace() {
    const cardStack = document.getElementById('cardStack');
    
    if (currentPlaceIndex >= places.length) {
        cardStack.innerHTML = `
            <div class="loading">
                <div style="font-size: 48px; margin-bottom: 20px;">🎉</div>
                <h3>Все места просмотрены!</h3>
                <p>Вы посмотрели все романтические места в ${currentCityName}</p>
                <button onclick="showCitySelection()" style="margin-top: 20px; padding: 12px 24px; background: var(--gradient-primary); color: white; border: none; border-radius: 8px; cursor: pointer;">
                    Выбрать другой город
                </button>
            </div>
        `;
        return;
    }
    
    const place = places[currentPlaceIndex];
    updateCityInfo();
    
    cardStack.innerHTML = `
        <div class="place-card" id="currentCard">
            <div class="place-image">
                <img src="${place.image_url}" alt="${place.name}" 
                     onerror="this.style.display='none'; this.parentNode.innerHTML='<div style=\\'padding: 40px; text-align: center; color: white;\\'><div style=\\'font-size: 48px; margin-bottom: 16px;\\'>📍</div><h3>${place.name}</h3></div>'">
            </div>
            <div class="place-content">
                <h2 class="place-title">${place.name}</h2>
                <p class="place-description">${place.excerpt}</p>
                <div class="place-tags">
                    ${place.tags ? place.tags.map(tag => `<span class="place-tag">#${tag}</span>`).join('') : '<span class="place-tag">#романтика</span>'}
                </div>
            </div>
        </div>
    `;
    
    // Add swipe functionality
    addSwipeListeners();
}

// Swipe Actions
async function likePlace() {
    if (currentPlaceIndex >= places.length) return;
    
    const place = places[currentPlaceIndex];
    
    // Record choice
    await recordChoice(place.id, 'like');
    
    // Show feedback
    showSwipeFeedback('like');
    
    // Move to next place
    setTimeout(() => {
        currentPlaceIndex++;
        displayCurrentPlace();
    }, 500);
}

async function skipPlace() {
    if (currentPlaceIndex >= places.length) return;
    
    const place = places[currentPlaceIndex];
    
    // Record choice
    await recordChoice(place.id, 'skip');
    
    // Show feedback
    showSwipeFeedback('skip');
    
    // Move to next place
    setTimeout(() => {
        currentPlaceIndex++;
        displayCurrentPlace();
    }, 500);
}

function showPlaceInfo() {
    if (currentPlaceIndex >= places.length) return;
    
    const place = places[currentPlaceIndex];
    const infoContent = document.getElementById('placeInfoContent');
    
    infoContent.innerHTML = `
        <div style="text-align: center; margin-bottom: 20px;">
            <div class="heart-logo small" style="margin: 0 auto 16px;">♥</div>
            <h3 style="font-size: 24px; font-weight: 700; margin-bottom: 8px;">${place.name}</h3>
            <p style="color: var(--gray-600); margin-bottom: 20px;">${currentCityName}</p>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h4 style="font-weight: 600; margin-bottom: 8px; color: var(--black-bean);">Описание</h4>
            <p style="line-height: 1.6; color: var(--gray-600);">${place.excerpt}</p>
        </div>
        
        ${place.tags ? `
            <div style="margin-bottom: 20px;">
                <h4 style="font-weight: 600; margin-bottom: 12px; color: var(--black-bean);">Теги</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    ${place.tags.map(tag => `<span class="place-tag">#${tag}</span>`).join('')}
                </div>
            </div>
        ` : ''}
        
        <div style="margin-bottom: 20px;">
            <h4 style="font-weight: 600; margin-bottom: 8px; color: var(--black-bean);">Источник изображения</h4>
            <p style="font-size: 14px; color: var(--gray-500);">${place.image_attribution || 'Wikimedia Commons'}</p>
        </div>
        
        <div style="display: flex; gap: 12px; margin-top: 30px;">
            <button onclick="skipPlace(); hideInfo();" style="flex: 1; padding: 12px; background: var(--gray-200); color: var(--gray-600); border: none; border-radius: 8px; cursor: pointer;">
                Пропустить
            </button>
            <button onclick="likePlace(); hideInfo();" style="flex: 1; padding: 12px; background: var(--gradient-primary); color: white; border: none; border-radius: 8px; cursor: pointer;">
                Нравится ♥
            </button>
        </div>
    `;
    
    showModal('infoModal');
}

async function recordChoice(placeId, choice) {
    if (!currentUser) return;
    
    try {
        await fetch('/api/choices', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                placeId: placeId,
                cityId: currentCity,
                choice: choice
            })
        });
    } catch (error) {
        console.error('Failed to record choice:', error);
    }
}

function showSwipeFeedback(type) {
    const card = document.getElementById('currentCard');
    if (!card) return;
    
    // Create indicator
    const indicator = document.createElement('div');
    indicator.className = `swipe-indicator ${type}`;
    indicator.textContent = type === 'like' ? '♥ НРАВИТСЯ' : '✕ ПРОПУСК';
    
    card.appendChild(indicator);
    
    // Show and animate
    requestAnimationFrame(() => {
        indicator.style.opacity = '1';
        card.style.transform = `translateX(${type === 'like' ? '100px' : '-100px'}) rotate(${type === 'like' ? '15deg' : '-15deg'})`;
        card.style.opacity = '0.7';
    });
}

// Swipe Touch Handling
function addSwipeListeners() {
    const card = document.getElementById('currentCard');
    if (!card) return;
    
    let startX = 0;
    let startY = 0;
    let currentX = 0;
    let currentY = 0;
    let isDragging = false;
    
    const handleStart = (e) => {
        isDragging = true;
        card.classList.add('dragging');
        
        const touch = e.touches ? e.touches[0] : e;
        startX = touch.clientX;
        startY = touch.clientY;
    };
    
    const handleMove = (e) => {
        if (!isDragging) return;
        e.preventDefault();
        
        const touch = e.touches ? e.touches[0] : e;
        currentX = touch.clientX - startX;
        currentY = touch.clientY - startY;
        
        const rotation = currentX * 0.1;
        card.style.transform = `translateX(${currentX}px) translateY(${currentY}px) rotate(${rotation}deg)`;
        
        // Show indicators
        const opacity = Math.abs(currentX) / 100;
        if (Math.abs(currentX) > 50) {
            let indicator = card.querySelector('.swipe-indicator');
            if (!indicator) {
                indicator = document.createElement('div');
                indicator.className = 'swipe-indicator';
                card.appendChild(indicator);
            }
            
            if (currentX > 0) {
                indicator.className = 'swipe-indicator like';
                indicator.textContent = '♥ НРАВИТСЯ';
            } else {
                indicator.className = 'swipe-indicator skip';
                indicator.textContent = '✕ ПРОПУСК';
            }
            
            indicator.style.opacity = Math.min(opacity, 1);
        } else {
            const indicator = card.querySelector('.swipe-indicator');
            if (indicator) {
                indicator.style.opacity = '0';
            }
        }
    };
    
    const handleEnd = (e) => {
        if (!isDragging) return;
        isDragging = false;
        card.classList.remove('dragging');
        
        const threshold = 100;
        
        if (Math.abs(currentX) > threshold) {
            // Trigger swipe action
            if (currentX > 0) {
                likePlace();
            } else {
                skipPlace();
            }
        } else {
            // Snap back
            card.style.transform = '';
            const indicator = card.querySelector('.swipe-indicator');
            if (indicator) {
                indicator.style.opacity = '0';
            }
        }
        
        currentX = 0;
        currentY = 0;
    };
    
    // Touch events
    card.addEventListener('touchstart', handleStart, { passive: true });
    card.addEventListener('touchmove', handleMove, { passive: false });
    card.addEventListener('touchend', handleEnd, { passive: true });
    
    // Mouse events
    card.addEventListener('mousedown', handleStart);
    card.addEventListener('mousemove', handleMove);
    card.addEventListener('mouseup', handleEnd);
    card.addEventListener('mouseleave', handleEnd);
}

// UI Helper Functions
function switchAuthTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
    
    // Show/hide forms
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (tab === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    } else {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
    }
}

function showScreen(screenId) {
    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.add('hidden');
    });
    
    // Show target screen
    document.getElementById(screenId).classList.remove('hidden');
}

function getCurrentScreen() {
    const screens = ['landingScreen', 'cityScreen', 'swipeScreen'];
    return screens.find(id => !document.getElementById(id).classList.contains('hidden'));
}

function showModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function hideModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

function showAuth() {
    showModal('authModal');
}

function hideAuth() {
    hideModal('authModal');
}

function hideInfo() {
    hideModal('infoModal');
}

function showLanding() {
    showScreen('landingScreen');
}

function showCitySelection() {
    showScreen('cityScreen');
}

function updateUserInfo() {
    const userInfo = document.getElementById('userInfo');
    const userName = document.getElementById('userName');
    
    if (currentUser) {
        userName.textContent = currentUser.firstName || currentUser.email;
        userInfo.classList.remove('hidden');
    } else {
        userInfo.classList.add('hidden');
    }
}

function setLoading(loading) {
    isLoading = loading;
    const overlay = document.getElementById('loadingOverlay');
    
    if (loading) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}