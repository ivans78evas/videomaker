'use client';

import React, { useState } from 'react';

interface Segment {
  id: string;
  start: number;
  end: number;
  text: string;
  translated_text: string;
  qa_score: number;
  status: 'ok' | 'warning' | 'error';
}

const mockSegments: Segment[] = [
  { id: '1', start: 0, end: 5.5, text: "Welcome to the future of translation.", translated_text: "Willkommen в будущее перевода.", qa_score: 9.5, status: 'ok' },
  { id: '2', start: 5.5, end: 12.0, text: "Today we will see how AI changes everything.", translated_text: "Сегодня мы увидим как ИИ меняет всё.", qa_score: 8.2, status: 'ok' },
  { id: '3', start: 12.0, end: 18.0, text: "This is a hallucination example.", translated_text: "Это пример галлюцинации и лишних фактов.", qa_score: 4.5, status: 'error' },
];

export default function HTILEditor() {
  const [segments, setSegments] = useState<Segment[]>(mockSegments);

  return (
    <div className="flex h-screen bg-gray-900 text-white overflow-hidden">
      {/* Sidebar: Navigation */}
      <aside className="w-16 border-r border-gray-800 flex flex-col items-center py-4 space-y-8">
        <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center font-bold">TT</div>
        <div className="text-gray-500 hover:text-white cursor-pointer">📁</div>
        <div className="text-gray-500 hover:text-white cursor-pointer">⚙️</div>
      </aside>

      {/* Main Workspace */}
      <main className="flex-1 flex flex-col">
        {/* Top Header */}
        <header className="h-16 border-b border-gray-800 flex items-center justify-between px-6 bg-gray-900">
          <div className="flex items-center space-y-0.5">
            <h2 className="text-lg font-semibold">HITL Studio: Project_Alpha_123</h2>
            <span className="ml-4 text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded border border-green-500/30">Vocal Isolated</span>
          </div>
          <div className="flex space-x-4">
            <button className="px-4 py-2 text-sm bg-gray-800 rounded-md hover:bg-gray-700 transition">Discard</button>
            <button className="px-4 py-2 text-sm bg-indigo-600 rounded-md hover:bg-indigo-500 transition font-medium">Final Render</button>
          </div>
        </header>

        <div className="flex-1 flex overflow-hidden">
          {/* Left Panel: Video Player */}
          <section className="w-1/2 p-6 flex flex-col space-y-6">
            <div className="aspect-video bg-black rounded-xl border border-gray-800 flex items-center justify-center relative overflow-hidden shadow-2xl">
              <span className="text-gray-600 italic">Video Player Preview</span>
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-700">
                <div className="h-full bg-red-600 w-1/3 relative">
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-red-600 rounded-full shadow-lg border-2 border-white"></div>
                </div>
              </div>
            </div>

            <div className="flex-1 bg-gray-800/30 rounded-xl p-4 border border-gray-800 overflow-y-auto">
              <h3 className="text-sm font-medium text-gray-400 mb-4 uppercase tracking-wider">Linguistic Intelligence Report (Groq)</h3>
              <div className="space-y-3">
                <div className="p-3 bg-green-500/5 border border-green-500/20 rounded-lg text-sm">
                  <span className="text-green-400 font-bold block mb-1">Pass: High Consistency</span>
                  Translation matches the source sentiment and emotional intensity for 85% of segments.
                </div>
                <div className="p-3 bg-yellow-500/5 border border-yellow-500/20 rounded-lg text-sm text-yellow-300">
                  <span className="font-bold block mb-1">Alert: Segment #3</span>
                  Hallucination detected. Fact-check on "numbers" required.
                </div>
              </div>
            </div>
          </section>

          {/* Right Panel: Transcription Editor */}
          <section className="w-1/2 border-l border-gray-800 flex flex-col bg-gray-900">
            <div className="p-4 border-b border-gray-800 flex justify-between items-center bg-gray-900/50">
              <span className="text-sm text-gray-400 uppercase tracking-widest font-bold">Transcription Segments</span>
              <div className="flex space-x-2">
                 <span className="text-xs bg-gray-800 px-2 py-1 rounded">DE -> EN</span>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {segments.map((seg, idx) => (
                <div key={seg.id} className={`p-4 rounded-xl border transition-all ${seg.status === 'error' ? 'border-red-500/50 bg-red-500/5 shadow-lg shadow-red-500/10' : 'border-gray-800 bg-gray-800/20 hover:border-gray-700'}`}>
                   <div className="flex justify-between items-start mb-2">
                      <span className="text-xs font-mono text-gray-500">{seg.start.toFixed(1)}s - {seg.end.toFixed(1)}s</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${seg.qa_score > 8 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                        QA: {seg.qa_score}
                      </span>
                   </div>
                   <div className="space-y-3">
                      <div>
                        <label className="text-[10px] text-gray-500 uppercase font-bold block mb-1">Source</label>
                        <p className="text-sm text-gray-300 italic">{seg.text}</p>
                      </div>
                      <div>
                        <label className="text-[10px] text-indigo-400 uppercase font-bold block mb-1">Translation</label>
                        <textarea
                          value={seg.translated_text}
                          onChange={(e) => {
                            const newSegs = [...segments];
                            newSegs[idx].translated_text = e.target.value;
                            setSegments(newSegs);
                          }}
                          className="w-full bg-black/40 border border-gray-700 rounded-md p-2 text-sm focus:border-indigo-500 focus:outline-none transition min-h-[60px]"
                        />
                      </div>
                   </div>
                   <div className="mt-3 flex justify-end space-x-2">
                      <button className="text-[10px] text-gray-500 hover:text-white uppercase font-bold px-2 py-1 border border-gray-800 rounded hover:bg-gray-800 transition">Regenerate Audio</button>
                   </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
