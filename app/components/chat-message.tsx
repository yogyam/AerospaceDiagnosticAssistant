"use client"

import React, { useState } from 'react';

const ChatMessage = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError('');
    setAnswer('');
    setSources([]);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        setAnswer(data.answer);
        setSources(data.sources || []);
      }
    } catch (err) {
      setError('Failed to get answer.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded mt-4">
      <h2 className="font-bold mb-2">Ask a Question</h2>
      <input
        type="text"
        className="border px-2 py-1 w-2/3"
        value={question}
        onChange={e => setQuestion(e.target.value)}
        placeholder="Type your question..."
        onKeyDown={e => { if (e.key === 'Enter') handleAsk(); }}
      />
      <button
        className="ml-2 px-4 py-1 bg-green-600 text-white rounded"
        onClick={handleAsk}
        disabled={loading}
      >
        {loading ? 'Asking...' : 'Ask'}
      </button>
      {error && <div className="mt-2 text-red-600 text-sm">{error}</div>}
      {answer && (
        <div className="mt-4">
          <div className="font-semibold">Answer:</div>
          <div className="bg-gray-100 p-2 rounded mb-2">{answer}</div>
          {sources.length > 0 && (
            <div>
              <div className="font-semibold">Sources:</div>
              <ul className="list-disc ml-6">
                {sources.map((src, idx) => (
                  <li key={idx} className="text-xs break-all">{JSON.stringify(src)}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
