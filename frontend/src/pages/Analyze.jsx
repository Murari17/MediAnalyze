import React, { useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Calendar,
  ClipboardCopy,
  FileText,
  Pill,
  ShieldCheck,
  Sparkles,
  SplitSquareHorizontal,
  Stethoscope,
  User,
  Eye,
  EyeOff,
  CheckCircle2,
  XCircle
} from "lucide-react";
import Badge from "../components/Badge";
import Button from "../components/Button";
import Card from "../components/Card";
import Loader from "../components/Loader";
import TextAreaField from "../components/TextAreaField";
import { analyzeText } from "../services/api";

const SEVERITY_VARIANT = {
  LOW: "success",
  HIGH: "warning",
  CRITICAL: "danger"
};

const DECISION_VARIANT = {
  SAFE: "success",
  "REQUIRES REVIEW": "danger",
  "INCOMPLETE SUBMISSION": "warning",
  "URGENT ATTENTION": "danger"
};

const FIELD_META = {
  patient_name: { label: "Patient name", icon: User },
  age: { label: "Age", icon: Calendar },
  drug_name: { label: "Medications", icon: Pill },
  adverse_event: { label: "Adverse event", icon: AlertTriangle }
};

const formatConfidence = (value) => {
  if (value === undefined || value === null || Number.isNaN(value)) return "0.00";
  return Number(value).toFixed(2);
};

const formatFieldValue = (value) => {
  const raw = value?.value ?? value;
  if (Array.isArray(raw)) return raw.join(", ");
  return raw || "—";
};

  const highlightTokens = (text) => {
    if (!text) return null;
    const parts = text.split(/(\b[A-Z]+_\d+\b)/g);
    return parts.map((part, idx) => {
      if (part.match(/\b[A-Z]+_\d+\b/)) {
        const classes =
          "rounded px-1.5 py-0.5 font-medium text-slate-200 bg-slate-500/20";
        return (
          <span key={idx} className={classes} title="Original value hidden for privacy">
            {part}
        </span>
      );
    }
    return <span key={idx}>{part}</span>;
  });
};

const DecisionReason = ({ reason }) => {
  if (!reason) {
    return (
      <ul className="list-disc space-y-1 pl-5 text-sm text-[#52525b] dark:text-slate-300">
        <li>Decision reasoning pending.</li>
      </ul>
    );
  }
  const parts = reason.split(":");
  const text = parts.length > 1 ? parts.slice(1).join(":").trim() : reason;
  const bullets = text
    .replace(/\.$/, "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  return (
    <ul className="list-disc space-y-1 pl-5 text-sm text-[#52525b] dark:text-slate-300">
      {bullets.length
        ? bullets.map((item, idx) => <li key={idx}>{item}</li>)
        : [<li key="single">{text}</li>]}
    </ul>
  );
};

