"""FastAPI backend — IR data management + PPT export."""

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from schema import IRDocument, SLIDE_NAMES

app = FastAPI(title="Rovothome IR Manager")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "ir_data.json"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def _load() -> IRDocument:
    if DATA_FILE.exists():
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return IRDocument(**raw)
    return IRDocument()


def _save(doc: IRDocument):
    DATA_DIR.mkdir(exist_ok=True)
    DATA_FILE.write_text(doc.model_dump_json(indent=2), encoding="utf-8")


# --- API endpoints ---

@app.get("/api/slides")
def get_all():
    """Get full IR document data."""
    doc = _load()
    return {
        "data": doc.model_dump(),
        "slide_names": SLIDE_NAMES,
    }


@app.put("/api/slides")
def save_all(doc: IRDocument):
    """Save full IR document."""
    _save(doc)
    return {"ok": True}


@app.patch("/api/slides/{slide_id}")
def update_slide(slide_id: str, body: dict):
    """Update a single slide's data."""
    doc = _load()
    if not hasattr(doc, slide_id):
        return {"error": f"Unknown slide: {slide_id}"}

    current = getattr(doc, slide_id)
    updated = current.model_copy(update=body)
    setattr(doc, slide_id, updated)
    _save(doc)
    return {"ok": True, "slide_id": slide_id}


@app.put("/api/config")
def update_config(config: list[dict]):
    """Update slide order and visibility."""
    from schema import SlideConfig
    doc = _load()
    doc.slide_config = [SlideConfig(**c) for c in config]
    _save(doc)
    return {"ok": True}


@app.post("/api/export")
def export_pptx():
    """Generate and return PPT file."""
    doc = _load()
    from pptx_engine import generate_pptx
    output_path = OUTPUT_DIR / "rovothome_ir.pptx"
    generate_pptx(doc, output_path)
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename="Rovothome_IR.pptx",
    )


@app.get("/api/export/download")
def download_pptx():
    """Download last generated PPT."""
    output_path = OUTPUT_DIR / "rovothome_ir.pptx"
    if not output_path.exists():
        doc = _load()
        from pptx_engine import generate_pptx
        generate_pptx(doc, output_path)
    return FileResponse(output_path, filename="Rovothome_IR.pptx")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
