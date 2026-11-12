import json
import logging
from pathlib import Path
from threading import Lock

from fastapi import Depends, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import Settings, get_setting
from .database import make_session_factory
from .dependencies import get_db
from .model_db import Invoice, Proposal, Transfer
from .tools import build_tools

MAX_TOOL_ROUNDS = 4
TRACE_FILE = Path(__file__).resolve().parents[1] / "chat_trace.jsonl"
trace_lock = Lock()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Bạn là trợ lý đối soát hóa đơn. Trả lời bằng tiếng Việt dựa trên kết quả tool. "
    "Khi cần kiểm tra một hóa đơn, hãy dùng tool với mã người dùng cung cấp. "
    "Báo rõ nếu không tìm thấy hóa đơn, không có cặp phù hợp hoặc tool báo lỗi. "
    "Chỉ gọi tool tạo bản nháp đối soát khi người dùng yêu cầu tạo đề xuất."
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


def save_turn(question: str, answer: str, trace: list[dict], status: str = "ok"):
    response = {"status": status, "answer": answer, "trace": trace}
    record = {"question": question, **response}

    with trace_lock, TRACE_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

    return response


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI()
    engine, session_factory = make_session_factory(settings.database_url)
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.settings = settings

    tools = build_tools(session_factory)
    tools_by_name = {item.name: item for item in tools}

    model = None
    if settings.openai_model and settings.openai_api_key:
        model = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0,
        ).bind_tools(tools)

    def run_tool(name: str, args: dict, trace: list[dict], call_id: str | None = None):
        selected_tool = tools_by_name.get(name)

        if selected_tool is None:
            result = {"error": "unknown_tool"}
        else:
            try:
                result = jsonable_encoder(selected_tool.invoke(args))
            except ValidationError:
                result = {"error": "invalid_tool_arguments"}
            except Exception as exc:
                logger.warning("Tool %s failed: %s", name, type(exc).__name__)
                result = {"error": "tool_execution_failed"}

        trace.append({
            "tool_call_id": call_id,
            "name": name,
            "args": args,
            "result": result,
        })
        return result

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(Path(__file__).with_name("frontend.html"))

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/records")
    def records(db: Session = Depends(get_db)):
        queries = {
            "invoices": select(
                Invoice.id, Invoice.customer_id, Invoice.currency,
                Invoice.total_amount, Invoice.missing_amount,
            ).order_by(Invoice.id),
            "transfers": select(
                Transfer.id, Transfer.received_at, Transfer.customer_id,
                Transfer.currency, Transfer.amount, Transfer.status,
            ).order_by(Transfer.received_at, Transfer.id),
            "proposals": select(
                Proposal.id, Proposal.invoice_id, Proposal.transfer_id1, Proposal.transfer_id2,
            ).order_by(Proposal.invoice_id, Proposal.id),
        }
        return {
            name: [dict(row) for row in db.execute(query).mappings()]
            for name, query in queries.items()
        }

    @app.post("/api/chat")
    def chat(body: ChatRequest):
        if model is None:
            raise HTTPException(503, "Chưa cấu hình OpenAI. Có thể thử /api/demo/I-77.")

        question = body.message
        trace = []
        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=question)]

        for round_number in range(MAX_TOOL_ROUNDS + 1):
            try:
                reply = model.invoke(messages)
            except Exception as exc:
                logger.warning("Model call failed: %s", type(exc).__name__)
                return save_turn(question, "Không gọi được model.", trace, "model_error")

            if reply.invalid_tool_calls or any(not call.get("id") for call in reply.tool_calls):
                return save_turn(question, "Model gửi yêu cầu gọi tool không hợp lệ.",
                                 trace, "invalid_tool_call")

            if not reply.tool_calls:
                return save_turn(question, str(reply.text), trace)

            if round_number == MAX_TOOL_ROUNDS:
                break

            messages.append(reply)
            for call in reply.tool_calls:
                result = run_tool(call["name"], call["args"], trace, call["id"])
                messages.append(ToolMessage(
                    content=json.dumps(result, ensure_ascii=False),
                    tool_call_id=call["id"],
                ))

        return save_turn(question, "Đã đạt giới hạn số vòng gọi tool.", trace, "tool_limit")

    @app.post("/api/demo/{invoice_id}")
    def demo(invoice_id: str):
        trace = []
        question = f"Tìm cặp giao dịch cho hóa đơn {invoice_id}"
        result = run_tool("find_two_transfer_match", {"invoice_id": invoice_id}, trace)

        if isinstance(result, list):
            answer = f"Cặp giao dịch phù hợp cho {invoice_id} là {' và '.join(result)}."
        elif result.get("status") == "no_match":
            answer = f"Không tìm thấy cặp giao dịch phù hợp cho {invoice_id}."
        else:
            reason = result.get("error", "unexpected_result")
            return save_turn(question, f"Không thể đối soát {invoice_id} ({reason}).", trace, "error")

        return save_turn(question, answer, trace)

    return app


app = create_app(get_setting())
