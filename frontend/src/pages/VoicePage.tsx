// [DEV1] VoicePage.tsx — Help tab with voice/text chat. Dev2: do not modify.
import { FormEvent, useEffect, useRef, useState } from "react";
import { processVoice, processVoiceAudio } from "../lib/api";

type ChatItem = { role: "user" | "agent"; text: string; audioUrl?: string };

export function VoicePage() {
  const mode: "agent" = "agent";
  const [language, setLanguage] = useState("en");
  const [text, setText] = useState("");
  const [chat, setChat] = useState<ChatItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [voiceError, setVoiceError] = useState("");
  const [ttsInfo, setTtsInfo] = useState("");
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const audioRefs = useRef<Record<number, HTMLAudioElement | null>>({});
  const [playingIdx, setPlayingIdx] = useState<number | null>(null);

  // Auto-play the latest agent message audio as soon as it arrives
  useEffect(() => {
    const lastIdx = chat.length - 1;
    if (lastIdx < 0) return;
    const last = chat[lastIdx];
    if (last.role !== "agent" || !last.audioUrl) return;
    const el = audioRefs.current[lastIdx];
    if (!el) return;
    Object.values(audioRefs.current).forEach((a, i) => { if (i !== lastIdx) a?.pause(); });
    el.play().catch(() => {});
    setPlayingIdx(lastIdx);
    el.onended = () => setPlayingIdx(null);
  }, [chat]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!text.trim()) {
      return;
    }

    const userText = text;
    setText("");
    setTtsInfo("");
    setChat((prev) => [...prev, { role: "user", text: userText }]);
    setLoading(true);

    try {
      const data = await processVoice({ text: userText, language, mode, useTts: true });
      let audioUrl: string | undefined;
      if (data.tts_audio_base64) {
        const blob = b64ToBlob(data.tts_audio_base64, data.tts_content_type || "audio/mpeg");
        audioUrl = URL.createObjectURL(blob);
      } else if (data.tts_requested && data.tts_skipped_reason) {
        setTtsInfo(data.tts_skipped_reason);
      }
      setChat((prev) => [...prev, { role: "agent", text: data.response, audioUrl }]);
    } finally {
      setLoading(false);
    }
  }

  function b64ToBlob(base64: string, contentType: string): Blob {
    const byteCharacters = atob(base64);
    const byteArrays: ArrayBuffer[] = [];
    const sliceSize = 1024;
    for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
      const slice = byteCharacters.slice(offset, offset + sliceSize);
      const byteNumbers = new Array(slice.length);
      for (let i = 0; i < slice.length; i += 1) {
        byteNumbers[i] = slice.charCodeAt(i);
      }
      byteArrays.push(new Uint8Array(byteNumbers).buffer);
    }
    return new Blob(byteArrays, { type: contentType });
  }

  async function startRecording() {
    setVoiceError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      chunksRef.current = [];

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.start();
      setRecording(true);
    } catch {
      setVoiceError("Microphone access denied or unavailable.");
    }
  }

  async function stopRecordingAndProcess() {
    if (!mediaRecorderRef.current) {
      return;
    }

    setLoading(true);
    const mediaRecorder = mediaRecorderRef.current;

    await new Promise<void>((resolve) => {
      mediaRecorder.onstop = () => resolve();
      mediaRecorder.stop();
    });

    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setRecording(false);

    try {
      setTtsInfo("");
      const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
      const audioFile = new File([audioBlob], "voice-input.webm", { type: "audio/webm" });

      const data = await processVoiceAudio({ audioFile, mode, language, useTts: true });
      if (data.transcript) {
        setChat((prev) => [...prev, { role: "user", text: data.transcript }]);
      }
      let audioUrl: string | undefined;
      if (data.tts_audio_base64) {
        const blob = b64ToBlob(data.tts_audio_base64, data.tts_content_type || "audio/mpeg");
        audioUrl = URL.createObjectURL(blob);
      } else if (data.tts_requested && data.tts_skipped_reason) {
        setTtsInfo(data.tts_skipped_reason);
      }
      setChat((prev) => [...prev, { role: "agent", text: data.response, audioUrl }]);
    } catch {
      setVoiceError("Audio processing failed. Try text fallback or check backend API key.");
    } finally {
      setLoading(false);
      chunksRef.current = [];
    }
  }

  function togglePlay(idx: number) {
    const el = audioRefs.current[idx];
    if (!el) return;
    if (playingIdx === idx && !el.paused) {
      el.pause();
      setPlayingIdx(null);
    } else {
      Object.values(audioRefs.current).forEach((a) => a?.pause());
      el.play();
      setPlayingIdx(idx);
      el.onended = () => setPlayingIdx(null);
    }
  }

  return (
    <section className="card">
      <div className="help-header">
        <h2>Help</h2>
      </div>

      <form onSubmit={onSubmit} className="form-grid">
        <label>
          Language
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="ta">Tamil</option>
            <option value="te">Telugu</option>
            <option value="bn">Bengali</option>
          </select>
        </label>

        <label className="full-width">
          Ask your question
          <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Type your question..." />
        </label>

        <button type="button" onClick={recording ? stopRecordingAndProcess : startRecording} disabled={loading}>
          {recording ? "⏹ Stop & Process" : "🎙 Record Voice"}
        </button>
        <button type="submit" disabled={loading}>{loading ? "Processing..." : "Send"}</button>
      </form>
      {voiceError ? <p className="error-text">{voiceError}</p> : null}
      {ttsInfo ? <p className="muted">{ttsInfo}</p> : null}

      <div className="chat-box">
        {chat.map((line, idx) => (
          <div key={idx} className={line.role === "agent" ? "bubble bubble-agent" : "bubble bubble-user"}>
            <span className="bubble-label">
              <strong>{line.role === "agent" ? "Mentor" : "You"}</strong>
              {line.role === "agent" && line.audioUrl && (
                <>
                  <audio
                    ref={(el) => { audioRefs.current[idx] = el; }}
                    src={line.audioUrl}
                    preload="auto"
                  />
                  <button
                    type="button"
                    className="mentor-play-btn"
                    onClick={() => togglePlay(idx)}
                    aria-label={playingIdx === idx ? "Pause" : "Play"}
                  >
                    {playingIdx === idx ? "⏸" : "▶"}
                  </button>
                </>
              )}
            </span>
            <span>{line.text}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
