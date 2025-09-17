// DOM Elements
const mainInput = document.getElementById('mainInput');
const clearBtn = document.getElementById('clearBtn');
const micBtn = document.getElementById('micBtn');
const recordBtn = document.getElementById('recordBtn');
const inputContainer = document.querySelector('.input-container');

// Initialize Orb Background
function initializeOrbBackground() {
    const orbContainer = document.getElementById('orb-background');
    if (!orbContainer) return;

    // Create the orb with options matching your design
    const orb = new Orb(orbContainer, {
        hue: 0, // Keep original colors
        hoverIntensity: 0.5,
        rotateOnHover: true,
        forceHoverState: false
    });

    // Store reference for cleanup if needed
    window.orbInstance = orb;
}

// State management
let isRecording = false;
let isMicEnabled = false;
let recognition = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function () {
    initializeOrbBackground();
    initializeApp();
    setupEventListeners();
    setupSpeechRecognition();
});

// Initialize app functionality
function initializeApp() {
    // Add loading animation on page load
    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 100);

    // Set initial states
    updateMicButton();
    updateRecordButton();
}

// Setup event listeners
function setupEventListeners() {
    // Input field events
    mainInput.addEventListener('input', handleInputChange);
    mainInput.addEventListener('keypress', handleKeyPress);
    mainInput.addEventListener('focus', handleInputFocus);
    mainInput.addEventListener('blur', handleInputBlur);

    // Button events
    clearBtn.addEventListener('click', clearInput);
    micBtn.addEventListener('click', toggleMicrophone);
    recordBtn.addEventListener('click', toggleRecording);

    // Navigation events
    setupNavigation();

    // Auth button events
    setupAuthButtons();

    // Footer link events
    setupFooterLinks();
}

// Handle input changes
function handleInputChange(e) {
    const value = e.target.value;

    // Show/hide clear button based on input
    if (value.length > 0) {
        clearBtn.style.opacity = '1';
        clearBtn.style.pointerEvents = 'auto';
    } else {
        clearBtn.style.opacity = '0.5';
        clearBtn.style.pointerEvents = 'none';
    }

    // Simulate search functionality
    if (value.length > 2) {
        simulateSearch(value);
    }
}

// Handle key press events
function handleKeyPress(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        handleSearch();
    }
}

// Handle input focus
function handleInputFocus() {
    inputContainer.classList.add('focused');
}

// Handle input blur
function handleInputBlur() {
    inputContainer.classList.remove('focused');
}

// Clear input field
function clearInput() {
    mainInput.value = '';
    mainInput.focus();
    clearBtn.style.opacity = '0.5';
    clearBtn.style.pointerEvents = 'none';

    // Remove any loading state
    inputContainer.classList.remove('loading');
}

// Handle search functionality
function handleSearch() {
    const query = mainInput.value.trim();

    if (query.length === 0) {
        showNotification('Please enter a search term', 'warning');
        return;
    }

    // Add loading state
    inputContainer.classList.add('loading');

    // Simulate API call
    setTimeout(() => {
        inputContainer.classList.remove('loading');
        showNotification(`Searching for: "${query}"`, 'success');

        // Here you would typically make an API call to your news aggregation service
        console.log('Search query:', query);

        // Example: Redirect to results page or show results
        // window.location.href = `results.html?q=${encodeURIComponent(query)}`;
    }, 1500);
}

// Simulate search as user types
function simulateSearch(query) {
    // Debounce the search
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(() => {
        console.log('Simulating search for:', query);
        // Here you could implement real-time search suggestions
    }, 300);
}

