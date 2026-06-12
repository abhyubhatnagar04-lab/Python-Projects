import streamlit as st
import os
from google import genai
from google.genai import types
from duckduckgo_search import DDGS
from datetime import date

# ==========================================
# 1. MODEL POOL — ordered by daily quota
# ==========================================
MODEL_POOL = [
    {"id": "gemini-2.5-flash-lite-preview-06-17", "label": "Gemini 2.5 Flash Lite", "rpd": 500,  "rpm": 10},
    {"id": "gemma-3-27b-it",                      "label": "Gemma 3 27B",            "rpd": 1500, "rpm": 30},
    {"id": "gemma-3n-e4b-it",                     "label": "Gemma 3n E4B",           "rpd": 1500, "rpm": 30},
    {"id": "gemini-2.0-flash-lite",               "label": "Gemini 2.0 Flash Lite",  "rpd": 200,  "rpm": 30},
    {"id": "gemini-2.0-flash",                    "label": "Gemini 2.0 Flash",       "rpd": 200,  "rpm": 15},
    {"id": "gemini-2.5-flash",                    "label": "Gemini 2.5 Flash",       "rpd": 20,   "rpm": 5},
]

TOTAL_DAILY = sum(m["rpd"] for m in MODEL_POOL)  # ~3920 requests/day

# ==========================================
# 2. UI CONFIGURATION
# ==========================================
st.set_page_config(page_title="Free AI Assistant", page_icon="🤖", layout="centered")

# ==========================================
# 3. SESSION STATE INIT
# ==========================================
TODAY = str(date.today())

