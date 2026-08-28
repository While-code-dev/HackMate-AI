import { useEffect, useRef, useState, useCallback } from "react";
import api from "./api.js";
import {
  LayoutDashboard, Lightbulb, Map, Code2, Rocket,
  Bot, CheckCircle2, Send, LogOut, ArrowRight,
  Target, Shield, FlaskConical, Plus, Trash2, ChevronRight,
  X, AlertCircle, Loader2, BookOpen, Presentation, Zap, Clock,
} from "lucide-react";
import "./index.css";

/* =========================================================
   HELPERS
========================================================= */

function getErrorMessage(error, fallback = "Something went wrong.") {
  if (error?.response?.data?.detail) {
    const d = error.response.data.detail;
    if (Array.isArray(d)) return d.map((i) => i.msg || JSON.stringify(i)).join(", ");
    return d;
  }
  if (error?.response?.status) return `Server error (${error.response.status})`;
  if (error?.request) return "Cannot reach HackMate AI backend. Is it running?";
  return error?.message || fallback;
}

const STAGE_ORDER = [
  "problem_discovery", "problem_validation", "solution_ideation",
  "product_planning", "technical_architecture", "development",
  "testing", "responsible_ai", "documentation", "pitch_submission",
];

const STAGE_META = {
  problem_discovery:     { label: "Problem Discovery",        icon: Target,       color: "#6366f1", desc: "Discover meaningful problems to solve" },
  problem_validation:    { label: "Problem Validation",       icon: CheckCircle2, color: "#8b5cf6", desc: "Validate your problem is worth solving" },
  solution_ideation:     { label: "Solution Ideation",        icon: Lightbulb,    color: "#a855f7", desc: "Generate and compare solution ideas" },
  product_planning:      { label: "Product Planning",         icon: Map,          color: "#ec4899", desc: "Define your MVP and feature roadmap" },
  technical_architecture:{ label: "Technical Architecture",   icon: Code2,        color: "#f59e0b", desc: "Design your system architecture" },
  development:           { label: "Development",              icon: Zap,          color: "#10b981", desc: "Get coding help and implementation guidance" },
  testing:               { label: "Testing & QA",             icon: FlaskConical, color: "#06b6d4", desc: "Test your project before submission" },
  responsible_ai:        { label: "Responsible AI & Security",icon: Shield,       color: "#3b82f6", desc: "Review security and responsible AI" },
  documentation:         { label: "Documentation",            icon: BookOpen,     color: "#64748b", desc: "Generate project documentation" },
  pitch_submission:      { label: "Pitch & Submission",       icon: Presentation, color: "#ef4444", desc: "Prepare your pitch and final submission" },
};

/* =========================================================
   BRAND
========================================================= */

function Brand() {
  return (
    <div className="brand">
      <div className="brand-icon">H</div>
      <div>
        <h2>HackMate AI</h2>
        <span>Hackathon Copilot</span>
      </div>
    </div>
  );
}

/* =========================================================
   LOGIN
========================================================= */

