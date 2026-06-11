import streamlit as st
import os
from google import genai
from google.genai import types
from duckduckgo_search import DDGS

# ==========================================
# 1. UI CONFIGURATION & SESSION STATE INIT
# ==========================================
st.set_page_config(page_title="Free Autonomous Agent", page_icon="🤖", layout="centered")

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {
        "chat_1": {
            "title": "New Chat",
            "messages": [] 
        }
    }

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "chat_1"

current_chat_id = st.session_state.current_chat_id
active_messages = st.session_state.all_chats[current_chat_id]["messages"]

# ==========================================
# 2. SIDEBAR MANAGER (History & Control)
# ==========================================
with st.sidebar:
    st.header("Chat Control")
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        new_id = f"chat_{len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_id] = {"title": "New Chat", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()
        
    st.markdown("---")
    st.subheader("Recent Conversations")
    
    for chat_id, chat_data in st.session_state.all_chats.items():
        is_active = (chat_id == current_chat_id)
        button_style = f"👉 {chat_data['title']}" if is_active else f"💬 {chat_data['title']}"
        if st.button(button_style, key=f"nav_{chat_id}", use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.markdown("---")
    # Paste your free Google AI Studio key here
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key (Free):", type="password")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
    else:
        st.caption("✓ Gemini Free API Key active")

# ==========================================
# 3. CORE AGENT TOOLS
# ==========================================
def calculate_investment_growth(principal: float, rate: float, years: int) -> str:
    """Calculates the compound interest growth of an investment over time."""
    amount = principal * ((1 + rate / 100) ** years)
    return f"After {years} years at {rate}% interest, the investment grows to ${amount:,.2f}"

def web_search(query: str) -> str:
    """Searches the internet for real-time information, weather, coordinates, or current events."""
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No results found."
        return "\n".join([f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n---" for r in results])
    except Exception as e:
        return f"Error performing search: {str(e)}"

# Define available Python execution routing map
AVAILABLE_TOOLS = {
    "calculate_investment_growth": calculate_investment_growth,
    "web_search": web_search
}

# ==========================================
# 4. CHAT INTERFACE RENDERING
# ==========================================
st.title("🤖 Free Autonomous Agentic AI")
st.caption(f"Powered by Gemini 2.5 Flash | Active Session: *{st.session_state.all_chats[current_chat_id]['title']}*")

# Render past messages safely from memory
for msg in active_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ==========================================
# 5. DYNAMIC INPUT RUNTIME LOOP
# ==========================================
# ==========================================
# 5. DYNAMIC INPUT RUNTIME LOOP
# ==========================================
# ==========================================
# 5. DYNAMIC INPUT RUNTIME LOOP (OPTIMIZED)
# ==========================================
if user_input := st.chat_input("What would you like me to look up or calculate?"):
    if not os.getenv("GEMINI_API_KEY"):
        st.error("Please enter a free Gemini API key in the sidebar.")
        st.stop()

    client = genai.Client()

    # 1. Update Title if it's the first message
    if st.session_state.all_chats[current_chat_id]["title"] == "New Chat":
        st.session_state.all_chats[current_chat_id]["title"] = user_input[:22] + "..." if len(user_input) > 22 else user_input

    # 2. Show user input
    with st.chat_message("user"):
        st.write(user_input)
    active_messages.append({"role": "user", "content": user_input})

    # 3. Setup Config
    config = types.GenerateContentConfig(
        system_instruction=(
            "You are an autonomous AI agent. Use your internal knowledge for science/history. "
            "Deploy the web_search tool for real-time events. "
            "Use the investment tool for compound calculations only."
        ),
        tools=[calculate_investment_growth, web_search], 
        temperature=0.3
    )
    
    # 4. History Prep
    gemini_history = []
    for msg in active_messages:
        gemini_role = "model" if msg["role"] == "assistant" else msg["role"]
        gemini_history.append(types.Content(role=gemini_role, parts=[types.Part.from_text(text=msg["content"])]))

    # 5. Generation
    with st.chat_message("assistant"):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash', # Changed to stable 2.0
                contents=gemini_history,
                config=config
            )

            # Handle Tools
            if response.function_calls:
                for call in response.function_calls:
                    tool_name = call.name
                    tool_args = call.args
                    
                    with st.status(f"🤖 Agent executing: {tool_name}...", expanded=True) as status:
                        observation = AVAILABLE_TOOLS[tool_name](**tool_args)
                        st.code(observation, language="text")
                        status.update(label=f"✓ Tool Complete", state="complete", expanded=False)

                    # Tool Response Synthesis
                    follow_up = gemini_history + [
                        types.Content(role="model", parts=[types.Part.from_function_call(name=tool_name, args=tool_args)]),
                        types.Content(role="user", parts=[types.Part.from_function_response(name=tool_name, response={"result": observation})])
                    ]
                    
                    final_response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=follow_up,
                        config=config
                    )
                    st.write(final_response.text)
                    active_messages.append({"role": "assistant", "content": final_response.text})
            else:
                st.write(response.text)
                active_messages.append({"role": "assistant", "content": response.text})
                
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
        # Handle autonomous tool loops seamlessly
        if response.function_calls:
            for call in response.function_calls:
                tool_name = call.name
                tool_args = call.args
                
                with st.status(f"🤖 Agent executing: {tool_name}...", expanded=True) as status:
                    st.write(f"**Arguments:** `{tool_args}`")
                    observation = AVAILABLE_TOOLS[tool_name](**tool_args)
                    st.write("**Observation:**")
                    st.code(observation, language="text")
                    status.update(label=f"✓ Tool Complete: {tool_name}", state="complete", expanded=False)

                follow_up_history = gemini_history + [
                    types.Content(role="model", parts=[types.Part.from_function_call(name=tool_name, args=tool_args)]),
                    types.Content(role="user", parts=[types.Part.from_function_response(name=tool_name, response={"result": observation})])
                ]
                
                try:
                    final_response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=follow_up_history,
                        config=config
                    )
                    final_text = final_response.text
                    st.write(final_text)
                    active_messages.append({"role": "assistant", "content": final_text})
                except Exception as e:
                    st.error(f"Could not complete tool response synthesis: {str(e)}")
                    st.stop()
        else:
            st.write(response.text)
            active_messages.append({"role": "assistant", "content": response.text})

    # FIXED MECHANIC: We change the chat title at the VERY END of the loop.
    # Because the agent has already answered, we don't need st.rerun() anymore.
    # The new title will simply show up naturally on the next interaction or page refresh.
    if st.session_state.all_chats[current_chat_id]["title"] == "New Chat":
        preview_title = user_input[:22] + "..." if len(user_input) > 22 else user_input
        st.session_state.all_chats[current_chat_id]["title"] = preview_title
