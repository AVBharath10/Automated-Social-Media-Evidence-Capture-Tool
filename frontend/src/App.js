import React, { useState } from "react";
import "./App.css";

function App() {
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
        body: JSON.stringify({ username, password }),
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
      <h1>Instagram Report Generator</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Instagram Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Instagram Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Generate Report</button>
      </form>
      <p>{status}</p>
      {pdfUrl && (
        <a href={pdfUrl} target="_blank" rel="noopener noreferrer" download>
          <button>⬇ Download PDF Report</button>
        </a>
      )}
    </div>
  );
}

export default App;
