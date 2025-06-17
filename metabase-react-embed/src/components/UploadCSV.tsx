import React, { useState, useRef } from "react";
import axios from "axios";

const UploadCSV = () => {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState("");
  const [progress, setProgress] = useState(0);
  const dropRef = useRef<HTMLDivElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
    setStatus("");
    setProgress(0);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setFile(e.dataTransfer.files[0]);
    setStatus("");
    setProgress(0);
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus("📁 Please choose a CSV file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:8000/upload-csv", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || 1)
          );
          setProgress(percent);
        },
      });

      setProgress(100);
      setStatus(`✅ ${response.data.message}`);

      // Optional: auto-reset after delay
      // setTimeout(() => {
      //   setFile(null);
      //   setProgress(0);
      //   setStatus("");
      // }, 3000);
    } catch (error: any) {
      setStatus(`❌ Upload failed: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h2>📤 Upload CSV to OBD-II Backend</h2>

      <div
        ref={dropRef}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        style={{
          border: "2px dashed #888",
          padding: "2rem",
          borderRadius: "8px",
          marginTop: "1rem",
          backgroundColor: "#f9f9f9",
          textAlign: "center",
        }}
      >
        {file ? (
          <p>📎 Selected: {file.name}</p>
        ) : (
          <p>📂 Drag and drop your CSV here or click to browse</p>
        )}
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          style={{ display: "none" }}
          id="fileInput"
        />
        <label htmlFor="fileInput" style={{ cursor: "pointer", color: "#0066cc" }}>
          Browse
        </label>
      </div>

      <button
        onClick={handleUpload}
        style={{
          marginTop: "1rem",
          padding: "0.5rem 1.5rem",
          background: "#18181b",
          color: "#fff",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Upload
      </button>

      {progress > 0 && (
        <div
          style={{
            marginTop: "1rem",
            width: "100%",
            background: "#eee",
            borderRadius: "4px",
            height: "10px",
          }}
        >
          <div
            style={{
              width: `${progress}%`,
              background: progress === 100 ? "#4caf50" : "#2196f3",
              height: "100%",
              borderRadius: "4px",
              transition: "width 0.3s ease",
            }}
          />
        </div>
      )}

      <p
        style={{
          marginTop: "1rem",
          color: status.startsWith("✅") ? "green" : status ? "red" : "black",
        }}
      >
        {status}
      </p>
    </div>
  );
};

export default UploadCSV;
