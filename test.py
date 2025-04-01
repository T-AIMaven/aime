import streamlit as st
import pandas as pd
from orchestrator import OrchestrateAgent
from plotly.exceptions import PlotlyError
import re

# Initialize session state for user selections and question list if not already done
if 'user_selections' not in st.session_state:
    st.session_state.user_selections = {}
if 'question_list' not in st.session_state:
    st.session_state.question_list = {}
if "Task" not in st.session_state:
    st.session_state.Task = ""
if "task_type" not in st.session_state:
    st.session_state.task_type = ""
if "task3_option" not in st.session_state:
    st.session_state.task3_option = ""
if "chat_method" not in st.session_state:
    st.session_state.chat_method = "Options"
# Function to reset session state variables
def reset_session_state():
    st.session_state.user_selections = {}
    st.session_state.questionList = {}
    st.session_state.Task = ""
    st.session_state.task_type = ""
    st.session_state.task3_option = ""
# Sidebar for selecting chat method
st.sidebar.title("Chat Method")
chat_method = st.sidebar.radio("Select Chat Method:", ["Options", "Question/Answer"], key="chat_method")
# Create a temperature range slider between 0 and 2 in the sidebar
st.sidebar.title("Temperature")
TempRange = st.sidebar.slider(
    'Select a range of values',
    0.0, 2.0, (0.7), step=0.1
)
# Reset session state when chat method changes
if st.session_state.chat_method != chat_method:
    reset_session_state()
    st.session_state.chat_method = chat_method
# Streamlit app layout
st.title("Query and File Input Example")
# CSS for chat messages
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
if st.session_state.chat_method == "Options":
    # Text input for the query
    query = st.text_input("Enter your query:")
    # File uploader for the file input
    filePath = st.file_uploader("Upload a CSV file", type=["csv"])
    if st.button("Process"):
        reset_session_state()
        agent = OrchestrateAgent()
        query = query.lower()
        query = query.replace("-", "")
        cleaned_query = re.sub(r'\s+', ' ', query).strip()
        task = agent.orchestrate(cleaned_query, filePath)
        st.session_state.Task = task
        display_message(st.session_state.Task.taskType, sender="assistant")
        ## Task 1.
        if st.session_state.Task.taskType == "ClassifyStrategyInfoTask":
            figOrigin, response = st.session_state.Task.execute(TempRange)
            display_message(response, sender="assistant")
            st.plotly_chart(figOrigin)
        ## Task 2.
        elif st.session_state.Task.taskType == "FilterTradeEconomicTask":
            st.session_state.task_type = "FilterTradeEconomicTask"
            questionList = st.session_state.Task.optionExecute(TempRange)
            st.session_state.questionList = questionList  # Store questionList in session state
    ## Task 2
    # Create radio options for each key in the question list
    if st.session_state.task_type == "FilterTradeEconomicTask" and st.session_state.questionList:
        for subject, options in st.session_state.questionList.items():
            # Skip the 'selectStatus' key
            if subject == "selectStatus":
                continue
            # Add an explanation for each subject
            st.markdown(f"### What do you care more about following in **{subject}**?")
            # Initialize user selections for the current subject if not already done
            if subject not in st.session_state.user_selections:
                st.session_state.user_selections[subject] = []
            if isinstance(options, list):
                selection = st.radio(subject, options, 
                                     index=options.index(st.session_state.user_selections[subject]) 
                                     if st.session_state.user_selections[subject] in options else 0, 
                                     key=subject)
                st.session_state.user_selections[subject] = selection
            elif isinstance(options, dict):
                for option_key, option_values in options.items():
                    if option_key == "events" and "all" in st.session_state.questionList.get("selectStatus", []):
                        st.markdown(f"Skipping selection for **{subject} - {option_key}** because selectStatus is 'all'.")
                        st.session_state.user_selections[f"{subject}_{option_key}"] = option_values
                    elif option_key == "imtLvls" and "all" in st.session_state.questionList.get("selectStatus", []):
                        st.markdown(f"Skipping selection for **{subject} - {option_key}** because selectStatus is 'all'.")
                        st.session_state.user_selections[f"{subject}_{option_key}"] = option_values
                    else:
                        current_selection = st.session_state.user_selections.get(f"{subject}_{option_key}", [])
                        selection = st.multiselect(f"{subject} - {option_key}", option_values, 
                                                default=current_selection, 
                                                key=f"{subject}_{option_key}")
                        st.session_state.user_selections[f"{subject}_{option_key}"] = selection
    # Button to submit selections
    if st.session_state.task_type == "FilterTradeEconomicTask" and st.button("Submit task_2"):
        output_dict = {}
        # Collect selected values from user selections
        for subject, selection in st.session_state.user_selections.items():
            # Check for "dateopt"
            if subject == "dateOpt":
                output_dict["dateOpt"] = selection
            # Check for "imtLvls"
            elif subject.endswith("imtLvls"):
                output_dict["imtLvls"] = selection
            # Check for "events"
            elif subject.endswith("events"):
                output_dict.setdefault("events", []).append(selection)
        # Display the collected user selections as a dictionary
        display_message("User Selections:", sender="assistant")
        st.json(output_dict)
        output_dict["events"] = [event for event in output_dict["events"] if event is not None]
        if len(output_dict["events"]) == 0:
            display_message("There is no event to handle!", sender="assistant")
        else:
            response, figOrigin, figFilter = st.session_state.Task.getResponse(output_dict, TempRange)
            display_message(response, sender="assistant")
            # Use try-except to catch PlotlyError
            try:
                st.plotly_chart(figOrigin, key="figOrigin")
                st.plotly_chart(figFilter, key="figFilter")
            except PlotlyError as e:
                st.error(f"An error occurred while plotting the figure: {e}")
    ## Task 3
    if st.session_state.task_type == "FilterTradeHolidayTask":
        options = ["Date Opened", "Date Closed"]
        selected_option = st.radio("Choose one of the following options:", options)
        st.session_state.task3_option = selected_option
    if st.session_state.task_type == "FilterTradeHolidayTask" and st.button("Submit task_3"):
        response, figOrigin, figFilter = st.session_state.Task.execute(selected_option, TempRange)
        display_message(response, sender="assistant")
        st.plotly_chart(figOrigin, key="figOrigin")
        st.plotly_chart(figFilter, key="figFilter")
