"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import Footer from "@/components/Footer";
import Zenyth from "@/components/svg/Zenyth";

export default function Home() {
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [language, setLanguage] = useState("english");
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState("");
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState("");

  const [steps, setSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSummary("");
    setTranscript("");
    setError("");
    setSteps([]);
    setCurrentStep("Initializing process...");

    try {
      const apiUrl = '/api';
      const res = await fetch(`${apiUrl}/summarize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ youtube_url: youtubeUrl, language: language }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "An error occurred during the request.");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          setCurrentStep("Process finished!");
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        
        for (let i = 0; i < parts.length - 1; i++) {
          const part = parts[i];
          if (part.startsWith("data: ")) {
            const jsonString = part.substring(6);
            if (jsonString) {
              try {
                const parsedData = JSON.parse(jsonString);
                const { node, data } = parsedData;

                if (data.step_progress) {
                  setSteps(data.step_progress);
                }
                if (data.status_message) {
                  setCurrentStep(data.status_message);
                }
                if (data.summary) {
                  setSummary(data.summary);
                }
                if (data.transcript) {
                  setTranscript(data.transcript);
                }
              } catch (e) {
                console.error("Failed to parse JSON:", jsonString, e);
                setError(`Failed to parse an update from the server. The content was: "${jsonString}"`);
              }
            }
          }
        }
        buffer = parts[parts.length - 1];
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Configuration des composants pour ReactMarkdown
  const markdownComponents = {
    h1: ({ children, ...props }) => (
      <h1 className="text-5xl font-bold my-100 text-secondary" {...props}>
        {children}
      </h1>
    ),
    h2: ({ children, ...props }) => (
      <h2 className="text-4xl font-bold my-8" {...props}>
        {children}
      </h2>
    ),
    h3: ({ children, ...props }) => (
      <h3 className="text-3xl font-bold text-warning my-6" {...props}>
        {children}
      </h3>
    ),
    h4: ({ children, ...props }) => (
      <h4 className="text-2xl font-bold text-warning mt-10" {...props}>
        {children}
      </h4>
    ),
    h5: ({ children, ...props }) => (
      <h5 className="text-xl font-bold my-3" {...props}>
        {children}
      </h5>
    ),
    h6: ({ children, ...props }) => (
      <h6 className="text-lg font-bold my-2" {...props}>
        {children}
      </h6>
    ),
    p: ({ children, ...props }) => (
      <p className="my-4 leading-relaxed" {...props}>
        {children}
      </p>
    ),
    ul: ({ children, ...props }) => (
      <ul className="list-disc pl-6 my-4 mb-10 space-y-1" {...props}>
        {children}
      </ul>
    ),
    ol: ({ children, ...props }) => (
      <ol className="list-decimal pl-6 my-4 mb-10 space-y-1" {...props}>
        {children}
      </ol>
    ),
    li: ({ children, ...props }) => (
      <li className="my-3" {...props}>
        {children}
      </li>
    ),
    blockquote: ({ children, ...props }) => (
      <blockquote className="border-l-4 border-primary pl-4 my-4 italic opacity-80" {...props}>
        {children}
      </blockquote>
    ),
    code: ({ inline, children, ...props }) => (
      inline ? (
        <code className="bg-base-300 px-2 py-1 rounded text-sm font-mono" {...props}>
          {children}
        </code>
      ) : (
        <code className="block bg-base-300 p-4 rounded-lg my-4 font-mono text-sm overflow-x-auto" {...props}>
          {children}
        </code>
      )
    ),
    pre: ({ children, ...props }) => (
      <pre className="bg-base-300 p-4 rounded-lg my-4 overflow-x-auto" {...props}>
        {children}
      </pre>
    ),
    a: ({ href, children, ...props }) => (
      <a href={href} className="text-primary hover:text-primary-focus underline" {...props}>
        {children}
      </a>
    ),
    strong: ({ children, ...props }) => (
      <strong className="font-bold text-warning" {...props}>
        {children}
      </strong>
    ),
    em: ({ children, ...props }) => (
      <em className="italic text-secondary" {...props}>
        {children}
      </em>
    ),
  };

  return (
    <main className="min-h-screen bg-base-200 flex flex-col items-center">
      <div className="navbar bg-base-100 shadow-sm">
        <Zenyth height={70} width={200}/>
      </div>
      {/* Conteneur principal qui grandit pour pousser le footer vers le bas */}
      <div className="flex flex-col items-center w-full min-h-screen py-8">
        <div className="w-full max-w-3xl px-6">
          <form className="flex flex-col gap-4 items-center my-12" onSubmit={handleSubmit}>
            <div className="form-control w-full">
              <label htmlFor="url-input" className="text-warning text-sm pb-1">
                URL
              </label>
              <input
                id="url-input"
                type="text"
                placeholder="Paste a YouTube video URL"
                className="input input-bordered w-full"
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                required
              />
            </div>
            <div className="flex w-full items-end gap-4">
              <div className="flex flex-col">
                <label htmlFor="language-input" className="text-warning text-sm pb-1">
                  Language
                </label>
                <input
                  id="language-input"
                  type="text"
                  placeholder="e.g., english"
                  className="input input-bordered w-full"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                />
              </div>
              <button
                className={`btn btn-primary flex-grow`}
                type="submit"
                disabled={loading}
              >
                Generate Summary
              </button>
            </div>
          </form>
          {error && (
            <div className="alert alert-error mt-4">{error}</div>
          )}
          {(loading || steps.length > 0) && (
            <div className="mt-4 flex flex-col items-center gap-4">
              {loading && <span className="loading loading-spinner loading-lg"></span>} 
              
              {/* Afficher les erreurs en premier */}
              <div className="mt-2 w-full max-w-xl">
                {steps.filter(s => s.status === 'error').map((step, index) => (
                  <div key={`error-${index}`} className="alert alert-error shadow-lg p-2 mt-2">
                    <div className="flex items-center gap-2">
                      <span>❌</span>
                      <span>{step.message}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Regrouper les succès dans un expander */}
              {steps.some(s => s.status === 'success') && (
                <div className="collapse collapse-arrow bg-base-100 shadow-md w-full max-w-xl mt-2">
                  <input type="checkbox" /> 
                  <div className="collapse-title text-md font-medium">
                    {currentStep}
                  </div>
                  <div className="collapse-content"> 
                    {steps.filter(s => s.status === 'success').map((step, index) => (
                      <div key={`success-${index}`} className="alert alert-success shadow-lg p-2 mt-2">
                        <div className="flex items-center gap-2">
                          <span>{step.step === "Extraction of ID" ? '🏷️' : step.step === "Creating summary" ? '✨' : '📝'}</span>
                          <span>{step.message}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          {summary && (
            <div className="mt-8">
              <div className="collapse collapse-arrow bg-base-100 shadow mb-4">
                <input type="checkbox" defaultChecked />
                <div className="collapse-title text-xl font-medium flex items-center gap-2">
                  <span role="img" aria-label="Summary">📝</span> Video Summary
                </div>
                <div className="collapse-content">
                  <div className="py-4 prose max-w-none">
                    <ReactMarkdown components={markdownComponents}>
                      {summary}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
              {transcript && (
                <div className="mt-4">
                  <div className="collapse collapse-arrow bg-base-100 shadow">
                    <input type="checkbox" />
                    <div className="collapse-title text-xl font-medium flex items-center gap-2">
                      <span role="img" aria-label="Transcript">📜</span> Transcript
                    </div>
                    <div className="collapse-content">
                      <div className="py-4 prose-sm max-w-none max-h-60 overflow-y-auto">
                        <ReactMarkdown components={markdownComponents}>
                          {transcript}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      <Footer />
    </main>
  );
}