const Analyze = () => {
  const [textA, setTextA] = useState("");
  const [textB, setTextB] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [expandedSummary, setExpandedSummary] = useState(false);
  const [showComparison, setShowComparison] = useState(true);

  const handleAnalyze = async () => {
    setError("");
    setResult(null);
    if (!textA.trim()) {
      setError("Please add Document A before analyzing.");
      return;
    }

    const payload = { text_a: textA.trim() };
    if (textB.trim()) payload.text_b = textB.trim();

    try {
      setLoading(true);
      const data = await analyzeText(payload);
      setResult(data);
      setShowComparison(true);
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        (err?.code === "ECONNABORTED"
          ? "The analysis took too long. Please retry in a moment."
          : "We could not analyze the document. Please try again.");
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const decisionVariant = useMemo(() => {
    const decision = result?.decision?.decision;
    return DECISION_VARIANT[decision] || "info";
  }, [result]);

  const severityVariant = useMemo(() => {
    const severity = result?.classification?.severity;
    return SEVERITY_VARIANT[severity] || "info";
  }, [result]);

  const decisionAccent =
    decisionVariant === "danger"
      ? "border-l-[#dc2626]"
      : decisionVariant === "warning"
      ? "border-l-[#d97706]"
      : decisionVariant === "success"
      ? "border-l-[#16a34a]"
      : "border-l-slate-400";

  const summaryText = result?.summary?.summary || "";
  const summaryPreview =
    summaryText.length > 420 && !expandedSummary
      ? `${summaryText.slice(0, 420)}...`
      : summaryText;

  const comparisonLabel =
    result?.comparison?.similarity_score && result.comparison.similarity_score >= 0.7
      ? "Improvement detected"
      : result?.comparison
      ? "Worsening detected"
      : "No comparison";
  const comparisonVariant = !result?.comparison
    ? "neutral"
    : comparisonLabel === "Improvement detected"
    ? "success"
    : "warning";

  const highlightChanges = (text, bestMatch) => {
    if (!text) return null;
    const compare = (bestMatch || "").toLowerCase();
    const words = text.split(/\s+/g);
    return words.map((word, idx) => {
      const normalized = word.replace(/[^\w]/g, "").toLowerCase();
      const isChanged = normalized && !compare.includes(normalized);
      return (
        <span key={idx} className={isChanged ? "rounded bg-[#f5f5f4] px-1" : ""}>
          {word}{" "}
        </span>
      );
    });
  };

  const detectedFields = result?.validation?.detected_fields || {};
  const lowConfidenceFields = result?.validation?.low_confidence_fields || {};
  const missingFields = result?.validation?.missing_fields || [];

  const handleCopy = async () => {
    if (!result?.anonymized_text?.anonymized_text) return;
    await navigator.clipboard.writeText(result.anonymized_text.anonymized_text);
  };

  const hasComparison = Boolean(result?.comparison);

  return (
    <div className="space-y-6">
      <Card
        title="Input"
        icon={<FileText className="h-4 w-4" />}
        badge="Analysis"
        badgeVariant="info"
        className="col-span-12"
      >
        <div className="grid gap-6 lg:grid-cols-2">
          <TextAreaField
            label="Document A"
            value={textA}
            onChange={setTextA}
            placeholder="Paste the primary document text here..."
            minRows={8}
          />
          <TextAreaField
            label="Document B (optional)"
            value={textB}
            onChange={setTextB}
            placeholder="Paste a comparison document here..."
            minRows={8}
          />
        </div>
        <div className="flex flex-wrap items-center gap-4 pt-4">
          <Button onClick={handleAnalyze} disabled={loading}>
            {loading ? "Analyzing..." : "Analyze"}
          </Button>
          {error ? (
            <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-600">
              {error}
            </p>
          ) : null}
        </div>
      </Card>

      {loading && <Loader />}

      {result && (
        <div className="space-y-6">
          <Card
            title="Decision"
            icon={<ShieldCheck className="h-4 w-4" />}
            badge={result.decision?.decision || "PENDING"}
            badgeVariant={decisionVariant}
            tone={decisionVariant}
            className={`border-l-4 ${decisionAccent}`}
          >
            <div className="flex flex-col gap-3">
              <p className="text-3xl font-semibold tracking-tight text-[#18181b] dark:text-white">
                {result.decision?.decision || "PENDING"}
              </p>
              <DecisionReason reason={result.decision?.reason} />
              <Badge
                label={`Confidence ${formatConfidence(result.decision?.confidence)}`}
                variant="info"
                className="w-fit"
              />
            </div>
          </Card>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-6">
              <Card
                title="Summary"
                icon={<Sparkles className="h-4 w-4" />}
                badge={`${formatConfidence(result.summary?.confidence)} conf`}
                badgeVariant="info"
              >
                <p className="leading-relaxed text-[#52525b] dark:text-slate-200">
                  {summaryPreview || "No summary available."}
                </p>
                {summaryText.length > 420 ? (
                  <button
                    className="inline-flex items-center gap-1 text-sm font-medium text-[#18181b]"
                    onClick={() => setExpandedSummary((prev) => !prev)}
                    type="button"
                  >
                    {expandedSummary ? "Show less" : "Read more"}
                  </button>
                ) : null}
              </Card>

              <Card
                title="Validation"
                icon={<Stethoscope className="h-4 w-4" />}
                badge={
                  missingFields.length
                    ? `${missingFields.length} missing`
                    : "All fields"
                }
                badgeVariant={missingFields.length ? "danger" : "success"}
              >
                <div className="grid gap-6 md:grid-cols-2">
                  <div>
                    <div className="flex items-center gap-2 text-sm font-semibold text-[#16a34a]">
                      <CheckCircle2 className="h-4 w-4" />
                      Detected
                    </div>
                    <div className="mt-3 space-y-2 text-sm text-[#52525b] dark:text-slate-200">
                      {Object.keys(detectedFields).length ? (
                        Object.entries(detectedFields).map(([key, value]) => {
                          const meta = FIELD_META[key] || { label: key };
                          const Icon = meta.icon;
                          return (
                            <div
                              key={key}
                              className="flex items-center justify-between rounded-lg px-2 py-1"
                            >
                              <div className="flex items-center gap-2">
                                {Icon ? <Icon className="h-4 w-4 text-slate-400" /> : null}
                                <span>{meta.label}</span>
                              </div>
                              <span className="text-xs text-slate-500">
                                {formatFieldValue(value)}
                              </span>
                            </div>
                          );
                        })
                      ) : (
                        <p className="text-sm text-slate-500">None detected.</p>
                      )}
                    </div>
                  </div>
                  <div className="border-t border-slate-200 pt-4 dark:border-slate-800 md:border-l md:border-t-0 md:pl-4 md:pt-0">
                    <div className="flex items-center gap-2 text-sm font-semibold text-[#dc2626]">
                      <XCircle className="h-4 w-4" />
                      Missing
                    </div>
                    <div className="mt-3 space-y-2 text-sm text-[#52525b] dark:text-slate-200">
                      {missingFields.length ? (
                        missingFields.map((field) => {
                          const meta = FIELD_META[field] || { label: field };
                          const Icon = meta.icon;
                          return (
                            <div key={field} className="flex items-center gap-2 rounded-lg px-2 py-1">
                              {Icon ? <Icon className="h-4 w-4 text-red-400" /> : null}
                              {meta.label}
                            </div>
                          );
                        })
                      ) : (
                        <p className="text-sm text-slate-500">None</p>
                      )}
                    </div>
                  </div>
                </div>
                {Object.keys(lowConfidenceFields).length ? (
                  <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50/60 p-4 text-sm text-amber-800">
                    <div className="flex items-center gap-2 font-semibold">
                      <AlertTriangle className="h-4 w-4" />
                      Low confidence
                    </div>
                    <div className="mt-2 space-y-2">
                      {Object.entries(lowConfidenceFields).map(([key, value]) => {
                        const meta = FIELD_META[key] || { label: key };
                        const Icon = meta.icon;
                        return (
                          <div
                            key={key}
                            className="flex items-center justify-between rounded-lg px-2 py-1"
                            title="Detected from unstructured text"
                          >
                            <div className="flex items-center gap-2">
                              {Icon ? <Icon className="h-4 w-4 text-amber-600" /> : null}
                              <span>{meta.label}</span>
                            </div>
                            <span className="text-xs text-amber-700">
                              {formatFieldValue(value)}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : null}
              </Card>
            </div>

            <div className="space-y-6">
              <Card
                title="Classification"
                icon={<Activity className="h-4 w-4" />}
                badge={result.classification?.severity || "UNKNOWN"}
                badgeVariant={severityVariant}
              >
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                  Risk level
                </p>
                <div className="h-2 w-full rounded-full bg-slate-100 dark:bg-slate-700">
                  <div
                    className={`h-2 rounded-full ${
                      severityVariant === "danger"
                        ? "bg-[#dc2626]"
                        : severityVariant === "warning"
                        ? "bg-[#d97706]"
                        : "bg-[#16a34a]"
                    }`}
                    style={{ width: "68%" }}
                  />
                </div>
                <p className="text-sm font-semibold text-[#18181b] dark:text-slate-200">
                  Category: {result.classification?.category}
                </p>
                <Badge
                  label={`Confidence ${formatConfidence(result.classification?.confidence)}`}
                  variant="info"
                  className="w-fit"
                />
                <p className="text-sm text-[#52525b] dark:text-slate-300">
                  {result.classification?.explanation}
                </p>
              </Card>

              <Card
                title="Anonymized Text"
                icon={<ShieldCheck className="h-4 w-4" />}
                actions={
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={handleCopy}
                    disabled={!result.anonymized_text?.anonymized_text}
                  >
                    <ClipboardCopy className="h-3.5 w-3.5" />
                    Copy
                  </Button>
                }
              >
                <div className="mt-1 max-h-64 overflow-y-auto rounded-lg bg-[#0b1220] p-4 font-mono text-xs text-[#e4e4e7]">
                  {highlightTokens(result.anonymized_text?.anonymized_text || "")}
                </div>
              </Card>
            </div>
          </div>

          <Card
            title="Comparison"
            icon={<SplitSquareHorizontal className="h-4 w-4" />}
            badge={comparisonLabel}
            badgeVariant={comparisonVariant}
            actions={
              <Button
                variant="ghost"
                size="sm"
                disabled={!hasComparison}
                onClick={() => setShowComparison((prev) => !prev)}
              >
                {showComparison ? (
                  <EyeOff className="h-3.5 w-3.5" />
                ) : (
                  <Eye className="h-3.5 w-3.5" />
                )}
                {showComparison ? "Hide" : "Show"}
              </Button>
            }
          >
            {hasComparison && showComparison ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm text-[#52525b]">
                  <span>
                    Patient condition {comparisonLabel === "Improvement detected" ? "improving" : "worsening"}.
                  </span>
                  <span>{formatConfidence(result.comparison.similarity_score)} similarity</span>
                </div>
                <div className="grid gap-6 md:grid-cols-2">
                  <div className="rounded-lg border border-[#e7e5e4] p-4">
                    <p className="text-xs font-semibold text-[#18181b]">Side A</p>
                    <div className="mt-3 space-y-3 text-sm text-[#52525b]">
                      {(result.comparison.changed_sections || [])
                        .filter((item) => item.side === "a")
                        .map((item, idx) => (
                          <div key={`a-${idx}`} className="rounded bg-[#fafaf9] p-2">
                            {highlightChanges(item.text, item.best_match)}
                          </div>
                        ))}
                    </div>
                  </div>
                  <div className="rounded-lg border border-[#e7e5e4] p-4">
                    <p className="text-xs font-semibold text-[#18181b]">Side B</p>
                    <div className="mt-3 space-y-3 text-sm text-[#52525b]">
                      {(result.comparison.changed_sections || [])
                        .filter((item) => item.side === "b")
                        .map((item, idx) => (
                          <div key={`b-${idx}`} className="rounded bg-[#fafaf9] p-2">
                            {highlightChanges(item.text, item.best_match)}
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-[#52525b]">
                {hasComparison ? "Comparison hidden." : "No comparison provided."}
              </p>
            )}
          </Card>
        </div>
      )}
    </div>
  );
};

export default Analyze;
