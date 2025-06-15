/**
 * Alethea - Higher Education Q&A Platform
 * Main JavaScript functionality file (English version)
 */

// Global variables
const API_BASE_URL = '/api';
let currentUser = null;
let currentQuestion = null;
let currentAnswer = null;
let darkMode = false;

// Language-specific text
const TEXTS = {
    // Notifications
    pleaseEnterQuestion: 'Please enter a question',
    pleaseLoginFirst: 'Please login first to rate',
    thankYouForFeedback: 'Thank you for your feedback!',
    ratingFailed: 'Rating submission failed, please try again later',
    loginSuccessful: 'Login successful!',
    loginFailed: 'Login failed, please check your username and password',
    registrationSuccessful: 'Registration successful! Please login',
    registrationFailed: 'Registration failed, please try again later',
    resetLinkSent: 'Reset link has been sent to your email, please check',
    resetLinkFailed: 'Failed to send reset link, please try again later',
    logoutSuccessful: 'Successfully logged out',
    
    // Form validation
    fillAllFields: 'Please fill in all required fields',
    passwordMismatch: 'Passwords do not match',
    pleaseEnterEmail: 'Please enter email address',
    
    // Loading states
    searching: 'Searching...',
    thinking: 'Thinking, please wait...',
    
    // Component selection
    selectedComponent: 'Selected component:',
    
    // Modal titles and labels
    login: 'Login',
    register: 'Register',
    resetPassword: 'Reset Password',
    username: 'Username',
    email: 'Email',
    password: 'Password',
    confirmPassword: 'Confirm Password',
    usernameOrEmail: 'Username or Email',
    role: 'Role',
    student: 'Student',
    teacher: 'Teacher',
    forgotPassword: 'Forgot Password?',
    backToLogin: 'Back to Login',
    alreadyHaveAccount: 'Already have an account?',
    noAccount: 'Don\'t have an account?',
    loginNow: 'Login Now',
    registerNow: 'Register Now',
    sendResetLink: 'Send Reset Link',
    resetPasswordDescription: 'Please enter your email address and we will send you a password reset link.',
    
    // Subject modal
    coreKnowledge: 'Core Knowledge Points',
    recommendedExperiments: 'Recommended Experiments',
    interactiveSimulation: 'Interactive Simulation Preview',
    startLearning: 'Start Learning',
    exploreExperiments: 'Explore Experiments',
    askQuestions: 'Ask Questions',
    subjectIntroduction: 'Subject Introduction',
    loading: 'Loading...',
    aiGeneratingContent: 'AI is generating content for',
    aiDesigningSimulation: 'AI is designing simulation experiments...',
    noRelatedKnowledge: 'No related knowledge points available',
    noRecommendedExperiments: 'No recommended experiments available',
    noSimulationAvailable: 'No simulation experiments available',
    knowledgeGenerationFailed: 'Knowledge point generation failed',
    experimentGenerationFailed: 'Experiment recommendation generation failed',
    simulationGenerationFailed: 'Simulation design generation failed',
    subjectIntroductionFailed: 'Subject introduction generation failed, please try again later',
    
    // Learning actions
    systematicLearning: 'I want to systematically learn',
    createLearningPlan: ', please create a detailed learning plan for me',
    recommendImportantExperiments: 'Please recommend important experimental projects in the field of',
    includeObjectiveStepsResults: ', including experimental objectives, steps and expected results',
    explainConcepts: 'Please explain in detail the concepts, principles and applications related to',
    experimentDetails: 'Please provide detailed information about the experimental steps, principles and precautions for',
    designInteractiveSimulation: 'Please design an interactive simulation experiment for',
    includeParameterControl: ', including parameter control and result analysis'
};

// DOM loaded event
document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI components
    initializeUI();
    
    // Check user login status
    checkLoginStatus();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize MathJax
    initMathJax();
    
    // Initialize code highlighting
    initCodeHighlighting();
    
    // Initialize charts
    initCharts();
    
    // Initialize circuit simulation
    initCircuitSimulation();
    
    // Initialize language switcher
    initLanguageSwitcher();
});

/**
 * Language switching function
 */
function switchLanguage() {
    // Detect current page language
    const currentLang = document.documentElement.lang;
    
    if (currentLang === 'zh-CN') {
        // Switch to English version
        window.location.href = '/static/index-en.html';
    } else {
        // Switch to Chinese version
        window.location.href = '/static/index.html';
    }
}

/**
 * Initialize language switcher
 */
