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
document.addEventListener('DOMContentLoaded', function () {
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

    // 初始化学科探索器
    initSubjectExplorer();
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
        mobileMenuButton.addEventListener('click', function () {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // 用户下拉菜单切换
    const userMenuButton = document.getElementById('user-menu-button');
    const userDropdown = document.getElementById('user-dropdown');
    const guestDropdown = document.getElementById('guest-dropdown');

    if (userMenuButton) {
        userMenuButton.addEventListener('click', function (e) {
            e.stopPropagation();

            // 根据登录状态显示不同的下拉菜单
            if (currentUser) {
                // 用户已登录，显示用户下拉菜单
                if (userDropdown) {
                    userDropdown.classList.toggle('hidden');
                }
                if (guestDropdown && !guestDropdown.classList.contains('hidden')) {
                    guestDropdown.classList.add('hidden');
                }
            } else {
                // 用户未登录，显示访客下拉菜单
                if (guestDropdown) {
                    guestDropdown.classList.toggle('hidden');
                }
                if (userDropdown && !userDropdown.classList.contains('hidden')) {
                    userDropdown.classList.add('hidden');
                }
            }
        });

        // 点击其他地方关闭下拉菜单
        document.addEventListener('click', function () {
            if (userDropdown && !userDropdown.classList.contains('hidden')) {
                userDropdown.classList.add('hidden');
            }
            if (guestDropdown && !guestDropdown.classList.contains('hidden')) {
                guestDropdown.classList.add('hidden');
            }
        });
    }

    // 主题切换功能已在index.html中实现，这里不再重复
    // 如果需要获取主题状态，可以通过检查body的class来判断
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        // 主题切换逻辑已在index.html的内联脚本中处理
        // 这里只需要同步darkMode变量的状态
        darkMode = document.body.classList.contains('dark-mode');

        // 监听主题变化，同步darkMode变量
        const observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    darkMode = document.body.classList.contains('dark-mode');
                }
            });
        });

        observer.observe(document.body, {
            attributes: true,
            attributeFilter: ['class']
        });
    }
}

/**
 * 检查用户登录状态
 */
function checkLoginStatus() {
    // 统一使用auth_token作为存储键名
    const token = localStorage.getItem('auth_token');
    const userStr = localStorage.getItem('current_user');

    if (token && userStr) {
        try {
            // 先从本地存储获取用户信息
            currentUser = JSON.parse(userStr);
            updateUserUI(currentUser);
            
            // 触发认证状态变化事件，更新导航栏
            if (window.authManager) {
                window.authManager.currentUser = currentUser;
                window.authManager.token = token;
                window.authManager.triggerAuthEvent('login', currentUser);
            }
            
            // 异步验证令牌有效性（如果API可用）
            fetch(`${API_BASE_URL}/user/profile`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        // 如果API返回错误，但不清除本地存储（可能是API服务器问题）
                        console.warn('Token verification failed, but keeping local session');
                        return null;
                    }
                })
                .then(data => {
                    if (data) {
                        // 更新当前用户信息
                        currentUser = data;
                        localStorage.setItem('current_user', JSON.stringify(currentUser));
                        updateUserUI(currentUser);
                        
                        // 触发认证状态变化事件，更新导航栏
                        if (window.authManager) {
                            window.authManager.currentUser = currentUser;
                            window.authManager.token = token;
                            window.authManager.triggerAuthEvent('login', currentUser);
                        }
                    }
                })
                .catch(error => {
                    // 网络错误或API不可用，保持本地登录状态
                    console.warn('API verification failed, keeping local session:', error);
                });
        } catch (e) {
            console.error('Error parsing user data:', e);
            localStorage.removeItem('auth_token');
            localStorage.removeItem('current_user');
            updateUserUI(null);
        }
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

            // 根据用户角色更新下拉菜单内容
            updateUserDropdownMenu(user);

            // 确保两个下拉菜单都是隐藏的（默认状态）
            if (userDropdown) userDropdown.classList.add('hidden');
            if (guestDropdown) guestDropdown.classList.add('hidden');

            // 移除之前的退出登录事件监听器，避免重复绑定
            const logoutLink = document.getElementById('logout-link');
            if (logoutLink) {
                // 克隆节点来移除所有事件监听器
                const newLogoutLink = logoutLink.cloneNode(true);
                logoutLink.parentNode.replaceChild(newLogoutLink, logoutLink);
                
                // 添加新的退出登录事件
                newLogoutLink.addEventListener('click', function (e) {
                    e.preventDefault();
                    logout();
                });
            }

        } else {
            // 用户未登录
            userMenuText.textContent = '登录/注册';

            // 确保两个下拉菜单都是隐藏的（默认状态）
            if (guestDropdown) guestDropdown.classList.add('hidden');
            if (userDropdown) userDropdown.classList.add('hidden');
        }
    }
}

/**
 * 根据用户角色更新下拉菜单内容
 * @param {Object} user - 用户信息对象
 */
function updateUserDropdownMenu(user) {
    const userDropdown = document.getElementById('user-dropdown');
    if (!userDropdown) return;

    // 保留用户信息部分
    const userInfoSection = `
        <div class="px-4 py-2 text-sm text-gray-500 border-b border-gray-100">
            <div class="font-medium" id="user-name">${user.username}</div>
            <div class="text-xs" id="user-email">${user.email}</div>
        </div>
    `;

    let menuItems = '';

    // 根据用户角色生成不同的菜单项
    if (user.role === 'student') {
        // 学生菜单：个人仪表板
        menuItems = `
            <a href="/static/dashboard.html" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                <i class="fas fa-tachometer-alt mr-2"></i>个人仪表板
            </a>
        `;
    } else if (user.role === 'teacher') {
        // 教师菜单：教师助手
        menuItems = `
            <a href="/static/teacher-dashboard.html" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                <i class="fas fa-chalkboard-teacher mr-2"></i>教师助手
            </a>
        `;
    } else if (user.role === 'admin') {
        // 管理员菜单：个人仪表板 + 教师助手
        menuItems = `
            <a href="/static/dashboard.html" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                <i class="fas fa-tachometer-alt mr-2"></i>个人仪表板
            </a>
            <a href="/static/teacher-dashboard.html" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                <i class="fas fa-chalkboard-teacher mr-2"></i>教师助手
            </a>
        `;
    }

        // 通用菜单项
        const commonItems = `
            <a href="/static/profile.html" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" id="profile-link">
                <i class="fas fa-user-circle mr-2"></i>个人资料
            </a>
            <a href="/static/settings.html" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" id="settings-link">
                <i class="fas fa-cog mr-2"></i>设置
            </a>
            <div class="border-t border-gray-100"></div>
            <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" id="logout-link">
                <i class="fas fa-sign-out-alt mr-2"></i>退出登录
            </a>
        `;

    // 更新下拉菜单内容
    userDropdown.innerHTML = userInfoSection + menuItems + commonItems;
}