// Setup speech recognition
function setupSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();

        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = function () {
            console.log('Speech recognition started');
            isRecording = true;
            updateRecordButton();
        };

        recognition.onresult = function (event) {
            const transcript = event.results[0][0].transcript;
            mainInput.value = transcript;
            handleInputChange({ target: { value: transcript } });
        };

        recognition.onerror = function (event) {
            console.error('Speech recognition error:', event.error);
            showNotification('Speech recognition error: ' + event.error, 'error');
            isRecording = false;
            updateRecordButton();
        };

        recognition.onend = function () {
            console.log('Speech recognition ended');
            isRecording = false;
            updateRecordButton();
        };
    } else {
        console.log('Speech recognition not supported');
        micBtn.style.display = 'none';
        recordBtn.style.display = 'none';
    }
}

// Toggle microphone
function toggleMicrophone() {
    isMicEnabled = !isMicEnabled;
    updateMicButton();

    if (isMicEnabled) {
        showNotification('Microphone enabled', 'success');
    } else {
        showNotification('Microphone disabled', 'info');
    }
}

// Toggle recording
function toggleRecording() {
    if (!recognition) {
        showNotification('Speech recognition not supported', 'error');
        return;
    }

    if (isRecording) {
        recognition.stop();
    } else {
        recognition.start();
    }
}

// Update microphone button state
function updateMicButton() {
    if (isMicEnabled) {
        micBtn.style.color = '#4a4a4a';
        micBtn.style.opacity = '1';
    } else {
        micBtn.style.color = '#999999';
        micBtn.style.opacity = '0.6';
    }
}

// Update record button state
function updateRecordButton() {
    if (isRecording) {
        recordBtn.style.backgroundColor = '#ff4444';
        recordBtn.style.transform = 'scale(1.1)';
    } else {
        recordBtn.style.backgroundColor = '#4a4a4a';
        recordBtn.style.transform = 'scale(1)';
    }
}

// Setup navigation functionality
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-links a');

    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');

            // Handle different navigation items
            switch (href) {
                case '#products':
                    showNotification('Products section coming soon!', 'info');
                    break;
                case '#solutions':
                    showNotification('Solutions section coming soon!', 'info');
                    break;
                case '#community':
                    showNotification('Community section coming soon!', 'info');
                    break;
                case '#resources':
                    showNotification('Resources section coming soon!', 'info');
                    break;
                case '#pricing':
                    showNotification('Pricing section coming soon!', 'info');
                    break;
                case '#contact':
                    showNotification('Contact section coming soon!', 'info');
                    break;
                case '#link':
                    showNotification('Link section coming soon!', 'info');
                    break;
                default:
                    console.log('Navigation to:', href);
            }
        });
    });
}

// Setup authentication buttons
function setupAuthButtons() {
    const signInBtn = document.querySelector('.btn-signin');
    const registerBtn = document.querySelector('.btn-register');

    signInBtn.addEventListener('click', function () {
        showNotification('Sign in functionality coming soon!', 'info');
        // Here you would typically open a sign-in modal or redirect to sign-in page
    });

    registerBtn.addEventListener('click', function () {
        showNotification('Registration functionality coming soon!', 'info');
        // Here you would typically open a registration modal or redirect to registration page
    });
}

// Setup footer links
function setupFooterLinks() {
    const footerLinks = document.querySelectorAll('.footer-column a');

    footerLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const text = this.textContent;
            showNotification(`${text} section coming soon!`, 'info');
        });
    });
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 90px;
        right: 20px;
        background: ${type === 'error' ? '#ff4444' : type === 'warning' ? '#ffaa00' : type === 'success' ? '#44aa44' : '#4a4a4a'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 3000);
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Keyboard shortcuts
document.addEventListener('keydown', function (e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        mainInput.focus();
    }

    // Escape to clear search
    if (e.key === 'Escape') {
        if (document.activeElement === mainInput) {
            clearInput();
        }
    }
});

// Handle window resize
window.addEventListener('resize', debounce(function () {
    // Handle responsive adjustments if needed
    console.log('Window resized');
}, 250));

// Export functions for potential external use
window.BrieflyApp = {
    clearInput,
    handleSearch,
    showNotification,
    toggleMicrophone,
    toggleRecording
};