function initLanguageSwitcher() {
    // Language switcher is already bound to switchLanguage function via onclick attribute in HTML
    // Additional language-related initialization logic can be added here
    
    // Check for language preference in URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const langParam = urlParams.get('lang');
    
    if (langParam) {
        localStorage.setItem('preferredLanguage', langParam);
        
        // If URL parameter doesn't match current page language, redirect
        const currentLang = document.documentElement.lang;
        if ((langParam === 'en' && currentLang === 'zh-CN') || 
            (langParam === 'zh' && currentLang === 'en')) {
            switchLanguage();
        }
    }
    
    // Get language preference from local storage
    const preferredLang = localStorage.getItem('preferredLanguage');
    if (preferredLang) {
        const currentLang = document.documentElement.lang;
        if ((preferredLang === 'en' && currentLang === 'zh-CN') || 
            (preferredLang === 'zh' && currentLang === 'en')) {
            // Can choose whether to auto-switch, commented out to avoid infinite redirect
            // switchLanguage();
        }
    }
}

/**
 * Initialize UI components
 */
function initializeUI() {
    // Mobile menu toggle
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // User dropdown menu toggle
    const userMenuButton = document.getElementById('user-menu-button');
    const userDropdown = document.getElementById('user-dropdown');
    const guestDropdown = document.getElementById('guest-dropdown');
    
    if (userMenuButton) {
        userMenuButton.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Show different dropdown menus based on login status
            if (currentUser) {
                if (userDropdown) {
                    userDropdown.classList.toggle('hidden');
                }
                if (guestDropdown && !guestDropdown.classList.contains('hidden')) {
                    guestDropdown.classList.add('hidden');
                }
            } else {
                if (guestDropdown) {
                    guestDropdown.classList.toggle('hidden');
                }
                if (userDropdown && !userDropdown.classList.contains('hidden')) {
                    userDropdown.classList.add('hidden');
                }
            }
        });
        
        // Click elsewhere to close dropdown menu
        document.addEventListener('click', function() {
            if (userDropdown && !userDropdown.classList.contains('hidden')) {
                userDropdown.classList.add('hidden');
            }
            if (guestDropdown && !guestDropdown.classList.contains('hidden')) {
                guestDropdown.classList.add('hidden');
            }
        });
    }
    
    // Dark mode toggle
    const themeToggle = document.getElementById('theme-toggle');
    
    if (themeToggle) {
        // Check theme preference in local storage
        darkMode = localStorage.getItem('darkMode') === 'true';
        
        // Apply theme
        if (darkMode) {
            document.body.classList.add('dark-mode');
            themeToggle.querySelector('i').classList.remove('fa-moon');
            themeToggle.querySelector('i').classList.add('fa-sun');
        }
        
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const icon = this.querySelector('i');
            
            if (icon.classList.contains('fa-moon')) {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
                darkMode = true;
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
                darkMode = false;
            }
            
            // Save theme preference to local storage
            localStorage.setItem('darkMode', darkMode);
        });
    }
}

/**
 * Check user login status
 */
function checkLoginStatus() {
    // Get token from local storage
    const token = localStorage.getItem('authToken');
    
    if (token) {
        // Validate token
        fetch(`${API_BASE_URL}/user/profile`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                // Invalid token, clear local storage
                localStorage.removeItem('authToken');
                throw new Error('Invalid token');
            }
        })
        .then(data => {
            // Update current user info
            currentUser = data;
            updateUserUI(currentUser);
        })
        .catch(error => {
            console.error('Error checking login status:', error);
            updateUserUI(null);
        });
    } else {
        updateUserUI(null);
    }
}

/**
 * Update user interface
 * @param {Object|null} user - User info object or null for not logged in
 */
