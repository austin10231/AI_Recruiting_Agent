import { useMemo, useState } from "react";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const PIPELINE_ENDPOINT = import.meta.env.VITE_PIPELINE_ENDPOINT || "/api/run-pipeline";

const initialForm = {
  job_description:
    "We are hiring an AI Engineer to build LLM-powered features using Python and ship fast in a startup environment.",
  hiring_manager_notes:
    "Strong ownership and product sense preferred. Seniority can be flexible."
};

function DataTag({ label, value }) {
  return (
    <div className="h-full rounded-xl border border-ink/10 bg-white/90 p-3 shadow-soft">
      <p className="text-[11px] uppercase tracking-[0.16em] text-ink/55">{label}</p>
      <p className="mt-1 break-words text-sm text-ink/90">{value || "-"}</p>
    </div>
  );
}

function ChipBlock({ title, items }) {
  return (
    <section className="rounded-2xl border border-ink/10 bg-paper/85 p-4 shadow-soft">
      <h4 className="font-body text-xs uppercase tracking-[0.18em] text-ink/55">{title}</h4>
      {items?.length ? (
        <ul className="mt-3 flex flex-wrap gap-2 text-sm text-ink/90">
          {items.map((item) => (
            <li
              key={item}
              className="rounded-full border border-ink/15 bg-white/90 px-3 py-1.5 text-xs tracking-wide"
            >
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-ink/55">No data yet.</p>
      )}
    </section>
  );
}

export default function App() {
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [showTrace, setShowTrace] = useState(false);
  const [showFullQuery, setShowFullQuery] = useState(false);

  const canSubmit = useMemo(() => form.job_description.trim().length > 0, [form.job_description]);

  const onChange = (field) => (event) => {
    setForm((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const runPipeline = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}${PIPELINE_ENDPOINT}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(form)
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.detail || "Pipeline request failed.");
      }

      setResult(payload);
      setShowFullQuery(false);
      setShowTrace(false);
    } catch (err) {
      setError(err.message || "Unexpected network error.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-fog font-body text-ink">
      <div className="backdrop" />
      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
        <header className="animate-reveal rounded-3xl border border-ink/10 bg-paper/95 p-7 shadow-card">
          <p className="text-xs uppercase tracking-[0.24em] text-moss">Recruiting Copilot</p>
          <h1 className="mt-3 font-title text-3xl leading-tight text-ink sm:text-4xl">
            Structured Hiring Workflow, Built for Real Recruiters
          </h1>
          <p className="mt-4 max-w-3xl text-sm leading-relaxed text-ink/70 sm:text-base">
            Submit a job description and receive a complete recruiting pipeline output: strategy,
            Boolean query, outreach, summary, and step-by-step trace.
          </p>
        </header>

        <section className="mt-6 grid gap-5 lg:grid-cols-[1.05fr_1fr]">
          <article
            className="animate-reveal rounded-3xl border border-ink/10 bg-paper/90 p-6 shadow-card"
            style={{ animationDelay: "80ms" }}
          >
            <h2 className="font-title text-2xl text-ink">Job Details</h2>

            <label className="mt-5 block text-xs uppercase tracking-[0.16em] text-ink/60">Job Description (JD)</label>
            <textarea
              value={form.job_description}
              onChange={onChange("job_description")}
              className="mt-2 min-h-[200px] w-full resize-y rounded-2xl border border-ink/15 bg-white/90 px-4 py-3 text-sm text-ink shadow-soft outline-none transition focus:border-moss"
              placeholder="Paste job description..."
            />

            <label className="mt-5 block text-xs uppercase tracking-[0.16em] text-ink/60">
              Manager Notes (Optional)
            </label>
            <textarea
              value={form.hiring_manager_notes}
              onChange={onChange("hiring_manager_notes")}
              className="mt-2 min-h-[120px] w-full resize-y rounded-2xl border border-ink/15 bg-white/90 px-4 py-3 text-sm text-ink shadow-soft outline-none transition focus:border-moss"
              placeholder="Add manager notes..."
            />

            <div className="mt-6 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={runPipeline}
                disabled={!canSubmit || loading}
                className="rounded-full bg-ink px-6 py-2.5 text-sm font-medium text-white transition hover:bg-ink/90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Running pipeline..." : "Run Pipeline"}
              </button>

              <button
                type="button"
                onClick={() => setForm(initialForm)}
                className="rounded-full border border-ink/20 bg-white/85 px-5 py-2.5 text-sm text-ink transition hover:bg-white"
              >
                Reset
              </button>
            </div>

            {error && (
              <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}
          </article>

          <article
            className="animate-reveal rounded-3xl border border-ink/10 bg-paper/90 p-6 shadow-card"
            style={{ animationDelay: "140ms" }}
          >
            <h2 className="font-title text-2xl text-ink">Results</h2>
            {!result ? (
              <p className="mt-5 rounded-2xl border border-dashed border-ink/25 bg-white/80 p-6 text-sm text-ink/60">
                No output yet. Run the pipeline to render strategy, query, outreach, summary, and trace.
              </p>
            ) : (
              <div className="mt-5 grid gap-3">
                <div className="grid gap-3 md:grid-cols-2 md:items-stretch">
                  <div className="h-full rounded-xl border border-ink/10 bg-white/90 p-3 shadow-soft">
                    <p className="text-[11px] uppercase tracking-[0.16em] text-ink/55">Search Query</p>
                    {(() => {
                      const queryText = result?.boolean_query?.boolean_query || "-";
                      const hasRealQuery = queryText !== "-";
                      return (
                        <>
                    <div
                      className={`mt-1 break-words text-sm text-ink/90 ${
                        showFullQuery ? "max-h-72 overflow-y-auto pr-1" : "max-h-24 overflow-hidden"
                      }`}
                    >
                          {queryText}
                    </div>
                          {hasRealQuery && (
                            <button
                              type="button"
                              onClick={() => setShowFullQuery((prev) => !prev)}
                              className="mt-2 text-xs text-moss underline-offset-2 hover:underline"
                            >
                              {showFullQuery ? "Show less" : "Show full query"}
                            </button>
                          )}
                        </>
                      );
                    })()}
                  </div>
                  <DataTag label="Message Draft" value={result?.outreach_message?.outreach_message} />
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <DataTag label="JD Detail Used" value={result?.outreach_message?.specific_detail} />
                  <DataTag label="Message Length" value={String(result?.outreach_message?.character_count ?? "-")} />
                  <DataTag label="Candidate Name" value={result?.candidate_summary?.name} />
                  <DataTag label="Current Company" value={result?.candidate_summary?.current_company} />
                </div>
              </div>
            )}
          </article>
        </section>

        <section className="mt-5 grid gap-4 lg:grid-cols-2">
          <div className="animate-reveal" style={{ animationDelay: "180ms" }}>
            <ChipBlock
              title="Ideal Backgrounds"
              items={result?.candidate_search_strategy?.target_backgrounds || []}
            />
          </div>
          <div className="animate-reveal" style={{ animationDelay: "210ms" }}>
            <ChipBlock
              title="Ideal Companies"
              items={result?.candidate_search_strategy?.target_companies || []}
            />
          </div>
          <div className="animate-reveal" style={{ animationDelay: "240ms" }}>
            <ChipBlock title="Key Terms" items={result?.candidate_search_strategy?.keywords || []} />
          </div>
          <div className="animate-reveal" style={{ animationDelay: "270ms" }}>
            <ChipBlock
              title="Skills to Look For"
              items={result?.candidate_summary?.key_skills || []}
            />
          </div>
        </section>

        <section
          className="mt-5 animate-reveal rounded-3xl border border-ink/10 bg-paper/90 p-6 shadow-card"
          style={{ animationDelay: "310ms" }}
        >
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h3 className="font-title text-2xl text-ink">Run Log</h3>
            <button
              type="button"
              onClick={() => setShowTrace((prev) => !prev)}
              className="rounded-full border border-ink/20 bg-white/85 px-4 py-1.5 text-xs tracking-wide text-ink transition hover:bg-white"
            >
              {showTrace ? "Hide Run Log" : "Show Run Log"}
            </button>
          </div>

          {showTrace ? (
            !result?.pipeline_trace?.length ? (
              <p className="mt-4 text-sm text-ink/60">Trace will appear after execution.</p>
            ) : (
              <div className="mt-4 grid gap-3">
                {result.pipeline_trace.map((row, index) => (
                  <div
                    key={`${row.step}-${row.attempt}-${index}`}
                    className="grid gap-2 rounded-2xl border border-ink/10 bg-white/85 px-4 py-3 sm:grid-cols-[70px_1fr_auto] sm:items-center"
                  >
                    <div className="text-xs uppercase tracking-[0.16em] text-ink/55">Step {row.step}</div>
                    <div>
                      <p className="text-sm font-medium text-ink">{row.action}</p>
                      <p className="text-xs text-ink/60">{row.note || "-"}</p>
                    </div>
                    <span
                      className={`justify-self-start rounded-full px-3 py-1 text-xs uppercase tracking-wide ${
                        row.result === "pass"
                          ? "bg-emerald-100 text-emerald-700"
                          : row.result === "retry"
                            ? "bg-amber-100 text-amber-700"
                            : "bg-red-100 text-red-700"
                      }`}
                    >
                      {row.result} · attempt {row.attempt}
                    </span>
                  </div>
                ))}
              </div>
            )
          ) : (
            <p className="mt-4 text-sm text-ink/60">
              Run log is collapsed by default. Expand to inspect step-by-step details.
            </p>
          )}
        </section>
      </main>
    </div>
  );
}
