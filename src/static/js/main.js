/**
 * Alethea - 高等教育知识问答平台
 * 主要JavaScript功能文件
 */

// 全局变量
const API_BASE_URL = '/api';
let currentUser = null;
let currentQuestion = null;
let currentAnswer = null;
let darkMode = false;

// DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化UI组件
    initializeUI();
    
    // 检查用户登录状态
    checkLoginStatus();
    
    // 初始化事件监听器
    setupEventListeners();
    
    // 初始化数学公式渲染
    initMathJax();
    
    // 初始化代码高亮
    initCodeHighlighting();
    
    // 初始化图表
    initCharts();
    
    // 初始化电路仿真
    initCircuitSimulation();
    
    // 初始化语言切换
    initLanguageSwitcher();
});

/**
 * 语言切换功能
 */
function switchLanguage() {
    // 检测当前页面语言
    const currentLang = document.documentElement.lang;
    
    if (currentLang === 'zh-CN') {
        // 切换到英文版
        window.location.href = '/static/index-en.html';
    } else {
        // 切换到中文版
        window.location.href = '/static/index.html';
    }
}

/**
 * 初始化语言切换器
 */
function initLanguageSwitcher() {
    // 语言切换器已经在HTML中通过onclick属性绑定了switchLanguage函数
    // 这里可以添加其他语言相关的初始化逻辑
    
    // 检查URL参数中是否有语言偏好
    const urlParams = new URLSearchParams(window.location.search);
    const langParam = urlParams.get('lang');
    
    if (langParam) {
        localStorage.setItem('preferredLanguage', langParam);
        
        // 如果URL参数与当前页面语言不匹配，则重定向
        const currentLang = document.documentElement.lang;
        if ((langParam === 'en' && currentLang === 'zh-CN') || 
            (langParam === 'zh' && currentLang === 'en')) {
            switchLanguage();
        }
    }
    
    // 从本地存储获取语言偏好
    const preferredLang = localStorage.getItem('preferredLanguage');
    if (preferredLang) {
        const currentLang = document.documentElement.lang;
        if ((preferredLang === 'en' && currentLang === 'zh-CN') || 
            (preferredLang === 'zh' && currentLang === 'en')) {
            // 可以选择是否自动切换，这里注释掉避免无限重定向
            // switchLanguage();
        }
    }
}

/**
 * 初始化UI组件
 */
function initializeUI() {
    // 移动菜单切换
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // 用户下拉菜单切换
    const userMenuButton = document.getElementById('user-menu-button');
    const userDropdown = document.getElementById('user-dropdown');
    const guestDropdown = document.getElementById('guest-dropdown');
    
    if (userMenuButton) {
        userMenuButton.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // 根据登录状态显示不同的下拉菜单
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
        
        // 点击其他地方关闭下拉菜单
        document.addEventListener('click', function() {
            if (userDropdown && !userDropdown.classList.contains('hidden')) {
                userDropdown.classList.add('hidden');
            }
            if (guestDropdown && !guestDropdown.classList.contains('hidden')) {
                guestDropdown.classList.add('hidden');
            }
        });
    }
    
    // 暗黑模式切换
    const themeToggle = document.getElementById('theme-toggle');
    
    if (themeToggle) {
        // 检查本地存储中的主题偏好
        darkMode = localStorage.getItem('darkMode') === 'true';
        
        // 应用主题
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
            
            // 保存主题偏好到本地存储
            localStorage.setItem('darkMode', darkMode);
        });
    }
}

/**
 * 检查用户登录状态
 */
