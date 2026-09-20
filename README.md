# PolyMatch: PXRD Peak Analysis & Polymorph Fingerprinting Web App

PolyMatch is a high-performance, full-stack software development engineering (SDE) solution designed to automate Powder X-ray Diffraction (PXRD) spectrum comparison. It replaces manual laboratory inspection by extracting $2\theta$ peak positions using signal processing, performing $O(\log N)$ binary search tolerance matching against patented reference profiles, and visually flagging novel crystalline polymorphs via an interactive React dashboard.

---

## 🛠 Tech Stack

* **Backend:** Python 3.10+, FastAPI, SciPy, NumPy, Uvicorn
* **Frontend:** React 18, Plotly.js, Axios
* **Algorithms:** Signal Processing (Local Maxima Detection), Binary Search Range Matching ($O(\log N)$)

---

## 🏗 Architecture & Workflow

```text
[ Experimental .csv / .xy File ]
               │
               ▼
┌──────────────────────────────┐
│  FastAPI Endpoint            │  Upload handler & multi-part parser
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  SciPy Signal Engine         │  Normalizes intensity & extracts local 2θ maxima
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Binary Search Matcher       │  Classifies peaks (±Δθ = 0.1°) into Matched,
│  O(Log N) Range Lookup       │  Unique/Novel, and Missing
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  React + Plotly.js Dashboard │  Renders 2θ spectrum and draws red visual 
└──────────────────────────────┘  markers over novel peak positions