function updateUserUI(user) {
    const userMenuText = document.getElementById('user-menu-text');
    const userDropdown = document.getElementById('user-dropdown');
    const guestDropdown = document.getElementById('guest-dropdown');
    const userName = document.getElementById('user-name');
    const userEmail = document.getElementById('user-email');
    
    if (userMenuText) {
        if (user) {
            // User is logged in
            userMenuText.textContent = user.username;
            
            // Update user info
            if (userName) userName.textContent = user.username;
            if (userEmail) userEmail.textContent = user.email;
            
            // Show user dropdown, hide guest dropdown
            if (userDropdown) userDropdown.classList.remove('hidden');
            if (guestDropdown) guestDropdown.classList.add('hidden');
            
            // Add logout event
            const logoutLink = document.getElementById('logout-link');
            if (logoutLink) {
                logoutLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    logout();
                });
            }
            
        } else {
            // User is not logged in
            userMenuText.textContent = 'Login/Register';
            
            // Show guest dropdown, hide user dropdown
            if (guestDropdown) guestDropdown.classList.remove('hidden');
            if (userDropdown) userDropdown.classList.add('hidden');
        }
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Submit question button
    const submitButton = document.getElementById('submit-question');
    const questionInput = document.getElementById('question-input');
    
    if (submitButton && questionInput) {
        submitButton.addEventListener('click', function() {
            const question = questionInput.value.trim();
            
            if (question) {
                submitQuestion(question);
            } else {
                showNotification(TEXTS.pleaseEnterQuestion, 'error');
            }
        });
        
        // Press Enter to submit question
        questionInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                submitButton.click();
            }
        });
    }
    
    // Answer rating buttons
    const helpfulButton = document.querySelector('.answer-card button:nth-child(1)');
    const unhelpfulButton = document.querySelector('.answer-card button:nth-child(2)');
    
    if (helpfulButton && unhelpfulButton) {
        helpfulButton.addEventListener('click', function() {
            if (currentAnswer) {
                rateAnswer(currentAnswer.id, true);
            }
        });
        
        unhelpfulButton.addEventListener('click', function() {
            if (currentAnswer) {
                rateAnswer(currentAnswer.id, false);
            }
        });
    }
    
    // Subject card click events
    const subjectCards = document.querySelectorAll('.subject-card');
    subjectCards.forEach(card => {
        card.addEventListener('click', function(e) {
            e.preventDefault();
            const subjectTitle = this.querySelector('h3').textContent;
            const subjectDescription = this.querySelector('p').textContent;
            showSubjectModal(subjectTitle, subjectDescription);
        });
    });
}

/**
 * Submit question to server
 * @param {string} question - Question text
 */
function submitQuestion(question) {
    // Show loading state
    showLoading(true);
    
    // Save current question to localStorage
    localStorage.setItem('currentQuestion', question);
    
        // Open answer page in new window
        window.open(`/static/answer-en.html?q=${encodeURIComponent(question)}`, '_blank');
    
    // Hide loading state
    showLoading(false);
}

/**
 * Rate answer
 * @param {string} answerId - Answer ID
 * @param {boolean} isHelpful - Whether helpful
 */
function rateAnswer(answerId, isHelpful) {
    // If user not logged in, prompt to login
    if (!currentUser) {
        showNotification(TEXTS.pleaseLoginFirst, 'info');
        return;
    }
    
    fetch(`${API_BASE_URL}/llm/rate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
            answer_id: answerId,
            rating: isHelpful ? 'helpful' : 'unhelpful'
        })
    })
    .then(response => {
        if (response.ok) {
            showNotification(TEXTS.thankYouForFeedback, 'success');
        } else {
            throw new Error('Failed to rate answer');
        }
    })
    .catch(error => {
        console.error('Error rating answer:', error);
        showNotification(TEXTS.ratingFailed, 'error');
    });
}

/**
 * Show login modal
 */
function showLoginModal() {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="fixed inset-0 bg-black opacity-50"></div>
        <div class="bg-white rounded-lg shadow-xl z-10 w-full max-w-md p-6 relative">
            <button class="absolute top-4 right-4 text-gray-500 hover:text-gray-700" id="close-modal">
                <i class="fas fa-times"></i>
            </button>
            <h2 class="text-2xl font-bold mb-6">${TEXTS.login}</h2>
            <form id="login-form">
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
                        ${TEXTS.usernameOrEmail}
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="username" type="text" placeholder="Please enter username or email">
                </div>
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                        ${TEXTS.password}
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="password" type="password" placeholder="Please enter password">
                </div>
                <div class="flex items-center justify-between">
                    <button class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit">
                        ${TEXTS.login}
                    </button>
                    <a class="inline-block align-baseline font-bold text-sm text-blue-600 hover:text-blue-800" href="#" id="forgot-password">
                        ${TEXTS.forgotPassword}
                    </a>
                </div>
                <div class="mt-4 text-center">
                    <p>${TEXTS.noAccount} <a href="#" class="text-blue-600 hover:text-blue-800" id="switch-to-register">${TEXTS.registerNow}</a></p>
                </div>
            </form>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(modal);
    
    // Close modal
    document.getElementById('close-modal').addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // Switch to register
    document.getElementById('switch-to-register').addEventListener('click', function(e) {
        e.preventDefault();
        document.body.removeChild(modal);
        showRegisterModal();
    });
    
    // Forgot password
    document.getElementById('forgot-password').addEventListener('click', function(e) {
        e.preventDefault();
        document.body.removeChild(modal);
        showForgotPasswordModal();
    });
    
    // Submit login form
    document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        if (!username || !password) {
            showNotification(TEXTS.fillAllFields, 'error');
            return;
        }
        
        // Send login request
        fetch(`${API_BASE_URL}/user/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username_or_email: username,
                password: password
            })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Login failed');
            }
        })
        .then(data => {
            // Save token to local storage
            localStorage.setItem('authToken', data.token);
            
            // Update current user
            currentUser = data.user;
            
            // Update UI
            updateUserUI(currentUser);
            
            // Close modal
            document.body.removeChild(modal);
            
            // Show success message
            showNotification(TEXTS.loginSuccessful, 'success');
        })
        .catch(error => {
            console.error('Error logging in:', error);
            showNotification(TEXTS.loginFailed, 'error');
        });
    });
}

