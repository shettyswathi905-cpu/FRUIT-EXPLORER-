import React, { useState, useCallback } from 'react';
import { UploadCloud, X, CheckCircle, Palette, Smile, Search } from 'lucide-react';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file) => {
    if (!file.type.startsWith('image/')) {
      setError("Oops! Please select an image file.");
      return;
    }

    setError(null);
    setSelectedFile(file);
    setResult(null);

    const reader = new FileReader();
    reader.onload = () => setPreviewUrl(reader.result);
    reader.readAsDataURL(file);
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
  };

  const classifyImage = async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:8000/classify', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();

      if (data.valid_fruit === false) {
        setError(data.error_message);
        setResult(null);
      } else {
        setResult(data);
      }

      setIsLoading(false);

    } catch (err) {
      setError(`Failed to connect to AI server. Make sure it is running!`);
      setIsLoading(false);
    }
  };

  return (
    <div className="dashboard-container">
      <header className="header">
        <h1>Fruit Explorer</h1>
        <p>Upload a fruit picture and let the AI tell you what it is!</p>
      </header>

      <main className="main-content">
        {/* Upload Area */}
        <section className="upload-section">
          {previewUrl ? (
            <div className="image-preview-container">
              <img src={previewUrl} alt="Preview" className="image-preview" />
              <button className="remove-btn" onClick={clearSelection} title="Remove image">
                <X size={24} />
              </button>
            </div>
          ) : (
            <div
              className={`drop-zone ${isDragging ? 'active' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                id="file-input"
              />
              <div className="drop-message">
                <UploadCloud size={80} className="icon" />
                <p>Drag your picture here!</p>
                <span>or click to browse your folders</span>
              </div>
            </div>
          )}

          {error && <div style={{ color: '#ef4444', background: '#fee2e2', padding: '16px', borderRadius: '12px', fontWeight: 'bold' }}>{error}</div>}

          <button
            className="classify-btn"
            onClick={classifyImage}
            disabled={!selectedFile || isLoading}
          >
            {isLoading ? (
              <><span className="loader"></span> Thinking...</>
            ) : (
              <><Search size={24} /> Name this Fruit!</>
            )}
          </button>
        </section>

        {/* Result Area */}
        <section className="result-section">
          {!result ? (
            <div className="placeholder-result">
              <Smile size={80} style={{ color: '#cbd5e1' }} />
              <h3>Waiting for a picture...</h3>
            </div>
          ) : (
            <div className="result-card">
              <h2 className="fruit-title" style={{ color: result.features.color_hex }}>
                {result.fruit_name}
              </h2>

              <div className="confidence-badge">
                <CheckCircle size={20} />
                AI is {result.confidence}% sure!
              </div>

              <div style={{ width: '100%', marginTop: '10px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
                <div className="student-card" style={{ borderLeftColor: result.features.color_hex }}>
                  <div className="student-card-icon">
                    <Palette size={32} style={{ color: result.features.color_hex }} />
                  </div>
                  <div className="student-card-content">
                    <h4>Color</h4>
                    <p>{result.features.color}</p>
                  </div>
                </div>

                <div className="student-card" style={{ borderLeftColor: '#f59e0b' }}>
                  <div className="student-card-icon">
                    <Smile size={32} style={{ color: '#f59e0b' }} />
                  </div>
                  <div className="student-card-content">
                    <h4>Taste</h4>
                    <p>{result.features.taste}</p>
                  </div>
                </div>
              </div>

            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