/**
 * 设置事件监听器
 */
function setupEventListeners() {
    // 提交问题按钮
    const submitButton = document.getElementById('submit-question');
    const questionInput = document.getElementById('question-input');

    if (submitButton && questionInput) {
        submitButton.addEventListener('click', function () {
            const question = questionInput.value.trim();

            if (question) {
                submitQuestion(question);
            } else {
                showNotification('请输入问题', 'error');
            }
        });

        // 按Enter键提交问题
        questionInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                submitButton.click();
            }
        });
    }

    // 回答评价按钮
    const helpfulButton = document.querySelector('.answer-card button:nth-child(1)');
    const unhelpfulButton = document.querySelector('.answer-card button:nth-child(2)');

    if (helpfulButton && unhelpfulButton) {
        helpfulButton.addEventListener('click', function () {
            if (currentAnswer) {
                rateAnswer(currentAnswer.id, true);
            }
        });

        unhelpfulButton.addEventListener('click', function () {
            if (currentAnswer) {
                rateAnswer(currentAnswer.id, false);
            }
        });
    }

    // 学科卡片点击事件 - 移除这里的重复事件监听器，因为在initSubjectExplorer中已经处理了
    // const subjectCards = document.querySelectorAll('.subject-card');
    // subjectCards.forEach(card => {
    //     card.addEventListener('click', function (e) {
    //         e.preventDefault();
    //         const subjectTitle = this.querySelector('h3').textContent;
    //         const subjectDescription = this.querySelector('p').textContent;
    //         showSubjectModal(subjectTitle, subjectDescription);
    //     });
    // });
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
    document.getElementById('close-modal').addEventListener('click', function () {
        document.body.removeChild(modal);
    });

    // 切换到注册
    document.getElementById('switch-to-register').addEventListener('click', function (e) {
        e.preventDefault();
        document.body.removeChild(modal);
        showRegisterModal();
    });

    // 忘记密码
    document.getElementById('forgot-password').addEventListener('click', function (e) {
        e.preventDefault();
        document.body.removeChild(modal);
        showForgotPasswordModal();
    });

    // 提交登录表单
    document.getElementById('login-form').addEventListener('submit', function (e) {
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
    document.getElementById('close-modal').addEventListener('click', function () {
        document.body.removeChild(modal);
    });

    // 切换到登录
    document.getElementById('switch-to-login').addEventListener('click', function (e) {
        e.preventDefault();
        document.body.removeChild(modal);
        showLoginModal();
    });

    // 提交注册表单
    document.getElementById('register-form').addEventListener('submit', function (e) {
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
    document.getElementById('close-modal').addEventListener('click', function () {
        document.body.removeChild(modal);
    });

    // 返回登录
    document.getElementById('back-to-login').addEventListener('click', function (e) {
        e.preventDefault();
        document.body.removeChild(modal);
        showLoginModal();
    });

    // 提交忘记密码表单
    document.getElementById('forgot-password-form').addEventListener('submit', function (e) {
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
 * 模拟登录功能（用于演示）
 */
function simulateLogin(username, password) {
    // 模拟用户数据
    const mockUsers = {
        'student': {
            id: 1,
            username: 'student',
            email: 'student@example.com',
            role: 'student',
            name: '张同学'
        },
        'teacher': {
            id: 2,
            username: 'teacher',
            email: 'teacher@example.com',
            role: 'teacher',
            name: '李老师'
        },
        'admin': {
            id: 3,
            username: 'admin',
            email: 'admin@example.com',
            role: 'admin',
            name: '王管理员'
        }
    };

    // 检查用户名和密码（简单验证，密码为用户名）
    if (mockUsers[username] && password === username) {
        const user = mockUsers[username];
        const token = 'mock_token_' + Date.now();
        
        // 保存到本地存储
        localStorage.setItem('auth_token', token);
        localStorage.setItem('current_user', JSON.stringify(user));
        
        // 更新全局变量
        currentUser = user;
        
        // 更新UI
        updateUserUI(user);
        
        // 触发认证状态变化事件
        if (window.authManager) {
            window.authManager.currentUser = user;
            window.authManager.token = token;
            window.authManager.triggerAuthEvent('login', user);
        }
        
        return { success: true, user: user };
    } else {
        return { success: false, error: '用户名或密码错误' };
    }
}

/**
 * 退出登录
 */
function logout() {
    // 清除本地存储中的令牌
    localStorage.removeItem('auth_token');
    localStorage.removeItem('current_user');

    // 更新当前用户
    currentUser = null;

    // 更新UI
    updateUserUI(null);
    
    // 触发认证状态变化事件
    if (window.authManager) {
        window.authManager.currentUser = null;
        window.authManager.token = null;
        window.authManager.triggerAuthEvent('logout');
    }

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
            item.addEventListener('click', function () {
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
    document.getElementById('close-subject-modal').addEventListener('click', function () {
        document.body.removeChild(modal);
    });

    // 点击背景关闭模态框
    modal.addEventListener('click', function (e) {
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

/**
 * 搜索学科功能 - AI智能更新卡片
 */
function searchSubjects() {
    const searchInput = document.getElementById('subject-search');
    const searchTerm = searchInput.value.trim();

    if (!searchTerm) {
        showNotification('请输入搜索关键词', 'warning');
        return;
    }

    // 显示加载状态
    showSearchLoading(true);

    // 调用AI生成相关学科卡片集合
    generateSubjectCardsFromKeyword(searchTerm);
}

/**
 * 根据关键词生成多个相关学科卡片
 */
function generateSubjectCardsFromKeyword(keyword) {
    const question = `根据关键词"${keyword}"，生成12个相关的学科领域。每个学科包含名称和简短描述（不超过15字）。要求：
1. 直接给出答案，不要思考过程
2. 每行格式：学科名称|简短描述|图标名
3. 学科要真实存在且与关键词相关
4. 图标名从这些中选择：lightbulb,cog,chart-line,atom,brain,microchip,dna,rocket,flask,graduation-cap,search,tools,code,database,network-wired,shield-alt,robot,eye,language,infinity,link,cloud,signal,memory,broadcast-tower,solar-panel,wifi,vr-cardboard,car,server,desktop,globe,gamepad,photo-video,hand-pointer`;

    fetch('/api/llm/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question,
            provider: null,
            model: null,
            options: {}
        })
    })
        .then(response => response.json())
        .then(data => {
            const cleanContent = filterAIThinking(data.content);

            try {
                // 解析AI生成的学科数据
                const lines = cleanContent.split('\n').filter(line => line.trim());
                const subjects = [];

                lines.forEach(line => {
                    const parts = line.split('|');
                    if (parts.length >= 3) {
                        subjects.push({
                            name: parts[0].trim(),
                            description: parts[1].trim(),
                            icon: parts[2].trim()
                        });
                    }
                });

                if (subjects.length > 0) {
                    // 用新的学科卡片替换当前显示的卡片
                    replaceAllSubjectCards(subjects);

                    // 清空搜索框
                    document.getElementById('subject-search').value = '';

                    showNotification(`已更新${subjects.length}个相关学科`, 'success');
                } else {
                    showNotification('生成学科失败，请重试', 'error');
                }
            } catch (error) {
                console.error('Error parsing AI response:', error);
                showNotification('解析学科数据失败，请重试', 'error');
            }

            showSearchLoading(false);
        })
        .catch(error => {
            console.error('Error generating subjects:', error);
            showNotification('生成学科失败，请重试', 'error');
            showSearchLoading(false);
        });
}

/**
 * 显示搜索加载状态
 */
function showSearchLoading(show) {
    const searchInput = document.getElementById('subject-search');
    const searchButton = searchInput.nextElementSibling;

    if (show) {
        searchInput.disabled = true;
        searchInput.placeholder = 'AI正在生成相关学科...';
        searchButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    } else {
        searchInput.disabled = false;
        searchInput.placeholder = '搜索学科或输入关键词...';
        searchButton.innerHTML = '<i class="fas fa-plus"></i>';
    }
}

/**
 * 替换所有学科卡片
 */
function replaceAllSubjectCards(subjects) {
    const mainGrid = document.getElementById('main-grid');
    if (!mainGrid) return;

    // 添加淡出动画
    mainGrid.style.transition = 'opacity 0.5s ease';
    mainGrid.style.opacity = '0';

    setTimeout(() => {
        // 清空现有卡片
        mainGrid.innerHTML = '';

        // 创建新卡片
        subjects.forEach((subject, index) => {
            const card = document.createElement('div');
            card.className = 'subject-card glass-card';
            card.setAttribute('data-subject', subject.name);

            card.innerHTML = `
                <div class="icon-container">
                    <i class="fas fa-${subject.icon}"></i>
                </div>
                <h3>${subject.name}</h3>
                <p>${subject.description}</p>
            `;

            // 添加点击事件
            card.addEventListener('click', function (e) {
                e.preventDefault();
                const subjectName = this.getAttribute('data-subject');
                const subjectTitle = this.querySelector('h3').textContent;
                const subjectDescription = this.querySelector('p').textContent;

                // 添加点击动画效果
                this.style.transform = 'translateY(-8px) scale(0.98)';
                setTimeout(() => {
                    this.style.transform = 'translateY(-8px) scale(1.03)';
                }, 150);

                // 跳转到学科详情页面
                const encodedSubject = encodeURIComponent(subjectName);
                const encodedTitle = encodeURIComponent(subjectTitle);
                const encodedDesc = encodeURIComponent(subjectDescription);
                window.location.href = `/static/subject-detail.html?subject=${encodedSubject}&title=${encodedTitle}&desc=${encodedDesc}`;
            });

            mainGrid.appendChild(card);
        });

        // 淡入动画
        mainGrid.style.opacity = '1';
    }, 500);
}

/**
 * 生成新的学科卡片（保留原有功能）
 */
function generateSubjectCard(keyword) {
    const question = `根据关键词"${keyword}"，生成一个相关的学科领域，包括学科名称和简短描述（不超过15字）。要求：1.直接给出答案，不要思考过程 2.格式为"学科名称：简短描述" 3.学科要真实存在且与关键词相关`;

    fetch('/api/llm/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question,
            provider: null,
            model: null,
            options: {}
        })
    })
        .then(response => response.json())
        .then(data => {
            const cleanContent = filterAIThinking(data.content);
            const parts = cleanContent.split(/[：:]/);

            if (parts.length >= 2) {
                const subjectName = parts[0].trim();
                const subjectDesc = parts[1].trim();

                // 创建新的学科卡片
                createNewSubjectCard(subjectName, subjectDesc);

                // 清空搜索框
                document.getElementById('subject-search').value = '';

                showNotification(`已添加新学科：${subjectName}`, 'success');
            } else {
                showNotification('生成学科失败，请重试', 'error');
            }
        })
        .catch(error => {
            console.error('Error generating subject:', error);
            showNotification('生成学科失败，请重试', 'error');
        });
}

/**
 * 创建新的学科卡片
 */
function createNewSubjectCard(name, description) {
    const container = document.getElementById('subject-cards-container');
    const newCard = document.createElement('div');

    // 随机位置
    const randomTop = Math.random() * 80 + 10; // 10-90%
    const randomLeft = Math.random() * 80 + 10; // 10-90%

    // 随机图标
    const icons = [
        'fas fa-lightbulb', 'fas fa-cog', 'fas fa-chart-line', 'fas fa-atom',
        'fas fa-brain', 'fas fa-microchip', 'fas fa-dna', 'fas fa-rocket',
        'fas fa-flask', 'fas fa-graduation-cap', 'fas fa-search', 'fas fa-tools',
        'fas fa-code', 'fas fa-database', 'fas fa-network-wired', 'fas fa-shield-alt'
    ];
    const randomIcon = icons[Math.floor(Math.random() * icons.length)];

    newCard.className = 'subject-card glass-card';
    newCard.setAttribute('data-subject', name);
    newCard.style.top = randomTop + '%';
    newCard.style.left = randomLeft + '%';
    newCard.style.zIndex = '100'; // 确保新卡片在最上层

    newCard.innerHTML = `
                <div class="icon-container">
                    <i class="${randomIcon}"></i>
                </div>
                <h3>${name}</h3>
                <p>${description}</p>
            `;

    // 添加点击事件
    newCard.addEventListener('click', function (e) {
        e.preventDefault();
        const subjectName = this.getAttribute('data-subject');
        const subjectTitle = this.querySelector('h3').textContent;
        const subjectDescription = this.querySelector('p').textContent;

        // 添加点击动画效果
        this.style.transform = 'scale(0.95)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 150);

        // 跳转到学科详情页面
        const encodedSubject = encodeURIComponent(subjectName);
        const encodedTitle = encodeURIComponent(subjectTitle);
        const encodedDesc = encodeURIComponent(subjectDescription);
        window.location.href = `/static/subject-detail.html?subject=${encodedSubject}&title=${encodedTitle}&desc=${encodedDesc}`;
    });

    // 添加到容器
    container.appendChild(newCard);

    // 添加出现动画
    newCard.style.opacity = '0';
    newCard.style.transform = 'scale(0.5)';
    setTimeout(() => {
        newCard.style.transition = 'all 0.5s ease';
        newCard.style.opacity = '0.8';
        newCard.style.transform = 'scale(1)';
    }, 100);
}

/**
 * 过滤AI思考过程
 */
function filterAIThinking(content) {
    // 移除DeepSeek思考过程标记
    let filtered = content.replace(/<think>[\s\S]*?<\/think>/gi, '');

    // 移除其他常见的思考过程标记
    filtered = filtered.replace(/【思考】[\s\S]*?【\/思考】/gi, '');
    filtered = filtered.replace(/\[思考\][\s\S]*?\[\/思考\]/gi, '');
    filtered = filtered.replace(/思考过程：[\s\S]*?(?=\n\n|\n[^思]|$)/gi, '');
    filtered = filtered.replace(/让我思考一下[\s\S]*?(?=\n\n|\n[^让]|$)/gi, '');

    // 移除多余的空行
    filtered = filtered.replace(/\n\s*\n\s*\n/g, '\n\n');
    filtered = filtered.trim();

    return filtered;
}

/**
 * 随机刷新学科卡片
 */
function refreshSubjectCards() {
    // 每次页面加载时随机重新排列卡片位置
    const cards = document.querySelectorAll('.glass-card');
    cards.forEach(card => {
        const randomTop = Math.random() * 80 + 10;
        const randomLeft = Math.random() * 80 + 10;
        card.style.top = randomTop + '%';
        card.style.left = randomLeft + '%';
    });
}

/**
 * 初始化学科探索器
 */
function initSubjectExplorer() {
    const subjectExplorer = document.getElementById('subject-explorer');
    const mouseFollower = document.getElementById('mouse-follower');
    const subjectCards = document.querySelectorAll('.glass-card');

    if (!subjectExplorer || !mouseFollower) {
        return;
    }

    // 初始化网格滑动系统
    initGridSliding();

    // 添加搜索框回车事件
    const searchInput = document.getElementById('subject-search');
    if (searchInput) {
        searchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                searchSubjects();
            }
        });
    }

    // 为所有卡片添加点击事件
    addCardClickEvents();
}

/**
 * 初始化网格滑动系统 - 左右无限探索
 */
function initGridSliding() {
    const subjectExplorer = document.getElementById('subject-explorer');
    const mainGrid = document.getElementById('main-grid');
    const leftGrid = document.getElementById('hidden-grid-left');
    const rightGrid = document.getElementById('hidden-grid-right');

    let currentGrid = 'main';
    let isSliding = false;
    let mouseX = 0;
    let mouseY = 0;
    let animationFrame = null;

    // 边缘检测区域大小
    const edgeZone = 120;
    const triggerZone = 30;

    // 物理参数
    let velocity = 0;
    let targetPosition = 0;
    let currentPosition = 0;
    const damping = 0.85;
    const springStrength = 0.15;

    // 设置所有网格的初始CSS过渡
    [mainGrid, leftGrid, rightGrid].forEach(grid => {
        if (grid) {
            grid.style.transition = 'transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.6s ease';
        }
    });

    subjectExplorer.addEventListener('mousemove', function (e) {
        if (isSliding) return;

        const rect = subjectExplorer.getBoundingClientRect();
        mouseX = e.clientX - rect.left;
        mouseY = e.clientY - rect.top;
        const width = rect.width;

        // 计算鼠标相对位置 (0-1)
        const relativeX = mouseX / width;

        // 检测是否在边缘区域
        const isLeftEdge = mouseX < edgeZone;
        const isRightEdge = mouseX > width - edgeZone;

        // 计算边缘强度 (0-1)
        let edgeStrength = 0;
        if (isLeftEdge) {
            edgeStrength = (edgeZone - mouseX) / edgeZone;
        } else if (isRightEdge) {
            edgeStrength = (mouseX - (width - edgeZone)) / edgeZone;
        }

        // 显示边缘卡片预览（带阻尼效果）
        if (isLeftEdge && currentGrid !== 'left') {
            showEdgePreview('left', edgeStrength);
        } else if (isRightEdge && currentGrid !== 'right') {
            showEdgePreview('right', edgeStrength);
        } else if (!isLeftEdge && !isRightEdge) {
            hideEdgePreview();
        }

        // 检测是否需要滑动（更敏感的触发）
        if (isLeftEdge && mouseX < triggerZone) {
            if (currentGrid === 'main') {
                slideToGrid('left');
            } else if (currentGrid === 'right') {
                slideToGrid('left');
            }
        } else if (isRightEdge && mouseX > width - triggerZone) {
            if (currentGrid === 'main') {
                slideToGrid('right');
            } else if (currentGrid === 'left') {
                slideToGrid('right');
            }
        }
    });

    /**
     * 显示边缘预览（带物理阻尼效果）
     */
    function showEdgePreview(direction, strength = 0.3) {
        const previewOffset = 20 + (strength * 60); // 20-80% 的预览偏移

        if (direction === 'left' && currentGrid === 'main') {
            leftGrid.style.transform = `translateX(-${100 - previewOffset}%)`;
            leftGrid.style.opacity = `${0.2 + strength * 0.4}`;
            leftGrid.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.3s ease';
        } else if (direction === 'right' && currentGrid === 'main') {
            rightGrid.style.transform = `translateX(${100 - previewOffset}%)`;
            rightGrid.style.opacity = `${0.2 + strength * 0.4}`;
            rightGrid.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.3s ease';
        } else if (direction === 'right' && currentGrid === 'left') {
            mainGrid.style.transform = `translateX(${100 - previewOffset}%)`;
            mainGrid.style.opacity = `${0.2 + strength * 0.4}`;
            mainGrid.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.3s ease';
        } else if (direction === 'left' && currentGrid === 'right') {
            mainGrid.style.transform = `translateX(-${100 - previewOffset}%)`;
            mainGrid.style.opacity = `${0.2 + strength * 0.4}`;
            mainGrid.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.3s ease';
        }
    }

    /**
     * 隐藏边缘预览（带回弹效果）
     */
    function hideEdgePreview() {
        if (currentGrid === 'main') {
            leftGrid.style.transform = 'translateX(-100%)';
            leftGrid.style.opacity = '0';
            leftGrid.style.transition = 'transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.4s ease';

            rightGrid.style.transform = 'translateX(100%)';
            rightGrid.style.opacity = '0';
            rightGrid.style.transition = 'transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.4s ease';
        } else if (currentGrid === 'left') {
            mainGrid.style.transform = 'translateX(100%)';
            mainGrid.style.opacity = '0';
            mainGrid.style.transition = 'transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.4s ease';

            rightGrid.style.transform = 'translateX(100%)';
            rightGrid.style.opacity = '0';
            rightGrid.style.transition = 'transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.4s ease';
        } else if (currentGrid === 'right') {
            mainGrid.style.transform = 'translateX(-100%)';
            mainGrid.style.opacity = '0';
            mainGrid.style.transition = 'transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.4s ease';

            leftGrid.style.transform = 'translateX(-100%)';
            leftGrid.style.opacity = '0';
            leftGrid.style.transition = 'transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.4s ease';
        }
    }

    /**
     * 滑动到指定网格（带物理阻尼效果）
     */
    function slideToGrid(direction) {
        if (isSliding) return;
        isSliding = true;

        // 添加滑动音效提示（视觉反馈）
        showSlideIndicator(direction);

        // 物理滑动动画 - 使用更自然的缓动函数
        if (direction === 'left' && currentGrid === 'main') {
            // 主网格向右滑出，左网格滑入
            mainGrid.style.transform = 'translateX(100%)';
            mainGrid.style.opacity = '0';
            leftGrid.style.transform = 'translateX(0%)';
            leftGrid.style.opacity = '1';
            currentGrid = 'left';

            // 生成新的右侧内容
            generateNewGridContent('right');

        } else if (direction === 'right' && currentGrid === 'main') {
            // 主网格向左滑出，右网格滑入
            mainGrid.style.transform = 'translateX(-100%)';
            mainGrid.style.opacity = '0';
            rightGrid.style.transform = 'translateX(0%)';
            rightGrid.style.opacity = '1';
            currentGrid = 'right';

            // 生成新的左侧内容
            generateNewGridContent('left');

        } else if (direction === 'right' && currentGrid === 'left') {
            // 左网格向左滑出，主网格滑入
            leftGrid.style.transform = 'translateX(-100%)';
            leftGrid.style.opacity = '0';
            mainGrid.style.transform = 'translateX(0%)';
            mainGrid.style.opacity = '1';
            currentGrid = 'main';

        } else if (direction === 'left' && currentGrid === 'right') {
            // 右网格向右滑出，主网格滑入
            rightGrid.style.transform = 'translateX(100%)';
            rightGrid.style.opacity = '0';
            mainGrid.style.transform = 'translateX(0%)';
            mainGrid.style.opacity = '1';
            currentGrid = 'main';
        }

        // 重新绑定卡片事件
        setTimeout(() => {
            isSliding = false;
            addCardClickEvents();
        }, 800);
    }

    /**
     * 显示滑动指示器
     */
    function showSlideIndicator(direction) {
        const indicator = document.createElement('div');
        indicator.className = 'slide-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 50%;
            ${direction === 'left' ? 'left: 20px' : 'right: 20px'};
            transform: translateY(-50%);
            background: rgba(79, 172, 254, 0.9);
            color: white;
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            z-index: 1000;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            opacity: 0;
            transform: translateY(-50%) scale(0.8);
        `;
        indicator.innerHTML = `<i class="fas fa-chevron-${direction}"></i> 探索${direction === 'left' ? '左侧' : '右侧'}知识`;

        document.body.appendChild(indicator);

        // 显示动画
        setTimeout(() => {
            indicator.style.opacity = '1';
            indicator.style.transform = 'translateY(-50%) scale(1)';
        }, 10);

        // 隐藏动画
        setTimeout(() => {
            indicator.style.opacity = '0';
            indicator.style.transform = 'translateY(-50%) scale(0.8)';
            setTimeout(() => {
                document.body.removeChild(indicator);
            }, 300);
        }, 1500);
    }

    /**
     * 生成新的网格内容（AI驱动的无限探索）
     */
    function generateNewGridContent(gridSide) {
        // 这里可以调用AI生成新的学科卡片
        // 暂时使用随机重排现有卡片作为演示
        setTimeout(() => {
            const targetGrid = gridSide === 'left' ? leftGrid : rightGrid;
            if (targetGrid) {
                // 重新排列卡片位置，模拟新内容
                const cards = targetGrid.querySelectorAll('.glass-card');
                cards.forEach(card => {
                    // 添加轻微的位置变化
                    const randomOffset = (Math.random() - 0.5) * 20;
                    card.style.transform = `translateX(${randomOffset}px) translateY(${randomOffset}px)`;
                });
            }
        }, 400);
    }

    // 键盘导航支持（带阻尼效果）
    document.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            if (currentGrid === 'main') slideToGrid('left');
            else if (currentGrid === 'right') slideToGrid('left');
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            if (currentGrid === 'main') slideToGrid('right');
            else if (currentGrid === 'left') slideToGrid('right');
        }
    });

    // 鼠标离开时重置预览
    subjectExplorer.addEventListener('mouseleave', function () {
        hideEdgePreview();
    });
}

/**
 * 为卡片添加点击事件
 */
function addCardClickEvents() {
    const allCards = document.querySelectorAll('.glass-card');

    allCards.forEach(card => {
        // 移除旧的事件监听器
        card.replaceWith(card.cloneNode(true));
    });

    // 重新获取卡片并添加事件
    const newCards = document.querySelectorAll('.glass-card');
    newCards.forEach(card => {
        card.addEventListener('click', function (e) {
            e.preventDefault();
            const subjectName = this.getAttribute('data-subject');
            const subjectTitle = this.querySelector('h3').textContent;
            const subjectDescription = this.querySelector('p').textContent;

            // 添加点击动画效果
            this.style.transform = 'translateY(-8px) scale(0.98)';
            setTimeout(() => {
                this.style.transform = 'translateY(-8px) scale(1.03)';
            }, 150);

            // 跳转到学科详情页面
            const encodedSubject = encodeURIComponent(subjectName);
            const encodedTitle = encodeURIComponent(subjectTitle);
            const encodedDesc = encodeURIComponent(subjectDescription);
            window.location.href = `/static/subject-detail.html?subject=${encodedSubject}&title=${encodedTitle}&desc=${encodedDesc}`;
        });

        // 悬停效果
        card.addEventListener('mouseenter', function () {
            this.style.transition = 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        });

        card.addEventListener('mouseleave', function () {
            this.style.transition = 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        });
    });
}

/**
 * 初始化黑板公式 - 像老师写在黑板上的固定公式
 */
function initBlackboardFormulas() {
    const subjectExplorer = document.getElementById('subject-explorer');
    if (!subjectExplorer) return;

    // 定义各种学科的公式和符号
    const formulas = [
        // 大型重要公式
        { text: 'E = mc²', size: 'large', x: 5, y: 15, rotation: -2 },
        { text: 'F = ma', size: 'large', x: 85, y: 20, rotation: 1 },
        { text: 'V = IR', size: 'large', x: 15, y: 80, rotation: -1 },
        { text: '∇²φ = 0', size: 'large', x: 75, y: 85, rotation: 2 },

        // 中型公式
        { text: 'P = VI', size: 'medium', x: 25, y: 25, rotation: 0 },
        { text: 'Q = CV', size: 'medium', x: 65, y: 30, rotation: -1 },
        { text: 'τ = RC', size: 'medium', x: 35, y: 70, rotation: 1 },
        { text: 'f = 1/T', size: 'medium', x: 55, y: 75, rotation: 0 },
        { text: 'ω = 2πf', size: 'medium', x: 10, y: 45, rotation: -2 },
        { text: 'Z = R + jX', size: 'medium', x: 80, y: 50, rotation: 1 },

        // 小型符号和公式
        { text: '∫', size: 'small', x: 20, y: 35, rotation: 0 },
        { text: '∂', size: 'small', x: 40, y: 40, rotation: 0 },
        { text: '∇', size: 'small', x: 60, y: 45, rotation: 0 },
        { text: 'Σ', size: 'small', x: 30, y: 55, rotation: 0 },
        { text: 'π', size: 'small', x: 70, y: 60, rotation: 0 },
        { text: 'λ', size: 'small', x: 45, y: 20, rotation: 0 },
        { text: 'ω', size: 'small', x: 85, y: 40, rotation: 0 },
        { text: 'α', size: 'small', x: 15, y: 60, rotation: 0 },
        { text: 'β', size: 'small', x: 50, y: 90, rotation: 0 },
        { text: 'γ', size: 'small', x: 90, y: 70, rotation: 0 },
        { text: '∞', size: 'small', x: 25, y: 10, rotation: 0 },
        { text: '≈', size: 'small', x: 75, y: 15, rotation: 0 },
        { text: '≡', size: 'small', x: 35, y: 85, rotation: 0 },
        { text: '±', size: 'small', x: 65, y: 10, rotation: 0 },
        { text: '√', size: 'small', x: 5, y: 35, rotation: 0 },

        // 更多专业公式
        { text: 'sin θ', size: 'medium', x: 45, y: 15, rotation: -1, faded: true },
        { text: 'cos θ', size: 'medium', x: 85, y: 65, rotation: 1, faded: true },
        { text: 'e^(jωt)', size: 'medium', x: 15, y: 25, rotation: 0, faded: true },
        { text: 'log₂ n', size: 'medium', x: 55, y: 35, rotation: -1, faded: true },
        { text: 'lim x→0', size: 'small', x: 25, y: 65, rotation: 0, faded: true },
        { text: 'dx/dt', size: 'small', x: 75, y: 25, rotation: 0, faded: true },
        { text: '∮ E·dl', size: 'medium', x: 5, y: 70, rotation: 2, faded: true },
        { text: 'H(jω)', size: 'medium', x: 90, y: 35, rotation: -2, faded: true },

        // 机器学习相关
        { text: 'y = wx + b', size: 'medium', x: 40, y: 60, rotation: 1, faded: true },
        { text: '∂L/∂w', size: 'small', x: 60, y: 80, rotation: 0, faded: true },
        { text: 'σ(x)', size: 'small', x: 80, y: 10, rotation: 0, faded: true },

        // 量子计算
        { text: '|ψ⟩', size: 'medium', x: 10, y: 10, rotation: -1, faded: true },
        { text: 'Ĥ|ψ⟩', size: 'small', x: 90, y: 90, rotation: 1, faded: true },

        // 信号处理
        { text: 'X(ω)', size: 'small', x: 35, y: 30, rotation: 0, faded: true },
        { text: 'FFT', size: 'small', x: 65, y: 65, rotation: 0, faded: true }
    ];

    // 创建公式元素
    formulas.forEach((formula, index) => {
        const formulaElement = document.createElement('div');
        formulaElement.className = `blackboard-formula formula-${formula.size}`;
        if (formula.faded) {
            formulaElement.classList.add('formula-faded');
        }

        formulaElement.textContent = formula.text;
        formulaElement.style.left = formula.x + '%';
        formulaElement.style.top = formula.y + '%';
        formulaElement.style.transform = `rotate(${formula.rotation}deg)`;
        formulaElement.style.zIndex = '1';

        // 添加轻微的动画延迟，让公式逐渐显现
        formulaElement.style.animationDelay = (index * 0.1) + 's';

        subjectExplorer.appendChild(formulaElement);
    });
}

// 全局变量：个性化AI开关状态
let aiPersonalizationEnabled = localStorage.getItem('aiPersonalizationEnabled') !== 'false';

/**
 * 初始化个性化AI开关
 */
function initAIPersonalizationToggle() {
    const aiToggle = document.getElementById('ai-personalization-toggle');

    if (aiToggle) {
        // 设置初始状态
        updateAIToggleUI();

        // 添加点击事件
        aiToggle.addEventListener('click', function () {
            toggleAIPersonalization();
        });
    }
}

/**
 * 切换个性化AI状态
 */
function toggleAIPersonalization() {
    aiPersonalizationEnabled = !aiPersonalizationEnabled;
    localStorage.setItem('aiPersonalizationEnabled', aiPersonalizationEnabled);

    updateAIToggleUI();

    // 显示状态通知
    const status = aiPersonalizationEnabled ? '已开启' : '已关闭';
    showNotification(`个性化AI ${status}`, aiPersonalizationEnabled ? 'success' : 'info');

    // 显示详细说明
    showAIPersonalizationModal();
}

/**
 * 更新AI开关按钮UI
 */
function updateAIToggleUI() {
    const aiToggle = document.getElementById('ai-personalization-toggle');
    if (!aiToggle) return;

    const icon = aiToggle.querySelector('i');

    if (aiPersonalizationEnabled) {
        icon.className = 'fas fa-user-cog text-blue-600';
        aiToggle.title = '个性化AI已开启 - 点击关闭';
        aiToggle.style.backgroundColor = '#dbeafe';
    } else {
        icon.className = 'fas fa-user-cog text-gray-400';
        aiToggle.title = '个性化AI已关闭 - 点击开启';
        aiToggle.style.backgroundColor = '#f3f4f6';
    }
}

/**
 * 显示AI个性化说明模态框
 */
function showAIPersonalizationModal() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="fixed inset-0 bg-black opacity-50"></div>
        <div class="bg-white rounded-lg shadow-xl z-10 w-full max-w-2xl p-6 relative">
            <button class="absolute top-4 right-4 text-gray-500 hover:text-gray-700" id="close-ai-modal">
                <i class="fas fa-times"></i>
            </button>
            
            <div class="text-center mb-6">
                <div class="w-16 h-16 mx-auto mb-4 rounded-full ${aiPersonalizationEnabled ? 'bg-blue-100' : 'bg-gray-100'} flex items-center justify-center">
                    <i class="fas fa-user-cog text-2xl ${aiPersonalizationEnabled ? 'text-blue-600' : 'text-gray-400'}"></i>
                </div>
                <h2 class="text-2xl font-bold text-gray-800">个性化AI ${aiPersonalizationEnabled ? '已开启' : '已关闭'}</h2>
            </div>
            
            <div class="space-y-4 mb-6">
                <div class="bg-${aiPersonalizationEnabled ? 'blue' : 'gray'}-50 p-4 rounded-lg">
                    <h3 class="font-bold text-${aiPersonalizationEnabled ? 'blue' : 'gray'}-800 mb-2">
                        ${aiPersonalizationEnabled ? '✅ 个性化功能已激活' : '❌ 个性化功能已禁用'}
                    </h3>
                    <p class="text-${aiPersonalizationEnabled ? 'blue' : 'gray'}-700 text-sm">
                        ${aiPersonalizationEnabled
            ? 'AI将根据您的偏好和知识库提供个性化回答'
            : 'AI将使用默认设置，不会访问您的个人偏好和知识库'}
                    </p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="border rounded-lg p-4">
                        <h4 class="font-semibold text-gray-800 mb-2">🎯 回答风格</h4>
                        <p class="text-sm text-gray-600">
                            ${aiPersonalizationEnabled
            ? '根据您设置的风格（详细/简洁/学术/轻松）调整回答'
            : '使用标准回答风格'}
                        </p>
                    </div>
                    
                    <div class="border rounded-lg p-4">
                        <h4 class="font-semibold text-gray-800 mb-2">📚 知识库集成</h4>
                        <p class="text-sm text-gray-600">
                            ${aiPersonalizationEnabled
            ? '自动搜索您的个人文档，提供相关引用'
            : '不会访问您的个人知识库'}
                        </p>
                    </div>
                    
                    <div class="border rounded-lg p-4">
                        <h4 class="font-semibold text-gray-800 mb-2">🤖 AI模型选择</h4>
                        <p class="text-sm text-gray-600">
                            ${aiPersonalizationEnabled
            ? '使用您偏好的AI模型和参数设置'
            : '使用系统默认AI模型'}
                        </p>
                    </div>
                    
                    <div class="border rounded-lg p-4">
                        <h4 class="font-semibold text-gray-800 mb-2">📏 回答长度</h4>
                        <p class="text-sm text-gray-600">
                            ${aiPersonalizationEnabled
            ? '根据您设置的偏好调整回答详细程度'
            : '使用标准回答长度'}
                        </p>
                    </div>
                </div>
            </div>
            
            <div class="flex justify-center space-x-4">
                <button onclick="testAIPersonalization()" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg">
                    <i class="fas fa-flask mr-2"></i>测试个性化效果
                </button>
                <button onclick="openPersonalKnowledge()" class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg">
                    <i class="fas fa-cog mr-2"></i>个性化设置
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // 关闭模态框
    document.getElementById('close-ai-modal').addEventListener('click', function () {
        document.body.removeChild(modal);
    });

    // 点击背景关闭
    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

/**
 * 测试AI个性化效果
 */
function testAIPersonalization() {
    // 关闭当前模态框
    const modal = document.querySelector('.fixed.inset-0');
    if (modal) {
        document.body.removeChild(modal);
    }

    // 生成测试问题
    const testQuestions = [
        '请解释电路中的基尔霍夫定律',
        '什么是运算放大器的虚短虚断',
        '如何分析RC电路的频率响应',
        '请介绍数字电路中的逻辑门',
        '什么是控制系统的稳定性'
    ];

    const randomQuestion = testQuestions[Math.floor(Math.random() * testQuestions.length)];

    // 在问题输入框中填入测试问题
    const questionInput = document.getElementById('question-input');
    if (questionInput) {
        questionInput.value = randomQuestion;
        questionInput.focus();
    }

    showNotification(`已填入测试问题，点击"搜索答案"查看${aiPersonalizationEnabled ? '个性化' : '标准'}效果`, 'info');
}

/**
 * 打开个人知识库设置
 */
function openPersonalKnowledge() {
    window.open('/static/personal-knowledge.html', '_blank');
}

/**
 * 获取AI个性化状态（供其他模块使用）
 */
function getAIPersonalizationStatus() {
    return aiPersonalizationEnabled;
}

// 在DOM加载完成后初始化个性化开关
document.addEventListener('DOMContentLoaded', function () {
    initAIPersonalizationToggle();
    initQuickLoginTest();
});

/**
 * 初始化快速登录测试功能
 */
function initQuickLoginTest() {
    const quickLoginButton = document.getElementById('quick-login-test');
    
    if (quickLoginButton) {
        // 只在开发环境显示快速登录按钮
        const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        if (isDevelopment) {
            quickLoginButton.style.display = 'block';
        }
        
        quickLoginButton.addEventListener('click', function() {
            showQuickLoginModal();
        });
    }
}

/**
 * 显示快速登录测试模态框
 */
function showQuickLoginModal() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="fixed inset-0 bg-black opacity-50"></div>
        <div class="bg-white rounded-lg shadow-xl z-10 w-full max-w-md p-6 relative">
            <button class="absolute top-4 right-4 text-gray-500 hover:text-gray-700" id="close-quick-login">
                <i class="fas fa-times"></i>
            </button>
            
            <div class="text-center mb-6">
                <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 flex items-center justify-center">
                    <i class="fas fa-user-check text-2xl text-green-600"></i>
                </div>
                <h2 class="text-2xl font-bold text-gray-800">快速登录测试</h2>
                <p class="text-gray-600 mt-2">选择一个测试账户快速体验登录功能</p>
            </div>
            
            <div class="space-y-3">
                <button onclick="quickLogin('student')" class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg flex items-center justify-center">
                    <i class="fas fa-graduation-cap mr-2"></i>
                    学生账户 (student)
                </button>
                <button onclick="quickLogin('teacher')" class="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-lg flex items-center justify-center">
                    <i class="fas fa-chalkboard-teacher mr-2"></i>
                    教师账户 (teacher)
                </button>
                <button onclick="quickLogin('admin')" class="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 px-4 rounded-lg flex items-center justify-center">
                    <i class="fas fa-user-shield mr-2"></i>
                    管理员账户 (admin)
                </button>
            </div>
            
            <div class="mt-6 text-center">
                <p class="text-sm text-gray-500">
                    <i class="fas fa-info-circle mr-1"></i>
                    这是开发环境的测试功能，密码与用户名相同
                </p>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // 关闭模态框
    document.getElementById('close-quick-login').addEventListener('click', function () {
        document.body.removeChild(modal);
    });

    // 点击背景关闭
    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

/**
 * 快速登录功能
 */
function quickLogin(userType) {
    const result = simulateLogin(userType, userType);
    
    if (result.success) {
        // 关闭模态框
        const modal = document.querySelector('.fixed.inset-0');
        if (modal) {
            document.body.removeChild(modal);
        }
        
        showNotification(`已成功登录为 ${result.user.name} (${result.user.role})`, 'success');
        
        // 显示登录成功的详细信息
        setTimeout(() => {
            showLoginSuccessInfo(result.user);
        }, 1000);
    } else {
        showNotification('登录失败：' + result.error, 'error');
    }
}

/**
 * 显示登录成功信息
 */
function showLoginSuccessInfo(user) {
    const infoModal = document.createElement('div');
    infoModal.className = 'fixed inset-0 flex items-center justify-center z-50';
    infoModal.innerHTML = `
        <div class="fixed inset-0 bg-black opacity-50"></div>
        <div class="bg-white rounded-lg shadow-xl z-10 w-full max-w-lg p-6 relative">
            <button class="absolute top-4 right-4 text-gray-500 hover:text-gray-700" id="close-success-info">
                <i class="fas fa-times"></i>
            </button>
            
            <div class="text-center mb-6">
                <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 flex items-center justify-center">
                    <i class="fas fa-check-circle text-2xl text-green-600"></i>
                </div>
                <h2 class="text-2xl font-bold text-gray-800">登录成功！</h2>
            </div>
            
            <div class="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 class="font-bold text-gray-800 mb-3">当前用户信息</h3>
                <div class="space-y-2">
                    <div class="flex justify-between">
                        <span class="text-gray-600">用户名：</span>
                        <span class="font-medium">${user.username}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">姓名：</span>
                        <span class="font-medium">${user.name}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">邮箱：</span>
                        <span class="font-medium">${user.email}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">角色：</span>
                        <span class="font-medium ${user.role === 'teacher' ? 'text-green-600' : user.role === 'admin' ? 'text-purple-600' : 'text-blue-600'}">${user.role === 'teacher' ? '教师' : user.role === 'admin' ? '管理员' : '学生'}</span>
                    </div>
                </div>
            </div>
            
            <div class="bg-blue-50 rounded-lg p-4 mb-6">
                <h3 class="font-bold text-blue-800 mb-3">界面变化</h3>
                <ul class="text-sm text-blue-700 space-y-1">
                    <li>✅ 右上角显示用户名：${user.username}</li>
                    <li>✅ 用户菜单已更新为登录状态</li>
                    <li>✅ 下拉菜单显示个人信息和操作选项</li>
                    ${user.role === 'teacher' || user.role === 'admin' ? '<li>✅ 教师助手功能已启用</li>' : ''}
                </ul>
            </div>
            
            <div class="flex justify-center space-x-3">
                <button onclick="testUserMenu()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                    <i class="fas fa-user mr-2"></i>测试用户菜单
                </button>
                ${user.role === 'teacher' || user.role === 'admin' ? 
                    '<button onclick="openTeacherDashboard()" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg"><i class="fas fa-chalkboard-teacher mr-2"></i>访问教师助手</button>' : 
                    ''
                }
            </div>
        </div>
    `;

    document.body.appendChild(infoModal);

    // 关闭模态框
    document.getElementById('close-success-info').addEventListener('click', function () {
        document.body.removeChild(infoModal);
    });

    // 点击背景关闭
    infoModal.addEventListener('click', function (e) {
        if (e.target === infoModal) {
            document.body.removeChild(infoModal);
        }
    });
}

/**
 * 测试用户菜单
 */
function testUserMenu() {
    // 关闭当前模态框
    const modal = document.querySelector('.fixed.inset-0');
    if (modal) {
        document.body.removeChild(modal);
    }
    
    // 模拟点击用户菜单按钮
    const userMenuButton = document.getElementById('user-menu-button');
    if (userMenuButton) {
        userMenuButton.click();
        showNotification('用户菜单已打开，请查看右上角', 'info');
    }
}

/**
 * 打开教师助手
 */
function openTeacherDashboard() {
    window.open('/static/teacher-dashboard.html', '_blank');
}
