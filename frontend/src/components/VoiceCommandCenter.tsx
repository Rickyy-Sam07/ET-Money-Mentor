import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  analyzePortfolio,
  analyzeTax,
  getNews,
  processVoiceAudio,
  resolveVoiceCommandIntent,
  type VoiceCommandOption,
} from "../lib/api";
import {
  loadNewsItems,
  loadPortfolioInput,
  loadPortfolioResult,
  loadTaxInput,
  loadTaxResult,
  loadUploadPayload,
  saveNewsItems,
  savePortfolioInput,
  savePortfolioResult,
  saveTaxInput,
  saveTaxResult,
  saveUnifiedReport,
} from "../lib/voiceState";

type CommandResult = {
  userText: string;
  mentorReply: string;
  actionSummary: string;
};

const SAMPLE_HOLDINGS = [
  { name: "Nifty Index Fund", units: 200, nav: 41.2, expense_ratio: 0.25, invested_amount: 8000, buy_date: "2024-01-01" },
  { name: "Flexi Cap Fund", units: 150, nav: 62.8, expense_ratio: 1.1, invested_amount: 9000, buy_date: "2024-02-01" },
];

const COMMAND_CATALOG: VoiceCommandOption[] = [
  {
    id: "navigate_dashboard",
    description: "Open dashboard or home page",
    examples: ["open dashboard", "go to home", "home kholo"],
  },
  {
    id: "navigate_voice",
    description: "Open voice page",
    examples: ["open voice", "voice section kholo"],
  },
  {
    id: "navigate_upload",
    description: "Open upload/document section",
    examples: ["open upload", "take me to upload section", "upload page kholo"],
  },
  {
    id: "navigate_tax",
    description: "Open tax wizard page",
    examples: ["open tax", "tax section kholo"],
  },
  {
    id: "navigate_portfolio",
    description: "Open portfolio x-ray page",
    examples: ["open portfolio", "portfolio kholo"],
  },
  {
    id: "navigate_news",
    description: "Open news page",
    examples: ["open news", "khabar kholo"],
  },
  {
    id: "navigate_report",
    description: "Open report page",
    examples: ["open report", "report kholo"],
  },
  {
    id: "run_tax",
    description: "Run tax analysis action",
    examples: ["run tax analysis", "tax chalao", "calculate tax"],
  },
  {
    id: "run_portfolio",
    description: "Run portfolio x-ray action",
    examples: ["run portfolio xray", "portfolio analyze", "portfolio dekh"],
  },
  {
    id: "run_news",
    description: "Fetch latest news",
    examples: ["refresh news", "market news dikhao", "khabar dikhao"],
  },
  {
    id: "generate_report",
    description: "Generate unified report and open report page",
    examples: ["generate report", "report banao", "final report dikhao"],
  },
  {
    id: "help",
    description: "Read supported command examples",
    examples: ["help", "madad", "commands batao"],
  },
];

function containsAny(text: string, patterns: RegExp[]): boolean {
  return patterns.some((rx) => rx.test(text));
}

function extractNumber(transcript: string, token: string): number | null {
  const rx = new RegExp(`${token}\\s*(?:is\\s*)?([0-9][0-9,]*(?:\\.[0-9]+)?)`, "i");
  const match = transcript.match(rx);
  if (!match) {
    return null;
  }
  return Number(match[1].replace(/,/g, ""));
}

function parseRegime(transcript: string): "old" | "new" | null {
  if (/old\s+regime|regime\s+old/i.test(transcript)) {
    return "old";
  }
  if (/new\s+regime|regime\s+new/i.test(transcript)) {
    return "new";
  }
  return null;
}

