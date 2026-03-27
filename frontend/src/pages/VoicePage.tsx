import { FormEvent, useRef, useState } from "react";
import { processVoice, processVoiceAudio } from "../lib/api";

type ChatItem = { role: "user" | "agent"; text: string };

export function VoicePage() {
  const mode: "agent" = "agent";
  const [language, setLanguage] = useState("en");
  const [text, setText] = useState("");
  const [chat, setChat] = useState<ChatItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [voiceError, setVoiceError] = useState("");
  const [ttsInfo, setTtsInfo] = useState("");
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const [audioPreviewUrl, setAudioPreviewUrl] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!text.trim()) {
      return;
    }

    const userText = text;
    setText("");
    setAudioPreviewUrl("");
    setTtsInfo("");
    setChat((prev) => [...prev, { role: "user", text: userText }]);
    setLoading(true);

    try {
      const data = await processVoice({ text: userText, language, mode, useTts: ttsEnabled });
      setChat((prev) => [...prev, { role: "agent", text: data.response }]);

      if (data.tts_audio_base64) {
        const audioBlob = b64ToBlob(data.tts_audio_base64, data.tts_content_type || "audio/wav");
        const url = URL.createObjectURL(audioBlob);
        setAudioPreviewUrl(url);
      } else if (data.tts_requested && data.tts_skipped_reason) {
        setTtsInfo(data.tts_skipped_reason);
      }
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
      setAudioPreviewUrl("");
      setTtsInfo("");
      const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
      const audioFile = new File([audioBlob], "voice-input.webm", { type: "audio/webm" });

      const data = await processVoiceAudio({ audioFile, mode, language, useTts: ttsEnabled });
      if (data.transcript) {
        setChat((prev) => [...prev, { role: "user", text: data.transcript }]);
      }
      setChat((prev) => [...prev, { role: "agent", text: data.response }]);

      if (data.tts_audio_base64) {
        const ttsBlob = b64ToBlob(data.tts_audio_base64, data.tts_content_type || "audio/wav");
        const url = URL.createObjectURL(ttsBlob);
        setAudioPreviewUrl(url);
      } else if (data.tts_requested && data.tts_skipped_reason) {
        setTtsInfo(data.tts_skipped_reason);
      }
    } catch {
      setVoiceError("Audio processing failed. Try text fallback or check backend API key.");
    } finally {
      setLoading(false);
      chunksRef.current = [];
    }
  }

  return (
    <section className="card">
      <h2>Voice Agent</h2>
      <form onSubmit={onSubmit} className="form-grid">
        <label>
          Mode
          <input value="agent" disabled />
        </label>

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

        <label>
          Mentor TTS
          <select value={ttsEnabled ? "on" : "off"} onChange={(e) => setTtsEnabled(e.target.value === "on")}>
            <option value="off">Off (save credits)</option>
            <option value="on">On (audio reply)</option>
          </select>
        </label>

        <label className="full-width">
          Text input (voice fallback)
          <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Type what user said..." />
        </label>

        <button type="button" onClick={recording ? stopRecordingAndProcess : startRecording} disabled={loading}>
          {recording ? "Stop + Process Audio" : "Record with Sarvam STT"}
        </button>
        <button type="submit" disabled={loading}>{loading ? "Processing..." : "Send"}</button>
      </form>
      {voiceError ? <p className="error-text">{voiceError}</p> : null}
      {ttsInfo ? <p className="muted">{ttsInfo}</p> : null}
      {audioPreviewUrl ? <audio controls src={audioPreviewUrl} className="audio-player" /> : null}

      <div className="chat-box">
        {chat.map((line, idx) => (
          <div key={idx} className={line.role === "agent" ? "bubble bubble-agent" : "bubble bubble-user"}>
            <strong>{line.role === "agent" ? "Mentor" : "User"}:</strong> {line.text}
          </div>
        ))}
      </div>
    </section>
  );
}
