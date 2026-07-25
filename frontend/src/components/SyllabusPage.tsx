import React, { useState, useEffect, ChangeEvent } from 'react';
import { Book, Upload, Trash2, Loader2, AlertCircle, FileText, CheckCircle, X, Plus } from 'lucide-react';

// Interface to match the backend's SyllabusResponse
interface Syllabus {
  id: number;
  name: string;
  created_at: string;
  topic_count: number;
}

interface SyllabusPageProps {
  API_BASE_URL: string;
  onBack: () => void;
  onSyllabusUploaded: () => void; // Function to tell Dashboard to reload
}

export const SyllabusPage: React.FC<SyllabusPageProps> = ({ API_BASE_URL, onBack, onSyllabusUploaded }) => {
  const [syllabuses, setSyllabuses] = useState<Syllabus[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // State for the upload form
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [syllabusName, setSyllabusName] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const fetchSyllabuses = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/syllabus`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch syllabuses.');
      }
      const data: Syllabus[] = await response.json();
      setSyllabuses(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSyllabuses();
  }, []);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setUploadFile(e.target.files[0]);
      // Auto-fill name input if it's empty
      if (!syllabusName) {
        setSyllabusName(e.target.files[0].name.replace(/\.(xlsx|xls)$/i, ''));
      }
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !syllabusName) {
      setUploadError("Please provide a name and select a file.");
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append('name', syllabusName);
    formData.append('file', uploadFile);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/syllabus/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      const result = await response.json();

      if (!response.ok) {
        // This will show format validation errors from the backend
        throw new Error(result.detail || 'Failed to upload syllabus.');
      }

      // Success!
      setSyllabusName("");
      setUploadFile(null);
      (document.getElementById('file-upload') as HTMLInputElement).value = ""; // Reset file input
      onSyllabusUploaded(); // Tell Dashboard to refresh its list
      fetchSyllabuses(); // Refresh this page's list
      
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (syllabusId: number) => {
    if (!window.confirm("Are you sure you want to delete this syllabus?")) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/syllabus/${syllabusId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.detail || 'Failed to delete syllabus.');
      }

      // Remove from UI
      setSyllabuses(prev => prev.filter(s => s.id !== syllabusId));
      onSyllabusUploaded(); // Tell Dashboard to refresh its list

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Book className="w-6 h-6 text-purple-500" />
          <h2 className="text-xl font-bold text-gray-800">Syllabus Management</h2>
        </div>
        <button
          onClick={onBack}
          className="text-sm font-medium text-cyan-600 hover:text-cyan-800"
        >
          &larr; Back to Dashboard
        </button>
      </div>

      {/* --- Upload Form --- */}
      <form onSubmit={handleUpload} className="p-4 border-2 border-dashed border-gray-200 rounded-lg mb-6 space-y-4">
        <h3 className="font-semibold text-lg text-gray-800">Add New Syllabus</h3>
        <div>
          <label htmlFor="syllabusName" className="block text-sm font-medium text-gray-700 mb-1">
            Syllabus Name
          </label>
          <input
            type="text"
            id="syllabusName"
            value={syllabusName}
            onChange={(e) => setSyllabusName(e.target.value)}
            placeholder="e.g., UGC-NET Paper 1"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            required
          />
        </div>
        <div>
          <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700 mb-1">
            Syllabus File (.xlsx, .xls)
          </label>
          <input
            id="file-upload"
            type="file"
            onChange={handleFileChange}
            accept=".xlsx, .xls"
            className="file-input"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Format: All topics must be in the first column, one per row.
          </p>
        </div>
        <button
          type="submit"
          disabled={isUploading}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-cyan-600 text-white rounded-lg font-semibold"
        >
          {isUploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Upload className="w-5 h-5" />}
          {isUploading ? 'Uploading...' : 'Upload Syllabus'}
        </button>
        {uploadError && (
          <div className="flex items-center gap-2 text-sm text-red-600">
            <AlertCircle className="w-4 h-4" /> {uploadError}
          </div>
        )}
      </form>

      {/* --- Syllabus List --- */}
      <h3 className="font-semibold text-lg text-gray-800 mb-4">Your Syllabuses</h3>
      {isLoading && (
        <div className="text-center py-8"><Loader2 className="w-6 h-6 text-gray-400 animate-spin mx-auto" /><p className="mt-2 text-gray-500">Loading...</p></div>
      )}
      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 text-red-700 border border-red-200 rounded-lg">
          <AlertCircle className="w-4 h-4" /> {error}
        </div>
      )}
      {!isLoading && !error && (
        <div className="space-y-3">
          {syllabuses.length === 0 && (
            <p className="text-gray-500 text-center py-4">You haven't uploaded any syllabuses yet.</p>
          )}
          {syllabuses.map(syllabus => (
            <div key={syllabus.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-gray-500" />
                <div>
                  <h4 className="font-medium text-gray-800">{syllabus.name}</h4>
                  <p className="text-sm text-gray-600">
                    {syllabus.topic_count} topics • Uploaded {new Date(syllabus.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleDelete(syllabus.id)}
                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full"
                title="Delete syllabus"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};