function checkLoginStatus() {
    // 从本地存储获取令牌
    const token = localStorage.getItem('authToken');
    
    if (token) {
        // 验证令牌有效性
        fetch(`${API_BASE_URL}/user/profile`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                // 令牌无效，清除本地存储
                localStorage.removeItem('authToken');
                throw new Error('Invalid token');
            }
        })
        .then(data => {
            // 更新当前用户信息
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
 * 更新用户界面
 * @param {Object|null} user - 用户信息对象或null表示未登录
 */
function updateUserUI(user) {
    const userMenuText = document.getElementById('user-menu-text');
    const userDropdown = document.getElementById('user-dropdown');
    const guestDropdown = document.getElementById('guest-dropdown');
    const userName = document.getElementById('user-name');
    const userEmail = document.getElementById('user-email');
    
    if (userMenuText) {
        if (user) {
            // 用户已登录
            userMenuText.textContent = user.username;
            
            // 更新用户信息
            if (userName) userName.textContent = user.username;
            if (userEmail) userEmail.textContent = user.email;
            
            // 显示用户下拉菜单，隐藏访客下拉菜单
            if (userDropdown) userDropdown.classList.remove('hidden');
            if (guestDropdown) guestDropdown.classList.add('hidden');
            
            // 添加退出登录事件
            const logoutLink = document.getElementById('logout-link');
            if (logoutLink) {
                logoutLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    logout();
                });
            }
            
        } else {
            // 用户未登录
            userMenuText.textContent = '登录/注册';
            
            // 显示访客下拉菜单，隐藏用户下拉菜单
            if (guestDropdown) guestDropdown.classList.remove('hidden');
            if (userDropdown) userDropdown.classList.add('hidden');
        }
    }
}

/**
 * 设置事件监听器
 */
function setupEventListeners() {
    // 提交问题按钮
    const submitButton = document.getElementById('submit-question');
    const questionInput = document.getElementById('question-input');
    
    if (submitButton && questionInput) {
        submitButton.addEventListener('click', function() {
            const question = questionInput.value.trim();
            
            if (question) {
                submitQuestion(question);
            } else {
                showNotification('请输入问题', 'error');
            }
        });
        
        // 按Enter键提交问题
        questionInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                submitButton.click();
            }
        });
    }
    
    // 回答评价按钮
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
    
    // 学科卡片点击事件
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
 * 提交问题到服务器
 * @param {string} question - 问题文本
 */
function submitQuestion(question) {
    // 显示加载状态
    showLoading(true);
    
    // 保存当前问题到localStorage
    localStorage.setItem('currentQuestion', question);
    
    // 在新窗口打开回答页面
    window.open(`/static/answer.html?q=${encodeURIComponent(question)}`, '_blank');
    
    // 隐藏加载状态
    showLoading(false);
}

/**
 * 显示回答
 * @param {Object} answerData - 回答数据
 */
function displayAnswer(answerData) {
    const answerSection = document.getElementById('answer-section');
    const answerContent = document.getElementById('answer-content');
    const answerModel = document.getElementById('answer-model');
    
    if (answerSection && answerContent) {
        // 设置回答内容
        answerContent.innerHTML = `<div class="prose max-w-none">${answerData.content.replace(/\n/g, '<br>')}</div>`;
        
        // 隐藏模型信息（不显示提供商）
        if (answerModel) {
            answerModel.parentElement.style.display = 'none';
        }
        
        // 显示回答部分
        answerSection.classList.remove('hidden');
        
        // 添加动画效果
        answerSection.classList.add('fade-in');
        
        // 滚动到回答部分
        answerSection.scrollIntoView({ behavior: 'smooth' });
        
        // 重新渲染数学公式
        if (window.MathJax) {
            MathJax.typesetPromise([answerContent]).catch((err) => console.log(err.message));
        }
        
        // 重新应用代码高亮
        if (window.hljs) {
            answerContent.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
        }
        
        // 初始化相关知识点和推荐实验
        updateRelatedContent(answerData);
    }
}

/**
 * 更新相关内容
 * @param {Object} answerData - 回答数据
 */
function updateRelatedContent(answerData) {
    // 如果回答数据包含相关知识点和推荐实验，则更新UI
    if (answerData.related_knowledge && answerData.related_experiments) {
        // 更新相关知识点
        const knowledgeList = document.querySelector('.answer-card + .grid > div:first-child ul');
        if (knowledgeList) {
            knowledgeList.innerHTML = '';
            
            answerData.related_knowledge.forEach(item => {
                const li = document.createElement('li');
                li.className = 'p-3 bg-blue-50 rounded-lg';
                li.innerHTML = `
                    <a href="/knowledge/${item.id}" class="flex justify-between items-center">
                        <span>${item.title}</span>
                        <i class="fas fa-chevron-right text-blue-500"></i>
                    </a>
                `;
                knowledgeList.appendChild(li);
            });
        }
        
        // 更新推荐实验
        const experimentList = document.querySelector('.answer-card + .grid > div:last-child ul');
        if (experimentList) {
            experimentList.innerHTML = '';
            
            answerData.related_experiments.forEach(item => {
                const li = document.createElement('li');
                li.className = 'p-3 bg-green-50 rounded-lg';
                li.innerHTML = `
                    <a href="/simulation/${item.id}" class="flex justify-between items-center">
                        <span>${item.title}</span>
                        <i class="fas fa-flask text-green-500"></i>
                    </a>
                `;
                experimentList.appendChild(li);
            });
        }
    }
}

