from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict
import requests
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import json
import shutil
from datetime import datetime
import PyPDF2
import docx
import hashlib

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=False,  # 改为False以避免凭证问题
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
    expose_headers=["*"]
)

# 配置文件存储路径
UPLOAD_DIR = "uploads"
KNOWLEDGE_BASE_FILE = "knowledge_base.json"
API_CONFIG_FILE = "../config/api.json"
KNOWLEDGE_BASE_DIR = "knowledge_base"

# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)

# Ollama API配置
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 读取文档内容
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 知识库检索类
class KnowledgeBase:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.documents = []
        self.vectors = None
        self.load_documents()

    def load_documents(self):
        """加载所有知识库文档"""
        try:
            with open(KNOWLEDGE_BASE_FILE, 'r', encoding='utf-8') as f:
                docs = json.load(f)
                for doc in docs:
                    file_path = doc['path']
                    if os.path.exists(file_path):
                        content = self.read_document_content(file_path)
                        if content:
                            self.documents.append({
                                'id': doc['id'],
                                'content': content,
                                'name': doc['name']
                            })
            if self.documents:
                contents = [doc['content'] for doc in self.documents]
                self.vectors = self.vectorizer.fit_transform(contents)
        except Exception as e:
            print(f"Error loading knowledge base: {str(e)}")

    def read_document_content(self, file_path):
        """读取文档内容"""
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.pdf':
                return extract_text_from_pdf(file_path)
            elif ext == '.docx':
                return extract_text_from_docx(file_path)
            elif ext == '.txt':
                return extract_text_from_txt(file_path)
        except Exception as e:
            print(f"Error reading document {file_path}: {str(e)}")
        return None

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """搜索相关文档片段"""
        if not self.vectors or not self.documents:
            return []

        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.vectors).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # 相似度阈值
                results.append({
                    'content': self.documents[idx]['content'],
                    'similarity': float(similarities[idx]),
                    'name': self.documents[idx]['name']
                })
        return results

# 初始化知识库
kb = KnowledgeBase()

