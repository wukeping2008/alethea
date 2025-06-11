// API端点
const API_BASE_URL = 'http://localhost:8005/api';

// DOM元素
const questionInput = document.getElementById('questionInput');
const submitButton = document.getElementById('submitQuestion');
const answerOutput = document.getElementById('answerOutput');

// 状态管理
let isProcessing = false;

// 事件监听
submitButton.addEventListener('click', handleSubmit);
questionInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        handleSubmit();
    }
});

// 处理提交
async function handleSubmit() {
    if (isProcessing) return;
    
    const question = questionInput.value.trim();
    if (!question) {
        showError('请输入您的问题');
        return;
    }

    try {
        isProcessing = true;
        updateUIState(true);
        
        const answer = await getAIResponse(question);
        displayAnswer(answer);
    } catch (error) {
        showError(error.message);
    } finally {
        isProcessing = false;
        updateUIState(false);
    }
}

// 获取AI回答
async function getAIResponse(question) {
    try {
        console.log('发送请求:', question);
        const response = await fetch(`${API_BASE_URL}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ question: question })
        });

        console.log('收到响应状态:', response.status);
        const contentType = response.headers.get('content-type');
        console.log('响应类型:', contentType);

        if (!response.ok) {
            let errorMessage;
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || '服务器返回错误';
            } catch (e) {
                const errorText = await response.text();
                errorMessage = errorText || `HTTP错误 ${response.status}`;
            }
            console.error('错误详情:', errorMessage);
            throw new Error(errorMessage);
        }

        const data = await response.json();
        console.log('响应数据:', data);
        
        if (!data.answer) {
            throw new Error('响应数据格式不正确');
        }

        return data.answer;
    } catch (error) {
        console.error('API请求错误:', error);
        throw new Error(`获取答案失败: ${error.message}`);
    }
}

// 显示答案
function displayAnswer(answer) {
    answerOutput.innerHTML = `
        <div class="answer-content">
            ${formatAnswer(answer)}
        </div>
    `;
}

// 格式化答案
function formatAnswer(text) {
    return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`(.*?)`/g, '<code>$1</code>');
}

// 显示错误信息
function showError(message) {
    answerOutput.innerHTML = `
        <div class="error-message">
            ${message}
        </div>
    `;
}

// 更新UI状态
function updateUIState(isLoading) {
    submitButton.disabled = isLoading;
    submitButton.textContent = isLoading ? '正在思考...' : '获取答案';
    
    if (isLoading) {
        answerOutput.innerHTML = `
            <div class="loading">
                <div class="loading-spinner"></div>
                <p>AI正在思考中...</p>
            </div>
        `;
    }
}