/**
 * 记录问题到历史记录
 * @param {Object} question - 问题对象
 * @param {Object} answer - 回答对象
 */
function recordQuestionToHistory(question, answer) {
    fetch(`${API_BASE_URL}/user/questions`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
            question: question.text,
            answer: answer.content
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to record question');
        }
    })
    .catch(error => {
        console.error('Error recording question to history:', error);
    });
}

/**
 * 评价回答
 * @param {string} answerId - 回答ID
 * @param {boolean} isHelpful - 是否有帮助
 */
function rateAnswer(answerId, isHelpful) {
    // 如果用户未登录，提示登录
    if (!currentUser) {
        showNotification('请先登录后再评价', 'info');
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
            showNotification('感谢您的反馈！', 'success');
        } else {
            throw new Error('Failed to rate answer');
        }
    })
    .catch(error => {
        console.error('Error rating answer:', error);
        showNotification('评价提交失败，请稍后再试', 'error');
    });
}

/**
 * 显示登录模态框
 */
function showLoginModal() {
    // 创建模态框
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="fixed inset-0 bg-black opacity-50"></div>
        <div class="bg-white rounded-lg shadow-xl z-10 w-full max-w-md p-6 relative">
            <button class="absolute top-4 right-4 text-gray-500 hover:text-gray-700" id="close-modal">
                <i class="fas fa-times"></i>
            </button>
            <h2 class="text-2xl font-bold mb-6">登录</h2>
            <form id="login-form">
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
                        用户名或邮箱
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="username" type="text" placeholder="请输入用户名或邮箱">
                </div>
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                        密码
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="password" type="password" placeholder="请输入密码">
                </div>
                <div class="flex items-center justify-between">
                    <button class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit">
                        登录
                    </button>
                    <a class="inline-block align-baseline font-bold text-sm text-blue-600 hover:text-blue-800" href="#" id="forgot-password">
                        忘记密码？
                    </a>
                </div>
                <div class="mt-4 text-center">
                    <p>还没有账号？ <a href="#" class="text-blue-600 hover:text-blue-800" id="switch-to-register">立即注册</a></p>
                </div>
            </form>
        </div>
    `;
    
    // 添加到文档
    document.body.appendChild(modal);
    
    // 关闭模态框
    document.getElementById('close-modal').addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // 切换到注册
    document.getElementById('switch-to-register').addEventListener('click', function(e) {
        e.preventDefault();
        document.body.removeChild(modal);
        showRegisterModal();
    });
    
    // 忘记密码
    document.getElementById('forgot-password').addEventListener('click', function(e) {
        e.preventDefault();
        document.body.removeChild(modal);
        showForgotPasswordModal();
    });
    
    // 提交登录表单
    document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        if (!username || !password) {
            showNotification('请填写所有必填字段', 'error');
            return;
        }
        
        // 发送登录请求
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
            // 保存令牌到本地存储
            localStorage.setItem('authToken', data.token);
            
            // 更新当前用户
            currentUser = data.user;
            
            // 更新UI
            updateUserUI(currentUser);
            
            // 关闭模态框
            document.body.removeChild(modal);
            
            // 显示成功消息
            showNotification('登录成功！', 'success');
        })
        .catch(error => {
            console.error('Error logging in:', error);
            showNotification('登录失败，请检查用户名和密码', 'error');
        });
    });
}

/**
 * 显示注册模态框
 */
function showRegisterModal() {
    // 创建模态框
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="fixed inset-0 bg-black opacity-50"></div>
        <div class="bg-white rounded-lg shadow-xl z-10 w-full max-w-md p-6 relative">
            <button class="absolute top-4 right-4 text-gray-500 hover:text-gray-700" id="close-modal">
                <i class="fas fa-times"></i>
            </button>
            <h2 class="text-2xl font-bold mb-6">注册</h2>
            <form id="register-form">
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
                        用户名
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="username" type="text" placeholder="请输入用户名">
                </div>
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="email">
                        邮箱
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="email" type="email" placeholder="请输入邮箱">
                </div>
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                        密码
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="password" type="password" placeholder="请输入密码">
                </div>
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="confirm-password">
                        确认密码
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="confirm-password" type="password" placeholder="请再次输入密码">
                </div>
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2">
                        角色
                    </label>
                    <div class="flex space-x-4">
                        <label class="inline-flex items-center">
                            <input type="radio" class="form-radio" name="role" value="student" checked>
                            <span class="ml-2">学生</span>
                        </label>
                        <label class="inline-flex items-center">
                            <input type="radio" class="form-radio" name="role" value="teacher">
                            <span class="ml-2">教师</span>
                        </label>
                    </div>
                </div>
                <div class="flex items-center justify-between">
                    <button class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit">
                        注册
                    </button>
                </div>
                <div class="mt-4 text-center">
                    <p>已有账号？ <a href="#" class="text-blue-600 hover:text-blue-800" id="switch-to-login">立即登录</a></p>
                </div>
            </form>
        </div>
    `;
    
    // 添加到文档
    document.body.appendChild(modal);
    
    // 关闭模态框
    document.getElementById('close-modal').addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // 切换到登录
    document.getElementById('switch-to-login').addEventListener('click', function(e) {
        e.preventDefault();
        document.body.removeChild(modal);
        showLoginModal();
    });
    
    // 提交注册表单
    document.getElementById('register-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        const role = document.querySelector('input[name="role"]:checked').value;
        
        if (!username || !email || !password || !confirmPassword) {
            showNotification('请填写所有必填字段', 'error');
            return;
        }
        
        if (password !== confirmPassword) {
            showNotification('两次输入的密码不一致', 'error');
            return;
        }
        
        // 发送注册请求
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
            // 关闭模态框
            document.body.removeChild(modal);
            
            // 显示成功消息
            showNotification('注册成功！请登录', 'success');
            
            // 显示登录模态框
            showLoginModal();
        })
        .catch(error => {
            console.error('Error registering:', error);
            showNotification('注册失败，请稍后再试', 'error');
        });
    });
}

