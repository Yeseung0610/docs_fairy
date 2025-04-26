import streamlit as st
import openai_api
import random  # Add randomness to force CSS refresh
import re

def initialize_chat():
    """Initialize the chat session state if not already done"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Initialize chat tabs
    if 'chat_tabs' not in st.session_state:
        st.session_state.chat_tabs = {
            "일반 대화": []
        }
    
    # Initialize current tab
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "일반 대화"
        
    # Migrate old messages to the tab system if needed
    if st.session_state.messages and not st.session_state.chat_tabs["일반 대화"]:
        st.session_state.chat_tabs["일반 대화"] = st.session_state.messages.copy()

def add_new_chat():
    """Add a new chat tab"""
    new_tab_name = f"새 대화 {len(st.session_state.chat_tabs) + 1}"
    st.session_state.chat_tabs[new_tab_name] = []
    st.session_state.current_tab = new_tab_name
    
def delete_chat(tab_name):
    """Delete a chat tab"""
    if tab_name in st.session_state.chat_tabs:
        # Delete the tab
        del st.session_state.chat_tabs[tab_name]
        
        # Set current tab to the first tab if the deleted tab was the current tab
        if tab_name == st.session_state.current_tab:
            if st.session_state.chat_tabs:
                st.session_state.current_tab = list(st.session_state.chat_tabs.keys())[0]
            else:
                # If no tabs left, create a new default tab
                st.session_state.chat_tabs = {"일반 대화": []}
                st.session_state.current_tab = "일반 대화"
    
def highlight_important_info(text):
    """Highlight links, important phrases and data in AI response"""
    # Highlight URLs with markdown syntax
    text = re.sub(r'(https?://[^\s]+)', r'[링크](\1)', text)
    
    # Highlight important keywords with bold
    keywords = ["중요", "주의", "필수", "핵심", "요약", "결론"]
    for keyword in keywords:
        text = re.sub(f'({keyword}[:\\s])', r'**\1**', text)
    
    # Highlight data points and numbers
    text = re.sub(r'(\d+\.?\d*\s*%)', r'**\1**', text) # Percentages
    text = re.sub(r'(\d{4}-\d{2}-\d{2})', r'**\1**', text) # Dates
    
    return text
    
def render_chat_interface():
    """Render the main chat interface"""
    # Title and subtitle
    st.title("My Task AI - 당신만을 위한 개인 업무 비서")
    st.caption("문서 요정 🧚🏻‍♀️")
    
    # Force all CSS cache to refresh
    random_id = random.randint(1, 1000000)
    
    # Apply custom CSS for the chat interface
    st.markdown(f"""
    <style data-version="{random_id}">
    /* Hide default avatar images */
    [data-testid="StChatMessageAvatar"] > div > img {{
        display: none !important;
    }}
    
    /* User avatar styling */
    .element-container .stChatMessage.user [data-testid="StChatMessageAvatar"] {{
        background-color: #D1F5F0 !important;
        border: 2px solid #FFFFFF !important;
    }}
    
    .element-container .stChatMessage.user [data-testid="StChatMessageAvatar"]::after {{
        content: "👤";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 20px;
    }}
    
    /* Assistant avatar styling */
    .element-container .stChatMessage.assistant [data-testid="StChatMessageAvatar"] {{
        background-color: #FFFFFF !important;
        border: 1px solid #F0F2F6 !important;
    }}
    
    .element-container .stChatMessage.assistant [data-testid="StChatMessageAvatar"]::after {{
        content: "🧚🏻‍♀️";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 20px;
    }}
    
    /* Style for highlighted information */
    .highlighted {{
        background-color: #FFEFD5;
        padding: 2px 4px;
        border-radius: 3px;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Clear existing cache
    st.markdown(f"""
    <script data-version="{random_id}">
    document.querySelectorAll('style:not([data-version="{random_id}"])').forEach(el => {{
        if (el.innerHTML.includes('StChatMessageAvatar')) {{
            el.remove();
        }}
    }});
    </script>
    """, unsafe_allow_html=True)
    
    # Chat tabs
    tab_cols = st.columns([0.7, 0.3])
    all_tabs = list(st.session_state.chat_tabs.keys())
    
    with tab_cols[0]:
        # Create tabs
        tabs = st.tabs(all_tabs)
        
        # Find index of current tab
        current_tab_index = all_tabs.index(st.session_state.current_tab)
        
        # Set up tab switching
        for i, tab_name in enumerate(all_tabs):
            with tabs[i]:
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    if st.session_state.current_tab != tab_name and st.button(f"대화 {i+1} 선택", key=f"select_tab_{i}"):
                        st.session_state.current_tab = tab_name
                        st.rerun()
                
                # Add delete button (don't allow deleting the last tab)
                with col2:
                    if len(st.session_state.chat_tabs) > 1 and st.button("🗑️", key=f"delete_tab_{i}"):
                        delete_chat(tab_name)
                        st.rerun()
    
    with tab_cols[1]:
        if st.button("💬 새 대화 추가", key="add_new_chat"):
            add_new_chat()
            st.rerun()
            
    # Reset current chat button
    if st.button("대화 기록 초기화"):
        st.session_state.chat_tabs[st.session_state.current_tab] = []
        st.rerun()
    
    # Display chat messages for the current tab
    with tabs[current_tab_index]:
        # Reference to the messages in the current tab
        messages = st.session_state.chat_tabs[st.session_state.current_tab]
        
        # Chat container to control the flow
        chat_container = st.container()
        
        # Input container (at the bottom)
        input_container = st.container()
        
        # Put the chat input at the bottom
        with input_container:
            user_input = st.chat_input("무엇이든 물어보세요")
        
        # Display messages (flowing upward)
        with chat_container:
            # Reverse messages for display to show newest at the bottom
            for i, message in enumerate(messages):
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["content"])
                else:
                    with st.chat_message("assistant"):
                        st.markdown(message["content"], unsafe_allow_html=True)
        
        # Process user input (if any)
        if user_input:
            # Add user message to chat history
            messages.append({"role": "user", "content": user_input})
            
            # Get AI response
            with st.spinner("AI가 응답 중입니다..."):
                # Need to convert to regular list format for API call
                api_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
                ai_response = openai_api.get_ai_response(api_messages)
                
                # Highlight important information
                highlighted_response = highlight_important_info(ai_response)
                
                # Add AI response to chat history (with highlighting)
                messages.append({"role": "assistant", "content": highlighted_response})
                
            # Update the chat tab data and refresh
            st.session_state.chat_tabs[st.session_state.current_tab] = messages
            st.rerun()
