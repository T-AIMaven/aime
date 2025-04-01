import streamlit as st
import re
import json
from inference_pipeline.salesAgent import SalesAgent
from inference_pipeline.trustAgent import TrustAgent
import uuid

# CSS for chat styling
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


def display_message(message, sender="assistant"):
    icon = "🤖" if sender == "assistant" else "👤"
    alignment = "assistant" if sender == "assistant" else "user"
    st.markdown(f"""
        <div class="chat-message {alignment}">
            <div class="icon">{icon}</div>
            <div class="text">{message}</div>
        </div>
    """, unsafe_allow_html=True)


# Callback function to handle sending messages
def send_message():
    user_input = st.session_state.user_input.strip()
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"message": user_input, "sender": "user"})

        # Get response from TrustAgent
        response = st.session_state.trustAgent.chat(user_input)

        # Check if the response contains "end"
        if "Thank you for sharing all these details" in response:
            st.text("Thank you for providing all the details! The conversation has ended.")
            st.session_state.chat_history.append({"message": response, "sender": "assistant"})
            # Clear the input field
            st.session_state.user_input = ""
            
            # Extract property requirements
            extracted_data = st.session_state.trustAgent.extract_property_requirements()
            
            
            # st.subheader("Extracted Data")
            # st.text(str(extracted_data))

            # Get top-K properties
            top_k_properties = st.session_state.salesAgent.execute_query(query=extracted_data)
            # st.subheader("Top-K Properties")
            # st.text(str(top_k_properties))

            # Build customer profile
            customer_profile = st.session_state.trustAgent.profile_building()
            # st.subheader("Customer Profile")
            # st.text(str(customer_profile))

            # Perform property matching
            property_matching = st.session_state.trustAgent.property_matching(
                customer_profile=customer_profile, 
                top_k_properties=top_k_properties
            )
            # st.subheader("Property Matching")
            # st.text(str(property_matching))

            st.session_state.chat_history.append({"message": str(property_matching), "sender": "assistant"})
            
        # Add assistant's response to chat history
        st.session_state.chat_history.append({"message": response, "sender": "assistant"})

        # Clear the input field
        st.session_state.user_input = ""


# Title of the app
st.title("TrustAgent Chat Application")

# Initialize TrustAgent
if "trustAgent" not in st.session_state:
    st.session_state.trustAgent = TrustAgent()

# Initialize SalesAgent
if "salesAgent" not in st.session_state:
    st.session_state.salesAgent = SalesAgent()

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display greeting message when the app is first loaded
if "greeting_displayed" not in st.session_state:
    st.session_state.greeting_displayed = False

if not st.session_state.greeting_displayed:
    # Send a "hello" message to TrustAgent and display the response
    greeting_response = st.session_state.trustAgent.chat("hello")
    display_message(greeting_response, sender="assistant")
    st.session_state.greeting_displayed = True

# Display chat history
for chat in st.session_state.chat_history:
    display_message(chat["message"], sender=chat["sender"])

# st.subheader("Top-K Properties") 
# st.text("top_k_properties")

# User input field
st.text_input("You:", key="user_input", placeholder="Type your message here...", on_change=send_message)