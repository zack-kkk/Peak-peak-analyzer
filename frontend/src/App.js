import React, { useState, useEffect } from "react";
import axios from "axios";

export default function App() {
  const [file, setFile] = useState(null);
  const [patents, setPatents] = useState({});
  const [selectedPatent, setSelectedPatent] = useState("PATENT_FORM_A");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get("http://localhost:8000/api/patents").then((res) => {
      setPatents(res.data.patents);
    });
  }, []);

  const handleUpload = async () => {
    if (!file) return alert("Please select a .xy or .csv PXRD file first.");
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("reference_patent_id", selectedPatent);

    try {
      const res = await axios.post("http://localhost:8000/api/analyze", formData);
      setResults(res.data);
      renderPlot(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Error analyzing PXRD file.");
    } finally {
      setLoading(false);
    }
  };

  const renderPlot = (data) => {
    const rawTrace = {
      x: data.raw_data.two_theta,
      y: data.raw_data.intensities,
      mode: "lines",
      name: "Experimental Scan",
      line: { color: "#2563eb", width: 1.5 },
    };

    // Plot vertical red dashed lines for unique/novel peaks
    const shapes = data.results.unique_new_peaks.map((peak) => ({
      type: "line",
      x0: peak,
      x1: peak,
      y0: 0,
      y1: Math.max(...data.raw_data.intensities),
      line: { color: "#dc2626", width: 2, dash: "dash" },
    }));

    const layout = {
      title: `PXRD Spectrum - Highlighted Novel Peaks (Red)`,
      xaxis: { title: "2-Theta Angle (°)" },
      yaxis: { title: "Intensity (Counts)" },
      shapes: shapes,
    };

    window.Plotly.newPlot("plot-container", [rawTrace], layout);
  };

  return (
    <div style={{ fontFamily: "Arial, sans-serif", padding: "20px", maxWidth: "1000px", margin: "auto" }}>
      <h2>PolyMatch: PXRD Peak Analysis Dashboard</h2>
      
      <div style={{ display: "flex", gap: "15px", marginBottom: "20px", background: "#f3f4f6", padding: "15px", borderRadius: "8px" }}>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        
        <select value={selectedPatent} onChange={(e) => setSelectedPatent(e.target.value)}>
          {Object.keys(patents).map((pat) => (
            <option key={pat} value={pat}>{pat}</option>
          ))}
        </select>

        <button onClick={handleUpload} disabled={loading} style={{ background: "#2563eb", color: "white", padding: "8px 16px", border: "none", borderRadius: "4px", cursor: "pointer" }}>
          {loading ? "Analyzing..." : "Run Analysis"}
        </button>
      </div>

      <div id="plot-container" style={{ width: "100%", height: "400px" }}></div>

      {results && (
        <div style={{ marginTop: "20px", background: "#f8fafc", padding: "15px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <h3>Match Analysis Summary</h3>
          <p><strong>Match Confidence:</strong> {results.results.match_score_percentage}%</p>
          <p><strong>Novel Form Indication:</strong> {results.results.is_potentially_novel ? "⚠️ Unique Peaks Detected (Potential New Polymorph)" : "✅ Pure Matches Patented Form"}</p>
          <p><strong>Unique New 2-Theta Peaks:</strong> {results.results.unique_new_peaks.join(", ") || "None"}</p>
          <p><strong>Missing Reference Peaks:</strong> {results.results.missing_ref_peaks.join(", ") || "None"}</p>
        </div>
      )}
    </div>
  );
}