/**
 * Show register modal
 */
function showRegisterModal() {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="fixed inset-0 bg-black opacity-50"></div>
        <div class="bg-white rounded-lg shadow-xl z-10 w-full max-w-md p-6 relative">
            <button class="absolute top-4 right-4 text-gray-500 hover:text-gray-700" id="close-modal">
                <i class="fas fa-times"></i>
            </button>
            <h2 class="text-2xl font-bold mb-6">${TEXTS.register}</h2>
            <form id="register-form">
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
                        ${TEXTS.username}
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="username" type="text" placeholder="Please enter username">
                </div>
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="email">
                        ${TEXTS.email}
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="email" type="email" placeholder="Please enter email">
                </div>
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                        ${TEXTS.password}
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="password" type="password" placeholder="Please enter password">
                </div>
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="confirm-password">
                        ${TEXTS.confirmPassword}
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="confirm-password" type="password" placeholder="Please enter password again">
                </div>
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2">
                        ${TEXTS.role}
                    </label>
                    <div class="flex space-x-4">
                        <label class="inline-flex items-center">
                            <input type="radio" class="form-radio" name="role" value="student" checked>
                            <span class="ml-2">${TEXTS.student}</span>
                        </label>
                        <label class="inline-flex items-center">
                            <input type="radio" class="form-radio" name="role" value="teacher">
                            <span class="ml-2">${TEXTS.teacher}</span>
                        </label>
                    </div>
                </div>
                <div class="flex items-center justify-between">
                    <button class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit">
                        ${TEXTS.register}
                    </button>
                </div>
                <div class="mt-4 text-center">
                    <p>${TEXTS.alreadyHaveAccount} <a href="#" class="text-blue-600 hover:text-blue-800" id="switch-to-login">${TEXTS.loginNow}</a></p>
                </div>
            </form>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(modal);
    
    // Close modal
    document.getElementById('close-modal').addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // Switch to login
    document.getElementById('switch-to-login').addEventListener('click', function(e) {
        e.preventDefault();
        document.body.removeChild(modal);
        showLoginModal();
    });
    
    // Submit register form
    document.getElementById('register-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        const role = document.querySelector('input[name="role"]:checked').value;
        
        if (!username || !email || !password || !confirmPassword) {
            showNotification(TEXTS.fillAllFields, 'error');
            return;
        }
        
        if (password !== confirmPassword) {
            showNotification(TEXTS.passwordMismatch, 'error');
            return;
        }
        
        // Send register request
        fetch(`${API_BASE_URL}/user/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
                role_name: role
            })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Registration failed');
            }
        })
        .then(data => {
            // Close modal
            document.body.removeChild(modal);
            
            // Show success message
            showNotification(TEXTS.registrationSuccessful, 'success');
            
            // Show login modal
            showLoginModal();
        })
        .catch(error => {
            console.error('Error registering:', error);
            showNotification(TEXTS.registrationFailed, 'error');
        });
    });
}

/**
 * Show forgot password modal
 */
function showForgotPasswordModal() {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="fixed inset-0 bg-black opacity-50"></div>
        <div class="bg-white rounded-lg shadow-xl z-10 w-full max-w-md p-6 relative">
            <button class="absolute top-4 right-4 text-gray-500 hover:text-gray-700" id="close-modal">
                <i class="fas fa-times"></i>
            </button>
            <h2 class="text-2xl font-bold mb-6">${TEXTS.resetPassword}</h2>
            <p class="mb-4">${TEXTS.resetPasswordDescription}</p>
            <form id="forgot-password-form">
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="email">
                        ${TEXTS.email}
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="email" type="email" placeholder="Please enter email">
                </div>
                <div class="flex items-center justify-between">
                    <button class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit">
                        ${TEXTS.sendResetLink}
                    </button>
                    <a class="inline-block align-baseline font-bold text-sm text-blue-600 hover:text-blue-800" href="#" id="back-to-login">
                        ${TEXTS.backToLogin}
                    </a>
                </div>
            </form>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(modal);
    
    // Close modal
    document.getElementById('close-modal').addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // Back to login
    document.getElementById('back-to-login').addEventListener('click', function(e) {
        e.preventDefault();
        document.body.removeChild(modal);
        showLoginModal();
    });
    
    // Submit forgot password form
    document.getElementById('forgot-password-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        
        if (!email) {
            showNotification(TEXTS.pleaseEnterEmail, 'error');
            return;
        }
        
        // Send forgot password request
        fetch(`${API_BASE_URL}/user/forgot-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email
            })
        })
        .then(response => {
            if (response.ok) {
                // Close modal
                document.body.removeChild(modal);
                
                // Show success message
                showNotification(TEXTS.resetLinkSent, 'success');
            } else {
                throw new Error('Failed to send reset link');
            }
        })
        .catch(error => {
            console.error('Error sending reset link:', error);
            showNotification(TEXTS.resetLinkFailed, 'error');
        });
    });
}

