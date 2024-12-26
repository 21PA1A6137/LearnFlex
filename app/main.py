import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import yaml
import streamlit as st
from models.text_generation import generate_explanation
from langchain_groq import ChatGroq
from utils.history import save_chat_history_json, get_time_stamp, load_chat_history_json, generate_summary
from models.pdf_generation import generate_pdf
from langchain.memory import StreamlitChatMessageHistory
from streamlit_mic_recorder import mic_recorder
from models.audio_handler import transcribe_audio
from models.text_to_speech import text_to_speech_pyttsx3
from utils.llm_chains import load_normal_chain
from dotenv import load_dotenv

load_dotenv()

# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
groq_api_key="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"

st.set_page_config(page_title="LearnFlex: Personalized Learning Assistant", layout="wide")


with open("config.yaml") as f:
    config = yaml.safe_load(f)
    
def load_chain(chat_history):
    return load_normal_chain(chat_history)

def clear_input_field():
    st.session_state.user_qa = st.session_state.user_input
    st.session_state.user_input = ""

# set the send input flag
def set_send_input():
    st.session_state.send_input = True
    clear_input_field()

# set the session index
def index_tracker():
    if st.session_state.session_key != "new_session":
        st.session_state.history = load_chat_history_json(os.path.join(config["sessions_dir"], st.session_state.session_key))
    else:
        st.session_state.history = []

def save_chat_history():
    """Save chat history with a summary-based filename."""
    if st.session_state.history:
        if st.session_state.session_key == "new_session":
            llm = ChatGroq(api_key=groq_api_key, model_name="llama-3.1-70b-versatile", temperature=0.7)
            summary = generate_summary(st.session_state.history, llm)
            filename = summary
            st.session_state.new_session_key = filename
            save_chat_history_json(st.session_state.history, os.path.join(config["sessions_dir"], filename))
        else:
            save_chat_history_json(st.session_state.history, os.path.join(config["sessions_dir"], st.session_state.session_key))

def generate_and_cache_pdf():
    """Generate and cache the PDF to avoid re-execution."""
    if "pdf_path" not in st.session_state or st.session_state.re_generate_pdf:
        st.session_state["pdf_path"] = generate_pdf(
            st.session_state.history,
            st.session_state.subject,
            st.session_state.unit_number,
            st.session_state.faculty_name,
            st.session_state.pdf_name,
            st.session_state.summary,
        )
        st.session_state.re_generate_pdf = False


def full_conversation_to_speech(history):
    # Check the message type and extract content accordingly
    full_text = " ".join([msg.content for msg in history])  # Access the content directly
    return text_to_speech_pyttsx3(full_text)

