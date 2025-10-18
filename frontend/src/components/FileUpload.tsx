'use client';

import { useRef, useState } from 'react';
import { Upload, FileCheck } from 'lucide-react';

interface FileUploadProps {
  onFileUpload: (file: File) => Promise<void>;
}

export default function FileUpload({ onFileUpload }: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setSuccess(false);

    try {
      await onFileUpload(file);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 2000);
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.txt,.docx,.csv,.xlsx"
        onChange={handleFileChange}
        className="hidden"
      />
      <button
        onClick={handleClick}
        disabled={uploading}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
          success
            ? 'bg-green-500 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        } disabled:opacity-50 disabled:cursor-not-allowed`}
      >
        {success ? (
          <>
            <FileCheck className="w-4 h-4" />
            <span>Uploaded!</span>
          </>
        ) : (
          <>
            <Upload className="w-4 h-4" />
            <span>{uploading ? 'Uploading...' : 'Upload Doc'}</span>
          </>
        )}
      </button>
    </>
  );
}