/**
 * Logout
 */
function logout() {
    // Clear token from local storage
    localStorage.removeItem('authToken');
    
    // Update current user
    currentUser = null;
    
    // Update UI
    updateUserUI(null);
    
    // Show success message
    showNotification(TEXTS.logoutSuccessful, 'success');
}

/**
 * Show notification
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, info, warning)
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transition-all duration-300 transform translate-y-full opacity-0';
    
    // Set notification type styles
    switch (type) {
        case 'success':
            notification.classList.add('bg-green-500', 'text-white');
            notification.innerHTML = `<i class="fas fa-check-circle mr-2"></i> ${message}`;
            break;
        case 'error':
            notification.classList.add('bg-red-500', 'text-white');
            notification.innerHTML = `<i class="fas fa-exclamation-circle mr-2"></i> ${message}`;
            break;
        case 'warning':
            notification.classList.add('bg-yellow-500', 'text-white');
            notification.innerHTML = `<i class="fas fa-exclamation-triangle mr-2"></i> ${message}`;
            break;
        default:
            notification.classList.add('bg-blue-500', 'text-white');
            notification.innerHTML = `<i class="fas fa-info-circle mr-2"></i> ${message}`;
    }
    
    // Add to document
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.remove('translate-y-full', 'opacity-0');
    }, 10);
    
    // Hide notification after 3 seconds
    setTimeout(() => {
        notification.classList.add('translate-y-full', 'opacity-0');
        
        // Remove element after animation
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

/**
 * Show/hide loading state
 * @param {boolean} show - Whether to show loading state
 */
function showLoading(show) {
    // If loading indicator already exists, remove it
    const existingLoader = document.getElementById('loading-indicator');
    if (existingLoader) {
        document.body.removeChild(existingLoader);
    }
    
    if (show) {
        // Create loading indicator
        const loader = document.createElement('div');
        loader.id = 'loading-indicator';
        loader.className = 'fixed inset-0 flex items-center justify-center z-50';
        loader.innerHTML = `
            <div class="fixed inset-0 bg-black opacity-30"></div>
            <div class="bg-white rounded-lg shadow-xl z-10 p-6 flex flex-col items-center">
                <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mb-4"></div>
                <p class="text-gray-700">${TEXTS.thinking}</p>
            </div>
        `;
        
        // Add to document
        document.body.appendChild(loader);
    }
}

/**
 * Initialize MathJax
 */
function initMathJax() {
    if (window.MathJax) {
        window.MathJax = {
            tex: {
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']],
                processEscapes: true,
                processEnvironments: true
            },
            options: {
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }
        };
    }
}

/**
 * Initialize code highlighting
 */
function initCodeHighlighting() {
    if (window.hljs) {
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }
}

/**
 * Initialize charts
 */