function parseCommand(transcript: string):
  | { kind: "navigate"; target: string }
  | { kind: "tax"; payload: { gross_salary: number; deductions_80c: number; deductions_80d: number; regime_preference: "old" | "new" } }
  | { kind: "portfolio" }
  | { kind: "news" }
  | { kind: "report" }
  | { kind: "help" }
  | { kind: "unknown" } {
  const t = transcript.toLowerCase();

  const helpPatterns = [
    /\b(help|commands|what can you do)\b/,
    /\bmadad\b/,
    /\bkaise\s+use\s+karu\b/,
  ];

  const openPatterns = [
    /\b(go to|open|navigate to)\b/,
    /\b(kholo|kholo|jao|chalo)\b/,
  ];

  const dashboardPatterns = [/(dashboard|home)\b/, /\b(home|ghar)\b/];
  const voicePatterns = [/\bvoice\b/, /\bawaaz\b/];
  const uploadPatterns = [/\bupload\b/, /\b(document|file)\b/, /\b(file\s+upload|document\s+upload)\b/];
  const taxPatterns = [/\btax\b/, /\btax\s+analysis\b/, /\btax\s+calculate\b/, /\btax\s+nikalo\b/, /\btax\s+chalao\b/];
  const portfolioPatterns = [/\bportfolio\b/, /\bx-?ray\b/, /\bportfolio\s+check\b/, /\bportfolio\s+dekh\b/];
  const newsPatterns = [/\bnews\b/, /\bmarket\b/, /\bheadlines\b/, /\bkhabar\b/, /\bnews\s+dikhao\b/];
  const reportPatterns = [/\breport\b/, /\bfinal\s+report\b/, /\breport\s+banao\b/, /\breport\s+dikhao\b/];

  const runTaxPatterns = [
    /\b(run|analyze|calculate).*(tax)\b/,
    /\btax\s+analysis\b/,
    /\btax\s+chalao\b/,
    /\btax\s+nikalo\b/,
    /\btax\s+calculate\b/,
  ];

  const runPortfolioPatterns = [
    /\b(run|analyze|check|x-?ray).*(portfolio)\b/,
    /\bportfolio\s+x\s*ray\b/,
    /\bportfolio\s+chalao\b/,
    /\bportfolio\s+analyze\b/,
  ];

  const runNewsPatterns = [
    /\b(news|market|headlines|refresh news)\b/,
    /\bnews\s+refresh\b/,
    /\bkhabar\s+dikhao\b/,
    /\bmarket\s+news\s+dikhao\b/,
  ];

  const generateReportPatterns = [
    /\b(generate|show|open).*(report)\b/,
    /\bfinal\s+report\b/,
    /\breport\s+banao\b/,
    /\breport\s+nikalo\b/,
  ];

  if (containsAny(t, helpPatterns)) {
    return { kind: "help" };
  }

  if (containsAny(t, openPatterns)) {
    if (containsAny(t, dashboardPatterns)) return { kind: "navigate", target: "/" };
    if (containsAny(t, voicePatterns)) return { kind: "navigate", target: "/voice" };
    if (containsAny(t, uploadPatterns)) return { kind: "navigate", target: "/upload" };
    if (containsAny(t, taxPatterns)) return { kind: "navigate", target: "/tax" };
    if (containsAny(t, portfolioPatterns)) return { kind: "navigate", target: "/portfolio" };
    if (containsAny(t, newsPatterns)) return { kind: "navigate", target: "/news" };
    if (containsAny(t, reportPatterns)) return { kind: "navigate", target: "/report" };
  }

  if (containsAny(t, runTaxPatterns)) {
    const existing = loadTaxInput();
    const salary = extractNumber(transcript, "salary") ?? existing?.gross_salary ?? 1200000;
    const ded80c = extractNumber(transcript, "80c") ?? existing?.deductions_80c ?? 60000;
    const ded80d = extractNumber(transcript, "80d") ?? existing?.deductions_80d ?? 12000;
    const regime = parseRegime(transcript) ?? existing?.regime_preference ?? "new";

    return {
      kind: "tax",
      payload: {
        gross_salary: salary,
        deductions_80c: ded80c,
        deductions_80d: ded80d,
        regime_preference: regime,
      },
    };
  }

  if (containsAny(t, runPortfolioPatterns)) {
    return { kind: "portfolio" };
  }

  if (containsAny(t, runNewsPatterns)) {
    return { kind: "news" };
  }

  if (containsAny(t, generateReportPatterns)) {
    return { kind: "report" };
  }

  return { kind: "unknown" };
}

