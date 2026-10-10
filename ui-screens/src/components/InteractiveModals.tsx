import React, { useState } from 'react';

// --- RAPID QUIZ MODAL ---
interface RapidQuizModalProps {
  onClose: () => void;
  onSubmit: (score: number) => void;
}

export const RapidQuizModal: React.FC<RapidQuizModalProps> = ({ onClose, onSubmit }) => {
  const questions = [
    {
      q: "1. Which ratio best measures sticky habituation and daily user retention?",
      options: ["DAU / MAU Ratio", "Total Signups / CAC", "Bounce Rate", "CSAT Score"],
      ans: 0
    },
    {
      q: "2. When defining a two-sided marketplace North Star, which focus is most robust?",
      options: ["Total Gross Merchandise App Visits", "Completed Core Transactions", "Total Seller Accounts", "App Store Ratings"],
      ans: 1
    },
    {
      q: "3. What p-value statistical significance threshold is standard in product A/B testing?",
      options: ["p < 0.50", "p < 0.05 (95% Confidence)", "p = 0.00", "p > 0.10"],
      ans: 1
    }
  ];

  const [selected, setSelected] = useState<{ [qIdx: number]: number }>({});

  const handleSubmit = () => {
    let score = 0;
    questions.forEach((q, idx) => {
      if (selected[idx] === q.ans) score++;
    });
    onSubmit(score);
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl relative border border-slate-200">
        <button onClick={onClose} className="absolute top-5 right-5 text-slate-400 hover:text-slate-600">
          <span className="material-symbols-outlined text-[20px]">close</span>
        </button>

        <div className="mb-4">
          <span className="text-xs font-bold text-indigo-700 uppercase tracking-wider">Product Analytics Lab</span>
          <h3 className="text-xl font-bold text-slate-900">Rapid Metric Formula Quiz</h3>
          <p className="text-xs text-slate-500">Answer all 3 questions to unlock +100 XP and competency credit.</p>
        </div>

        <div className="flex flex-col gap-4 text-xs">
          {questions.map((item, qIdx) => (
            <div key={qIdx} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <p className="font-bold text-slate-800 text-sm mb-2">{item.q}</p>
              <div className="flex flex-col gap-1.5">
                {item.options.map((opt, oIdx) => (
                  <label key={oIdx} className="flex items-center gap-2 cursor-pointer p-1.5 rounded-lg hover:bg-white transition-colors">
                    <input
                      type="radio"
                      name={`q-${qIdx}`}
                      checked={selected[qIdx] === oIdx}
                      onChange={() => setSelected(prev => ({ ...prev, [qIdx]: oIdx }))}
                      className="accent-indigo-700"
                    />
                    <span className="text-slate-700">{opt}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={handleSubmit}
          className="mt-6 w-full py-3 bg-indigo-700 hover:bg-indigo-800 text-white rounded-xl font-bold text-sm shadow-xs transition-all active:scale-95"
        >
          Submit Quiz Answers
        </button>
      </div>
    </div>
  );
};

// --- ASSIGNMENT UPLOAD MODAL ---
interface AssignmentModalProps {
  isSubmitted: boolean;
  onClose: () => void;
  onSubmit: () => void;
}

export const AssignmentUploadModal: React.FC<AssignmentModalProps> = ({ isSubmitted, onClose, onSubmit }) => {
  const [fileName, setFileName] = useState(isSubmitted ? "Elena_Vance_Discovery_Deck_v1.pdf" : "");

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl relative border border-slate-200">
        <button onClick={onClose} className="absolute top-5 right-5 text-slate-400 hover:text-slate-600">
          <span className="material-symbols-outlined text-[20px]">close</span>
        </button>

        <div className="mb-4">
          <span className="text-xs font-bold text-indigo-700 uppercase tracking-wider">Portfolio Deliverable</span>
          <h3 className="text-xl font-bold text-slate-900">Sprint Assignment Submission</h3>
          <p className="text-xs text-slate-500">Discovery Deck Review with Mentor Sarah Blake.</p>
        </div>

        <div className="p-6 rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 flex flex-col items-center justify-center text-center">
          <span className="material-symbols-outlined text-[36px] text-indigo-600 mb-2">upload_file</span>
          <span className="text-xs font-bold text-slate-800 block">Drag & Drop Affinity Deck (PDF, Figma link, or PPTX)</span>
          <span className="text-[11px] text-slate-400 block mt-1">Maximum file size: 25MB</span>
          <input
            type="file"
            id="file-input-modal"
            className="hidden"
            onChange={(e: any) => setFileName(e.target.files[0]?.name || "discovery_deck.pdf")}
          />
          <button
            type="button"
            onClick={() => document.getElementById('file-input-modal')?.click()}
            className="mt-3 px-3 py-1.5 bg-white border border-slate-300 rounded-lg text-xs font-semibold hover:bg-slate-100"
          >
            Choose Local File
          </button>
          {fileName && (
            <div className="mt-3 p-2 bg-emerald-50 text-emerald-800 rounded-lg text-xs font-medium border border-emerald-200">
              Selected: <strong>{fileName}</strong>
            </div>
          )}
        </div>

        <div className="mt-4 p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600">
          <span className="font-bold block mb-1">Evaluation Rubrics:</span>
          <ul className="list-disc list-inside space-y-0.5 text-[11px]">
            <li>Non-biased interview questions formulation (35%)</li>
            <li>Clear categorization into high vs low urgency clusters (35%)</li>
            <li>Actionable User Story Map transition (30%)</li>
          </ul>
        </div>

        <button
          onClick={onSubmit}
          className="mt-5 w-full py-3 bg-indigo-700 hover:bg-indigo-800 text-white rounded-xl font-bold text-sm shadow-xs transition-all active:scale-95"
        >
          {isSubmitted ? 'Update Submission' : 'Submit for Mentor Review'}
        </button>
      </div>
    </div>
  );
};
