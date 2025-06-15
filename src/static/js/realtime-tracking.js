/**
 * Real-time Analytics Tracking for Alethea Platform
 * Tracks user behavior and updates dashboard in real-time
 */

class RealtimeTracker {
    constructor() {
        this.userId = 1; // Demo user ID
        this.sessionId = null;
        this.isTracking = false;
        this.trackingInterval = null;
        this.dashboardUpdateInterval = null;
        this.sessionStartTime = null;
        
        this.init();
    }
    
    init() {
        console.log('🚀 初始化实时追踪系统...');
        this.startSession();
        this.setupEventListeners();
        this.startTracking();
        this.startDashboardUpdates();
    }
    
    async startSession() {
        try {
            const response = await fetch('/api/realtime/session/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.userId
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.sessionId = data.session_id;
                this.sessionStartTime = new Date();
                console.log('✅ 学习会话已开始:', this.sessionId);
                this.showNotification('学习会话已开始，开始追踪您的学习数据', 'success');
            }
        } catch (error) {
            console.error('❌ 启动会话失败:', error);
        }
    }
    
    setupEventListeners() {
        // 页面访问追踪
        this.trackPageView();
        
        // 点击事件追踪
        document.addEventListener('click', (e) => {
            this.trackClick(e);
        });
        
        // 表单提交追踪
        document.addEventListener('submit', (e) => {
            this.trackFormSubmit(e);
        });
        
        // 页面离开时结束会话
        window.addEventListener('beforeunload', () => {
            this.endSession();
        });
        
        // 页面可见性变化追踪
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.trackBehavior('page_hidden', {
                    page: window.location.pathname,
                    duration: this.getSessionDuration()
                });
            } else {
                this.trackBehavior('page_visible', {
                    page: window.location.pathname
                });
            }
        });
    }
    
    trackPageView() {
        const pageData = {
            page: window.location.pathname,
            title: document.title,
            referrer: document.referrer,
            timestamp: new Date().toISOString()
        };
        
        this.trackBehavior('page_view', pageData);
        console.log('📄 页面访问:', pageData.page);
    }
    
    trackClick(event) {
        const element = event.target;
        const clickData = {
            element_type: element.tagName.toLowerCase(),
            element_id: element.id || null,
            element_class: element.className || null,
            element_text: element.textContent?.substring(0, 100) || null,
            page: window.location.pathname,
            timestamp: new Date().toISOString()
        };
        
        // 特殊元素追踪
        if (element.matches('a[href]')) {
            clickData.link_url = element.href;
            clickData.action_type = 'link_click';
        } else if (element.matches('button')) {
            clickData.action_type = 'button_click';
        } else if (element.matches('.project-card, .project-item')) {
            clickData.action_type = 'project_view';
            clickData.project_name = element.querySelector('h3, .title')?.textContent || 'Unknown';
        } else if (element.matches('.subject-item, .subject-card')) {
            clickData.action_type = 'subject_explore';
            clickData.subject_name = element.querySelector('.subject-name, h3')?.textContent || 'Unknown';
        }
        
        this.trackBehavior('click', clickData);
    }
    
    trackFormSubmit(event) {
        const form = event.target;
        const formData = {
            form_id: form.id || null,
            form_action: form.action || null,
            form_method: form.method || 'get',
            page: window.location.pathname,
            timestamp: new Date().toISOString()
        };
        
        // 检查是否是问答表单
        if (form.matches('#question-form, .question-form')) {
            const questionInput = form.querySelector('input[name="question"], textarea[name="question"]');
            if (questionInput) {
                formData.action_type = 'ask_question';
                formData.question_content = questionInput.value?.substring(0, 200) || '';
                formData.subject = this.detectSubject(questionInput.value);
            }
        } else if (form.matches('#search-form, .search-form')) {
            const searchInput = form.querySelector('input[name="query"], input[type="search"]');
            if (searchInput) {
                formData.action_type = 'search';
                formData.search_query = searchInput.value?.substring(0, 100) || '';
                formData.subject = this.detectSubject(searchInput.value);
            }
        }
        
        this.trackBehavior('form_submit', formData);
    }
    
    detectSubject(text) {
        if (!text) return null;
        
        const subjectKeywords = {
            '电工电子实验': ['电路', '电阻', '电容', '电感', '二极管', '三极管', 'LED', '电压', '电流'],
            '自动控制原理': ['PID', '控制', '反馈', '传递函数', '稳定性', '响应', '控制器'],
            '数字电子技术': ['数字电路', '逻辑门', '触发器', '计数器', '编码器', '译码器'],
            '信号与系统': ['信号处理', '滤波', '频域', '时域', '傅里叶', '拉普拉斯'],
            '机械设计': ['机械', '齿轮', '轴承', '传动', '结构设计', '材料力学']
        };
        
        const lowerText = text.toLowerCase();
        for (const [subject, keywords] of Object.entries(subjectKeywords)) {
            if (keywords.some(keyword => lowerText.includes(keyword.toLowerCase()))) {
                return subject;
            }
        }
        
        return null;
    }
    
    async trackBehavior(actionType, actionData = {}) {
        if (!this.isTracking) return;
        
        try {
            const trackingData = {
                user_id: this.userId,
                action_type: actionType,
                action_data: actionData,
                subject_id: this.getSubjectId(actionData.subject),
                duration: actionData.duration || null
            };
            
            const response = await fetch('/api/realtime/track', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(trackingData)
            });
            
            const result = await response.json();
            if (result.success) {
                console.log('📊 行为已追踪:', actionType, actionData);
                this.updateRealtimeStats();
            }
        } catch (error) {
            console.error('❌ 追踪行为失败:', error);
        }
    }
    
    getSubjectId(subjectName) {
        const subjectMap = {
            '电工电子实验': 1,
            '自动控制原理': 2,
            '数字电子技术': 3,
            '信号与系统': 4,
            '机械设计': 5
        };
        
        return subjectMap[subjectName] || null;
    }
    
    startTracking() {
        this.isTracking = true;
        
        // 定期追踪活跃状态
        this.trackingInterval = setInterval(() => {
            if (!document.hidden) {
                this.trackBehavior('active_session', {
                    page: window.location.pathname,
                    session_duration: this.getSessionDuration(),
                    timestamp: new Date().toISOString()
                });
            }
        }, 30000); // 每30秒追踪一次活跃状态
        
        console.log('✅ 实时追踪已启动');
    }
    
    startDashboardUpdates() {
        // 定期更新仪表板数据
        this.dashboardUpdateInterval = setInterval(() => {
            this.updateDashboard();
        }, 5000); // 每5秒更新一次仪表板
        
        // 立即更新一次
        this.updateDashboard();
    }
    
    async updateDashboard() {
        try {
            const response = await fetch(`/api/realtime/dashboard/${this.userId}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderDashboard(data.data);
            }
        } catch (error) {
            console.error('❌ 更新仪表板失败:', error);
        }
    }
    
    renderDashboard(dashboardData) {
        // 更新统计卡片
        this.updateStatCards(dashboardData.statistics);
        
        // 更新进度信息
        this.updateProgress(dashboardData.progress);
        
        // 更新学科进度
        this.updateSubjectProgress(dashboardData.subject_progress);
        
        // 更新学习分析图表
        this.updateLearningAnalytics(dashboardData.learning_analytics);
        
        // 更新成就徽章
        this.updateAchievements(dashboardData.achievements);
        
        // 更新AI推荐
        this.updateAIRecommendations(dashboardData.ai_recommendations);
        
        // 更新最近活动
        this.updateRecentActivities(dashboardData.recent_activities);
        
        // 更新学习日历
        this.updateLearningCalendar(dashboardData.learning_calendar);
        
        // 更新实时统计
        this.updateRealtimeStats(dashboardData.real_time_stats);
    }
    
    updateStatCards(statistics) {
        const statElements = {
            'total_projects': document.querySelector('.stat-projects .stat-number'),
            'completed_tests': document.querySelector('.stat-tests .stat-number'),
            'study_hours': document.querySelector('.stat-hours .stat-number'),
            'knowledge_points': document.querySelector('.stat-knowledge .stat-number')
        };
        
        Object.entries(statElements).forEach(([key, element]) => {
            if (element && statistics[key] !== undefined) {
                this.animateNumber(element, statistics[key]);
            }
        });
    }
    
    updateProgress(progress) {
        // 更新总体进度
        const overallProgress = document.querySelector('.overall-progress .progress-value');
        if (overallProgress) {
            overallProgress.textContent = `${Math.round(progress.overall_progress)}%`;
        }
        
        const progressBar = document.querySelector('.overall-progress .progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progress.overall_progress}%`;
        }
        
        // 更新其他进度指标
        const progressElements = {
            'subjects_studied': document.querySelector('.subjects-studied .progress-number'),
            'avg_score': document.querySelector('.avg-score .progress-number'),
            'completion_rate': document.querySelector('.completion-rate .progress-number')
        };
        
        Object.entries(progressElements).forEach(([key, element]) => {
            if (element && progress[key] !== undefined) {
                this.animateNumber(element, progress[key]);
            }
        });
    }
    
    updateSubjectProgress(subjectProgress) {
        const container = document.querySelector('.subject-progress-list');
        if (!container || !subjectProgress) return;
        
        container.innerHTML = '';
        
        subjectProgress.forEach(subject => {
            const subjectElement = document.createElement('div');
            subjectElement.className = 'subject-progress-item';
            subjectElement.innerHTML = `
                <div class="subject-info">
                    <span class="subject-name">${subject.name}</span>
                    <span class="subject-progress">${subject.progress}%</span>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: ${subject.progress}%"></div>
                </div>
                <div class="knowledge-points">${subject.knowledge_points}个知识点</div>
            `;
            container.appendChild(subjectElement);
        });
    }
    
    updateLearningAnalytics(analytics) {
        if (!analytics) return;
        
        // 更新学习分析图表（这里可以集成Chart.js等图表库）
        this.updateActivityChart(analytics.daily_activity);
        this.updateEngagementTrend(analytics.engagement_trend);
    }
    
    updateActivityChart(dailyActivity) {
        // 简单的活动图表更新
        const chartContainer = document.querySelector('.activity-chart');
        if (!chartContainer || !dailyActivity) return;
        
        // 这里可以使用Chart.js等库来创建更复杂的图表
        const maxActivity = Math.max(...dailyActivity.map(d => d.actions));
        
        chartContainer.innerHTML = dailyActivity.slice(-7).map(day => {
            const height = maxActivity > 0 ? (day.actions / maxActivity) * 100 : 0;
            return `
                <div class="chart-bar" style="height: ${height}%" title="${day.date}: ${day.actions}次活动">
                    <span class="bar-value">${day.actions}</span>
                </div>
            `;
        }).join('');
    }
    
    updateEngagementTrend(engagementTrend) {
        // 更新参与度趋势
        const trendContainer = document.querySelector('.engagement-trend');
        if (!trendContainer || !engagementTrend) return;
        
        const avgEngagement = engagementTrend.reduce((sum, d) => sum + d.engagement, 0) / engagementTrend.length;
        trendContainer.innerHTML = `
            <div class="trend-value">${Math.round(avgEngagement)}%</div>
            <div class="trend-label">平均参与度</div>
        `;
    }
    
    updateAchievements(achievements) {
        const container = document.querySelector('.achievements-list');
        if (!container || !achievements) return;
        
        container.innerHTML = achievements.map(achievement => `
            <div class="achievement-item">
                <span class="achievement-icon">${achievement.icon}</span>
                <div class="achievement-info">
                    <div class="achievement-title">${achievement.title}</div>
                    <div class="achievement-description">${achievement.description}</div>
                </div>
            </div>
        `).join('');
    }
    
    updateAIRecommendations(recommendations) {
        const container = document.querySelector('.ai-recommendations-list');
        if (!container || !recommendations) return;
        
        container.innerHTML = recommendations.map(rec => `
            <div class="recommendation-item">
                <span class="recommendation-icon">${rec.icon}</span>
                <div class="recommendation-info">
                    <div class="recommendation-title">${rec.title}</div>
                    <div class="recommendation-description">${rec.description}</div>
                    <button class="recommendation-action" onclick="realtimeTracker.handleRecommendationClick('${rec.action}')">${rec.action}</button>
                </div>
            </div>
        `).join('');
    }
    
    updateRecentActivities(activities) {
        const container = document.querySelector('.recent-activities-list');
        if (!container || !activities) return;
        
        container.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <span class="activity-icon">${activity.icon}</span>
                <div class="activity-info">
                    <div class="activity-description">${activity.description}</div>
                    <div class="activity-time">${this.formatTime(activity.time)}</div>
                </div>
            </div>
        `).join('');
    }
    
    updateLearningCalendar(calendar) {
        const container = document.querySelector('.learning-calendar');
        if (!container || !calendar) return;
        
        const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
        
        container.innerHTML = `
            <div class="calendar-header">
                <h3>${calendar.year}年${monthNames[calendar.month - 1]}</h3>
            </div>
            <div class="calendar-grid">
                ${calendar.days.map(day => `
                    <div class="calendar-day ${day.has_activity ? 'has-activity' : ''} ${day.is_today ? 'today' : ''}" 
                         data-activity-level="${day.activity_level}">
                        ${day.day}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    updateRealtimeStats(realtimeStats) {
        if (!realtimeStats) return;
        
        // 更新当前会话时长
        const sessionDuration = document.querySelector('.current-session-duration');
        if (sessionDuration) {
            sessionDuration.textContent = this.formatDuration(realtimeStats.current_session_duration);
        }
        
        // 更新今日活动
        const todayActions = document.querySelector('.today-actions');
        if (todayActions) {
            todayActions.textContent = realtimeStats.today_actions;
        }
        
        // 更新学习连续天数
        const weeklyStreak = document.querySelector('.weekly-streak');
        if (weeklyStreak) {
            weeklyStreak.textContent = `${realtimeStats.weekly_streak}天`;
        }
    }
    
    animateNumber(element, targetValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const increment = (targetValue - currentValue) / 20;
        let current = currentValue;
        
        const animation = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= targetValue) || (increment < 0 && current <= targetValue)) {
                current = targetValue;
                clearInterval(animation);
            }
            element.textContent = Math.round(current);
        }, 50);
    }
    
    formatTime(timeString) {
        if (!timeString) return '';
        
        const time = new Date(timeString);
        const now = new Date();
        const diff = now - time;
        
        if (diff < 60000) return '刚刚';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
        return `${Math.floor(diff / 86400000)}天前`;
    }
    
    formatDuration(seconds) {
        if (!seconds) return '0秒';
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) return `${hours}小时${minutes}分钟`;
        if (minutes > 0) return `${minutes}分钟${secs}秒`;
        return `${secs}秒`;
    }
    
    getSessionDuration() {
        if (!this.sessionStartTime) return 0;
        return Math.floor((new Date() - this.sessionStartTime) / 1000);
    }
    
    handleRecommendationClick(action) {
        this.trackBehavior('recommendation_click', {
            action: action,
            page: window.location.pathname
        });
        
        // 这里可以添加具体的推荐操作逻辑
        this.showNotification(`正在执行：${action}`, 'info');
    }
    
    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        // 添加到页面
        let container = document.querySelector('.notifications-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notifications-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // 自动移除
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    async endSession() {
        if (!this.sessionId) return;
        
        try {
            await fetch('/api/realtime/session/end', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            console.log('✅ 学习会话已结束');
        } catch (error) {
            console.error('❌ 结束会话失败:', error);
        }
    }
    
    stopTracking() {
        this.isTracking = false;
        
        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
            this.trackingInterval = null;
        }
        
        if (this.dashboardUpdateInterval) {
            clearInterval(this.dashboardUpdateInterval);
            this.dashboardUpdateInterval = null;
        }
        
        console.log('⏹️ 实时追踪已停止');
    }
}

// 全局实例
let realtimeTracker;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    realtimeTracker = new RealtimeTracker();
});

// 导出供其他脚本使用
window.RealtimeTracker = RealtimeTracker;
window.realtimeTracker = realtimeTracker;
