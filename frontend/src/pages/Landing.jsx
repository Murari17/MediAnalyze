import React from "react";
import { Link } from "react-router-dom";
import Button from "../components/Button";

const features = [
  {
    title: "Document analysis",
    description:
      "Summarize clinical narratives and regulatory reports with structured insights."
  },
  {
    title: "Anonymization",
    description:
      "Protect PHI/PII while preserving medical context and traceability."
  },
  {
    title: "Validation",
    description: "Detect missing or inconsistent fields before submission."
  },
  {
    title: "Decision support",
    description:
      "Apply severity and compliance logic to prioritize review."
  }
];

const steps = [
  {
    title: "Upload",
    description: "Provide a document or paste raw text into the analyzer."
  },
  {
    title: "Analyze",
    description:
      "MedIntel AI extracts key fields, anonymizes data, and classifies severity."
  },
  {
    title: "Decide",
    description: "Review the recommendation with evidence and confidence scores."
  }
];

const Landing = () => {
  return (
    <div className="min-h-screen bg-[#f5f5f4] text-[#18181b]">
      <header className="border-b border-[#e7e5e4] bg-[#fafaf9]">
        <div className="mx-auto flex w-full max-w-[1200px] items-center justify-between px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-[#18181b]" />
            <span className="text-base font-semibold tracking-tight">MedIntel AI</span>
          </div>
          <nav className="hidden items-center gap-6 text-sm text-[#52525b] md:flex">
            <a href="#features">Features</a>
            <a href="#how-it-works">How it works</a>
            <a href="#preview">Product</a>
            <a href="#cta">Contact</a>
            <Link to="/dashboard">Dashboard</Link>
          </nav>
          <div className="flex items-center gap-3">
            <Link to="/analyze">
              <Button size="sm">Try Demo</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-[1200px] space-y-20 px-6 py-20">
        <section className="text-center">
          <div className="mx-auto max-w-3xl space-y-6">
            <p className="text-xs font-semibold uppercase tracking-[0.4em] text-slate-400">
              Regulatory intelligence
            </p>
            <h1 className="text-4xl font-semibold tracking-tight text-[#18181b] md:text-5xl">
              AI-powered regulatory document intelligence for clinical operations
            </h1>
            <p className="text-lg text-[#52525b]">
              MedIntel AI converts medical and regulatory submissions into verified,
              anonymized, and decision-ready outputs for compliance teams.
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              <Link to="/analyze">
                <Button size="lg">Try Demo</Button>
              </Link>
              <Link to="/dashboard">
                <Button size="lg" variant="secondary">
                  View Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </section>

        <section className="grid gap-10 lg:grid-cols-2">
          <div className="space-y-4">
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">
              The problem
            </p>
            <h2 className="text-2xl font-semibold tracking-tight text-[#18181b]">
              Regulatory review is slow, manual, and inconsistent.
            </h2>
            <p className="text-sm text-[#52525b]">
              Compliance teams spend hours extracting fields, checking for missing data,
              and assessing severity. Critical signals can be missed, and timelines slip.
            </p>
          </div>
          <div className="space-y-4">
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">
              The solution
            </p>
            <h2 className="text-2xl font-semibold tracking-tight text-[#18181b]">
              A unified regulatory intelligence layer for clinical documents.
            </h2>
            <p className="text-sm text-[#52525b]">
              MedIntel AI summarizes, anonymizes, validates, and classifies each case
              with clear recommendations and traceable evidence.
            </p>
          </div>
        </section>

        <section id="features" className="space-y-8">
          <div className="space-y-2 text-center">
            <h3 className="text-2xl font-semibold tracking-tight text-[#18181b]">
              Core capabilities
            </h3>
            <p className="text-sm text-[#52525b]">
              Everything needed to process regulatory documents with confidence.
            </p>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="rounded-xl border border-[#e7e5e4] bg-white p-6 shadow-sm"
              >
                <h4 className="text-base font-semibold text-[#18181b]">
                  {feature.title}
                </h4>
                <p className="mt-2 text-sm text-[#52525b]">{feature.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="how-it-works" className="space-y-8">
          <div className="space-y-2 text-center">
            <h3 className="text-2xl font-semibold tracking-tight text-[#18181b]">
              How it works
            </h3>
            <p className="text-sm text-[#52525b]">
              A guided workflow from intake to decision support.
            </p>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            {steps.map((step, index) => (
              <div
                key={step.title}
                className="rounded-xl border border-[#e7e5e4] bg-white p-6"
              >
                <p className="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">
                  Step {index + 1}
                </p>
                <p className="mt-3 text-sm font-semibold text-[#18181b]">{step.title}</p>
                <p className="text-sm text-[#52525b]">{step.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="preview" className="space-y-8">
          <div className="space-y-2 text-center">
            <h3 className="text-2xl font-semibold tracking-tight text-[#18181b]">
              Product preview
            </h3>
            <p className="text-sm text-[#52525b]">
              A focused workspace built for regulated medical review.
            </p>
          </div>
          <div className="rounded-2xl border border-[#e7e5e4] bg-white p-6 shadow-sm">
            <div className="rounded-xl border border-[#e7e5e4] bg-[#fafaf9] p-10 text-center text-sm text-[#52525b]">
              Dashboard preview placeholder
            </div>
          </div>
        </section>

        <section id="cta" className="rounded-2xl border border-[#e7e5e4] bg-white p-8 shadow-sm">
          <div className="flex flex-col items-center gap-4 text-center">
            <h3 className="text-2xl font-semibold tracking-tight text-[#18181b]">
              Ready to modernize regulatory review?
            </h3>
            <p className="text-sm text-[#52525b]">
              Start with a demo analysis and see how MedIntel AI streamlines compliance workflows.
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              <Link to="/analyze">
                <Button size="lg">Try Demo</Button>
              </Link>
              <Link to="/dashboard">
                <Button size="lg" variant="secondary">
                  View Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-[#e7e5e4] bg-[#fafaf9]">
        <div className="mx-auto flex w-full max-w-[1200px] flex-col gap-2 px-6 py-8 text-xs text-[#52525b] md:flex-row md:items-center md:justify-between">
          <span>MedIntel AI – Autonomous Regulatory Intelligence System</span>
          <span>AI-powered regulatory intelligence</span>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
