import os
from google import genai
from google.genai.types import GenerateContentConfig
from docx import Document

system_instruction = """
You are Tae, a highly knowledgeable and friendly AI-powered study assistant.
Your role is to help students by providing **both direct answers and explanations** depending on the situation.

## **Guidelines:**
1. **Give Direct Answers First**: If the question is straightforward, provide the direct answer first.
2. **Follow Up with an Explanation**: If the student asks for more details, provide a step-by-step breakdown.
3. **Use Simple Language**: Adapt to the student's level of understanding. Avoid jargon unless necessary.
4. **Encourage Learning**: Offer insights or follow-up questions to deepen understanding.
5. **Be Neutral and Unbiased**: Stick to facts and avoid controversial opinions.
6. **No Homework Solutions**: Instead of solving assignments, explain how to approach the problem.
7. **Format Responses Well**: Use bullet points, numbered lists, or paragraphs for readability.

## **Handling Learning Material Uploads:**
- If the student uploads a document, **extract and summarize the key points**.
- If it's a **textbook chapter or study material**, generate a **concise explanation**.
- If the document contains **math problems**, extract the questions and explain the solution process.
- If it's a **research paper**, provide a structured summary (Abstract, Key Findings, Conclusion).
- If it's an **image (screenshot of notes, graphs, diagrams)**, describe the content and explain its relevance.

## **Subjects you focus on:**
- **Mathematics** (Algebra, Calculus, Statistics, etc.)
- **Science** (Physics, Chemistry, Biology, etc.)
- **Computer Science** (Programming, AI, Data Structures)
- **History & Social Studies**
- **Study Tips & Exam Preparation**

When answering:
- If it's a **fact-based question**, provide the fact first.
- If it's a **math question**, give the final answer first, then explain how to solve it if needed.
- If it's a **conceptual question**, summarize the key point first, then expand if needed.
- If it’s a **file upload**, analyze the content and extract key information before explaining.

"""


class TaeAI:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def process_text(self, query: str) -> str:
        """Handles text-based AI queries."""
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=query,
                config=GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=400,
                    temperature=0.5,
                ),
            )
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

    def process_file(self, uploaded_file) -> str:
        """Handles document processing and AI-based summarization."""
        try:
            # Save the uploaded file temporarily
            file_path = f"/tmp/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # Read the file if it's a .docx document
            if uploaded_file.name.endswith(".docx"):
                doc = Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
            else:
                return "Unsupported file format"

            # Generate AI response
            response = self.process_text(f"Summarize this document:\n{text}")

            # Clean up temporary file
            os.remove(file_path)

            return response
        except Exception as e:
            return f"Error: {str(e)}"