elif st.session_state.chat_method == "Question/Answer":
    # Text input for the query
    query = st.text_input("Enter your query:", key="taskClassify")
    # File uploader for the file input
    filePath = st.file_uploader("Upload a CSV file", type=["csv"])
    if st.button("Process"):
        display_message(query, sender="user")
        agent = OrchestrateAgent()
        query = query.lower()
        query = query.replace("-", "")
        cleaned_query = re.sub(r'\s+', ' ', query).strip()
        task = agent.orchestrate(cleaned_query, filePath)
        st.session_state.Task = task
        display_message(st.session_state.Task.taskType, sender="assistant")
        ## Task 1.
        if st.session_state.Task.taskType == "ClassifyStrategyInfoTask":
            figOrigin, response = st.session_state.Task.execute(TempRange)
            display_message(response, sender="assistant")
            st.plotly_chart(figOrigin)
        ## Task 2.
        elif st.session_state.Task.taskType == "FilterTradeEconomicTask":
            st.session_state.task_type = "FilterTradeEconomicTask"
            
            response, chatHistory, _ = st.session_state.Task.chatExecute(query, TempRange)
            display_message(response, sender="assistant")

            # st.text_input("Enter your query:", key="taskClassify", disabled=True)
        ## Task 3
        elif st.session_state.Task.taskType == "FilterTradeHolidayTask":
            st.session_state.task_type = "FilterTradeHolidayTask"
            options = ["Date Opened", "Date Closed"]
        ## Task 4
        elif st.session_state.Task.taskType == "IdentifyVixSpikeTask":
            print("app here")
            response, figOrigin, figFilter, figScatter = st.session_state.Task.execute(TempRange)
            display_message(response, sender="assistant")
            st.plotly_chart(figScatter, key="figScatter")
            st.plotly_chart(figOrigin, key="figOrigin")
            st.plotly_chart(figFilter, key="figFilter")
    ## Task 2
    # Create radio options for each key in the question list
    if st.session_state.task_type == "FilterTradeEconomicTask":
            query = st.text_input("Enter your answer to agent:")
            query = query.lower()
            query = query.replace("-", "")
            cleaned_query = re.sub(r'\s+', ' ', query).strip()
            if st.button("chat"):
                response, chatHistory, output_dict = st.session_state.Task.chatExecute(cleaned_query, TempRange)
                for message in chatHistory:
                    role = message["role"]
                    content = message["content"]
                    display_message(content, sender=role)
                
                if response == True:
                    response, figOrigin, figFilter = st.session_state.Task.chatFinalResponse(TempRange)
                    display_message(output_dict, sender="assistant")
                    display_message(response, sender="assistant")
                    # Use try-except to catch PlotlyError
                    try:
                        st.plotly_chart(figOrigin, key="figOrigin")
                        st.plotly_chart(figFilter, key="figFilter")
                    except PlotlyError as e:
                        st.error(f"An error occurred while plotting the figure: {e}")
    ## Task 3
    if st.session_state.task_type == "FilterTradeHolidayTask":
        options = ["Date Opened", "Date Closed"]
        selected_option = st.radio("Choose one of the following options:", options)
        st.session_state.task3_option = selected_option

    if st.session_state.task_type == "FilterTradeHolidayTask" and st.button("Submit task_3"):
        response, figOrigin, figFilter = st.session_state.Task.execute(selected_option, TempRange)
        display_message(response, sender="assistant")
        st.plotly_chart(figOrigin, key="figOrigin")
        st.plotly_chart(figFilter, key="figFilter")