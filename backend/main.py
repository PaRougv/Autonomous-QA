from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    BuildKBRequest,
    BuildKBResponse,
    GenerateTestCasesRequest,
    GenerateTestCasesResponse,
    GenerateSeleniumScriptRequest,
    GenerateSeleniumScriptResponse,
    TestCase,
)
from .rag_engine import build_knowledge_base, generate_test_cases, generate_selenium_script_from_test_case

app = FastAPI(title="Autonomous QA Agent Backend")

# Allow Streamlit on localhost to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local dev; tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/build_kb", response_model=BuildKBResponse)
def build_kb(req: BuildKBRequest):
    docs = [
        {
            "filename": d.filename,
            "content": d.content,
            "doc_type": d.doc_type,
        }
        for d in req.documents
    ]
    num_chunks = build_knowledge_base(docs)
    return BuildKBResponse(
        message="Knowledge Base Built",
        num_chunks=num_chunks,
    )


@app.post("/generate_test_cases", response_model=GenerateTestCasesResponse)
def generate_test_cases_endpoint(req: GenerateTestCasesRequest):
    result = generate_test_cases(req.query)
    return GenerateTestCasesResponse(
        raw_output=result["raw_output"],
        test_cases=result["test_cases"],
    )


@app.post("/generate_selenium_script", response_model=GenerateSeleniumScriptResponse)
def generate_selenium_script_endpoint(req: GenerateSeleniumScriptRequest):
    tc: TestCase = req.test_case
    script = generate_selenium_script_from_test_case(tc)
    return GenerateSeleniumScriptResponse(script=script)
