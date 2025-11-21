from typing import List, Optional
from pydantic import BaseModel


class Document(BaseModel):
    filename: str
    content: str
    doc_type: str  # "support" or "html"


class BuildKBRequest(BaseModel):
    documents: List[Document]


class BuildKBResponse(BaseModel):
    message: str
    num_chunks: int


class TestCase(BaseModel):
    id: str
    feature: str
    scenario: str
    steps: List[str]
    expected_result: str
    grounded_in: List[str]


class GenerateTestCasesRequest(BaseModel):
    query: str


class GenerateTestCasesResponse(BaseModel):
    raw_output: str
    test_cases: List[TestCase]


class GenerateSeleniumScriptRequest(BaseModel):
    test_case: TestCase


class GenerateSeleniumScriptResponse(BaseModel):
    script: str
