# import json
# from datetime import datetime
# from langchain.schema.messages import HumanMessage,AIMessage

# def save_chat_history_json(chat_history, file_path):
#     with open(file_path, "w") as f:
#         json_data = [message.dict() for message in chat_history]
#         json.dump(json_data, f)

# def load_chat_history_json(file_path):
#     with open(file_path, "r") as f:
#         json_data = json.load(f)
#         messages = [HumanMessage(**message) if message["type"] == "human" else AIMessage(**message) for message in json_data]
#         return messages
    
# def get_time_stamp():
#     return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


import json
from datetime import datetime
from langchain.schema.messages import HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain


# def save_chat_history_json(chat_history, summary, file_path):
#     """Save chat history as a JSON file."""
#     # Create a safe filename with summary and timestamp
#     timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
#     sanitized_summary = "".join(c if c.isalnum() or c in " _-" else "_" for c in summary)[:50]
#     file_name = f"{sanitized_summary}_{timestamp}.json"
#     full_path = f"{file_path}/{file_name}"
    
#     # Save chat history
#     with open(full_path, "w") as f:
#         json_data = [message.dict() for message in chat_history]
#         json.dump(json_data, f)
#     return full_path




# def generate_summary(chat_history, llm):
#     """Generate a summary of the chat history."""
#     chat_content = "\n".join(
#         f"Human: {message.content}" if isinstance(message, HumanMessage)
#         else f"AI: {message.content}"
#         for message in chat_history
#     )
    
#     # Use an LLM to summarize the chat
#     prompt = PromptTemplate(
#         input_variables=["chat_content"],
#         template="Summarize the following chat in a few descriptive words:\n{chat_content}"
#     )
#     chain = LLMChain(llm=llm, prompt=prompt)
#     summary = chain.run({"chat_content": chat_content})
#     return summary.strip()



def save_chat_history_json(chat_history, file_path):
    """Save chat history in JSON format."""
    with open(file_path, "w") as f:
        json_data = [message.dict() for message in chat_history]
        json.dump(json_data, f)

def generate_summary(chat_history, llm):
    """Generate a descriptive summary for the chat history."""
    # Combine user messages for the summary
    conversation = " ".join([msg.content for msg in chat_history if msg.type == "human"])
    
    # Generate a summary from the LLM
    prompt = f"Summarize this chat briefly in a way suitable for naming a file: {conversation}"
    summary = llm.predict(prompt).strip()
    
    # Ensure the filename is safe for the filesystem
    sanitized_summary = "".join(c if c.isalnum() or c in " _-" else "_" for c in summary).strip()
    return sanitized_summary

def load_chat_history_json(file_path):
    """Load chat history from a JSON file."""
    with open(file_path, "r") as f:
        json_data = json.load(f)
        messages = [
            HumanMessage(**message) if message["type"] == "human" else AIMessage(**message)
            for message in json_data
        ]
        return messages

def get_time_stamp():
    """Get the current timestamp."""
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")



    
    
    
    
    
    
# def main():
#     st.set_page_config(page_title="QueryBridge - Talk to your data!", layout="wide")
    
#     st.title("QueryBridge - Talk to your data!")

#     st.subheader("Chat Interface")

#     if st.session_state["engine"] is None:
#         st.session_state["engine"] = initialize_sql_engine()

#     # uploaded_files = st.sidebar.file_uploader("Upload Files", type=["csv", "xlsx"], accept_multiple_files=True)

#     # if uploaded_files:
#     #     st.write("Processing uploaded files...")
#     #     save_uploaded_files_to_sql(uploaded_files, st.session_state["engine"])
#     #     # list_tables(st.session_state["engine"])  # Check uploaded tables
#     # else:
#     #     st.write("No files uploaded.")
    
#     for message in st.session_state["messages"]:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

#     if prompt := st.chat_input("What is your question?"):
#         st.session_state["messages"].append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.markdown(prompt)

#         with st.chat_message("assistant"):
#             response = generate_response(prompt, st.session_state["engine"])
#             st.markdown(response)
#         st.session_state["messages"].append({"role": "assistant", "content": response})

#     if st.sidebar.button("Clear Chat"):
#         st.session_state["messages"] = []