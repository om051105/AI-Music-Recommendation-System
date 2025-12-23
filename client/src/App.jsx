import React, { useState, useRef, useCallback } from 'react';
import axios from 'axios';
import Webcam from 'react-webcam';
import { Camera, Mic, Send, Music, User, Bot, Play, Pause, X } from 'lucide-react';
import ThreeBackground from './components/ThreeBackground';
import { motion, AnimatePresence } from 'framer-motion';

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [messages, setMessages] = useState([{ type: 'ai', text: "I am your AI DJ. Tell me your vibe or scan your face.", songs: [] }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("All");

  // Camera State
  const [showCamera, setShowCamera] = useState(false);
  const webcamRef = useRef(null);

  const handeSend = async () => {
    if (!input.trim()) return;

    const userMsg = { type: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(`${API_URL}/recommend`, {
        query: input,
        language: language
      });

      const aiMsg = {
        type: 'ai',
        text: `Found ${res.data.tracks.length} tracks matching your vibe!`,
        songs: res.data.tracks
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { type: 'ai', text: "Error connecting to AI Brain. Is the backend running?" }]);
    }
    setLoading(false);
  };

  const capture = useCallback(async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setShowCamera(false);

    if (!imageSrc) return;

    setLoading(true);
    // Convert base64 to blob
    const res = await fetch(imageSrc);
    const blob = await res.blob();
    const file = new File([blob], "webcam.jpg", { type: "image/jpeg" });

    const formData = new FormData();
    formData.append('file', file);

    try {
      // 1. Detect Emotion
      const emRes = await axios.post(`${API_URL}/detect-emotion`, formData);
      const emotion = emRes.data.emotion;

      setMessages(prev => [...prev, { type: 'user', text: `[Scanned Face] Detected: ${emotion}` }]);

      // 2. Get Recommendations based on Emotion
      const recRes = await axios.post(`${API_URL}/recommend`, {
        query: `songs for ${emotion} mood`,
        emotion: emotion,
        language: language
      });

      setMessages(prev => [...prev, {
        type: 'ai',
        text: `I see you are feeling ${emotion}. Here is a playlist to heal you.`,
        songs: recRes.data.tracks
      }]);

    } catch (err) {
      setMessages(prev => [...prev, { type: 'ai', text: "Failed to analyze face." }]);
    }
    setLoading(false);
  }, [webcamRef, language]);


  return (
    <div className="min-h-screen text-white relative">
      <ThreeBackground />

      {/* Camera Modal */}
      <AnimatePresence>
        {showCamera && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4"
          >
            <div className="bg-zinc-900 p-4 rounded-2xl border border-green-500 w-full max-w-lg flex flex-col gap-4">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-bold text-green-400">Scan Your Vibe</h3>
                <button onClick={() => setShowCamera(false)} className="text-white hover:text-red-500"><X /></button>
              </div>

              <div className="rounded-xl overflow-hidden border border-zinc-700 bg-black">
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  className="w-full"
                  videoConstraints={{ facingMode: "user" }}
                />
              </div>

              <button
                onClick={capture}
                className="w-full bg-green-500 hover:bg-green-600 text-black font-bold p-4 rounded-xl"
              >
                📸 CAPTURE
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="container mx-auto p-4 flex h-screen gap-6">

        {/* Sidebar */}
        <div className="w-1/4 glass-panel p-6 flex flex-col gap-6 hidden md:flex">
          <h1 className="text-4xl font-bold neon-text">ULTRA DJ</h1>

          <div className="space-y-4">
            <h3 className="text-xl font-bold">Filters</h3>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-black border border-green-500 p-2 rounded text-white"
            >
              <option value="All">All Languages</option>
              <option value="Hindi">Hindi</option>
              <option value="Punjabi">Punjabi</option>
              <option value="English">English</option>
              <option value="Korean">K-Pop</option>
            </select>
          </div>

          <div className="mt-auto">
            <button
              onClick={() => setShowCamera(true)}
              className="w-full bg-green-500 hover:bg-green-600 text-black font-bold p-4 rounded-xl flex items-center justify-center gap-2 transition-all"
            >
              <Camera size={24} /> SCAN VIBE
            </button>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 glass-panel flex flex-col overflow-hidden relative">
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            <AnimatePresence>
              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex flex-col ${msg.type === 'user' ? 'items-end' : 'items-start'}`}
                >
                  <div className={`p-4 rounded-2xl max-w-[80%] ${msg.type === 'user'
                      ? 'bg-green-600 text-black font-medium'
                      : 'bg-zinc-800 border border-zinc-700'
                    }`}>
                    {msg.text}
                  </div>

                  {/* Song Cards */}
                  {msg.songs && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 w-full">
                      {msg.songs.map((song, idx) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: idx * 0.05 }}
                          className="card bg-black/60 p-4 rounded-xl border border-zinc-700 flex items-center gap-4 cursor-pointer group"
                          onClick={() => window.open(`https://open.spotify.com/search/${song.name} ${song.artist}`, '_blank')}
                        >
                          <img src={song.cover} alt="art" className="w-16 h-16 rounded object-cover" />
                          <div className="flex-1 min-w-0">
                            <h4 className="font-bold truncate text-green-400 group-hover:text-white transition-colors">
                              {song.name}
                            </h4>
                            <p className="text-sm text-gray-400 truncate">{song.artist}</p>
                          </div>
                          <Play size={20} className="text-green-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </motion.div>
                      ))}
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
            {loading && <div className="text-green-500 animate-pulse">Thinking...</div>}
            <div ref={(el) => el?.scrollIntoView({ behavior: 'smooth' })} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-zinc-800 bg-black/50">
            <div className="flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handeSend()}
                placeholder="Type your mood..."
                className="flex-1 bg-zinc-900 border border-zinc-700 rounded-xl p-4 text-white placeholder-zinc-500 focus:border-green-500 transition-all"
              />
              <button
                onClick={handeSend}
                className="bg-green-500 text-black p-4 rounded-xl hover:bg-green-400 transition-colors"
              >
                <Send size={24} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