def main():
    st.title("LearnFlex: Personalized Learning Assistant")
    
    chat_container = st.container()
    
    st.sidebar.title("Sessions")

    chat_sessions = ["new_session"]+os.listdir(config["sessions_dir"])
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        
    if "history" not in st.session_state:
        st.session_state["history"] = [] 
    
    if "pdf_generated" not in st.session_state:
        st.session_state.pdf_generated = False 
        
    if "generated_answer" not in st.session_state:
        st.session_state.generated_answer = False  

    
    if "send_input" not in st.session_state:
        st.session_state.session_key = "new_session"
        st.session_state.send_input = False
        st.session_state.user_qa = ""
        st.session_state.new_session_key = None
        st.session_state.session_index_tracker = "new_session"
        st.session_state.generated_answer = False
        st.session_state.pdf_generated = False
        
    if st.session_state.session_key == "new_session" and st.session_state.new_session_key != None:
        st.session_state.session_index_tracker = st.session_state.new_session_key
        st.session_state.new_session_key = None
        
    index = chat_sessions.index(st.session_state.session_index_tracker)
    st.sidebar.selectbox("Select a chat session", chat_sessions, key="session_key", index=index, on_change=index_tracker)

    if st.session_state.session_key != "new_session":
        st.session_state.history = load_chat_history_json(config["sessions_dir"] + st.session_state.session_key)
    else:
        st.session_state.history = []
    
    
    
    chat_history = StreamlitChatMessageHistory(key="history")
    # groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("Error: GROQ_API_KEY is missing. Please add it to your .env file.")
        return

    llm = ChatGroq(api_key=groq_api_key, model_name="llama-3.1-70b-versatile", temperature=0.7)

    st.sidebar.title("Options")
    st.session_state.subject = st.sidebar.text_input("Enter Subject", "")
    st.session_state.difficulty = st.sidebar.selectbox("Select Difficulty", ["easy", "medium", "hard"])
    st.session_state.pdf_name = st.sidebar.text_input("Enter PDF Name", "")
    st.session_state.unit_number = st.sidebar.text_input("Enter Unit Number", "") # Replace with your dynamic unit number
    st.session_state.faculty_name = st.sidebar.text_input("Enter Faculty Name", "")
    
    user_input = st.text_input("Enter your message:", key="user_input",on_change=set_send_input)
    voice_recording_col,submit_col = st.columns(2)
    
    with voice_recording_col:
        voice_recording=mic_recorder(start_prompt="Start recording",stop_prompt="Stop recording", just_once=True)
        
    with submit_col:
        submit = st.button("Submit", key="submit", help="Click to send your input")

    
    if voice_recording:
        transcribed_audio = transcribe_audio(voice_recording["bytes"])
        print(transcribed_audio)
        llm_chain = load_chain(chat_history)
        llm_chain.run(transcribed_audio)
    
    
    if submit or st.session_state.get("send_input", False): 
        with st.spinner("Processing your message..."):
            user_message = st.session_state.user_qa
            if user_message:
                llm_response = generate_explanation(
                    user_message, 
                    st.session_state.difficulty, 
                    llm, 
                    st.session_state.subject
                )
                chat_history.add_user_message(user_message)
                chat_history.add_ai_message(llm_response)
                
                st.session_state.generated_answer = True
                st.session_state.pdf_generated = False 

        st.session_state.send_input = False

    if chat_history.messages:
        with chat_container:
            st.write("Chat History")
            for message in chat_history.messages:
                st.chat_message(message.type).write(message.content)

    save_chat_history() 




    if st.sidebar.button("Generate PDF"):
        if "pdf_path" not in st.session_state or st.session_state.pdf_generated is False:
            with st.spinner("Generating PDF..."):
                st.session_state["pdf_path"] = generate_pdf(
                    st.session_state.history,
                    st.session_state.subject,
                    st.session_state.unit_number,
                    st.session_state.faculty_name,
                    st.session_state.pdf_name,
                    generate_summary(st.session_state.history, llm)
                )
                st.session_state.pdf_generated = True 
                st.sidebar.success("PDF has been generated.")

        if st.session_state.get("pdf_path"):
            with open(st.session_state["pdf_path"], "rb") as pdf_file:
                st.sidebar.download_button(
                    label="Download PDF",
                    data=pdf_file,
                    file_name=st.session_state["pdf_path"],
                    mime="application/pdf"
                )
        else:
            st.error("Failed to generate or locate the PDF.")

    chat_number = st.sidebar.text_input("Enter chat number (or 'all' for full conversation):")

    if not chat_number:
        chat_number = 'all'
    if st.sidebar.button("Convert to Speech"):
        full_text = None  # Default value for the text to be converted

        if chat_number.lower() == 'all':
            if len(st.session_state.history) > 0:
                full_text = ""
                for i in range(0, len(st.session_state.history), 2):
                    user_msg = st.session_state.history[i]
                    if i + 1 < len(st.session_state.history):
                        assistant_msg = st.session_state.history[i + 1]
                        full_text += f"Question: {user_msg.content} .... Answer: {assistant_msg.content} "
            else:
                st.error("No conversation history available to convert!")
        else:
            try:
                chat_index = int(chat_number) -1  # Convert to 0-based index
                if 0 <= chat_index < len(st.session_state.history):
                    selected_chat = st.session_state.history[chat_index]
                    full_text = f"Question: {selected_chat.content} " 
                    if chat_index + 1 < len(st.session_state.history):
                        assistant_response = st.session_state.history[chat_index + 1]
                        full_text += f"Answer: {assistant_response.content}"
                    
                else:
                    st.error(f"Invalid chat number! Please enter a number between 1 and {len(st.session_state.history)}.")
            except ValueError:
                st.error("Please enter a valid number or 'all' for full conversation.")

        if full_text:
            audio_file = text_to_speech_pyttsx3(full_text)

            st.sidebar.audio(audio_file, format="audio/mp3")

            st.sidebar.download_button(
                label="Download Audio",
                data=audio_file,
                file_name="selected_chat.mp3" if chat_number.lower() != 'all' else "full_conversation.mp3",
                mime="audio/mp3"
            )
if __name__ == "__main__":
    main()
