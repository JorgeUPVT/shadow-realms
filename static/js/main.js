/* ============================================
   SHADOW REALMS - JAVASCRIPT PRINCIPAL
   ============================================ */

// ===== UTILIDADES GLOBALES =====
const ShadowRealms = {
    // Inicialización
    init() {
        this.createParticles();
        this.setupEventListeners();
        this.checkUserData();
    },

    // Crear partículas de fondo
    createParticles() {
        const particlesContainer = document.getElementById('particles');
        const particlesBg = document.getElementById('particlesBg');
        
        if (particlesContainer) {
            for (let i = 0; i < 50; i++) {
                this.createParticle(particlesContainer);
            }
        }
        
        if (particlesBg) {
            for (let i = 0; i < 30; i++) {
                this.createParticle(particlesBg);
            }
        }
    },

    // Crear una partícula individual
    createParticle(container) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 8 + 's';
        particle.style.animationDuration = (Math.random() * 5 + 5) + 's';
        container.appendChild(particle);
    },

    // Setup de event listeners
    setupEventListeners() {
        // Smooth scroll para enlaces
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        });

        // Animación de entrada para elementos
        this.observeElements();
    },

    // Intersection Observer para animaciones
    observeElements() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, {
            threshold: 0.1
        });

        document.querySelectorAll('.feature-card, .character-preview, .level-card').forEach(el => {
            observer.observe(el);
        });
    },

    // Verificar datos de usuario en localStorage
    checkUserData() {
        const userData = localStorage.getItem('userData');
        if (userData) {
            try {
                const data = JSON.parse(userData);
                this.updateUserInterface(data);
            } catch (e) {
                console.error('Error parsing user data:', e);
            }
        }
    },

    // Actualizar interfaz con datos de usuario
    updateUserInterface(data) {
        // Actualizar nombre de usuario
        const usernameElements = document.querySelectorAll('.username, .admin-user');
        usernameElements.forEach(el => {
            el.textContent = data.username || 'Usuario';
        });

        // Actualizar nivel
        const levelElements = document.querySelectorAll('.level');
        levelElements.forEach(el => {
            el.textContent = `Nivel ${data.level || 1}`;
        });

        // Actualizar personaje seleccionado
        if (data.selectedCharacter) {
            const characterBadge = document.querySelector('.character-badge');
            if (characterBadge) {
                characterBadge.textContent = this.getCharacterIcon(data.selectedCharacter);
            }
        }
    },

    // Obtener icono de personaje
    getCharacterIcon(character) {
        const icons = {
            'knight': '⚔️ Caballero',
            'mage': '🔮 Hechicera',
            'archer': '🏹 Arquero',
            'paladin': '🛡️ Paladín'
        };
        return icons[character] || '⚔️';
    },

    // Guardar datos de usuario
    saveUserData(data) {
        const currentData = this.getUserData();
        const updatedData = { ...currentData, ...data };
        localStorage.setItem('userData', JSON.stringify(updatedData));
        this.updateUserInterface(updatedData);
    },

    // Obtener datos de usuario
    getUserData() {
        const userData = localStorage.getItem('userData');
        if (userData) {
            try {
                return JSON.parse(userData);
            } catch (e) {
                return {};
            }
        }
        return {};
    }
};

// ===== FUNCIONES DE SELECCIÓN DE PERSONAJE =====
function selectCharacter(character) {
    ShadowRealms.saveUserData({ selectedCharacter: character });
    
    // Animación de selección
    const cards = document.querySelectorAll('.character-card');
    cards.forEach(card => {
        if (card.dataset.character === character) {
            card.style.transform = 'scale(1.1)';
            card.style.borderColor = '#d4af37';
        }
    });
    
    // Redirigir después de un breve delay
    setTimeout(() => {
        window.location.href = 'level_selection.html';
    }, 500);
}

// ===== FUNCIONES DE NIVEL =====
function playLevel(levelNumber) {
    ShadowRealms.saveUserData({ currentLevel: levelNumber });
    
    // Mostrar loading
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = 'Cargando...';
    btn.disabled = true;
    
    setTimeout(() => {
        window.location.href = 'game.html';
    }, 1000);
}

// ===== FUNCIONES DE TABS =====
function showTab(tabName) {
    // Ocultar todos los tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        tab.style.display = 'none';
        tab.classList.remove('active');
    });

    // Remover clase active de todos los botones
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));

    // Mostrar tab seleccionado
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.style.display = 'block';
        selectedTab.classList.add('active');
    }

    // Activar botón correspondiente
    event.target.classList.add('active');
}

