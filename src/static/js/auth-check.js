/**
 * 用户权限检查模块
 * 负责验证用户身份和权限，控制页面访问
 */

class AuthManager {
    constructor() {
        this.currentUser = null;
        this.token = null;
        this.init();
    }

    init() {
        // 从localStorage获取用户信息和token
        this.token = localStorage.getItem('auth_token');
        const userStr = localStorage.getItem('current_user');
        
        if (userStr) {
            try {
                this.currentUser = JSON.parse(userStr);
            } catch (e) {
                console.error('解析用户信息失败:', e);
                this.clearAuth();
            }
        }

        // 验证token有效性
        if (this.token && this.currentUser) {
            this.verifyToken();
        }
    }

    async verifyToken() {
        try {
            const response = await fetch('/api/user/profile', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Token验证失败');
            }

            const data = await response.json();
            this.currentUser = data;
            localStorage.setItem('current_user', JSON.stringify(this.currentUser));
        } catch (error) {
            console.error('Token验证错误:', error);
            this.clearAuth();
        }
    }

    isLoggedIn() {
        return this.currentUser !== null && this.token !== null;
    }

    isTeacher() {
        return this.isLoggedIn() && this.currentUser.role === 'teacher';
    }

    isAdmin() {
        return this.isLoggedIn() && this.currentUser.role === 'admin';
    }

    isStudent() {
        return this.isLoggedIn() && this.currentUser.role === 'student';
    }

    hasPermission(permission) {
        if (!this.isLoggedIn()) {
            return false;
        }

        // 管理员拥有所有权限
        if (this.isAdmin()) {
            return true;
        }

        // 检查用户权限
        return this.currentUser.permissions && this.currentUser.permissions.includes(permission);
    }

    canAccessTeacherDashboard() {
        return this.isTeacher() || this.isAdmin();
    }

    getCurrentUser() {
        return this.currentUser;
    }

    getToken() {
        return this.token;
    }

    async login(username, password) {
        try {
            const response = await fetch('/api/user/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.token = data.token;
                this.currentUser = data.user;
                
                // 保存到localStorage
                localStorage.setItem('auth_token', this.token);
                localStorage.setItem('current_user', JSON.stringify(this.currentUser));
                
                // 触发登录事件
                this.triggerAuthEvent('login', this.currentUser);
                
                return { success: true, user: this.currentUser };
            } else {
                return { success: false, error: data.error };
            }
        } catch (error) {
            console.error('登录错误:', error);
            return { success: false, error: '网络错误，请重试' };
        }
    }

    logout() {
        this.clearAuth();
        this.triggerAuthEvent('logout');
        
        // 如果在教师助手页面，重定向到首页
        if (window.location.pathname.includes('teacher-dashboard')) {
            window.location.href = '/static/index.html';
        }
    }

    clearAuth() {
        this.currentUser = null;
        this.token = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('current_user');
    }

    triggerAuthEvent(type, data = null) {
        const event = new CustomEvent('authStateChange', {
            detail: { type, data }
        });
        window.dispatchEvent(event);
    }

    // 检查页面访问权限
    checkPageAccess(requiredRole = null, requiredPermission = null) {
        // 如果需要特定角色
        if (requiredRole) {
            if (requiredRole === 'teacher' && !this.canAccessTeacherDashboard()) {
                this.redirectToLogin('您需要教师权限才能访问此页面');
                return false;
            }
            
            if (requiredRole === 'admin' && !this.isAdmin()) {
                this.redirectToLogin('您需要管理员权限才能访问此页面');
                return false;
            }
        }

        // 如果需要特定权限
        if (requiredPermission && !this.hasPermission(requiredPermission)) {
            this.redirectToLogin('您没有访问此页面的权限');
            return false;
        }

        return true;
    }

    redirectToLogin(message = '请先登录') {
        alert(message);
        window.location.href = '/static/login.html?redirect=' + encodeURIComponent(window.location.pathname);
    }