function initCharts() {
    // Draw circuit example
    const circuitCanvas = document.getElementById('circuit-example');
    if (circuitCanvas && circuitCanvas.getContext) {
        const ctx = circuitCanvas.getContext('2d');
        
        // Draw battery
        ctx.beginPath();
        ctx.moveTo(50, 100);
        ctx.lineTo(50, 60);
        ctx.moveTo(40, 60);
        ctx.lineTo(60, 60);
        ctx.moveTo(45, 50);
        ctx.lineTo(55, 50);
        ctx.moveTo(50, 50);
        ctx.lineTo(50, 30);
        ctx.stroke();
        
        // Draw resistors
        // R1
        ctx.beginPath();
        ctx.moveTo(50, 30);
        ctx.lineTo(150, 30);
        ctx.stroke();
        ctx.fillText("R1", 90, 25);
        
        // Draw R1 zigzag
        ctx.beginPath();
        ctx.moveTo(70, 30);
        ctx.lineTo(75, 20);
        ctx.lineTo(85, 40);
        ctx.lineTo(95, 20);
        ctx.lineTo(105, 40);
        ctx.lineTo(115, 20);
        ctx.lineTo(125, 40);
        ctx.lineTo(130, 30);
        ctx.stroke();
        
        // R2
        ctx.beginPath();
        ctx.moveTo(150, 30);
        ctx.lineTo(150, 170);
        ctx.stroke();
        ctx.fillText("R2", 155, 100);
        
        // Draw R2 zigzag
        ctx.beginPath();
        ctx.moveTo(150, 50);
        ctx.lineTo(140, 55);
        ctx.lineTo(160, 65);
        ctx.lineTo(140, 75);
        ctx.lineTo(160, 85);
        ctx.lineTo(140, 95);
        ctx.lineTo(160, 105);
        ctx.lineTo(150, 110);
        ctx.stroke();
        
        // R3
        ctx.beginPath();
        ctx.moveTo(150, 170);
        ctx.lineTo(50, 170);
        ctx.lineTo(50, 100);
        ctx.stroke();
        ctx.fillText("R3", 90, 185);
        
        // Draw R3 zigzag
        ctx.beginPath();
        ctx.moveTo(70, 170);
        ctx.lineTo(75, 160);
        ctx.lineTo(85, 180);
        ctx.lineTo(95, 160);
        ctx.lineTo(105, 180);
        ctx.lineTo(115, 160);
        ctx.lineTo(125, 180);
        ctx.lineTo(130, 170);
        ctx.stroke();
        
        // Draw current directions
        // I1
        ctx.beginPath();
        ctx.moveTo(100, 15);
        ctx.lineTo(110, 15);
        ctx.lineTo(105, 10);
        ctx.moveTo(110, 15);
        ctx.lineTo(105, 20);
        ctx.stroke();
        ctx.fillText("I1", 95, 15);
        
        // I2
        ctx.beginPath();
        ctx.moveTo(165, 100);
        ctx.lineTo(165, 110);
        ctx.lineTo(160, 105);
        ctx.moveTo(165, 110);
        ctx.lineTo(170, 105);
        ctx.stroke();
        ctx.fillText("I2", 165, 95);
        
        // I3
        ctx.beginPath();
        ctx.moveTo(100, 155);
        ctx.lineTo(90, 155);
        ctx.lineTo(95, 150);
        ctx.moveTo(90, 155);
        ctx.lineTo(95, 160);
        ctx.stroke();
        ctx.fillText("I3", 105, 155);
    }
}

/**
 * Initialize circuit simulation
 */
function initCircuitSimulation() {
    // Circuit simulation initialization code
    // For complete circuit simulation, more complex implementation is needed
    
    // This is just a sample framework
    const componentItems = document.querySelectorAll('.component-item');
    const simulationCanvas = document.querySelector('.simulation-canvas');
    
    if (componentItems && simulationCanvas) {
        componentItems.forEach(item => {
            item.addEventListener('click', function() {
                const componentName = this.querySelector('span').textContent;
                showNotification(`${TEXTS.selectedComponent} ${componentName}`, 'info');
                
                // In actual implementation, this would create components and add to simulation canvas
            });
        });
    }
}

/**
 * Show subject modal
 * @param {string} subjectTitle - Subject title
 * @param {string} subjectDescription - Subject description
 */