# 调用Ollama API
async def query_ollama(prompt: str, context: str = "") -> str:
    try:
        # 读取API配置
        with open(API_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            ollama_config = config['ollama']

        print("发送请求到Ollama...")
        print(f"使用模型: {ollama_config['model']}")
        print(f"提示词: {prompt[:200]}...")  # 只打印前200个字符

        # 构建请求体
        request_body = {
            "model": ollama_config['model'],
            "prompt": prompt,
            "system": ollama_config['systemPrompt'],
            "options": {
                "temperature": ollama_config['settings']['temperature'],
                "top_p": ollama_config['settings']['top_p']
            }
        }

        print("发送请求到:", OLLAMA_API_URL)
        response = requests.post(OLLAMA_API_URL, json=request_body)
        print(f"收到响应状态码: {response.status_code}")
        print("响应内容:", response.text[:200])  # 打印响应内容的前200个字符
        
        if response.status_code == 200:
            try:
                # 尝试解析第一行JSON
                first_line = response.text.strip().split('\n')[0]
                result = json.loads(first_line)
                if 'response' in result:
                    print("成功获取回答")
                    return result['response']
                else:
                    print("响应格式错误:", result)
                    raise HTTPException(status_code=500, detail="AI响应格式错误")
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {str(e)}")
                raise HTTPException(status_code=500, detail="响应格式解析失败")
        else:
            error_msg = f"Ollama API调用失败: {response.text}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
    except requests.exceptions.ConnectionError:
        error_msg = "无法连接到Ollama服务，请确保Ollama正在运行"
        print(error_msg)
        raise HTTPException(status_code=503, detail=error_msg)
    except Exception as e:
        error_msg = f"API调用错误: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# 更新知识库
def update_knowledge_base(new_content: str):
    try:
        # 读取现有的API配置
        with open(API_CONFIG_FILE, 'r', encoding='utf-8') as f:
            api_config = json.load(f)
        
        # 更新知识库内容
        current_knowledge = api_config['ollama']['knowledgeBase']
        updated_knowledge = current_knowledge + "\n\n" + new_content
        
        # 更新配置文件
        api_config['ollama']['knowledgeBase'] = updated_knowledge
        
        # 保存更新后的配置
        with open(API_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(api_config, f, ensure_ascii=False, indent=4)
            
        return True
    except Exception as e:
        print(f"Error updating knowledge base: {str(e)}")
        return False

# 获取文档列表
@app.get("/api/documents")
async def get_documents():
    try:
        with open(KNOWLEDGE_BASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# 上传文档
@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        uploaded_docs = []
        
        # 加载现有文档列表
        try:
            with open(KNOWLEDGE_BASE_FILE, 'r', encoding='utf-8') as f:
                documents = json.load(f)
        except FileNotFoundError:
            documents = []

        for file in files:
            # 生成文件ID
            file_id = hashlib.md5(f"{file.filename}{datetime.now()}".encode()).hexdigest()
            
            # 获取文件扩展名
            ext = os.path.splitext(file.filename)[1].lower()
            
            # 保存文件
            file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 提取文本内容
            try:
                if ext == '.pdf':
                    content = extract_text_from_pdf(file_path)
                elif ext == '.docx':
                    content = extract_text_from_docx(file_path)
                elif ext == '.txt':
                    content = extract_text_from_txt(file_path)
                else:
                    raise ValueError(f"Unsupported file type: {ext}")
                
                # 更新知识库
                if update_knowledge_base(content):
                    # 添加文档信息
                    doc_info = {
                        "id": file_id,
                        "name": file.filename,
                        "uploadDate": datetime.now().isoformat(),
                        "path": file_path
                    }
                    documents.append(doc_info)
                    uploaded_docs.append(doc_info)
                
            except Exception as e:
                print(f"Error processing file {file.filename}: {str(e)}")
                continue
        
        # 保存更新后的文档列表
        with open(KNOWLEDGE_BASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=4)
        
        return JSONResponse(content={
            "message": "Files uploaded successfully",
            "uploaded": uploaded_docs
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 删除文档
@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    try:
        # 加载文档列表
        with open(KNOWLEDGE_BASE_FILE, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        # 查找要删除的文档
        doc_to_delete = None
        updated_docs = []
        for doc in documents:
            if doc['id'] == doc_id:
                doc_to_delete = doc
            else:
                updated_docs.append(doc)
        
        if not doc_to_delete:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # 删除文件
        if os.path.exists(doc_to_delete['path']):
            os.remove(doc_to_delete['path'])
        
        # 更新文档列表
        with open(KNOWLEDGE_BASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(updated_docs, f, ensure_ascii=False, indent=4)
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 搜索文档
@app.get("/api/documents/search")
async def search_documents(q: str):
    try:
        with open(KNOWLEDGE_BASE_FILE, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        # 简单的文件名搜索
        results = [
            doc for doc in documents
            if q.lower() in doc['name'].lower()
        ]
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 添加AI问答接口
from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str

@app.post("/api/ask")
async def ask_question(request: Dict):
    try:
        if not isinstance(request, dict):
            return JSONResponse(
                status_code=400,
                content={"detail": "无效的请求格式"}
            )

        question = request.get('question')
        if not question or not isinstance(question, str):
            return JSONResponse(
                status_code=400,
                content={"detail": "问题不能为空且必须是字符串"}
            )

        # 读取API配置
        try:
            with open(API_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                ollama_config = config['ollama']
        except Exception as e:
            print(f"配置文件读取错误: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "服务器配置错误"}
            )

        try:
            # 搜索相关文档
            relevant_docs = kb.search(question)
            
            # 构建知识库上下文
            context = ""
            if relevant_docs:
                context = "以下是相关的知识库内容：\n\n" + "\n\n".join([
                    f"[{doc['name']}]\n{doc['content'][:1500].strip()}"
                    for doc in relevant_docs
                    if doc['similarity'] > 0.2
                ])
            
            # 添加基础知识
            context = ollama_config['knowledgeBase'] + "\n\n" + context

            # 构建提示词
            prompt = f"""请基于以下信息回答用户的问题。如果问题与提供的信息无关，请基于你的专业知识作答。如果不确定答案，请明确告知。

背景信息：
{context}

用户问题：{question}"""

            # 调用Ollama API生成回答
            answer = await query_ollama(prompt, context)
            
            if not answer:
                return JSONResponse(
                    status_code=500,
                    content={"detail": "AI生成答案失败"}
                )
                
            return JSONResponse(
                status_code=200,
                content={"answer": answer}
            )

        except Exception as e:
            error_msg = f"处理问题时出错: {str(e)}"
            print(error_msg)
            return JSONResponse(
                status_code=500,
                content={"detail": error_msg}
            )

    except Exception as e:
        error_msg = f"系统错误: {str(e)}"
        print(error_msg)
        return JSONResponse(
            status_code=500,
            content={"detail": error_msg}
        )

# 重新加载知识库
@app.post("/api/reload-kb")
async def reload_knowledge_base():
    try:
        kb.load_documents()
        return {"message": "知识库已重新加载"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