    // 显示未授权访问提示
    showUnauthorizedMessage() {
        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        overlay.innerHTML = `
            <div class="bg-white rounded-lg p-8 max-w-md mx-4 text-center">
                <div class="text-red-500 text-6xl mb-4">
                    <i class="fas fa-lock"></i>
                </div>
                <h2 class="text-2xl font-bold text-gray-800 mb-4">访问受限</h2>
                <p class="text-gray-600 mb-6">
                    教师助手功能仅对教师和管理员开放。<br>
                    如果您是教师，请联系管理员升级您的账户权限。
                </p>
                <div class="space-y-3">
                    <button onclick="window.location.href='/static/login.html'" 
                            class="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
                        登录教师账户
                    </button>
                    <button onclick="window.location.href='/static/index.html'" 
                            class="w-full bg-gray-300 text-gray-700 py-2 px-4 rounded hover:bg-gray-400">
                        返回首页
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // 点击遮罩层关闭
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                document.body.removeChild(overlay);
            }
        });
    }
}

// 创建全局实例
window.authManager = new AuthManager();

// 导航栏权限控制
function updateNavigationByRole() {
    const teacherLink = document.querySelector('a[href="/static/teacher-dashboard.html"]');
    const mobileTeacherLink = document.querySelector('#mobile-menu a[href="/static/teacher-dashboard.html"]');
    
    // 始终显示教师助手链接，但在点击时进行权限检查
    if (teacherLink) {
        teacherLink.style.display = '';
        
        // 移除旧的事件监听器
        const newTeacherLink = teacherLink.cloneNode(true);
        teacherLink.parentNode.replaceChild(newTeacherLink, teacherLink);
        
        // 添加点击事件处理
        newTeacherLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 检查权限
            if (window.authManager.canAccessTeacherDashboard()) {
                // 有权限，直接跳转
                window.location.href = '/static/teacher-dashboard.html';
            } else {
                // 没有权限，显示登录提示或权限说明
                showTeacherAccessPrompt();
            }
        });
    }
    
    if (mobileTeacherLink) {
        mobileTeacherLink.style.display = '';
        
        // 移除旧的事件监听器
        const newMobileTeacherLink = mobileTeacherLink.cloneNode(true);
        mobileTeacherLink.parentNode.replaceChild(newMobileTeacherLink, mobileTeacherLink);
        
        // 添加点击事件处理
        newMobileTeacherLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 检查权限
            if (window.authManager.canAccessTeacherDashboard()) {
                // 有权限，直接跳转
                window.location.href = '/static/teacher-dashboard.html';
            } else {
                // 没有权限，显示登录提示或权限说明
                showTeacherAccessPrompt();
            }
        });
    }
}

// 用户菜单更新
function updateUserMenu() {
    const userMenuText = document.getElementById('user-menu-text');
    const userDropdown = document.getElementById('user-dropdown');
    const guestDropdown = document.getElementById('guest-dropdown');
    const userName = document.getElementById('user-name');
    const userEmail = document.getElementById('user-email');
    const userMenuArrow = document.getElementById('user-menu-arrow');

    if (window.authManager.isLoggedIn()) {
        const user = window.authManager.getCurrentUser();
        
        if (userMenuText) {
            userMenuText.textContent = user.username;
        }
        
        if (userName) {
            userName.textContent = user.username;
        }
        
        if (userEmail) {
            userEmail.textContent = user.email;
        }
        
        // 显示用户菜单，隐藏游客菜单
        if (userDropdown) userDropdown.classList.remove('hidden');
        if (guestDropdown) guestDropdown.classList.add('hidden');
        
        // 显示下拉箭头
        if (userMenuArrow) {
            userMenuArrow.classList.remove('hidden');
            userMenuArrow.classList.add('md:inline-block');
        }
        
        // 添加角色标识
        if (userName && user.role) {
            const roleText = {
                'teacher': '教师',
                'admin': '管理员',
                'student': '学生'
            };
            userName.innerHTML = `${user.username} <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">${roleText[user.role] || user.role}</span>`;
        }
    } else {
        if (userMenuText) {
            userMenuText.textContent = '登录/注册';
        }
        
        // 显示游客菜单，隐藏用户菜单
        if (guestDropdown) guestDropdown.classList.remove('hidden');
        if (userDropdown) userDropdown.classList.add('hidden');
        
        // 隐藏下拉箭头
        if (userMenuArrow) {
            userMenuArrow.classList.add('hidden');
            userMenuArrow.classList.remove('md:inline-block');
        }
    }
}

// 监听认证状态变化
window.addEventListener('authStateChange', function(event) {
    updateNavigationByRole();
    updateUserMenu();
});

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    updateNavigationByRole();
    updateUserMenu();
    
    // 绑定退出登录事件
    const logoutLink = document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.authManager.logout();
        });
    }
});

// 教师助手页面权限检查
function checkTeacherDashboardAccess() {
    if (window.location.pathname.includes('teacher-dashboard')) {
        // 等待authManager初始化完成
        setTimeout(() => {
            // 开发模式下允许访问，或者用户有教师权限
            const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            
            if (!isDevelopment && !window.authManager.canAccessTeacherDashboard()) {
                // 隐藏页面内容
                document.body.style.display = 'none';
                
                // 显示未授权提示
                window.authManager.showUnauthorizedMessage();
                
                return false;
            } else if (isDevelopment) {
                // 开发模式下显示提示信息
                console.log('开发模式：教师助手页面已启用，无需权限验证');
                
                // 在页面顶部添加开发模式提示
                const devNotice = document.createElement('div');
                devNotice.className = 'bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4';
                devNotice.innerHTML = `
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm">
                                <strong>开发模式</strong> - 教师助手功能已启用，生产环境下需要教师权限才能访问。
                            </p>
                        </div>
                    </div>
                `;
                
                // 插入到页面顶部
                const container = document.querySelector('.container');
                if (container) {
                    container.insertBefore(devNotice, container.firstChild);
                }
            }
        }, 100);
    }
    return true;
}

