from fastapi import FastAPI, WebSocket
from database import engine, Base, SessionLocal
from models import Document
from sqlalchemy.orm import Session

app = FastAPI()

Base.metadata.create_all(bind=engine)

connections = []

@app.get("/")
def home():
    return {"message": "Server running"}

@app.get("/document/{doc_id}")
def get_document(doc_id: int):
    db: Session = SessionLocal()
    doc = db.query(Document).filter(Document.id == doc_id).first()
    return {"content": doc.content if doc else ""}

@app.post("/document/{doc_id}")
def save_document(doc_id: int, content: str):
    db: Session = SessionLocal()
    doc = db.query(Document).filter(Document.id == doc_id).first()

    if doc:
        doc.content = content
    else:
        doc = Document(id=doc_id, content=content)
        db.add(doc)

    db.commit()
    return {"status": "saved"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            for conn in connections:
                await conn.send_text(data)
    except:
        connections.remove(websocket)
