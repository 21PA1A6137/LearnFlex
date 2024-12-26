# import streamlit as st
# from models.text_generation import generate_explanation
# # from models.text_to_speech import text_to_speech
# # from app.pdf_generator import generate_pdf
# # from app.quiz import generate_quiz
# # from app.user_progress import update_user_score
# from langchain_groq import ChatGroq
# from dotenv import load_dotenv
# load_dotenv()


# def main():
#     groq_api_key = os.getenv("GROQ_API_KEY")
    
#     llm = ChatGroq(api_key=groq_api_key, model_name="llama-3.1-70b-versatile", temperature=0)
#     topic = st.text_input("Enter Topic")
#     difficulty = st.sidebar.selectbox("Select Difficulty", ["easy", "medium", "hard"])


#     if st.button("Generate Explanation"):
#         explanation = generate_explanation(topic, difficulty,llm)
#         st.write(explanation)
        
#         pdf_name = f"explanation_{topic}_{difficulty}.pdf"
#         audio_name = f"explanation_{topic}_{difficulty}.mp3"
        
#         # if st.button("Download PDF"):
#         #     generate_pdf(explanation, pdf_name)
#         #     st.download_button("Download PDF", pdf_name)
        
#         # if st.button("Download Audio"):
#         #     text_to_speech(explanation, audio_name)
#         #     st.download_button("Download Audio", audio_name)

#     # Quiz Section
#     # st.subheader("Take a Quiz")
#     # quiz = generate_quiz(difficulty)
#     # score = 0
    
#     # for q in quiz:
#     #     answer = st.text_input(q['question'])
#     #     if answer == q['answer']:
#     #         score += 1
    
#     # st.write(f"Your Score: {score}")
#     # if st.button("Submit Quiz"):
#     #     update_user_score(user_id, score)

# main()