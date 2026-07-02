import { useState } from "react";
import { useAuth } from "../context/AuthContextCore";

export default function Upload() {
  const { token } = useAuth();
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState(null);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleUpload = async () => {
    if (!files.length) {
      setStatus({ type: "error", message: "Select at least one file." });
      return;
    }
    const formData = new FormData();
    files.forEach((f) => formData.append("files", f));
    try {
      const res = await fetch("/api/rag/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });
      if (!res.ok) throw new Error("Upload failed");
      const data = await res.json();
      setStatus({ type: "success", message: `Uploaded ${data.document_ids.length} document(s).` });
      setFiles([]);
    } catch (err) {
      setStatus({ type: "error", message: err.message });
    }
  };

  return (
    <div className="min-h-screen bg-[#080810] flex flex-col items-center justify-center p-6 text-neutral-200">
      <h2 className="text-2xl font-semibold mb-4">Upload Documents for RAG</h2>
      <input
        type="file"
        multiple
        onChange={handleFileChange}
        className="mb-4 text-neutral-200 file:bg-violet-600 file:text-white file:border-0 file:rounded-md"
      />
      <button
        onClick={handleUpload}
        className="px-6 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-md transition"
      >
        Upload
      </button>
      {status && (
        <p className={`mt-4 ${status.type === "error" ? "text-red-400" : "text-green-400"}`}>
          {status.message}
        </p>
      )}
    </div>
  );
}