function extractHoldingsFromUpload(): Array<Record<string, unknown>> | null {
  const payload = loadUploadPayload<any>();
  if (!payload) {
    return null;
  }

  const parsedFunds = payload?.parsed?.extracted_fields?.funds;
  if (Array.isArray(parsedFunds) && parsedFunds.length > 0) {
    return parsedFunds;
  }

  return null;
}

function commandFromId(commandId: string, transcript: string):
  | { kind: "navigate"; target: string }
  | { kind: "tax"; payload: { gross_salary: number; deductions_80c: number; deductions_80d: number; regime_preference: "old" | "new" } }
  | { kind: "portfolio" }
  | { kind: "news" }
  | { kind: "report" }
  | { kind: "help" }
  | { kind: "unknown" } {
  if (commandId === "navigate_dashboard") return { kind: "navigate", target: "/" };
  if (commandId === "navigate_voice") return { kind: "navigate", target: "/voice" };
  if (commandId === "navigate_upload") return { kind: "navigate", target: "/upload" };
  if (commandId === "navigate_tax") return { kind: "navigate", target: "/tax" };
  if (commandId === "navigate_portfolio") return { kind: "navigate", target: "/portfolio" };
  if (commandId === "navigate_news") return { kind: "navigate", target: "/news" };
  if (commandId === "navigate_report") return { kind: "navigate", target: "/report" };

  if (commandId === "run_tax") {
    const existing = loadTaxInput();
    const salary = extractNumber(transcript, "salary") ?? existing?.gross_salary ?? 1200000;
    const ded80c = extractNumber(transcript, "80c") ?? existing?.deductions_80c ?? 60000;
    const ded80d = extractNumber(transcript, "80d") ?? existing?.deductions_80d ?? 12000;
    const regime = parseRegime(transcript) ?? existing?.regime_preference ?? "new";
    return {
      kind: "tax",
      payload: {
        gross_salary: salary,
        deductions_80c: ded80c,
        deductions_80d: ded80d,
        regime_preference: regime,
      },
    };
  }

  if (commandId === "run_portfolio") return { kind: "portfolio" };
  if (commandId === "run_news") return { kind: "news" };
  if (commandId === "generate_report") return { kind: "report" };
  if (commandId === "help") return { kind: "help" };
  return { kind: "unknown" };
}

