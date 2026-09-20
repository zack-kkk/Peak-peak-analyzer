"""
FastAPI Server for PolyMatch PXRD Analysis Engine
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from pxrd_engine import PXRDAnalyzer

app = FastAPI(title="PolyMatch PXRD Engine API")

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = PXRDAnalyzer(tolerance=0.1, prominence=5.0)

# Mock Patented Reference Database
PATENT_DATABASE = {
    "PATENT_FORM_A": [8.20, 12.40, 15.10, 18.60, 22.30, 26.10],
    "PATENT_FORM_B": [9.10, 13.50, 16.80, 20.20, 24.50, 28.00]
}


@app.get("/api/patents")
def get_patents():
    """Returns available reference patented peak lists."""
    return {"patents": PATENT_DATABASE}


@app.post("/api/analyze")
async def analyze_pxrd(
    file: UploadFile = File(...),
    reference_patent_id: str = Form("PATENT_FORM_A")
):
    """Processes uploaded PXRD data file and compares peak positions against reference."""
    if reference_patent_id not in PATENT_DATABASE:
        raise HTTPException(status_code=400, detail="Invalid patent reference ID")

    contents = await file.read()
    two_theta, intensities = analyzer.parse_xy_file(contents)

    if len(two_theta) == 0:
        raise HTTPException(status_code=400, detail="Could not parse valid 2-theta/Intensity data from file.")

    exp_peaks = analyzer.extract_peaks(two_theta, intensities)
    ref_peaks = PATENT_DATABASE[reference_patent_id]

    analysis = analyzer.match_positions(exp_peaks, ref_peaks)

    return {
        "filename": file.filename,
        "raw_data": {
            "two_theta": two_theta.tolist(),
            "intensities": intensities.tolist()
        },
        "extracted_experimental_peaks": exp_peaks,
        "reference_patent_peaks": ref_peaks,
        "results": analysis
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
