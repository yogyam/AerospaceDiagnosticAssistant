"use client"

import React, { useState } from 'react';

const DocumentUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus('Please select a file.');
      return;
    }
    setStatus('Uploading...');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.error) {
        setStatus(`Error: ${data.error}`);
      } else {
        setStatus('Upload successful!');
      }
    } catch (err) {
      setStatus('Upload failed.');
    }
  };

  return (
    <div className="p-4 border rounded">
      <h2 className="font-bold mb-2">Upload Document</h2>
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      <button className="ml-2 px-4 py-1 bg-blue-600 text-white rounded" onClick={handleUpload}>
        Upload
      </button>
      {status && <div className="mt-2 text-sm">{status}</div>}
    </div>
  );
};

export default DocumentUpload;