function showSubjectModal(subjectTitle, subjectDescription) {
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="fixed inset-0 bg-black opacity-50"></div>
        <div class="bg-white rounded-lg shadow-xl z-10 w-full max-w-4xl max-h-[90vh] overflow-y-auto relative">
            <button class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 z-10" id="close-subject-modal">
                <i class="fas fa-times text-xl"></i>
            </button>
            
            <!-- Header -->
            <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
                <h2 class="text-3xl font-bold mb-2">${subjectTitle}</h2>
                <p class="text-blue-100">${subjectDescription}</p>
            </div>
            
            <!-- Content -->
            <div class="p-6">
                <!-- AI Generated Content -->
                <div id="subject-content" class="mb-8">
                    <div class="flex items-center justify-center py-8">
                        <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-600 mr-3"></div>
                        <span class="text-gray-600">${TEXTS.aiGeneratingContent} ${subjectTitle}...</span>
                    </div>
                </div>
                
                <!-- Knowledge Points Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <!-- Core Knowledge -->
                    <div class="bg-blue-50 rounded-lg p-6">
                        <h3 class="text-xl font-bold text-blue-800 mb-4">
                            <i class="fas fa-book mr-2"></i>${TEXTS.coreKnowledge}
                        </h3>
                        <div id="subject-knowledge" class="space-y-3">
                            <div class="flex items-center justify-center py-4">
                                <div class="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-600 mr-2"></div>
                                <span class="text-gray-600">${TEXTS.loading}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Recommended Experiments -->
                    <div class="bg-green-50 rounded-lg p-6">
                        <h3 class="text-xl font-bold text-green-800 mb-4">
                            <i class="fas fa-flask mr-2"></i>${TEXTS.recommendedExperiments}
                        </h3>
                        <div id="subject-experiments" class="space-y-3">
                            <div class="flex items-center justify-center py-4">
                                <div class="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-green-600 mr-2"></div>
                                <span class="text-gray-600">${TEXTS.loading}</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Interactive Simulation Preview -->
                <div class="bg-purple-50 rounded-lg p-6">
                    <h3 class="text-xl font-bold text-purple-800 mb-4">
                        <i class="fas fa-cogs mr-2"></i>${TEXTS.interactiveSimulation}
                    </h3>
                    <div id="subject-simulation" class="text-center py-8">
                        <div class="flex items-center justify-center mb-4">
                            <div class="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-purple-600 mr-2"></div>
                            <span class="text-gray-600">${TEXTS.aiDesigningSimulation}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div class="flex justify-center space-x-4 mt-8">
                    <button onclick="startSubjectLearning('${subjectTitle}')" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                        <i class="fas fa-play mr-2"></i>${TEXTS.startLearning}
                    </button>
                    <button onclick="exploreSubjectExperiments('${subjectTitle}')" class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                        <i class="fas fa-flask mr-2"></i>${TEXTS.exploreExperiments}
                    </button>
                    <button onclick="askSubjectQuestion('${subjectTitle}')" class="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                        <i class="fas fa-question-circle mr-2"></i>${TEXTS.askQuestions}
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(modal);
    
    // Close modal event
    document.getElementById('close-subject-modal').addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // Click background to close modal
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
    
    // Generate subject-related content
    generateSubjectContent(subjectTitle, subjectDescription);
}

/**
 * Generate subject-related content
 * @param {string} subjectTitle - Subject title
 * @param {string} subjectDescription - Subject description
 */
function generateSubjectContent(subjectTitle, subjectDescription) {
    // Build subject introduction question
    const subjectQuestion = `Please provide a detailed introduction to ${subjectTitle}, including main learning content, core concepts and application areas. ${subjectDescription}`;
    
    // Call AI to generate related content
    fetch('/api/llm/generate-related-content', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: subjectQuestion,
            answer: `${subjectTitle} is an important engineering discipline. ${subjectDescription}. This discipline covers both theoretical learning and practical applications.`
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displaySubjectContent(data);
        } else {
            showSubjectContentError();
        }
    })
    .catch(error => {
        console.error('Error generating subject content:', error);
        showSubjectContentError();
    });
    
    // Also generate subject introduction
    fetch('/api/llm/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: subjectQuestion,
            provider: null,
            model: null,
            options: {}
        })
    })
    .then(response => response.json())
    .then(data => {
        displaySubjectIntroduction(data.content);
    })
    .catch(error => {
        console.error('Error generating subject introduction:', error);
        document.getElementById('subject-content').innerHTML = 
            `<p class="text-red-600">${TEXTS.subjectIntroductionFailed}</p>`;
    });
}

/**
 * Display subject content
 * @param {Object} data - AI generated content data
 */
