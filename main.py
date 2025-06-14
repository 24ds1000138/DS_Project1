from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from qa_engine import QAEngine
from models import QuestionRequest
from pydantic import BaseModel
from typing import List
import os, re, json, requests
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
qa_engine = QAEngine(data_paths=["discourse_data.json", "tds_landing_content.json"])

AI_PROXY_URL = "https://aiproxy.sanand.workers.dev/v1/chat/completions"
AI_MODEL = "gpt-3.5-turbo"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('AI_PROXY_API_KEY')}"
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

def clean_answer(text):
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"(?i)^hi\\s+@?\\w+", "", text).strip()
    text = re.sub(r"(?i)^reply\\s+\\d+[:\\-\\s]*", "", text).strip()
    return text

class AnswerResponse(BaseModel):
    answer: str
    links: List[dict]

@app.post("/api/")
async def answer_question(req: Request):
    try:
        try:
            req_data = await req.json()
        except:
            raw = await req.body()
            req_data = json.loads(raw.decode())

        question = req_data.get("question", "")
        if not question:
            raise HTTPException(status_code=400, detail="Missing 'question' field")

        results = qa_engine.search(question, top_k=3)
        for result in results:
            raw_answer = clean_answer(result["answer"])

            payload = {
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Summarize: {raw_answer}"}
                ]
            }

            try:
                r = requests.post(AI_PROXY_URL, headers=HEADERS, json=payload)
                if r.status_code == 200:
                    answer = r.json()["choices"][0]["message"]["content"].strip()
                else:
                    print("⚠️ Proxy failure, status:", r.status_code)
                    answer = raw_answer
            except Exception as e:
                print("⚠️ Proxy error:", e)
                answer = raw_answer

            response_json = {"answer": answer, "links": result.get("links", [])}
            return response_json

        return {"answer": "No matching content found.", "links": []}
    except Exception as e:
        print("❌ Exception:", e)
        raise HTTPException(status_code=500, detail=str(e))
