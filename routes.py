from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
import json
import re

from gemini_service import generate_response


router = APIRouter()


# -----------------------------------------
# QnA
# -----------------------------------------

@router.post("/qa")
async def question_answer(
    question: str = Form(...)
):

    prompt = f"""
You are EduGenie, an educational AI assistant.

Answer the student's question clearly and accurately.

Question:
{question}

Requirements:
- Use simple language.
- Explain the answer clearly.
- Use short paragraphs.
- Use headings when useful.
- Use bullet points when useful.
- Give examples when helpful.
- Make the explanation suitable for a school or college student.
- Do not invent facts.
"""

    answer = await generate_response(prompt)

    return {
        "feature": "QnA",
        "answer": answer
    }


# -----------------------------------------
# Explain
# -----------------------------------------

@router.post("/explain")
async def explain(
    topic: str = Form(...)
):

    prompt = f"""
You are EduGenie, an educational AI assistant.

Explain the following topic in simple,
scientifically accurate language.

Topic:
{topic}

Requirements:

- Start with a clear definition.
- Explain the main idea.
- Break complicated ideas into simple steps.
- Use headings.
- Use bullet points when useful.
- Give a simple real-world example when appropriate.
- Use correct terminology.
- Avoid unnecessary technical language.
- Do not make unsupported claims.
- Make the answer suitable for a school or college student.
"""

    answer = await generate_response(prompt)

    return {
        "feature": "Explain",
        "answer": answer
    }


# -----------------------------------------
# Interactive Quiz
# -----------------------------------------

@router.post("/quiz")
async def quiz(
    topic: str = Form(...)
):

    prompt = f"""
You are EduGenie, an educational quiz generator.

Create a quiz about:

{topic}

Create exactly 5 multiple-choice questions.

Each question must contain:

- question
- exactly 4 options
- correct answer
- short explanation

IMPORTANT:

Return ONLY valid JSON.

Do not use Markdown.
Do not use ```json.
Do not write anything before or after the JSON.

Use exactly this structure:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": 0,
            "explanation": "Short explanation"
        }}
    ]
}}

The "answer" field must be the zero-based index
of the correct option.

For example:

0 = first option
1 = second option
2 = third option
3 = fourth option

Make the questions suitable for a school or college student.
Make sure there is only one correct answer for each question.
"""

    answer = await generate_response(prompt)

    try:

        # Remove accidental Markdown code fences
        cleaned = answer.strip()

        cleaned = re.sub(
            r"^```json\s*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = re.sub(
            r"^```\s*",
            "",
            cleaned
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned
        )

        quiz_data = json.loads(cleaned)

        # Basic validation
        if "questions" not in quiz_data:
            raise ValueError("Missing questions")

        if not isinstance(
            quiz_data["questions"],
            list
        ):
            raise ValueError("Questions must be a list")

        if len(quiz_data["questions"]) != 5:
            raise ValueError(
                "Quiz must contain exactly 5 questions"
            )

        for question in quiz_data["questions"]:

            if "question" not in question:
                raise ValueError(
                    "Question text missing"
                )

            if "options" not in question:
                raise ValueError(
                    "Options missing"
                )

            if len(question["options"]) != 4:
                raise ValueError(
                    "Each question must have 4 options"
                )

            if "answer" not in question:
                raise ValueError(
                    "Correct answer missing"
                )

            if not isinstance(
                question["answer"],
                int
            ):
                raise ValueError(
                    "Answer must be an integer"
                )

            if question["answer"] not in [0, 1, 2, 3]:
                raise ValueError(
                    "Answer must be between 0 and 3"
                )

            if "explanation" not in question:
                raise ValueError(
                    "Explanation missing"
                )

        return JSONResponse({
            "feature": "Quiz",
            "quiz": quiz_data
        })

    except Exception as e:

        print("Quiz parsing error:", e)
        print("Gemini response:", answer)

        return JSONResponse(
            status_code=500,
            content={
                "error": (
                    "EduGenie could not create "
                    "the quiz correctly. "
                    "Please try again."
                )
            }
        )


# -----------------------------------------
# Summary
# -----------------------------------------

@router.post("/summarize")
async def summarize(
    text: str = Form(...)
):

    prompt = f"""
You are EduGenie, an educational summarization assistant.

Summarize the following text:

{text}

Requirements:

- Use simple language.
- Keep the summary concise.
- Include the most important points.
- Use headings when useful.
- Use bullet points when useful.
- Do not add information that is not present
  in the original text.
- Do not change the meaning of the original text.
"""

    answer = await generate_response(prompt)

    return {
        "feature": "Summary",
        "answer": answer
    }


# -----------------------------------------
# Learning Path
# -----------------------------------------

@router.post("/learn/recommendations")
async def learning_recommendations(
    topic: str = Form(...)
):

    prompt = f"""
You are EduGenie, an educational learning-path assistant.

Create a structured learning path for a student
who wants to learn:

{topic}

Requirements:

## 1. Beginner Level

List the important beginner topics.

## 2. Intermediate Level

List the important intermediate topics.

## 3. Advanced Level

List the important advanced topics.

## 4. Practice

Suggest practical exercises.

## 5. Mini Projects

Suggest small projects that help the student
apply what they learned.

Use simple language and clear Markdown formatting.
"""

    answer = await generate_response(prompt)

    return {
        "feature": "Learning Path",
        "answer": answer
    }