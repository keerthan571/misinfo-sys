import { useState } from "react";
import apiClient from "../api/apiClient";

export default function OCR() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [text, setText] = useState("");

  const handleFileChange = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Please select an image.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setLoading(true);

      const response = await apiClient.post(
        "/api/ocr/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setText(response.data.text || response.data.extracted_text || JSON.stringify(response.data));
    } catch (err) {
      console.error(err);
      alert("OCR Failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">

      <h1 className="text-3xl font-bold text-white">
        OCR Analysis
      </h1>

      <div className="bg-slate-800 rounded-xl p-6">

        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="mb-5"
        />

        {preview && (
          <img
            src={preview}
            alt="Preview"
            className="rounded-lg w-80 mb-5"
          />
        )}

        <button
          onClick={handleUpload}
          className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg"
        >
          {loading ? "Extracting..." : "Extract Text"}
        </button>

      </div>

      {text && (
        <div className="bg-slate-800 rounded-xl p-6">
          <h2 className="text-xl font-bold mb-3">
            Extracted Text
          </h2>

          <p className="whitespace-pre-wrap">
            {text}
          </p>
        </div>
      )}

    </div>
  );
}