function displaySubjectContent(data) {
    // Display core knowledge points
    const knowledgeContainer = document.getElementById('subject-knowledge');
    if (data.knowledge_points && data.knowledge_points.length > 0) {
        knowledgeContainer.innerHTML = '';
        data.knowledge_points.forEach(knowledge => {
            const item = document.createElement('div');
            item.className = 'bg-white p-3 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer';
            item.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="font-medium text-blue-800">${knowledge.title}</span>
                    <i class="fas fa-chevron-right text-blue-500"></i>
                </div>
                <p class="text-sm text-gray-600 mt-1">${knowledge.description || ''}</p>
            `;
            item.onclick = () => askSubjectQuestion(knowledge.title);
            knowledgeContainer.appendChild(item);
        });
    } else {
        knowledgeContainer.innerHTML = `<p class="text-gray-500">${TEXTS.noRelatedKnowledge}</p>`;
    }
    
    // Display recommended experiments
    const experimentsContainer = document.getElementById('subject-experiments');
    if (data.experiments && data.experiments.length > 0) {
        experimentsContainer.innerHTML = '';
        data.experiments.forEach(experiment => {
            const item = document.createElement('div');
            item.className = 'bg-white p-3 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer';
            item.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="font-medium text-green-800">${experiment.title}</span>
                    <i class="fas fa-play-circle text-green-500"></i>
                </div>
                <p class="text-sm text-gray-600 mt-1">${experiment.description || ''}</p>
            `;
            item.onclick = () => startExperiment(experiment);
            experimentsContainer.appendChild(item);
        });
    } else {
        experimentsContainer.innerHTML = `<p class="text-gray-500">${TEXTS.noRecommendedExperiments}</p>`;
    }
    
    // Display simulation preview
    const simulationContainer = document.getElementById('subject-simulation');
    if (data.simulation && data.simulation.title) {
        simulationContainer.innerHTML = `
            <div class="bg-white p-6 rounded-lg shadow-sm">
                <h4 class="text-lg font-bold text-purple-800 mb-2">${data.simulation.title}</h4>
                <p class="text-gray-600 mb-4">${data.simulation.description || ''}</p>
                <div class="flex justify-center">
                    <button onclick="startSimulation('${data.simulation.type}')" class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg">
                        <i class="fas fa-play mr-2"></i>Start Simulation
                    </button>
                </div>
            </div>
        `;
    } else {
        simulationContainer.innerHTML = `
            <div class="text-gray-500">
                <i class="fas fa-info-circle mr-2"></i>
                ${TEXTS.noSimulationAvailable}
            </div>
        `;
    }
}

/**
 * Display subject introduction
 * @param {string} content - Subject introduction content
 */
function displaySubjectIntroduction(content) {
    const contentContainer = document.getElementById('subject-content');
    
    // Format content
    let formattedContent = content.replace(/\n/g, '<br>');
    formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formattedContent = formattedContent.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    contentContainer.innerHTML = `
        <div class="prose max-w-none">
            <h3 class="text-xl font-bold text-gray-800 mb-4">${TEXTS.subjectIntroduction}</h3>
            <div class="text-gray-700 leading-relaxed">${formattedContent}</div>
        </div>
    `;
}

/**
 * Show subject content error
 */
function showSubjectContentError() {
    document.getElementById('subject-knowledge').innerHTML = 
        `<p class="text-red-600">${TEXTS.knowledgeGenerationFailed}</p>`;
    document.getElementById('subject-experiments').innerHTML = 
        `<p class="text-red-600">${TEXTS.experimentGenerationFailed}</p>`;
    document.getElementById('subject-simulation').innerHTML = 
        `<p class="text-red-600">${TEXTS.simulationGenerationFailed}</p>`;
}

/**
 * Start subject learning
 * @param {string} subjectTitle - Subject title
 */
function startSubjectLearning(subjectTitle) {
    const question = `${TEXTS.systematicLearning} ${subjectTitle}${TEXTS.createLearningPlan}`;
    window.open(`/static/answer-en.html?q=${encodeURIComponent(question)}`, '_blank');
}

/**
 * Explore subject experiments
 * @param {string} subjectTitle - Subject title
 */
function exploreSubjectExperiments(subjectTitle) {
    const question = `${TEXTS.recommendImportantExperiments} ${subjectTitle}${TEXTS.includeObjectiveStepsResults}`;
    window.open(`/static/answer-en.html?q=${encodeURIComponent(question)}`, '_blank');
}

/**
 * Ask subject question
 * @param {string} topic - Topic or subject title
 */
function askSubjectQuestion(topic) {
    const question = `${TEXTS.explainConcepts} ${topic}`;
    window.open(`/static/answer-en.html?q=${encodeURIComponent(question)}`, '_blank');
}

/**
 * Start experiment
 * @param {Object} experiment - Experiment object
 */
function startExperiment(experiment) {
    const question = `${TEXTS.experimentDetails} ${experiment.title}`;
    window.open(`/static/answer-en.html?q=${encodeURIComponent(question)}`, '_blank');
}

/**
 * Start simulation
 * @param {string} simulationType - Simulation type
 */
function startSimulation(simulationType) {
    const question = `${TEXTS.designInteractiveSimulation} ${simulationType}${TEXTS.includeParameterControl}`;
    window.open(`/static/answer-en.html?q=${encodeURIComponent(question)}`, '_blank');
}