function Login({ onLogin, goRegister }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const login = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.post("/auth/login", {
        username: username.trim(),
        password,
      });
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("username", username.trim());
      onLogin();
    } catch (err) {
      setError(getErrorMessage(err, "Unable to login."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <Brand />
        <div className="auth-heading">
          <h1>Welcome back 👋</h1>
          <p>Continue your hackathon journey with your AI copilot.</p>
        </div>
        <form onSubmit={login}>
          <label>Username</label>
          <input type="text" placeholder="Enter your username" value={username}
            onChange={(e) => setUsername(e.target.value)} required />
          <label>Password</label>
          <input type="password" placeholder="Enter your password" value={password}
            onChange={(e) => setPassword(e.target.value)} required />
          {error && <div className="error-box"><AlertCircle size={15} /> {error}</div>}
          <button className="primary-button" disabled={loading} type="submit">
            {loading ? <><Loader2 size={16} className="spin" /> Logging in...</> : <>Login <ArrowRight size={18} /></>}
          </button>
        </form>
        <p className="auth-switch">
          Don't have an account?{" "}
          <button onClick={goRegister}>Create account</button>
        </p>
      </div>
    </div>
  );
}

/* =========================================================
   REGISTER
========================================================= */

function Register({ goLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const register = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    setLoading(true);
    try {
      await api.post("/auth/register", {
        username: username.trim(),
        password,
      });
      setSuccess("Account created! Redirecting to login...");
      setTimeout(() => goLogin(), 1500);
    } catch (err) {
      setError(getErrorMessage(err, "Unable to create account."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <Brand />
        <div className="auth-heading">
          <h1>Create your account 🚀</h1>
          <p>Start your journey from problem statement to submission.</p>
        </div>
        <form onSubmit={register}>
          <label>Username</label>
          <input type="text" placeholder="Choose a username" value={username}
            onChange={(e) => setUsername(e.target.value)} minLength={3} required />
          <label>Password</label>
          <input type="password" placeholder="Create a password (min 6 chars)" value={password}
            onChange={(e) => setPassword(e.target.value)} minLength={6} required />
          {error && <div className="error-box"><AlertCircle size={15} /> {error}</div>}
          {success && <div className="success-box">{success}</div>}
          <button className="primary-button" disabled={loading} type="submit">
            {loading ? <><Loader2 size={16} className="spin" /> Creating...</> : <>Create Account <ArrowRight size={18} /></>}
          </button>
        </form>
        <p className="auth-switch">
          Already have an account?{" "}
          <button onClick={goLogin}>Login</button>
        </p>
      </div>
    </div>
  );
}

/* =========================================================
   AI BADGE — shown on AI-generated content
========================================================= */

function AIBadge({ agent }) {
  return (
    <div className="ai-badge">
      <Bot size={12} />
      <span>AI-generated{agent ? ` · ${agent}` : ""}</span>
    </div>
  );
}

/* =========================================================
   MARKDOWN RENDERER (simple)
========================================================= */

function MarkdownText({ text }) {
  if (!text) return null;
  // Simple markdown: bold, headers, bullets
  const lines = text.split("\n");
  const elements = [];
  let listItems = [];

  const flushList = () => {
    if (listItems.length) {
      elements.push(<ul key={`ul-${elements.length}`}>{listItems}</ul>);
      listItems = [];
    }
  };

  lines.forEach((line, i) => {
    if (line.startsWith("### ")) {
      flushList();
      elements.push(<h4 key={i}>{line.slice(4)}</h4>);
    } else if (line.startsWith("## ")) {
      flushList();
      elements.push(<h3 key={i}>{line.slice(3)}</h3>);
    } else if (line.startsWith("# ")) {
      flushList();
      elements.push(<h2 key={i}>{line.slice(2)}</h2>);
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      listItems.push(<li key={i}>{formatInline(line.slice(2))}</li>);
    } else if (line.trim() === "") {
      flushList();
      elements.push(<br key={i} />);
    } else {
      flushList();
      elements.push(<p key={i}>{formatInline(line)}</p>);
    }
  });
  flushList();
  return <div className="markdown-body">{elements}</div>;
}

function formatInline(text) {
  // Bold **text**
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) =>
    part.startsWith("**") && part.endsWith("**")
      ? <strong key={i}>{part.slice(2, -2)}</strong>
      : part
  );
}

/* =========================================================
   STAGE CHAT — the core agent workspace
========================================================= */

function StageChat({ project, stage, onStageCompleted }) {
  const meta = STAGE_META[stage] || {};
  const StageIcon = meta.icon || Bot;

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [stageStatus, setStageStatus] = useState("pending");
  const [completing, setCompleting] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  // Load existing chat history when stage or project changes
  useEffect(() => {
    let cancelled = false;
    setLoadingHistory(true);
    setMessages([]);
    setError("");
    api.get(`/projects/${project.id}/stages/${stage}`)
      .then((res) => {
        if (cancelled) return;
        setStageStatus(res.data.status || "pending");
        const hist = res.data.chat_history || [];
        setMessages(hist.map((m) => ({ role: m.role, text: m.content })));
      })
      .catch(() => {
        if (!cancelled) setMessages([]);
      })
      .finally(() => {
        if (!cancelled) setLoadingHistory(false);
      });
    return () => { cancelled = true; };
  }, [project.id, stage]);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setError("");
    setMessages((prev) => [...prev, { role: "user", text }]);
    setLoading(true);
    try {
      const res = await api.post(`/projects/${project.id}/stages/${stage}/chat`, {
        message: text,
      });
      setMessages((prev) => [...prev, { role: "assistant", text: res.data.ai_response }]);
      setStageStatus("in_progress");
    } catch (err) {
      const msg = getErrorMessage(err, "Failed to get AI response.");
      setMessages((prev) => [...prev, { role: "assistant", text: `⚠️ ${msg}` }]);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const completeStage = async () => {
    setCompleting(true);
    try {
      const res = await api.post(`/projects/${project.id}/stages/${stage}/complete`, {
        advance: true,
      });
      setStageStatus("completed");
      onStageCompleted(res.data);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to complete stage."));
    } finally {
      setCompleting(false);
    }
  };

  const contextTip = () => {
    const ctx = [];
    if (project.hackathon_name) ctx.push(`Hackathon: ${project.hackathon_name}`);
    if (project.theme) ctx.push(`Theme: ${project.theme}`);
    if (project.interests) ctx.push(`Interests: ${project.interests}`);
    if (project.skills) ctx.push(`Skills: ${project.skills}`);
    if (project.team_info) ctx.push(`Team: ${project.team_info}`);
    return ctx;
  };

  return (
    <div className="stage-chat-page">
      {/* Stage header */}
      <div className="stage-chat-header">
        <div className="stage-chat-title">
          <div className="stage-icon-circle" style={{ background: meta.color + "22", color: meta.color }}>
            <StageIcon size={22} />
          </div>
          <div>
            <h2>{meta.label}</h2>
            <p>{meta.desc}</p>
          </div>
        </div>
        <div className="stage-actions">
          {stageStatus === "completed" ? (
            <span className="badge completed"><CheckCircle2 size={14} /> Completed</span>
          ) : stageStatus === "in_progress" ? (
            <span className="badge in-progress"><Clock size={14} /> In Progress</span>
          ) : (
            <span className="badge pending">Not started</span>
          )}
          {stageStatus !== "completed" && messages.length > 0 && (
            <button className="complete-btn" onClick={completeStage} disabled={completing}>
              {completing ? <><Loader2 size={14} className="spin" /> Completing...</> : <><CheckCircle2 size={14} /> Mark Complete</>}
            </button>
          )}
        </div>
      </div>

      {/* Context bar */}
      {contextTip().length > 0 && (
        <div className="context-bar">
          <span className="context-label">Project context:</span>
          {contextTip().map((c, i) => <span key={i} className="context-chip">{c}</span>)}
        </div>
      )}

      {/* Chat area */}
      <div className="stage-chat-messages">
        {loadingHistory ? (
          <div className="chat-loading"><Loader2 size={28} className="spin" /><p>Loading conversation...</p></div>
        ) : messages.length === 0 ? (
          <div className="empty-chat">
            <div className="empty-chat-icon" style={{ color: meta.color }}>
              <StageIcon size={48} />
            </div>
            <h3>Start the {meta.label} stage</h3>
            <p>Your <strong>{meta.label} Agent</strong> is ready. Ask a question or type "Start" to begin.</p>
            <div className="starter-chips">
              {getStarterPrompts(stage).map((p, i) => (
                <button key={i} className="starter-chip" onClick={() => setInput(p)}>{p}</button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              {msg.role === "assistant" && (
                <div className="message-header">
                  <div className="agent-avatar" style={{ background: meta.color + "22", color: meta.color }}>
                    <StageIcon size={14} />
                  </div>
                  <span className="agent-name">{meta.label} Agent</span>
                  <AIBadge />
                </div>
              )}
              <div className="message-body">
                {msg.role === "assistant"
                  ? <MarkdownText text={msg.text} />
                  : msg.text}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="message assistant">
            <div className="message-header">
              <div className="agent-avatar" style={{ background: meta.color + "22", color: meta.color }}>
                <StageIcon size={14} />
              </div>
              <span className="agent-name">{meta.label} Agent</span>
            </div>
            <div className="message-body typing">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && <div className="error-bar"><AlertCircle size={14} /> {error}</div>}

      {/* Input */}
      <div className="chat-input">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
          placeholder={`Message the ${meta.label} Agent...`}
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()} className="send-btn">
          {loading ? <Loader2 size={18} className="spin" /> : <Send size={18} />}
        </button>
      </div>

      <p className="ai-disclaimer">
        <Bot size={12} /> Responses are AI-generated. Review and verify before relying on them for important decisions.
      </p>
    </div>
  );
}

function getStarterPrompts(stage) {
  const map = {
    problem_discovery:      ["Help me discover problems in education", "I'm interested in sustainability — what problems can I solve?", "Generate 5 problem ideas for my hackathon"],
    problem_validation:     ["Validate my problem statement", "Is this problem realistic for a hackathon?", "Who are the target users for this problem?"],
    solution_ideation:      ["Generate solution ideas for my problem", "What are 3 different approaches I could take?", "Which solution is most feasible for a hackathon?"],
    product_planning:       ["Define the MVP for my solution", "Create user stories for my product", "What features are must-have vs nice-to-have?"],
    technical_architecture: ["Recommend a tech stack for my project", "Design the system architecture", "What APIs should I use?"],
    development:            ["Help me implement the core feature", "I'm getting an error — help me debug", "Generate starter code for the backend"],
    testing:                ["Generate a test checklist for my project", "What edge cases should I test?", "Help me create a demo-ready test plan"],
    responsible_ai:         ["Review my project for security risks", "How should I handle user data?", "What responsible AI considerations apply?"],
    documentation:          ["Generate a README for my project", "Write the project summary for submission", "Document my architecture"],
    pitch_submission:       ["Write my elevator pitch", "Create a demo flow", "Generate a submission checklist"],
  };
  return map[stage] || ["Start", "What should I do first?", "Help me with this stage"];
}

/* =========================================================
   PROGRESS BAR
========================================================= */

function ProgressBar({ value }) {
  return (
    <div className="progress-bar-outer">
      <div className="progress-bar-inner" style={{ width: `${value}%` }} />
    </div>
  );
}

/* =========================================================
   PROJECT OVERVIEW — progress view inside a project
========================================================= */

function ProjectOverview({ project, onSelectStage }) {
  const completedCount = (project.stages || []).filter((s) => s.status === "completed").length;

  return (
    <div className="project-overview">
      <div className="overview-hero">
        <div>
          <span className="eyebrow">HACKATHON PROJECT</span>
          <h1>{project.project_name}</h1>
          {project.hackathon_name && <p className="hack-name">📍 {project.hackathon_name}</p>}
          {project.theme && <p className="hack-theme">🎯 {project.theme}</p>}
        </div>
        <div className="overview-progress-box">
          <div className="progress-ring">
            <svg viewBox="0 0 80 80" width="80" height="80">
              <circle cx="40" cy="40" r="32" stroke="#e2e8f0" strokeWidth="8" fill="none" />
              <circle cx="40" cy="40" r="32" stroke="#6366f1" strokeWidth="8" fill="none"
                strokeDasharray={`${2 * Math.PI * 32}`}
                strokeDashoffset={`${2 * Math.PI * 32 * (1 - project.progress / 100)}`}
                strokeLinecap="round"
                style={{ transform: "rotate(-90deg)", transformOrigin: "center", transition: "stroke-dashoffset 0.5s ease" }}
              />
            </svg>
            <div className="progress-ring-label">{project.progress}%</div>
          </div>
          <div>
            <strong>{completedCount} / {STAGE_ORDER.length}</strong>
            <span>stages done</span>
          </div>
        </div>
      </div>

      <div className="stage-pipeline">
        {STAGE_ORDER.map((key, idx) => {
          const stageData = (project.stages || []).find((s) => s.stage === key);
          const status = stageData?.status || "pending";
          const meta = STAGE_META[key];
          const Icon = meta.icon;
          const isCurrent = project.current_stage === key;

          return (
            <div key={key} className={`pipeline-step ${status} ${isCurrent ? "current" : ""}`}
              onClick={() => onSelectStage(key)}>
              <div className="pipeline-icon" style={{
                background: status === "completed" ? "#10b981" : isCurrent ? meta.color : "#e2e8f0",
                color: (status === "completed" || isCurrent) ? "#fff" : "#94a3b8",
              }}>
                {status === "completed" ? <CheckCircle2 size={18} /> : <Icon size={18} />}
              </div>
              <span className="pipeline-label">{meta.label}</span>
              {status === "completed" && <span className="pipeline-badge done">Done</span>}
              {isCurrent && status !== "completed" && <span className="pipeline-badge active">Active</span>}
              {idx < STAGE_ORDER.length - 1 && (
                <div className={`pipeline-connector ${status === "completed" ? "done" : ""}`} />
              )}
            </div>
          );
        })}
      </div>

      <div className="overview-cta">
        <button className="primary-button" onClick={() => onSelectStage(project.current_stage)}>
          Continue: {STAGE_META[project.current_stage]?.label} <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );
}

/* =========================================================
   PROJECT WORKSPACE — shell that holds overview + stage chat
========================================================= */

function ProjectWorkspace({ projectId, onBack, onProjectDeleted }) {
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeStage, setActiveStage] = useState(null); // null = overview
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    setLoading(true);
    api.get(`/projects/${projectId}`)
      .then((res) => {
        setProject(res.data);
        setLoading(false);
      })
      .catch((err) => {
        setError(getErrorMessage(err, "Failed to load project."));
        setLoading(false);
      });
  }, [projectId, refreshKey]);

  const loadProject = useCallback(() => {
    setRefreshKey((k) => k + 1);
  }, []);

  const handleStageCompleted = (result) => {
    // Refresh project data after stage completion
    loadProject();
    if (result.next_stage) {
      setActiveStage(result.next_stage);
    }
  };

  const deleteProject = async () => {
    if (!window.confirm(`Delete "${project?.project_name}"? This cannot be undone.`)) return;
    try {
      await api.delete(`/projects/${projectId}`);
      onProjectDeleted();
    } catch (err) {
      setError(getErrorMessage(err, "Failed to delete project."));
    }
  };

  if (loading) return (
    <div className="center-loader"><Loader2 size={36} className="spin" /><p>Loading project...</p></div>
  );
  if (error) return (
    <div className="center-error"><AlertCircle size={36} /><p>{error}</p><button onClick={onBack}>Back</button></div>
  );
  if (!project) return null;

  return (
    <div className="project-workspace">
      {/* Top nav */}
      <div className="project-nav">
        <button className="back-btn" onClick={onBack}><X size={16} /> Projects</button>
        <div className="project-nav-title">
          <strong>{project.project_name}</strong>
          <ProgressBar value={project.progress} />
          <span>{project.progress}%</span>
        </div>
        <div className="project-nav-stages">
          <button
            className={`stage-tab ${!activeStage ? "active" : ""}`}
            onClick={() => setActiveStage(null)}
          >Overview</button>
          {STAGE_ORDER.map((key) => {
            const stageData = (project.stages || []).find((s) => s.stage === key);
            const status = stageData?.status || "pending";
            const meta = STAGE_META[key];
            const Icon = meta.icon;
            return (
              <button
                key={key}
                className={`stage-tab ${activeStage === key ? "active" : ""} ${status}`}
                onClick={() => setActiveStage(key)}
                title={meta.label}
              >
                <Icon size={14} />
                <span>{meta.label}</span>
                {status === "completed" && <CheckCircle2 size={11} className="tab-done" />}
              </button>
            );
          })}
        </div>
        <button className="delete-btn" onClick={deleteProject} title="Delete project"><Trash2 size={16} /></button>
      </div>

      {/* Content */}
      <div className="project-content">
        {!activeStage
          ? <ProjectOverview project={project} onSelectStage={setActiveStage} />
          : <StageChat
              project={project}
              stage={activeStage}
              onStageCompleted={handleStageCompleted}
            />
        }
      </div>
    </div>
  );
}

/* =========================================================
   NEW PROJECT MODAL
========================================================= */

function NewProjectModal({ onClose, onCreated }) {
  const [form, setForm] = useState({
    project_name: "",
    hackathon_name: "",
    theme: "",
    interests: "",
    skills: "",
    team_info: "",
    constraints: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    if (!form.project_name.trim()) { setError("Project name is required."); return; }
    setError("");
    setLoading(true);
    try {
      const res = await api.post("/projects", form);
      onCreated(res.data);
    } catch (err) {
      setError(getErrorMessage(err, "Failed to create project."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h2>🚀 New Hackathon Project</h2>
          <button className="modal-close" onClick={onClose}><X size={20} /></button>
        </div>
        <form onSubmit={submit} className="modal-form">
          <div className="form-row">
            <div className="form-group required">
              <label>Project Name *</label>
              <input placeholder="e.g. EduHelper AI" value={form.project_name} onChange={set("project_name")} required />
            </div>
            <div className="form-group">
              <label>Hackathon Name</label>
              <input placeholder="e.g. IBM Hackathon 2025" value={form.hackathon_name} onChange={set("hackathon_name")} />
            </div>
          </div>
          <div className="form-group">
            <label>Theme / Problem Area</label>
            <input placeholder="e.g. Education, Healthcare, Sustainability" value={form.theme} onChange={set("theme")} />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Your Interests</label>
              <input placeholder="e.g. AI, web dev, mobile apps" value={form.interests} onChange={set("interests")} />
            </div>
            <div className="form-group">
              <label>Skills</label>
              <input placeholder="e.g. Python, React, ML" value={form.skills} onChange={set("skills")} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Team Info</label>
              <input placeholder="e.g. 3 members — frontend, backend, ML" value={form.team_info} onChange={set("team_info")} />
            </div>
            <div className="form-group">
              <label>Constraints</label>
              <input placeholder="e.g. 24 hours, no cloud, beginner team" value={form.constraints} onChange={set("constraints")} />
            </div>
          </div>
          {error && <div className="error-box"><AlertCircle size={15} /> {error}</div>}
          <div className="modal-actions">
            <button type="button" className="secondary-button" onClick={onClose}>Cancel</button>
            <button type="submit" className="primary-button" disabled={loading}>
              {loading ? <><Loader2 size={15} className="spin" /> Creating...</> : <>Create Project <ArrowRight size={16} /></>}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

/* =========================================================
   PROJECTS LIST
========================================================= */

function ProjectsList({ onOpenProject, onCreateNew }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/projects")
      .then((res) => { setProjects(res.data); setLoading(false); })
      .catch((err) => { setError(getErrorMessage(err, "Failed to load projects.")); setLoading(false); });
  }, []);

  if (loading) return (
    <div className="center-loader"><Loader2 size={32} className="spin" /><p>Loading projects...</p></div>
  );

  return (
    <div className="projects-page">
      <div className="projects-header">
        <div>
          <span className="eyebrow">MY PROJECTS</span>
          <h1>Hackathon Projects</h1>
          <p>Start a new project or continue where you left off.</p>
        </div>
        <button className="primary-button" onClick={onCreateNew}>
          <Plus size={18} /> New Project
        </button>
      </div>

      {error && <div className="error-box"><AlertCircle size={15} /> {error}</div>}

      {projects.length === 0 ? (
        <div className="empty-projects">
          <Rocket size={52} />
          <h2>No projects yet</h2>
          <p>Create your first hackathon project and let AI guide you from idea to submission.</p>
          <button className="primary-button" onClick={onCreateNew}>
            <Plus size={18} /> Create Your First Project
          </button>
        </div>
      ) : (
        <div className="project-cards">
          {projects.map((p) => (
            <div key={p.id} className="project-card" onClick={() => onOpenProject(p.id)}>
              <div className="project-card-header">
                <div>
                  <h3>{p.project_name}</h3>
                  {p.hackathon_name && <span className="project-hack">{p.hackathon_name}</span>}
                </div>
                <ChevronRight size={20} className="project-arrow" />
              </div>
              <ProgressBar value={p.progress} />
              <div className="project-card-footer">
                <span className="stage-chip">
                  {STAGE_META[p.current_stage]?.label || p.current_stage_label}
                </span>
                <span className="project-pct">{p.progress}% complete</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* =========================================================
   DASHBOARD (landing after login)
========================================================= */

function DashboardHome({ onNavigate, username }) {
  const [recentProjects, setRecentProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(true);

  useEffect(() => {
    api.get("/projects")
      .then((res) => { setRecentProjects(res.data.slice(0, 3)); setLoadingProjects(false); })
      .catch(() => setLoadingProjects(false));
  }, []);

  const agentCards = [
    { stage: "problem_discovery",  emoji: "🎯", short: "Problem Discovery" },
    { stage: "problem_validation", emoji: "✅", short: "Validation" },
    { stage: "solution_ideation",  emoji: "💡", short: "Ideation" },
    { stage: "product_planning",   emoji: "📋", short: "Planning" },
    { stage: "technical_architecture", emoji: "🏗️", short: "Architecture" },
    { stage: "development",        emoji: "⚡", short: "Development" },
    { stage: "testing",            emoji: "🧪", short: "Testing & QA" },
    { stage: "responsible_ai",     emoji: "🛡️", short: "Responsible AI" },
    { stage: "documentation",      emoji: "📖", short: "Documentation" },
    { stage: "pitch_submission",   emoji: "🚀", short: "Pitch & Submit" },
  ];

  return (
    <div className="dashboard-home">
      {/* Hero */}
      <section className="hero">
        <div>
          <span className="eyebrow">YOUR HACKATHON JOURNEY</span>
          <h1>Welcome back, {username}! 👋</h1>
          <p>Your multi-agent AI copilot from problem statement to final submission.</p>
          <button className="primary-button" onClick={() => onNavigate("projects")}>
            {recentProjects.length > 0 ? "Continue a Project" : "Start a New Project"} <ArrowRight size={18} />
          </button>
        </div>
        <div className="mode-pill"><span></span> 10 AI Agents Online</div>
      </section>

      {/* Recent Projects */}
      {!loadingProjects && recentProjects.length > 0 && (
        <section className="dashboard-section">
          <div className="section-heading">
            <h2>Recent Projects</h2>
            <button className="link-btn" onClick={() => onNavigate("projects")}>View all →</button>
          </div>
          <div className="project-cards compact">
            {recentProjects.map((p) => (
              <div key={p.id} className="project-card" onClick={() => onNavigate("project", p.id)}>
                <div className="project-card-header">
                  <div>
                    <h3>{p.project_name}</h3>
                    {p.hackathon_name && <span className="project-hack">{p.hackathon_name}</span>}
                  </div>
                  <ChevronRight size={18} />
                </div>
                <ProgressBar value={p.progress} />
                <div className="project-card-footer">
                  <span className="stage-chip">{STAGE_META[p.current_stage]?.label || p.current_stage}</span>
                  <span className="project-pct">{p.progress}%</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Agents overview */}
      <section className="dashboard-section">
        <div className="section-heading">
          <h2>Your 10 AI Agents</h2>
          <span className="section-sub">Specialized agents for every stage of your hackathon</span>
        </div>
        <div className="agent-grid">
          {agentCards.map((a) => {
            const meta = STAGE_META[a.stage];
            const Icon = meta.icon;
            return (
              <div key={a.stage} className="agent-card">
                <div className="agent-card-icon" style={{ background: meta.color + "22", color: meta.color }}>
                  <Icon size={20} />
                </div>
                <span>{a.short}</span>
              </div>
            );
          })}
        </div>
      </section>

      {/* How it works */}
      <section className="dashboard-section">
        <h2>How It Works</h2>
        <div className="how-steps">
          {[
            ["1", "Create Project", "Enter your hackathon details, interests and team info."],
            ["2", "Work Through Stages", "Each stage has a specialized AI agent to guide you."],
            ["3", "Build & Ship", "Go from idea to demo-ready submission with AI at every step."],
          ].map(([n, t, d]) => (
            <div key={n} className="how-step">
              <div className="how-number">{n}</div>
              <h4>{t}</h4>
              <p>{d}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

/* =========================================================
   SIDEBAR NAV
========================================================= */

function Sidebar({ active, onNavigate, logout, username }) {
  const nav = [
    ["dashboard", "Dashboard",     LayoutDashboard],
    ["projects",  "My Projects",   Rocket],
  ];

  return (
    <aside className="sidebar">
      <Brand />
      <nav className="sidebar-nav">
        {nav.map(([key, label, Icon]) => (
          <button key={key} className={active === key ? "active" : ""}
            onClick={() => onNavigate(key)}>
            <Icon size={20} />
            <span>{label}</span>
          </button>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <div className="online"><span></span> 10 AI Agents Online</div>
        <div className="user-box">
          <div className="avatar">{username?.[0]?.toUpperCase() || "U"}</div>
          <div className="user-info">
            <strong>{username}</strong>
            <small>Hackathon Participant</small>
          </div>
          <button className="logout-button" onClick={logout} title="Logout">
            <LogOut size={17} />
          </button>
        </div>
      </div>
    </aside>
  );
}

/* =========================================================
   MAIN APP SHELL
========================================================= */

function AppShell({ logout, username }) {
  const [view, setView] = useState("dashboard"); // dashboard | projects | project
  const [activeProjectId, setActiveProjectId] = useState(null);
  const [showNewProjectModal, setShowNewProjectModal] = useState(false);

  const navigate = (page, projectId = null) => {
    if (page === "project" && projectId) {
      setActiveProjectId(projectId);
      setView("project");
    } else {
      setView(page);
      setActiveProjectId(null);
    }
  };

  const handleProjectCreated = (project) => {
    setShowNewProjectModal(false);
    navigate("project", project.id);
  };

  const renderContent = () => {
    if (view === "project" && activeProjectId) {
      return (
        <ProjectWorkspace
          projectId={activeProjectId}
          onBack={() => navigate("projects")}
          onProjectDeleted={() => navigate("projects")}
        />
      );
    }
    if (view === "projects") {
      return (
        <ProjectsList
          onOpenProject={(id) => navigate("project", id)}
          onCreateNew={() => setShowNewProjectModal(true)}
        />
      );
    }
    // dashboard
    return <DashboardHome onNavigate={navigate} username={username} />;
  };

  return (
    <div className="app-shell">
      {view !== "project" && (
        <Sidebar
          active={view}
          onNavigate={navigate}
          logout={logout}
          username={username}
        />
      )}
      <main className={`main-content ${view === "project" ? "full-width" : ""}`}>
        {renderContent()}
      </main>
      {showNewProjectModal && (
        <NewProjectModal
          onClose={() => setShowNewProjectModal(false)}
          onCreated={handleProjectCreated}
        />
      )}
    </div>
  );
}

/* =========================================================
   ROOT APP
========================================================= */

export default function App() {
  const [authenticated, setAuthenticated] = useState(!!localStorage.getItem("token"));
  const [registerPage, setRegisterPage] = useState(false);
  const [username, setUsername] = useState(localStorage.getItem("username") || "Student");

  useEffect(() => { document.title = "HackMate AI"; }, []);

  const handleLogin = () => {
    setAuthenticated(true);
    setUsername(localStorage.getItem("username") || "Student");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    setAuthenticated(false);
  };

  if (!authenticated) {
    if (registerPage) {
      return <Register goLogin={() => setRegisterPage(false)} />;
    }
    return (
      <Login
        onLogin={handleLogin}
        goRegister={() => setRegisterPage(true)}
      />
    );
  }

  return <AppShell logout={handleLogout} username={username} />;
}
