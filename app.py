import streamlit as st
import time
from agent import IntelligentAgent
import os

# 页面配置
st.set_page_config(
    page_title="教培管家 - 智能客服",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 页面居中布局 */
    .main .block-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* 主界面固定布局 */
    .main .block-container > div:first-child {
        position: relative;
        width: 100%;
    }
    
    /* 强制固定主界面位置 */
    .main .block-container {
        max-width: 1200px !important;
        margin: 0 auto !important;
        padding: 0 2rem !important;
        transition: none !important;
        position: relative !important;
    }
    
    /* 防止侧边栏影响主界面 */
    .main .block-container {
        transform: none !important;
        left: auto !important;
    }
    
    /* 确保主界面容器固定 */
    .main .block-container > div {
        margin: 0 auto !important;
        padding: 0 !important;
    }
    
    /* 覆盖Streamlit的侧边栏响应式布局 */
    @media (max-width: 768px) {
        .main .block-container {
            margin: 0 auto !important;
            padding: 0 2rem !important;
        }
    }
    
    /* 侧边栏居中 */
    .css-1d391kg {
        margin: 0 auto;
    }
    
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        display: flex;
        align-items: flex-start;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .quick-action {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .quick-action:hover {
        transform: translateY(-2px);
    }
    
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #5a6fd8 0%, #6a4190 100%);
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'agent' not in st.session_state:
    st.session_state.agent = IntelligentAgent()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'processing' not in st.session_state:
    st.session_state.processing = False

if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

def main():
    # 侧边栏
    with st.sidebar:
        # 功能说明
        st.markdown("### 💡 四大核心能力")
        st.markdown("""
        - **🏃‍♂️ 陪跑教练**: 指导0-1线下店全流程
        - **💰 财务管家**: 解读财务指标与规划
        - **🚨 急诊医生**: 快速风险处理方案
        - **💝 情感链接**: 理解创业者压力
        """)
        
        st.markdown("---")
        
        st.markdown("### 🚀 常见问题")
        
        # 快捷操作
        quick_actions = st.session_state.agent.get_quick_actions()
        for action in quick_actions:
            if st.button(f"📋 {action['title']}", key=f"quick_{action['title']}"):
                st.session_state.messages.append({"role": "user", "content": action['query']})
                st.session_state.processing = True
                st.rerun()
        
        # 缓存统计信息
        cache_stats = st.session_state.agent.cache.get_cache_stats()
        st.markdown(f"**缓存状态**: {cache_stats['total_cached']} 个缓存")
        
        # 清空缓存按钮
        if st.button("🗑️ 清空缓存", key="clear_cache"):
            st.session_state.agent.cache.clear_cache()
            st.success("缓存已清空")
            st.rerun()
        
        st.markdown("---")
        
        
        # 系统信息
        st.markdown("### ℹ️ 系统信息")
        st.markdown(f"对话轮数: {len(st.session_state.messages) // 2}")
        
        # API状态检查
        try:
            import dashscope
            if dashscope.api_key:
                st.success("✅ API连接正常")
            else:
                st.error("❌ 请设置API密钥")
        except Exception as e:
            st.error("❌ API配置错误")
        
        st.markdown("---")
        st.markdown("### 📊 知识库状态")
        # 向量数据库信息
        if hasattr(st.session_state.agent.vector_store, 'vectors'):
            vector_count = len(st.session_state.agent.vector_store.vectors)
        
            if vector_count > 0:
                st.success("✅ 知识库已加载")
            else:
                st.warning("⚠️ 知识库为空")
        else:
            st.error("❌ 知识库未初始化")
    
    # 主界面
    # 使用container确保主界面固定布局
    main_container = st.container()
    
    with main_container:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 主标题
            st.markdown("""
            <div class="main-header">
                <h1>🎓 教培管家 - 您口袋里的智能客服</h1>
                <p>专注于线下店运营的专业指导，为教育创业者提供全方位支持</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 对话区域
            st.markdown("### 💬 智能对话")
            
            # 显示对话历史
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div style="flex: 1;">
                            <strong>👤 您:</strong><br>
                            {message["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div style="flex: 1;">
                            <strong>🤖 教培管家:</strong><br>
                            {message["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 处理中的状态
            if st.session_state.processing:
                with st.spinner("🤔 正在思考中..."):
                    # 获取最后一条用户消息
                    if st.session_state.messages:
                        last_user_message = st.session_state.messages[-1]["content"]
                        # 使用带缓存的查询方法
                        response = st.session_state.agent.query_with_cache(last_user_message)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.session_state.processing = False
                        st.rerun()
            
            # 输入区域
            st.markdown("---")
            
            # 使用text_input支持回车键发送
            # 动态key来清空输入框
            input_key = f"chat_input_{st.session_state.get('input_counter', 0)}"
            user_input = st.text_input(
                "💭 请输入您的问题:",
                placeholder="例如：线下店选址有什么注意事项？如何控制运营成本？",
                key=input_key
            )
            
            # 处理发送逻辑
            if user_input and user_input.strip():
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.processing = True
                # 增加计数器来清空输入框
                st.session_state.input_counter = st.session_state.get('input_counter', 0) + 1
                st.rerun()
            
            # 发送按钮（备用）
            if st.button("🚀 发送", use_container_width=True):
                if user_input and user_input.strip():
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    # 处理用户输入，触发后续响应生成流程
                    st.session_state.processing = True
                    # 增加计数器来清空输入框
                    st.session_state.input_counter = st.session_state.get('input_counter', 0) + 1
                    st.rerun()
                else:
                    st.warning("请输入问题内容")
            # 操作按钮
            if st.button("🗑️ 清空对话历史", use_container_width=True):
                st.session_state.messages = []
                st.session_state.agent.clear_history()
                st.rerun()
       

if __name__ == "__main__":
    main()

