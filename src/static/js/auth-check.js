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
            const response = await fetch('/api/user/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Token验证失败');
            }

            const data = await response.json();
            if (data.success) {
                this.currentUser = data.user;
                localStorage.setItem('current_user', JSON.stringify(this.currentUser));
            } else {
                this.clearAuth();
            }
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
    
    if (teacherLink) {
        if (window.authManager.canAccessTeacherDashboard()) {
            teacherLink.style.display = '';
            teacherLink.innerHTML = '<i class="fas fa-chalkboard-teacher mr-1"></i>教师助手';
        } else {
            teacherLink.style.display = 'none';
        }
    }
    
    if (mobileTeacherLink) {
        if (window.authManager.canAccessTeacherDashboard()) {
            mobileTeacherLink.style.display = '';
        } else {
            mobileTeacherLink.style.display = 'none';
        }
    }
}

// 用户菜单更新
function updateUserMenu() {
    const userMenuText = document.getElementById('user-menu-text');
    const userDropdown = document.getElementById('user-dropdown');
    const guestDropdown = document.getElementById('guest-dropdown');
    const userName = document.getElementById('user-name');
    const userEmail = document.getElementById('user-email');

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
        if (!window.authManager.canAccessTeacherDashboard()) {
            // 隐藏页面内容
            document.body.style.display = 'none';
            
            // 显示未授权提示
            window.authManager.showUnauthorizedMessage();
            
            return false;
        }
    }
    return true;
}

// 页面加载完成后检查权限
window.addEventListener('load', function() {
    checkTeacherDashboardAccess();
});
