import React, { useState } from "react";
import "./App.css";

function App() {
  const [platform, setPlatform] = useState("instagram");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState("");
  const [pdfUrl, setPdfUrl] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("Generating report...");
    setPdfUrl("");

    try {
      const response = await fetch("http://localhost:5000/generate-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, platform }),
      });

      const data = await response.json();

      if (response.ok) {
        setPdfUrl(data.pdf_url);
        setStatus("✅ Report generated! You can download it below.");
      } else {
        setStatus(`❌ Error: ${data.error}`);
      }
    } catch (error) {
      setStatus("❌ Something went wrong. Please try again.");
    }
  };

  return (
    <div className="App">
      <h1>📊 Social Media Report</h1>
      <form onSubmit={handleSubmit} className="form-container">
        <label>
          Platform:
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            required
          >
            <option value="instagram">Instagram</option>
            <option value="twitter">Twitter</option>
          </select>
        </label>

        <input
          type="text"
          placeholder={`${platform.charAt(0).toUpperCase() + platform.slice(1)} Username`}
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder={`${platform.charAt(0).toUpperCase() + platform.slice(1)} Password`}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Generate Report</button>
      </form>

      <p className="status-message">{status}</p>

      {pdfUrl && (
        <a href={pdfUrl} target="_blank" rel="noopener noreferrer" download>
          <button className="download-btn">⬇ Download PDF</button>
        </a>
      )}
    </div>
  );
}

export default App;