defaults = {
    "all_chats": {"chat_1": {"title": "New Chat", "messages": []}},
    "current_chat_id": "chat_1",
    # Per-model usage tracking (resets daily)
    "usage_date": TODAY,
    "usage_today": {m["id"]: 0 for m in MODEL_POOL},
    "model_idx": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Reset usage counters if it's a new day
if st.session_state.usage_date != TODAY:
    st.session_state.usage_date = TODAY
    st.session_state.usage_today = {m["id"]: 0 for m in MODEL_POOL}
    st.session_state.model_idx = 0

current_chat_id = st.session_state.current_chat_id
active_messages = st.session_state.all_chats[current_chat_id]["messages"]

# ==========================================
# 4. MODEL ROTATION LOGIC
# ==========================================
def get_available_model():
    """Return the next model that still has daily quota, or None if all exhausted."""
    for i in range(len(MODEL_POOL)):
        idx = (st.session_state.model_idx + i) % len(MODEL_POOL)
        model = MODEL_POOL[idx]
        used = st.session_state.usage_today.get(model["id"], 0)
        if used < model["rpd"]:
            st.session_state.model_idx = idx
            return model
    return None

def mark_model_exhausted(model_id):
    """Force-exhaust a model when a quota error is received."""
    for m in MODEL_POOL:
        if m["id"] == model_id:
            st.session_state.usage_today[model_id] = m["rpd"]
    # Advance to next model
    st.session_state.model_idx = (st.session_state.model_idx + 1) % len(MODEL_POOL)

def bump_usage(model_id):
    st.session_state.usage_today[model_id] = st.session_state.usage_today.get(model_id, 0) + 1

def total_used():
    return sum(st.session_state.usage_today.values())

# ==========================================
# 5. SIDEBAR
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
        label = f"👉 {chat_data['title']}" if is_active else f"💬 {chat_data['title']}"
        if st.button(label, key=f"nav_{chat_id}", use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.markdown("---")

    # API Key
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Gemini API Key (free):", type="password")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
    else:
        st.caption("✓ Gemini API Key active")

    st.markdown("---")

    # Daily quota dashboard
    st.subheader("📊 Daily Quota")
    used = total_used()
    st.progress(min(used / TOTAL_DAILY, 1.0), text=f"{used} / {TOTAL_DAILY} requests used")

    for m in MODEL_POOL:
        u = st.session_state.usage_today.get(m["id"], 0)
        pct = u / m["rpd"]
        icon = "🔴" if pct >= 1 else "🟡" if pct >= 0.7 else "🟢"
        st.caption(f"{icon} {m['label']}: {u}/{m['rpd']}")

# ==========================================
# 6. TOOLS
# ==========================================
def calculate_investment_growth(principal: float, rate: float, years: int) -> str:
    """Calculates the compound interest growth of an investment over time."""
    amount = principal * ((1 + rate / 100) ** years)
    return f"After {years} years at {rate}% interest, ${principal:,.2f} grows to ${amount:,.2f}"

def web_search(query: str) -> str:
    """Searches the internet for real-time information, news, or current events."""
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No results found."
        return "\n".join([
            f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n---"
            for r in results
        ])
    except Exception as e:
        return f"Search error: {str(e)}"

AVAILABLE_TOOLS = {
    "calculate_investment_growth": calculate_investment_growth,
    "web_search": web_search,
}

# ==========================================
# 7. CHAT INTERFACE
# ==========================================
current_model = get_available_model()
model_label = current_model["label"] if current_model else "⚠️ All quotas exhausted"

st.title("🤖 Free Autonomous AI Assistant")
st.caption(
    f"Active model: **{model_label}** · "
    f"Session: *{st.session_state.all_chats[current_chat_id]['title']}*"
)

for msg in active_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ==========================================
# 8. INPUT & AGENT LOOP
# ==========================================
if user_input := st.chat_input("Ask me anything…"):
    if not os.getenv("GEMINI_API_KEY"):
        st.error("Please enter your free Gemini API key in the sidebar.")
        st.stop()

    model = get_available_model()
    if model is None:
        st.error("All model quotas are exhausted for today. They reset at midnight UTC.")
        st.stop()

    client = genai.Client()

    with st.chat_message("user"):
        st.write(user_input)
    active_messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        config = types.GenerateContentConfig(
            system_instruction=(
                "You are a helpful autonomous AI agent. Use your knowledge to answer "
                "general questions directly. Use web_search only for real-time or "
                "current-events queries. Use calculate_investment_growth only for "
                "compound interest calculations."
            ),
            tools=[calculate_investment_growth, web_search],
            temperature=0.3,
        )

        gemini_history = []
        for msg in active_messages:
            role = "model" if msg["role"] == "assistant" else msg["role"]
            gemini_history.append(
                types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
            )

        # --- Retry loop: try models until one works ---
        response = None
        for attempt in range(len(MODEL_POOL)):
            model = get_available_model()
            if model is None:
                st.error("All model quotas exhausted for today.")
                st.stop()

            try:
                response = client.models.generate_content(
                    model=model["id"],
                    contents=gemini_history,
                    config=config,
                )
                bump_usage(model["id"])
                break  # success

            except Exception as e:
                err = str(e)
                if any(code in err for code in ["429", "quota", "QUOTA", "RESOURCE_EXHAUSTED"]):
                    st.toast(f"⚠️ {model['label']} quota hit — switching model…", icon="🔄")
                    mark_model_exhausted(model["id"])
                    continue  # try next model
                elif any(code in err for code in ["503", "UNAVAILABLE"]):
                    st.error("Google's servers are overloaded. Wait a moment and retry.")
                    st.stop()
                else:
                    st.error(f"Unexpected error: {err}")
                    st.stop()

        if response is None:
            st.error("Could not get a response from any model.")
            st.stop()

        # --- Handle tool calls ---
        if response.function_calls:
            for call in response.function_calls:
                tool_name = call.name
                tool_args = call.args

                with st.status(f"🔧 Running: {tool_name}…", expanded=True) as status:
                    st.write(f"**Arguments:** `{tool_args}`")
                    observation = AVAILABLE_TOOLS[tool_name](**tool_args)
                    st.write("**Result:**")
                    st.code(observation, language="text")
                    status.update(label=f"✓ Done: {tool_name}", state="complete", expanded=False)

                follow_up_history = gemini_history + [
                    types.Content(role="model", parts=[
                        types.Part.from_function_call(name=tool_name, args=tool_args)
                    ]),
                    types.Content(role="user", parts=[
                        types.Part.from_function_response(
                            name=tool_name, response={"result": observation}
                        )
                    ]),
                ]

                # Retry synthesis with fallback too
                final_response = None
                for attempt in range(len(MODEL_POOL)):
                    model = get_available_model()
                    if model is None:
                        break
                    try:
                        final_response = client.models.generate_content(
                            model=model["id"],
                            contents=follow_up_history,
                            config=config,
                        )
                        bump_usage(model["id"])
                        break
                    except Exception as e:
                        err = str(e)
                        if any(code in err for code in ["429", "quota", "QUOTA", "RESOURCE_EXHAUSTED"]):
                            mark_model_exhausted(model["id"])
                            continue
                        st.error(f"Tool synthesis error: {err}")
                        st.stop()

                if final_response:
                    final_text = final_response.text
                    st.write(final_text)
                    active_messages.append({"role": "assistant", "content": final_text})
                else:
                    st.error("All models exhausted during tool synthesis.")
        else:
            st.write(response.text)
            active_messages.append({"role": "assistant", "content": response.text})

    # Update chat title from first message
    if st.session_state.all_chats[current_chat_id]["title"] == "New Chat":
        preview = user_input[:22] + "…" if len(user_input) > 22 else user_input
        st.session_state.all_chats[current_chat_id]["title"] = preview