export function VoiceCommandCenter() {
  const navigate = useNavigate();
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  const [recording, setRecording] = useState(false);
  const [busy, setBusy] = useState(false);
  const [last, setLast] = useState<CommandResult | null>(null);
  const [error, setError] = useState("");
  const [ttsInfo, setTtsInfo] = useState("");
  const [mentorAudioUrl, setMentorAudioUrl] = useState("");

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

  function speakShortReply(text: string) {
    const clean = text.trim();
    if (!clean || typeof window === "undefined" || !("speechSynthesis" in window)) {
      return;
    }
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  }

  async function startRecording() {
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      chunksRef.current = [];

      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.start();
      setRecording(true);
    } catch {
      setError("Microphone permission is required for voice commands.");
    }
  }

  async function stopAndRun() {
    if (!mediaRecorderRef.current) {
      return;
    }

    setBusy(true);
    const recorder = mediaRecorderRef.current;

    await new Promise<void>((resolve) => {
      recorder.onstop = () => resolve();
      recorder.stop();
    });

    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setRecording(false);

    try {
      setTtsInfo("");
      setMentorAudioUrl("");
      const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
      const audioFile = new File([audioBlob], "voice-command.webm", { type: "audio/webm" });
      const voiceData = await processVoiceAudio({
        audioFile,
        language: undefined,
        mode: "agent",
        useTts: true,
      });

      const transcript = String(voiceData.transcript || "").trim();
      const mentor = String(voiceData.response || "").trim();
      let command = parseCommand(transcript);
      let llmReason = "";

      if (transcript) {
        try {
          const resolved = await resolveVoiceCommandIntent({
            transcript,
            commands: COMMAND_CATALOG,
          });
          llmReason = resolved.reason || "";
          if (resolved.command_id && resolved.command_id !== "unknown") {
            command = commandFromId(resolved.command_id, transcript);
          }
        } catch {
          // Keep regex fallback parsing path.
        }
      }

      if (!transcript) {
        setLast({ userText: "", mentorReply: mentor, actionSummary: "No transcript recognized. Please retry." });
        return;
      }

      if (command.kind === "navigate") {
        navigate(command.target);
        const shortReply =
          command.target === "/upload"
            ? "Opening upload section."
            : command.target === "/tax"
            ? "Opening tax wizard."
            : command.target === "/portfolio"
            ? "Opening portfolio page."
            : command.target === "/news"
            ? "Opening news page."
            : command.target === "/report"
            ? "Opening report page."
            : "Opening requested section.";

        if (voiceData.tts_audio_base64) {
          const ttsBlob = b64ToBlob(voiceData.tts_audio_base64, voiceData.tts_content_type || "audio/wav");
          const url = URL.createObjectURL(ttsBlob);
          setMentorAudioUrl(url);
        } else {
          if (voiceData.tts_skipped_reason) {
            setTtsInfo(voiceData.tts_skipped_reason);
          }
          speakShortReply(shortReply);
        }

        setLast({
          userText: transcript,
          mentorReply: shortReply,
          actionSummary: llmReason ? `Navigated to ${command.target}. (${llmReason})` : `Navigated to ${command.target}.`,
        });
        return;
      }

      if (command.kind === "tax") {
        saveTaxInput(command.payload);
        const taxResult = await analyzeTax(
          {
            gross_salary: command.payload.gross_salary,
            deductions_80c: command.payload.deductions_80c,
            deductions_80d: command.payload.deductions_80d,
          },
          command.payload.regime_preference
        );
        saveTaxResult(taxResult);
        navigate("/tax");
        const shortReply = "Tax analysis completed. Opening tax page.";
        if (voiceData.tts_audio_base64) {
          const ttsBlob = b64ToBlob(voiceData.tts_audio_base64, voiceData.tts_content_type || "audio/wav");
          const url = URL.createObjectURL(ttsBlob);
          setMentorAudioUrl(url);
        } else {
          if (voiceData.tts_skipped_reason) {
            setTtsInfo(voiceData.tts_skipped_reason);
          }
          speakShortReply(shortReply);
        }
        setLast({
          userText: transcript,
          mentorReply: shortReply,
          actionSummary: `Tax analyzed with salary ${command.payload.gross_salary} and regime ${command.payload.regime_preference}.`,
        });
        return;
      }

      if (command.kind === "portfolio") {
        const holdings = loadPortfolioInput<Array<Record<string, unknown>>>() || extractHoldingsFromUpload() || SAMPLE_HOLDINGS;
        savePortfolioInput(holdings);
        const portfolioResult = await analyzePortfolio(holdings);
        savePortfolioResult(portfolioResult);
        navigate("/portfolio");
        const shortReply = "Portfolio analysis completed. Opening portfolio page.";
        if (voiceData.tts_audio_base64) {
          const ttsBlob = b64ToBlob(voiceData.tts_audio_base64, voiceData.tts_content_type || "audio/wav");
          const url = URL.createObjectURL(ttsBlob);
          setMentorAudioUrl(url);
        } else {
          if (voiceData.tts_skipped_reason) {
            setTtsInfo(voiceData.tts_skipped_reason);
          }
          speakShortReply(shortReply);
        }
        setLast({
          userText: transcript,
          mentorReply: shortReply,
          actionSummary: `Portfolio X-Ray completed for ${holdings.length} holding entries.`,
        });
        return;
      }

      if (command.kind === "news") {
        const news = await getNews();
        const items = Array.isArray(news?.items) ? news.items : [];
        saveNewsItems(items);
        navigate("/news");
        const shortReply = "News refreshed. Opening news page.";
        if (voiceData.tts_audio_base64) {
          const ttsBlob = b64ToBlob(voiceData.tts_audio_base64, voiceData.tts_content_type || "audio/wav");
          const url = URL.createObjectURL(ttsBlob);
          setMentorAudioUrl(url);
        } else {
          if (voiceData.tts_skipped_reason) {
            setTtsInfo(voiceData.tts_skipped_reason);
          }
          speakShortReply(shortReply);
        }
        setLast({ userText: transcript, mentorReply: shortReply, actionSummary: `News refreshed with ${items.length} items.` });
        return;
      }

      if (command.kind === "report") {
        const taxInput = loadTaxInput();
        const taxResult = loadTaxResult();
        const portfolioInput = loadPortfolioInput();
        const portfolioResult = loadPortfolioResult();
        const newsItems = loadNewsItems();

        const report = {
          generated_at: new Date().toISOString(),
          source: "voice-command-center-agent-mode",
          tax_input: taxInput,
          tax_result: taxResult,
          portfolio_input: portfolioInput,
          portfolio_result: portfolioResult,
          news: newsItems,
        };

        saveUnifiedReport(report);
        navigate("/report");
        const shortReply = "Report generated. Opening report page.";
        if (voiceData.tts_audio_base64) {
          const ttsBlob = b64ToBlob(voiceData.tts_audio_base64, voiceData.tts_content_type || "audio/wav");
          const url = URL.createObjectURL(ttsBlob);
          setMentorAudioUrl(url);
        } else {
          if (voiceData.tts_skipped_reason) {
            setTtsInfo(voiceData.tts_skipped_reason);
          }
          speakShortReply(shortReply);
        }
        setLast({ userText: transcript, mentorReply: shortReply, actionSummary: "Unified report generated and opened." });
        return;
      }

      if (command.kind === "help") {
        const shortReply = "You can say: open upload, run tax, run portfolio, refresh news, generate report.";
        speakShortReply(shortReply);
        setLast({
          userText: transcript,
          mentorReply: shortReply,
          actionSummary:
            "Try: open tax, run tax analysis salary 1400000 80c 150000 80d 25000 old regime, run portfolio xray, refresh news, generate report. Hinglish also works: tax chalao, portfolio dekh, khabar dikhao, report banao.",
        });
        return;
      }

      speakShortReply("I did not understand. Say help for command examples.");
      setLast({
        userText: transcript,
        mentorReply: "I did not understand. Say help for command examples.",
        actionSummary: "Command not recognized. Say help to hear valid voice commands.",
      });
    } catch {
      setError("Voice command processing failed. Check backend and API keys.");
    } finally {
      setBusy(false);
      chunksRef.current = [];
    }
  }

  return (
    <section className="voice-command-center">
      <h3>Hands-Free Voice Commands (Agent Mode)</h3>
      <p className="muted">Use speech only: navigate pages, run tax, run portfolio, refresh news, and generate report.</p>
      <button type="button" onClick={recording ? stopAndRun : startRecording} disabled={busy}>
        {recording ? "Stop and Execute Command" : busy ? "Processing..." : "Start Voice Command"}
      </button>
      {error ? <p className="error-text">{error}</p> : null}
      {ttsInfo ? <p className="muted">{ttsInfo}</p> : null}
      {mentorAudioUrl ? <audio controls autoPlay src={mentorAudioUrl} className="audio-player" /> : null}
      {last ? (
        <div className="voice-command-log">
          <p><strong>Heard:</strong> {last.userText || "(empty)"}</p>
          <p><strong>Mentor:</strong> {last.mentorReply || "(no reply)"}</p>
          <p><strong>Action:</strong> {last.actionSummary}</p>
        </div>
      ) : null}
    </section>
  );
}
