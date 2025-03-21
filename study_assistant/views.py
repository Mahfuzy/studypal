import os
import hashlib
import tempfile
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AIRequestSerializer
from google import genai
from docx import Document
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# ✅ System Instruction for AI
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
"""

def process_uploaded_file(file_bytes, file_name):
    """Processes an uploaded file and returns AI-generated insights."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    file_extension = os.path.splitext(file_name)[1].lower()

    if file_extension == ".docx":
        # ✅ Extract text from DOCX
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        doc = Document(temp_file_path)
        extracted_text = "\n".join([para.text for para in doc.paragraphs])

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[f"Summarize this text: {extracted_text}"],
            config={"max_output_tokens": 500, "temperature": 0.5},
        )

    elif file_extension == ".pdf":
        # ✅ Save and process PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        my_file = client.files.upload(file=temp_file_path)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=["Can you summarize this file?", my_file],
            config={"max_output_tokens": 500, "temperature": 0.5},
        )

        os.remove(temp_file_path)  # ✅ Clean up

    else:
        return {"error": "Unsupported file type"}

    return {"response": response.text}

# ✅ Main API View
class TaeAIView(APIView):
    """Handles AI study assistant queries via Google Gemini API, including file processing."""

    @swagger_auto_schema(
        operation_description="Send a query to the AI study assistant or upload a file for processing",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'query': openapi.Schema(type=openapi.TYPE_STRING, description='The question or prompt for the AI'),
                'file': openapi.Schema(type=openapi.TYPE_FILE, description='Optional file to process (PDF or DOCX)'),
            },
            required=['query']
        ),
        responses={
            200: openapi.Response(
                description="Query processed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'response': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    def post(self, request):
        serializer = AIRequestSerializer(data=request.data)
        if serializer.is_valid():
            prompt = serializer.validated_data.get("query")
            uploaded_file = request.FILES.get("file")

            # ✅ Check Cache Before AI Call
            query_hash = hashlib.md5(prompt.encode()).hexdigest()
            cached_response = cache.get(query_hash)

            if cached_response:
                return Response({"response": cached_response})  # ✅ Return cached result

            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

            try:
                if uploaded_file:
                    # ✅ Process File
                    result = process_uploaded_file(uploaded_file.read(), uploaded_file.name)
                    return Response(result)

                else:
                    # ✅ Process Text Query
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[prompt],
                        config={"max_output_tokens": 400, "temperature": 0.5},
                    )

                    response_text = response.text
                    cache.set(query_hash, response_text, timeout=86400)  # ✅ Cache for 24 hours

                    return Response({"response": response_text})

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def some_task_function():
    # Task logic here
    pass
