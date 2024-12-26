from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

def generate_explanation(topic, difficulty, llm, subject):
    """
    Generate an explanation based on the topic and difficulty level.
    """

    
    if difficulty.lower() == "easy":
        prompt = PromptTemplate(
            input_variables=["topic", "subject"],
            template="""
                Explain the topic '{topic}' from the subject '{subject}' in a fun and simple way that a 10-year-old kid can understand.
                Use examples, comparisons, and simple language. Avoid technical jargon and make it relatable with stories or analogies.
            """
        )
    elif difficulty.lower() == "medium":
        prompt = PromptTemplate(
            input_variables=["topic", "subject"],
            template="""
                Provide a detailed explanation of the topic '{topic}' from the subject '{subject}' for a college-level audience.
                Include key concepts, relevant examples, and practical applications. Use some technical terms but ensure the explanation is clear and structured.
                Assume the reader has basic prior knowledge of the subject.
            """
        )
    elif difficulty.lower() == "hard":
        prompt = PromptTemplate(
            input_variables=["topic", "subject"],
            template="""
                Explain the topic '{topic}' from the subject '{subject}' comprehensively, tailored for a professional or subject expert.
                Dive into the advanced technical details, supporting theories, and use industry-specific terminology where appropriate.
                Include references to research, practical implications, and emerging trends.
            """
        )
    else:
        raise ValueError("Invalid difficulty level. Please choose 'easy', 'medium', or 'hard'.")


    chain = LLMChain(llm=llm, prompt=prompt)

    explanation = chain.run({"topic": topic, "difficulty": difficulty,"subject": subject})
    
    return explanation