function showSettingsTab(tabName) {
    showTab(tabName);
}

// ===== FUNCIONES DE MODAL =====
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        // Añadir animación
        modal.querySelector('.modal-content').style.animation = 'fadeIn 0.3s ease';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// ===== FUNCIONES DE NAVEGACIÓN =====
function nextLevel() {
    const userData = ShadowRealms.getUserData();
    const currentLevel = userData.currentLevel || 1;
    const nextLevel = currentLevel + 1;
    
    if (nextLevel <= 5) {
        ShadowRealms.saveUserData({ currentLevel: nextLevel });
        closeModal('victoryModal');
        window.location.href = 'game.html';
    } else {
        // Juego completado
        alert('¡Felicidades! Has completado Shadow Realms');
        window.location.href = 'level_selection.html';
    }
}

function returnToMap() {
    window.location.href = 'level_selection.html';
}

function retry() {
    window.location.reload();
}

function openSettings() {
    window.location.href = 'settings.html';
}

// ===== VALIDACIÓN DE FORMULARIOS =====
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = '#ef4444';
        } else {
            input.style.borderColor = '';
        }
    });
    
    return isValid;
}

// Event listener para formularios
document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
                alert('Por favor completa todos los campos requeridos');
            }
        });
    });
});

// ===== ACTUALIZACIÓN DE SLIDERS DE VOLUMEN =====
document.addEventListener('DOMContentLoaded', () => {
    const volumeSliders = document.querySelectorAll('input[type="range"]');
    volumeSliders.forEach(slider => {
        slider.addEventListener('input', function() {
            const valueSpan = this.nextElementSibling;
            if (valueSpan && valueSpan.classList.contains('volume-value')) {
                valueSpan.textContent = this.value + '%';
            }
        });
    });
});

// ===== CHECKBOX "SELECCIONAR TODO" =====
document.addEventListener('DOMContentLoaded', () => {
    const checkboxAll = document.querySelector('.checkbox-all');
    if (checkboxAll) {
        checkboxAll.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.admin-table tbody input[type="checkbox"]');
            checkboxes.forEach(cb => {
                cb.checked = this.checked;
            });
        });
    }
});

// ===== PERSISTENCIA DE DATOS =====
const GameData = {
    // Guardar progreso
    saveProgress(levelNumber, score, stars, time) {
        const progress = this.getProgress();
        
        if (!progress.levels) {
            progress.levels = {};
        }
        
        if (!progress.levels[levelNumber] || score > progress.levels[levelNumber].score) {
            progress.levels[levelNumber] = {
                score,
                stars,
                time,
                completed: true,
                date: new Date().toISOString()
            };
        }
        
        localStorage.setItem('gameProgress', JSON.stringify(progress));
    },
    
    // Obtener progreso
    getProgress() {
        const progress = localStorage.getItem('gameProgress');
        if (progress) {
            try {
                return JSON.parse(progress);
            } catch (e) {
                return {};
            }
        }
        return {};
    },
    
    // Verificar si un nivel está desbloqueado
    isLevelUnlocked(levelNumber) {
        if (levelNumber === 1) return true;
        
        const progress = this.getProgress();
        const previousLevel = levelNumber - 1;
        
        return progress.levels && 
               progress.levels[previousLevel] && 
               progress.levels[previousLevel].completed;
    }
};

// ===== EFECTOS DE SONIDO (PLACEHOLDER) =====
const SoundEffects = {
    play(soundName) {
        // Placeholder para efectos de sonido
        console.log(`Playing sound: ${soundName}`);
        // En producción, esto reproduciría un archivo de audio
    },
    
    playMusic(musicName) {
        console.log(`Playing music: ${musicName}`);
    },
    
    stopAll() {
        console.log('Stopping all sounds');
    }
};

// ===== INICIALIZACIÓN AL CARGAR LA PÁGINA =====
document.addEventListener('DOMContentLoaded', () => {
    ShadowRealms.init();
    
    // Agregar clase de carga completada
    document.body.classList.add('loaded');
    
    console.log('Shadow Realms initialized successfully! ⚔️');
});

// ===== PREVENIR RECARGA ACCIDENTAL =====
window.addEventListener('beforeunload', (e) => {
    // Solo prevenir en páginas de juego
    if (window.location.pathname.includes('game.html')) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// ===== DETECTAR MODO OSCURO DEL SISTEMA =====
if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.classList.add('dark-mode');
}

// ===== EXPORTAR FUNCIONES GLOBALES =====
window.ShadowRealms = ShadowRealms;
window.GameData = GameData;
window.SoundEffects = SoundEffects;
