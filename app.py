import subprocess
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from birdnetlib import RecordingBuffer
from birdnetlib.analyzer import Analyzer

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
analyzer = Analyzer()
MAX_BYTES = 8_000_000

@app.get("/")
def health():
    return {"ok": True}

@app.post("/identify")
async def identify(file: UploadFile = File(...), lat: float = Form(None), lon: float = Form(None), min_conf: float = Form(0.25)):
    data = await file.read()
    if len(data) > MAX_BYTES:
        return {"error": "too large", "detections": []}
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-t", "30", "-ar", "48000", "-ac", "1", "-f", "s16le", "pipe:1"],
                       input=data, capture_output=True)
    if p.returncode != 0 or not p.stdout:
        return {"error": "could not decode audio", "detections": []}
    buf = np.frombuffer(p.stdout, dtype="int16").astype("float32") / 32768.0
    kw = {"lat": lat, "lon": lon} if lat is not None and lon is not None else {}
    rec = RecordingBuffer(analyzer, buf, 48000, min_conf=min_conf, **kw)
    rec.analyze()
    best = {}
    for d in rec.detections:
        k = d["scientific_name"]
        if k not in best or d["confidence"] > best[k]["confidence"]:
            best[k] = {"common_name": d["common_name"], "scientific_name": k, "confidence": round(d["confidence"], 3)}
    return {"detections": sorted(best.values(), key=lambda d: -d["confidence"])}
