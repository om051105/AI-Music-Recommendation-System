import React, { useState, useRef, useCallback, useEffect } from 'react';
import axios from 'axios';
import Webcam from 'react-webcam';
import { Camera, Mic, Send, Music, User, Bot, Play, Pause, X } from 'lucide-react';
import ThreeBackground from './components/ThreeBackground';
import { motion, AnimatePresence } from 'framer-motion';

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8001";

function App() {
  const [messages, setMessages] = useState([{ type: 'ai', text: "I am your AI DJ. Tell me your vibe or scan your face.", songs: [] }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("All");

  // Camera State
  const [showCamera, setShowCamera] = useState(false);
  const webcamRef = useRef(null);

  // Smart Scroll: Scroll to the top of the new message
  useEffect(() => {
    setTimeout(() => {
      const lastMsg = document.getElementById("last-message");
      if (lastMsg) {
        lastMsg.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }, 100); // Small delay to ensure DOM paint
  }, [messages, loading]);

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
                  id={i === messages.length - 1 ? "last-message" : ""}
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
                          className="card bg-black/60 p-4 rounded-xl border border-zinc-700 flex items-center gap-4 group"
                        >
                          <img src={song.cover} alt="art" className="w-16 h-16 rounded object-cover" />
                          <div className="flex-1 min-w-0">
                            <h4 className="font-bold truncate text-green-400 group-hover:text-white transition-colors">
                              {song.name}
                            </h4>
                            <p className="text-sm text-gray-400 truncate">{song.artist}</p>
                          </div>
                          <div className="flex gap-2">
                            {/* Spotify Official Logo */}
                            <button
                              onClick={() => window.open(song.links.spotify, '_blank')}
                              className="p-2 transition hover:scale-110"
                              title="Open in Spotify"
                            >
                              <svg viewBox="0 0 24 24" width="24" height="24" fill="#1DB954">
                                <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z" />
                              </svg>
                            </button>

                            {/* YouTube Official Logo */}
                            <button
                              onClick={() => window.open(song.links.youtube, '_blank')}
                              className="p-2 transition hover:scale-110"
                              title="Open in YouTube"
                            >
                              <svg viewBox="0 0 24 24" width="24" height="24" fill="#FF0000">
                                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                              </svg>
                            </button>

                            {/* Apple Music Official Logo */}
                            <button
                              onClick={() => window.open(song.links.apple, '_blank')}
                              className="p-2 transition hover:scale-110"
                              title="Open in Apple Music"
                            >
                              <svg viewBox="0 0 24 24" width="24" height="24" fill="#FA243C">
                                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm3.899 15.928c-.563.856-1.536 1.488-2.671 1.488-2.348 0-4.25-2.584-4.25-5.772 0-3.187 1.902-5.772 4.25-5.772 1.127 0 2.096.623 2.658 1.468v-1.171c-.704-1.258-2.028-2.113-3.559-2.113-2.261 0-4.093 1.832-4.093 4.093s1.832 4.093 4.093 4.093c1.516 0 2.83-.836 3.539-2.073v1.171l.033.618z" />
                                <path d="M14.659 8.3c-.567-.84-1.529-1.455-2.656-1.455-2.317 0-4.195 2.559-4.195 5.715 0 3.156 1.878 5.715 4.195 5.715 1.135 0 2.103-.624 2.668-1.475V8.3z" fill="#fff" />
                              </svg>
                            </button>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
            {loading && <div className="text-green-500 animate-pulse">Thinking...</div>}
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
