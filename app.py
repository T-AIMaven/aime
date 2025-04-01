import streamlit as st
import re
import json
from inference_pipeline.salesAgent import SalesAgent
import uuid

st.markdown("""
    <style>
    .chat-message {
        border: 1px solid #ccc;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        display: flex;
        max-width: 75%;
    }
    .chat-message.assistant {
        background-color: #f1f1f1;
        text-align: left;
        align-items: center;
        justify-content: left;
    }
    .chat-message.user {
        background-color: #e1f5fe;
        align-items: center;
        justify-content: left;
    }
    .chat-message .icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
    }
    .chat-message.user .icon {
        margin-left: 10px;
        margin-right: 0;
    }
    .chat-message .text {
        color: black;
    }
    </style>
""", unsafe_allow_html=True)


# Function to generate unique keys
def create_unique_key(base):
    return f"{base}_{uuid.uuid4().hex}"


def display_message(message, sender="assistant"):
    icon = "🤖" if sender == "assistant" else "👤"
    alignment = "assistant" if sender == "assistant" else "user"
    st.markdown(f"""
        <div class="chat-message {alignment}">
            <div class="icon">{icon}</div>
            <div class="text">{message}</div>
        </div>
    """, unsafe_allow_html=True)


# Title of the app
st.title("Q&A Application")

# Initialize session state for property requirements
if "property_requirements" not in st.session_state:
    agent = SalesAgent("")
    st.session_state.agent = agent  # Store the agent in session state
    st.session_state.property_requirements = agent.property_requirements
    st.session_state.current_key = None
    st.session_state.question_count = 0
    st.session_state.asked_questions = set()
    st.session_state.collected_values = {}
    st.session_state.selections = {}  # New: Store selections for each key
    st.session_state.query_completed = False  # Track if the query has been executed

# Retrieve the agent from session state
agent = st.session_state.get("agent", None)

# Ensure the agent is properly initialized
if agent is None or not isinstance(agent, SalesAgent):
    st.session_state.agent = SalesAgent("")
    agent = st.session_state.agent

# Predefined options for each property requirement
options = {
    "project_name": ["Aspen Village", "The Establishment", "High Society"],
    "state": ["NSW", "VIC", "QLD"],
    "listing_price": ["403900", "488900", "581900", "679900", "685900"],
    "Bedroom": ["1", "2", "3"],
    "Bathroom": ["1", "2", "3"],
    "car_park": ["1", "2", "3"],
    "aspect": ["N", "SW", "E", "NW"],
    "level": ["10"],
    "storage": ["Yes", "No"],
    "int": ["47", "69", "73", "91", "100"],
    "ext": ["8", "9", "24"]
}

# Check if all property requirements are collected
all_collected = all(value is not None for value in st.session_state.property_requirements.values())

if not all_collected:
    # Find the next unanswered question
    for key, value in st.session_state.property_requirements.items():
        if not value and key not in st.session_state.asked_questions:
            st.session_state.current_key = key
            break

    if st.session_state.current_key:
        display_message(
            f"Let's talk about your preferences. Could you please provide details for **{st.session_state.current_key}**? "
            f"Here are some options to choose from:",
            sender="assistant"
        )
        
        selectbox_key = f"selectbox_{st.session_state.current_key}"
        options_list = options.get(st.session_state.current_key, [])
        
        # Initialize the selection for this key if it doesn't exist
        if st.session_state.current_key not in st.session_state.selections:
            st.session_state.selections[st.session_state.current_key] = options_list[0]
        
        # Use the stored selection as the index
        selected_index = options_list.index(st.session_state.selections[st.session_state.current_key])
        
        # Updated selectbox with index to retain selection state
        selected_value = st.selectbox(
            f"Select a value for {st.session_state.current_key}:",
            options_list,
            index=selected_index,
            key=selectbox_key
        )

        # Update selection in session state based on user interaction
        st.session_state.selections[st.session_state.current_key] = selected_value

        if st.button("Submit"):
            # Update session state with selected value
            st.session_state.property_requirements[st.session_state.current_key] = selected_value
            st.session_state.collected_values[st.session_state.current_key] = selected_value
            st.session_state.asked_questions.add(st.session_state.current_key)
            
            display_message(
                f"Thank you! I've noted that your preference for **{st.session_state.current_key}** is **{selected_value}**.",
                sender="assistant"
            )
            
            # Reset current key, then rerun the script to move to the next question
            st.session_state.current_key = None
            
            # Rerun the app to refresh and move to the next question
            st.rerun()

# If all property requirements are collected and query has not been executed yet
if all_collected and not st.session_state.query_completed:
    print(st.session_state.collected_values)
    QA = SalesAgent("")
    response = QA.execute_query(st.session_state.collected_values)  # Changed method call
    display_message("Here are the top results based on your preferences:", sender="assistant")
    display_message(response, sender="assistant")
    st.session_state.query_completed = True