// 显示教师访问提示
function showTeacherAccessPrompt() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg shadow-xl z-10 w-full max-w-md p-6 relative">
            <button class="absolute top-4 right-4 text-gray-500 hover:text-gray-700" id="close-teacher-prompt">
                <i class="fas fa-times"></i>
            </button>
            
            <div class="text-center mb-6">
                <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-100 flex items-center justify-center">
                    <i class="fas fa-chalkboard-teacher text-2xl text-blue-600"></i>
                </div>
                <h2 class="text-2xl font-bold text-gray-800">教师助手</h2>
                <p class="text-gray-600 mt-2">专为教师打造的智能教学工具</p>
            </div>
            
            <div class="space-y-4 mb-6">
                <div class="bg-blue-50 p-4 rounded-lg">
                    <h3 class="font-bold text-blue-800 mb-2">🎯 功能特色</h3>
                    <ul class="text-sm text-blue-700 space-y-1">
                        <li>• 智能课程设计与教案生成</li>
                        <li>• 学生学习数据分析</li>
                        <li>• 个性化作业布置</li>
                        <li>• 教学效果评估</li>
                    </ul>
                </div>
                
                ${window.authManager.isLoggedIn() ? `
                <div class="bg-yellow-50 p-4 rounded-lg">
                    <h3 class="font-bold text-yellow-800 mb-2">⚠️ 权限说明</h3>
                    <p class="text-sm text-yellow-700">
                        您当前是${window.authManager.getCurrentUser().role === 'student' ? '学生' : '普通用户'}账户，
                        需要教师权限才能访问教师助手功能。
                    </p>
                </div>
                ` : `
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h3 class="font-bold text-gray-800 mb-2">🔐 访问要求</h3>
                    <p class="text-sm text-gray-700">
                        教师助手功能需要登录教师账户才能使用。
                    </p>
                </div>
                `}
            </div>
            
            <div class="space-y-3">
                ${!window.authManager.isLoggedIn() ? `
                <button onclick="window.location.href='/static/login.html'" 
                        class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg font-medium transition-colors">
                    <i class="fas fa-sign-in-alt mr-2"></i>登录教师账户
                </button>
                <button onclick="window.location.href='/static/register.html'" 
                        class="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-lg font-medium transition-colors">
                    <i class="fas fa-user-plus mr-2"></i>注册教师账户
                </button>
                ` : `
                <button onclick="contactAdmin()" 
                        class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg font-medium transition-colors">
                    <i class="fas fa-envelope mr-2"></i>申请教师权限
                </button>
                `}
                
                <!-- 开发模式快速测试 -->
                <div class="border-t pt-3" id="dev-test-section" style="display: none;">
                    <p class="text-xs text-gray-500 mb-2">开发模式 - 快速测试</p>
                    <button onclick="quickTestTeacher()" 
                            class="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded-lg text-sm">
                        <i class="fas fa-flask mr-2"></i>快速体验教师功能
                    </button>
                </div>
                
                <button onclick="closeTeacherPrompt()" 
                        class="w-full bg-gray-300 hover:bg-gray-400 text-gray-700 py-3 px-4 rounded-lg font-medium transition-colors">
                    返回
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 检查是否是开发环境
    const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (isDevelopment) {
        document.getElementById('dev-test-section').style.display = 'block';
    }
    
    // 关闭模态框
    document.getElementById('close-teacher-prompt').addEventListener('click', function () {
        document.body.removeChild(modal);
    });
    
    // 点击背景关闭
    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
    
    // 全局函数定义
    window.closeTeacherPrompt = function() {
        document.body.removeChild(modal);
    };
    
    window.contactAdmin = function() {
        alert('请联系系统管理员申请教师权限。\n邮箱：admin@alethea.edu\n电话：400-123-4567');
    };
    
    window.quickTestTeacher = function() {
        // 开发模式下的快速测试功能
        if (window.simulateLogin) {
            const result = window.simulateLogin('teacher', 'teacher');
            if (result.success) {
                document.body.removeChild(modal);
                setTimeout(() => {
                    window.location.href = '/static/teacher-dashboard.html';
                }, 500);
            }
        }
    };
}

// 页面加载完成后检查权限
window.addEventListener('load', function() {
    checkTeacherDashboardAccess();
});