/**
 * 显示忘记密码模态框
 */
function showForgotPasswordModal() {
    // 创建模态框
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="fixed inset-0 bg-black opacity-50"></div>
        <div class="bg-white rounded-lg shadow-xl z-10 w-full max-w-md p-6 relative">
            <button class="absolute top-4 right-4 text-gray-500 hover:text-gray-700" id="close-modal">
                <i class="fas fa-times"></i>
            </button>
            <h2 class="text-2xl font-bold mb-6">重置密码</h2>
            <p class="mb-4">请输入您的邮箱，我们将向您发送密码重置链接。</p>
            <form id="forgot-password-form">
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="email">
                        邮箱
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="email" type="email" placeholder="请输入邮箱">
                </div>
                <div class="flex items-center justify-between">
                    <button class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit">
                        发送重置链接
                    </button>
                    <a class="inline-block align-baseline font-bold text-sm text-blue-600 hover:text-blue-800" href="#" id="back-to-login">
                        返回登录
                    </a>
                </div>
            </form>
        </div>
    `;
    
    // 添加到文档
    document.body.appendChild(modal);
    
    // 关闭模态框
    document.getElementById('close-modal').addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // 返回登录
    document.getElementById('back-to-login').addEventListener('click', function(e) {
        e.preventDefault();
        document.body.removeChild(modal);
        showLoginModal();
    });
    
    // 提交忘记密码表单
    document.getElementById('forgot-password-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        
        if (!email) {
            showNotification('请输入邮箱', 'error');
            return;
        }
        
        // 发送忘记密码请求
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
                // 关闭模态框
                document.body.removeChild(modal);
                
                // 显示成功消息
                showNotification('重置链接已发送到您的邮箱，请查收', 'success');
            } else {
                throw new Error('Failed to send reset link');
            }
        })
        .catch(error => {
            console.error('Error sending reset link:', error);
            showNotification('发送重置链接失败，请稍后再试', 'error');
        });
    });
}

/**
 * 退出登录
 */
function logout() {
    // 清除本地存储中的令牌
    localStorage.removeItem('authToken');
    
    // 更新当前用户
    currentUser = null;
    
    // 更新UI
    updateUserUI(null);
    
    // 显示成功消息
    showNotification('已成功退出登录', 'success');
}

/**
 * 显示通知
 * @param {string} message - 通知消息
 * @param {string} type - 通知类型（success, error, info, warning）
 */
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = 'fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transition-all duration-300 transform translate-y-full opacity-0';
    
    // 设置通知类型样式
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
    
    // 添加到文档
    document.body.appendChild(notification);
    
    // 显示通知
    setTimeout(() => {
        notification.classList.remove('translate-y-full', 'opacity-0');
    }, 10);
    
    // 3秒后隐藏通知
    setTimeout(() => {
        notification.classList.add('translate-y-full', 'opacity-0');
        
        // 动画结束后移除元素
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

/**
 * 显示/隐藏加载状态
 * @param {boolean} show - 是否显示加载状态
 */
function showLoading(show) {
    // 如果已存在加载指示器，则移除
    const existingLoader = document.getElementById('loading-indicator');
    if (existingLoader) {
        document.body.removeChild(existingLoader);
    }
    
    if (show) {
        // 创建加载指示器
        const loader = document.createElement('div');
        loader.id = 'loading-indicator';
        loader.className = 'fixed inset-0 flex items-center justify-center z-50';
        loader.innerHTML = `
            <div class="fixed inset-0 bg-black opacity-30"></div>
            <div class="bg-white rounded-lg shadow-xl z-10 p-6 flex flex-col items-center">
                <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mb-4"></div>
                <p class="text-gray-700">正在思考中，请稍候...</p>
            </div>
        `;
        
        // 添加到文档
        document.body.appendChild(loader);
    }
}

/**
 * 初始化MathJax
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
 * 初始化代码高亮
 */
function initCodeHighlighting() {
    if (window.hljs) {
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }
}

/**
 * 初始化图表
 */
function initCharts() {
    // 绘制电路示例
    const circuitCanvas = document.getElementById('circuit-example');
    if (circuitCanvas && circuitCanvas.getContext) {
        const ctx = circuitCanvas.getContext('2d');
        
        // 绘制电池
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
        
        // 绘制电阻
        // R1
        ctx.beginPath();
        ctx.moveTo(50, 30);
        ctx.lineTo(150, 30);
        ctx.stroke();
        ctx.fillText("R1", 90, 25);
        
        // 绘制R1的锯齿形
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
        
        // 绘制R2的锯齿形
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
        
        // 绘制R3的锯齿形
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
        
        // 绘制电流方向
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
    
    // 绘制仿真结果
    const resultCanvas = document.getElementById('simulation-result');
    if (resultCanvas && resultCanvas.getContext) {
        const ctx = resultCanvas.getContext('2d');
        
        // 设置图表背景
        ctx.fillStyle = '#f8f9fa';
        ctx.fillRect(0, 0, 600, 150);
        
        // 绘制坐标轴
        ctx.beginPath();
        ctx.moveTo(50, 20);
        ctx.lineTo(50, 130);
        ctx.lineTo(550, 130);
        ctx.strokeStyle = '#333';
        ctx.stroke();
        
        // 标记坐标轴
        ctx.fillStyle = '#333';
        ctx.font = '12px Arial';
        ctx.fillText('电压 (V)', 20, 75);
        ctx.fillText('时间 (ms)', 300, 145);
        
        // 绘制网格
        ctx.beginPath();
        ctx.strokeStyle = '#ddd';
        for (let i = 50; i <= 550; i += 50) {
            ctx.moveTo(i, 20);
            ctx.lineTo(i, 130);
        }
        for (let i = 30; i <= 130; i += 20) {
            ctx.moveTo(50, i);
            ctx.lineTo(550, i);
        }
        ctx.stroke();
        
        // 绘制正弦波
        ctx.beginPath();
        ctx.strokeStyle = '#0066cc';
        ctx.lineWidth = 2;
        for (let x = 0; x <= 500; x++) {
            const y = 75 + 50 * Math.sin(x * 0.02);
            if (x === 0) {
                ctx.moveTo(x + 50, y);
            } else {
                ctx.lineTo(x + 50, y);
            }
        }
        ctx.stroke();
        
        // 绘制图例
        ctx.fillStyle = '#0066cc';
        ctx.fillRect(450, 30, 20, 10);
        ctx.fillStyle = '#333';
        ctx.fillText('电压波形', 475, 38);
    }
}

/**
 * 初始化电路仿真
 */
function initCircuitSimulation() {
    // 这里可以添加电路仿真的初始化代码
    // 例如，设置拖放功能，初始化仿真引擎等
    
    // 由于完整的电路仿真需要更复杂的实现，这里只是一个示例框架
    const componentItems = document.querySelectorAll('.component-item');
    const simulationCanvas = document.querySelector('.simulation-canvas');
    
    if (componentItems && simulationCanvas) {
        componentItems.forEach(item => {
            item.addEventListener('click', function() {
                const componentName = this.querySelector('span').textContent;
                showNotification(`选择了组件：${componentName}`, 'info');
                
                // 在实际实现中，这里会创建组件并添加到仿真画布
            });
        });
    }
}

/**
 * 显示学科模态框
 * @param {string} subjectTitle - 学科标题
 * @param {string} subjectDescription - 学科描述
 */
function showSubjectModal(subjectTitle, subjectDescription) {
    // 创建模态框
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
                        <span class="text-gray-600">AI正在生成${subjectTitle}相关内容...</span>
                    </div>
                </div>
                
                <!-- Knowledge Points Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <!-- Core Knowledge -->
                    <div class="bg-blue-50 rounded-lg p-6">
                        <h3 class="text-xl font-bold text-blue-800 mb-4">
                            <i class="fas fa-book mr-2"></i>核心知识点
                        </h3>
                        <div id="subject-knowledge" class="space-y-3">
                            <div class="flex items-center justify-center py-4">
                                <div class="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-600 mr-2"></div>
                                <span class="text-gray-600">加载中...</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Recommended Experiments -->
                    <div class="bg-green-50 rounded-lg p-6">
                        <h3 class="text-xl font-bold text-green-800 mb-4">
                            <i class="fas fa-flask mr-2"></i>推荐实验
                        </h3>
                        <div id="subject-experiments" class="space-y-3">
                            <div class="flex items-center justify-center py-4">
                                <div class="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-green-600 mr-2"></div>
                                <span class="text-gray-600">加载中...</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Interactive Simulation Preview -->
                <div class="bg-purple-50 rounded-lg p-6">
                    <h3 class="text-xl font-bold text-purple-800 mb-4">
                        <i class="fas fa-cogs mr-2"></i>交互式仿真预览
                    </h3>
                    <div id="subject-simulation" class="text-center py-8">
                        <div class="flex items-center justify-center mb-4">
                            <div class="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-purple-600 mr-2"></div>
                            <span class="text-gray-600">AI正在设计仿真实验...</span>
                        </div>
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div class="flex justify-center space-x-4 mt-8">
                    <button onclick="startSubjectLearning('${subjectTitle}')" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                        <i class="fas fa-play mr-2"></i>开始学习
                    </button>
                    <button onclick="exploreSubjectExperiments('${subjectTitle}')" class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                        <i class="fas fa-flask mr-2"></i>探索实验
                    </button>
                    <button onclick="askSubjectQuestion('${subjectTitle}')" class="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                        <i class="fas fa-question-circle mr-2"></i>提问学习
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // 添加到文档
    document.body.appendChild(modal);
    
    // 关闭模态框事件
    document.getElementById('close-subject-modal').addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // 点击背景关闭模态框
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
    
    // 生成学科相关内容
    generateSubjectContent(subjectTitle, subjectDescription);
}

/**
 * 生成学科相关内容
 * @param {string} subjectTitle - 学科标题
 * @param {string} subjectDescription - 学科描述
 */
function generateSubjectContent(subjectTitle, subjectDescription) {
    // 构建学科介绍问题
    const subjectQuestion = `请详细介绍${subjectTitle}学科，包括主要学习内容、核心概念和应用领域。${subjectDescription}`;
    
    // 调用AI生成相关内容
    fetch('/api/llm/generate-related-content', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: subjectQuestion,
            answer: `${subjectTitle}是一门重要的工程学科，${subjectDescription}。该学科涵盖了理论学习和实践应用两个方面。`
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
    
    // 同时生成学科介绍
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
            '<p class="text-red-600">学科介绍生成失败，请稍后重试</p>';
    });
}

/**
 * 显示学科内容
 * @param {Object} data - AI生成的内容数据
 */
function displaySubjectContent(data) {
    // 显示核心知识点
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
        knowledgeContainer.innerHTML = '<p class="text-gray-500">暂无相关知识点</p>';
    }
    
    // 显示推荐实验
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
        experimentsContainer.innerHTML = '<p class="text-gray-500">暂无推荐实验</p>';
    }
    
    // 显示仿真预览
    const simulationContainer = document.getElementById('subject-simulation');
    if (data.simulation && data.simulation.title) {
        simulationContainer.innerHTML = `
            <div class="bg-white p-6 rounded-lg shadow-sm">
                <h4 class="text-lg font-bold text-purple-800 mb-2">${data.simulation.title}</h4>
                <p class="text-gray-600 mb-4">${data.simulation.description || ''}</p>
                <div class="flex justify-center">
                    <button onclick="startSimulation('${data.simulation.type}')" class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg">
                        <i class="fas fa-play mr-2"></i>启动仿真
                    </button>
                </div>
            </div>
        `;
    } else {
        simulationContainer.innerHTML = `
            <div class="text-gray-500">
                <i class="fas fa-info-circle mr-2"></i>
                暂无可用的仿真实验
            </div>
        `;
    }
}

/**
 * 显示学科介绍
 * @param {string} content - 学科介绍内容
 */
function displaySubjectIntroduction(content) {
    const contentContainer = document.getElementById('subject-content');
    
    // 格式化内容
    let formattedContent = content.replace(/\n/g, '<br>');
    formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formattedContent = formattedContent.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    contentContainer.innerHTML = `
        <div class="prose max-w-none">
            <h3 class="text-xl font-bold text-gray-800 mb-4">学科介绍</h3>
            <div class="text-gray-700 leading-relaxed">${formattedContent}</div>
        </div>
    `;
}

/**
 * 显示学科内容错误
 */
function showSubjectContentError() {
    document.getElementById('subject-knowledge').innerHTML = 
        '<p class="text-red-600">知识点生成失败</p>';
    document.getElementById('subject-experiments').innerHTML = 
        '<p class="text-red-600">实验推荐生成失败</p>';
    document.getElementById('subject-simulation').innerHTML = 
        '<p class="text-red-600">仿真设计生成失败</p>';
}

/**
 * 开始学科学习
 * @param {string} subjectTitle - 学科标题
 */
function startSubjectLearning(subjectTitle) {
    const question = `我想系统学习${subjectTitle}，请为我制定一个详细的学习计划`;
    window.open(`/static/answer.html?q=${encodeURIComponent(question)}`, '_blank');
}

/**
 * 探索学科实验
 * @param {string} subjectTitle - 学科标题
 */
function exploreSubjectExperiments(subjectTitle) {
    const question = `请推荐${subjectTitle}领域的重要实验项目，包括实验目的、步骤和预期结果`;
    window.open(`/static/answer.html?q=${encodeURIComponent(question)}`, '_blank');
}

/**
 * 提问学科问题
 * @param {string} topic - 话题或学科标题
 */
function askSubjectQuestion(topic) {
    const question = `请详细解释${topic}的相关概念、原理和应用`;
    window.open(`/static/answer.html?q=${encodeURIComponent(question)}`, '_blank');
}

/**
 * 开始实验
 * @param {Object} experiment - 实验对象
 */
function startExperiment(experiment) {
    const question = `请详细介绍${experiment.title}的实验步骤、原理和注意事项`;
    window.open(`/static/answer.html?q=${encodeURIComponent(question)}`, '_blank');
}

/**
 * 启动仿真
 * @param {string} simulationType - 仿真类型
 */
function startSimulation(simulationType) {
    const question = `请设计一个${simulationType}的交互式仿真实验，包括参数控制和结果分析`;
    window.open(`/static/answer.html?q=${encodeURIComponent(question)}`, '_blank');
}
