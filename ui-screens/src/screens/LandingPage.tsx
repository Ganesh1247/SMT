import React from 'react';

interface LandingPageProps {
  onGetStarted: () => void;
  onSignIn: () => void;
  onExploreCatalog: () => void;
  onGoDashboard: () => void;
  isAuthenticated: boolean;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onGetStarted,
  onSignIn,
  onExploreCatalog,
  onGoDashboard,
  isAuthenticated
}) => {
  return (
    <div className="flex flex-col w-full bg-[#f8f9ff]">
      {/* Top Navbar */}
      <nav className="h-20 px-8 lg:px-16 flex items-center justify-between border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-40">
        <div className="flex items-center gap-3 cursor-pointer" onClick={onGoDashboard}>
          <div className="w-10 h-10 rounded-xl bg-indigo-700 text-white flex items-center justify-center font-bold shadow-sm">
            <span className="material-symbols-outlined text-[24px]">school</span>
          </div>
          <span className="font-bold text-xl text-indigo-700 tracking-tight">Pathway LMS</span>
        </div>

        <div className="hidden md:flex items-center gap-8 font-medium text-sm text-slate-600">
          <a href="#tracks" className="hover:text-indigo-700 transition-colors">Career Tracks</a>
          <button onClick={onExploreCatalog} className="hover:text-indigo-700 transition-colors">Course Catalog</button>
          <a href="#features" className="hover:text-indigo-700 transition-colors">Assessment Sandboxes</a>
          <a href="#mentors" className="hover:text-indigo-700 transition-colors">Mentorship</a>
        </div>

        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <button
              onClick={onGoDashboard}
              className="px-5 py-2.5 rounded-xl bg-indigo-700 hover:bg-indigo-800 text-white font-semibold text-sm shadow-sm transition-all"
            >
              Enter Dashboard →
            </button>
          ) : (
            <>
              <button
                onClick={onSignIn}
                className="px-4 py-2 rounded-xl text-slate-700 hover:text-indigo-700 font-semibold text-sm transition-colors"
              >
                Sign In
              </button>
              <button
                onClick={onGetStarted}
                className="px-5 py-2.5 rounded-xl bg-indigo-700 hover:bg-indigo-800 text-white font-semibold text-sm shadow-sm transition-all active:scale-95"
              >
                Get Started Free
              </button>
            </>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative px-8 lg:px-16 pt-16 pb-20 flex flex-col items-center text-center max-w-5xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-bold mb-6">
          <span className="w-2 h-2 rounded-full bg-indigo-600 animate-pulse"></span>
          Curated Workforce Readiness LMS • 2025 Cohorts
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.15]">
          Master Job-Ready Skills Through <br className="hidden sm:inline"/>
          <span className="text-indigo-700 underline decoration-indigo-300">Evidence-Based</span> Sandboxes
        </h1>

        <p className="text-lg text-slate-600 mt-6 max-w-2xl leading-relaxed">
          Ditch passive certificate tests. Pathway LMS delivers realistic task simulations, criterion-level AI rubrics, and verified mentor-graded capstone portfolios.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 mt-8">
          <button
            onClick={onGetStarted}
            className="px-8 py-3.5 rounded-xl bg-indigo-700 hover:bg-indigo-800 text-white font-bold text-base shadow-lg shadow-indigo-700/20 transition-all transform active:scale-95"
          >
            Start Learning Free
          </button>
          <button
            onClick={onExploreCatalog}
            className="px-6 py-3.5 rounded-xl bg-white border border-slate-300 hover:bg-slate-50 text-slate-800 font-bold text-base shadow-sm transition-all"
          >
            Explore 250+ Courses
          </button>
        </div>

        {/* Interactive PM Track Preview Card */}
        <div className="mt-16 w-full rounded-2xl bg-white border border-slate-200 p-6 shadow-2xl text-left">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-6">
            <div className="flex items-center gap-3">
              <span className="w-3 h-3 rounded-full bg-red-400"></span>
              <span className="w-3 h-3 rounded-full bg-amber-400"></span>
              <span className="w-3 h-3 rounded-full bg-emerald-400"></span>
              <span className="text-xs font-semibold text-slate-400 ml-2">Product Manager Career Sandbox • Week 6 Overview</span>
            </div>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">● 68% Milestone Velocity</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-xs font-bold uppercase text-slate-400 tracking-wider">Current Sprint</span>
              <h4 className="font-bold text-base text-slate-900 mt-1">Affinity Mapping & Interview Synthesis</h4>
              <p className="text-xs text-slate-500 mt-1">Interactive Figma exercise teardown with mentor feedback.</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-xs font-bold uppercase text-slate-400 tracking-wider">Verified Competency</span>
              <h4 className="font-bold text-base text-slate-900 mt-1">Agile PRDs & Backlog Grooming</h4>
              <div className="w-full h-1.5 rounded-full bg-slate-200 mt-2 overflow-hidden">
                <div className="bg-emerald-600 h-full rounded-full" style={{ width: '90%' }}></div>
              </div>
              <span className="text-xs text-emerald-700 font-bold mt-1 block">90% Mastery Score</span>
            </div>
            <div className="p-4 rounded-xl bg-indigo-50/60 border border-indigo-200 flex flex-col justify-between">
              <div>
                <span className="text-xs font-bold uppercase text-indigo-700 tracking-wider">Next Live Session</span>
                <h4 className="font-bold text-sm text-slate-900 mt-1">Live Q&A with Melissa Chen (FinScale)</h4>
              </div>
              <button onClick={onGoDashboard} className="mt-3 py-1.5 bg-indigo-700 text-white rounded-lg text-xs font-bold hover:bg-indigo-800">
                Preview in Dashboard →
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Value Pillars */}
      <section id="features" className="px-8 lg:px-16 py-16 bg-white border-y border-slate-200">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Built for Real Capability, Not Just Completion</h2>
            <p className="text-sm text-slate-600 mt-2">Every lesson connects to verifiable workplace tasks evaluated against transparent rubrics.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="p-6 rounded-2xl bg-[#f8f9ff] border border-slate-200">
              <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold mb-4">
                <span className="material-symbols-outlined text-[26px]">terminal</span>
              </div>
              <h3 className="font-bold text-base text-slate-900">Task-Based Labs</h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">Solve real data, PRD, and architecture puzzles instead of trivial multiple-choice quizzes.</p>
            </div>

            <div className="p-6 rounded-2xl bg-[#f8f9ff] border border-slate-200">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold mb-4">
                <span className="material-symbols-outlined text-[26px]">smart_toy</span>
              </div>
              <h3 className="font-bold text-base text-slate-900">Deterministic Rubrics</h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">AI and automated tests evaluate submissions against explicit industry rubrics with clear retry paths.</p>
            </div>

            <div className="p-6 rounded-2xl bg-[#f8f9ff] border border-slate-200">
              <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center font-bold mb-4">
                <span className="material-symbols-outlined text-[26px]">verified</span>
              </div>
              <h3 className="font-bold text-base text-slate-900">Evidence Profiles</h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">Scores link directly to tasks, criteria, and submission timestamps. Shareable with recruiters.</p>
            </div>

            <div className="p-6 rounded-2xl bg-[#f8f9ff] border border-slate-200">
              <div className="w-12 h-12 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center font-bold mb-4">
                <span className="material-symbols-outlined text-[26px]">groups</span>
              </div>
              <h3 className="font-bold text-base text-slate-900">Live Mentorship</h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">Weekly live teardowns and human reviews on consequential capstone submissions.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-8 lg:px-16 py-12 bg-slate-900 text-slate-400 text-xs">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-white font-bold text-sm">
            <span className="material-symbols-outlined text-[20px] text-indigo-400">school</span>
            <span>Pathway LMS</span>
            <span className="text-slate-500 font-normal">© 2025 All rights reserved.</span>
          </div>
          <div className="flex gap-6">
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-white transition-colors">Enterprise Licensing</a>
          </div>
        </div>
      </footer>
    </div>
  );
};
