import React from 'react';
import { VerifiedCompetency, CurriculumPhase } from '../types';

interface LearningPathScreenProps {
  competencies: VerifiedCompetency[];
  phases: CurriculumPhase[];
}

export const LearningPathScreen: React.FC<LearningPathScreenProps> = ({ competencies, phases }) => {
  return (
    <div className="flex flex-col w-full">
      {/* Top Ambient Glow Decorator & Hero Header Unit */}
      <div className="relative w-full">
        <div className="absolute -top-10 left-1/3 w-96 h-48 bg-primary/5 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute -top-8 right-10 w-72 h-40 bg-secondary/10 rounded-full blur-2xl pointer-events-none"></div>

        <div className="relative bg-surface-container-lowest rounded-2xl shadow-sm p-space-lg mb-space-lg border border-outline-variant/30">
          <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-space-lg">
            <div className="flex-1 min-w-0">
              {/* Badges */}
              <div className="flex flex-wrap items-center gap-space-sm mb-space-xs">
                <span className="inline-flex items-center gap-1.5 px-space-sm py-0.5 rounded-full bg-surface-container-low text-primary font-label-sm text-label-sm font-semibold text-[11px] border border-primary/20">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
                  Curated Workforce Path
                </span>
                <span className="inline-flex items-center gap-1 px-space-sm py-0.5 rounded-full bg-surface-container text-on-surface-variant font-label-sm text-label-sm font-semibold text-[11px]">
                  <span className="material-symbols-outlined text-[14px]">verified</span>
                  Enterprise Endorsed
                </span>
                <span className="font-code-sm text-code-sm text-on-surface-variant text-[11px]">
                  ID: PM-TRACK-2025
                </span>
              </div>

              {/* Title & Narrative */}
              <h1 className="font-headline-xl text-headline-xl text-on-surface tracking-tight mb-space-xs font-bold">
                Product Manager Career Path
              </h1>
              <p className="font-body-md text-body-md text-on-surface-variant max-w-3xl mb-space-md leading-relaxed">
                A curated 6-month industry path from Associate to Senior Product Manager, verified by industry mentors with real-world case simulations.
              </p>

              {/* Path Parameters Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-space-sm p-space-sm rounded-xl bg-surface-container-low max-w-2xl border border-surface-container">
                <div className="flex flex-col px-space-xs">
                  <span className="font-label-sm text-label-sm text-on-surface-variant text-[11px]">Target Role</span>
                  <span className="font-title-sm text-title-sm text-on-surface font-semibold truncate">
                    Product Manager
                  </span>
                </div>
                <div className="flex flex-col px-space-xs">
                  <span className="font-label-sm text-label-sm text-on-surface-variant text-[11px]">Seniority Level</span>
                  <span className="font-title-sm text-title-sm text-on-surface font-semibold">Mid-Level</span>
                </div>
                <div className="flex flex-col px-space-xs">
                  <span className="font-label-sm text-label-sm text-on-surface-variant text-[11px]">Duration</span>
                  <span className="font-title-sm text-title-sm text-on-surface font-semibold">24 Wks (~120h)</span>
                </div>
                <div className="flex flex-col px-space-xs">
                  <span className="font-label-sm text-label-sm text-on-surface-variant text-[11px]">Velocity</span>
                  <span className="font-title-sm text-title-sm text-secondary font-semibold flex items-center gap-1">
                    <span className="material-symbols-outlined text-[16px]">bolt</span> On Track
                  </span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row lg:flex-col items-stretch lg:items-end gap-space-xs shrink-0 pt-space-xs">
              <button
                type="button"
                className="inline-flex items-center justify-center gap-space-xs px-space-md py-space-sm rounded-xl bg-primary text-on-primary hover:bg-primary-container font-label-md text-label-md shadow-sm transition-all transform active:scale-95 font-semibold"
              >
                <span className="material-symbols-outlined text-[18px]">play_circle</span>
                <span>Continue Active Course</span>
              </button>
              <div className="flex items-center gap-space-xs">
                <button
                  type="button"
                  className="flex-1 inline-flex items-center justify-center gap-1.5 px-space-sm py-space-xs rounded-xl bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md text-label-md transition-colors text-[13px] font-semibold"
                >
                  <span className="material-symbols-outlined text-[16px] text-on-surface-variant">tune</span>
                  <span>Customize</span>
                </button>
                <button
                  type="button"
                  className="flex-1 inline-flex items-center justify-center gap-1.5 px-space-sm py-space-xs rounded-xl bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md text-label-md transition-colors text-[13px] font-semibold"
                >
                  <span className="material-symbols-outlined text-[16px] text-on-surface-variant">download</span>
                  <span>Syllabus PDF</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Overall Progress & Competencies Overview Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg mb-space-lg">
        {/* Macro Progress Metric Card (5 cols) */}
        <div className="lg:col-span-5 bg-surface-container-lowest rounded-2xl shadow-sm p-space-lg flex flex-col justify-between border border-outline-variant/30">
          <div>
            <div className="flex items-center justify-between mb-space-sm">
              <div>
                <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
                  Overall Velocity
                </span>
                <h2 className="font-headline-lg text-headline-lg text-on-surface font-bold">Curriculum Progress</h2>
              </div>
              <span className="inline-flex items-center gap-1 px-space-xs py-0.5 rounded-full bg-secondary-fixed/50 text-secondary font-label-sm text-label-sm font-semibold text-[11px]">
                <span className="material-symbols-outlined text-[14px]">trending_up</span> +14% this month
              </span>
            </div>

            {/* Radial Donut + Linear Stack */}
            <div className="flex items-center gap-space-lg my-space-md">
              <div className="relative w-24 h-24 shrink-0 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 96 96">
                  <circle
                    className="text-surface-container"
                    cx="48"
                    cy="48"
                    fill="transparent"
                    r="40"
                    stroke="currentColor"
                    strokeWidth="8"
                  ></circle>
                  <circle
                    className="text-primary transition-all duration-1000"
                    cx="48"
                    cy="48"
                    fill="transparent"
                    r="40"
                    stroke="currentColor"
                    strokeDasharray="251.32"
                    strokeDashoffset="105.5"
                    strokeLinecap="round"
                    strokeWidth="8"
                  ></circle>
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="font-headline-lg text-headline-lg text-on-surface leading-none font-bold">58%</span>
                  <span className="font-label-sm text-label-sm text-on-surface-variant text-[10px] font-semibold">TOTAL</span>
                </div>
              </div>
              <div className="flex-1 flex flex-col gap-space-xs">
                <div className="w-full h-2 rounded-full bg-surface-container overflow-hidden flex">
                  <div className="bg-secondary h-full" style={{ width: '54%' }} title="Completed"></div>
                  <div className="bg-primary h-full" style={{ width: '15%' }} title="In Progress"></div>
                  <div className="bg-surface-container-high h-full" style={{ width: '31%' }} title="Upcoming"></div>
                </div>
                <p className="font-body-sm text-body-sm text-on-surface-variant text-[13px] leading-snug">
                  14 of 24 weeks elapsed. Estimated completion: <span className="font-semibold text-on-surface">May 18, 2025</span>.
                </p>
              </div>
            </div>
          </div>

          {/* Counts */}
          <div className="grid grid-cols-3 gap-space-xs pt-space-md border-t border-surface-container">
            <div className="p-space-xs rounded-xl bg-surface-container-low flex flex-col items-center text-center">
              <span className="font-headline-md text-headline-md text-secondary leading-tight font-bold">7</span>
              <span className="font-label-sm text-label-sm text-on-surface-variant text-[11px]">Completed</span>
            </div>
            <div className="p-space-xs rounded-xl bg-surface-container-low flex flex-col items-center text-center">
              <span className="font-headline-md text-headline-md text-primary leading-tight font-bold">2</span>
              <span className="font-label-sm text-label-sm text-on-surface-variant text-[11px]">In Progress</span>
            </div>
            <div className="p-space-xs rounded-xl bg-surface-container-low flex flex-col items-center text-center">
              <span className="font-headline-md text-headline-md text-on-surface-variant leading-tight font-bold">4</span>
              <span className="font-label-sm text-label-sm text-on-surface-variant text-[11px]">Upcoming</span>
            </div>
          </div>
        </div>

        {/* Core Skills Tracked Matrix (7 cols) */}
        <div className="lg:col-span-7 bg-surface-container-lowest rounded-2xl shadow-sm p-space-lg flex flex-col justify-between border border-outline-variant/30">
          <div className="flex items-center justify-between mb-space-sm">
            <div>
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
                Skill Mastery Target
              </span>
              <h2 className="font-headline-lg text-headline-lg text-on-surface font-bold">Verified Competencies</h2>
            </div>
            <span className="font-label-sm text-label-sm text-primary font-semibold flex items-center gap-1 cursor-pointer hover:underline text-[13px]">
              <span className="material-symbols-outlined text-[16px]">radar</span> Assessment Radar
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-space-lg gap-y-space-md py-space-xs">
            {competencies.map((comp, idx) => (
              <div key={idx} className={`flex flex-col gap-1 ${idx === 4 ? 'md:col-span-2' : ''}`}>
                <div className="flex justify-between items-center">
                  <span className="font-label-md text-label-md text-on-surface font-semibold text-[13px]">
                    {comp.name}
                  </span>
                  <span
                    className={`font-code-sm text-code-sm font-bold ${
                      comp.scorePercent >= 80
                        ? 'text-secondary'
                        : comp.scorePercent >= 60
                        ? 'text-primary'
                        : 'text-tertiary-container'
                    }`}
                  >
                    {comp.scorePercent}%
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-surface-container overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      comp.scorePercent >= 80
                        ? 'bg-secondary'
                        : comp.scorePercent >= 60
                        ? 'bg-primary'
                        : 'bg-tertiary-fixed-dim'
                    }`}
                    style={{ width: `${comp.scorePercent}%` }}
                  ></div>
                </div>
                <span className="font-label-sm text-label-sm text-on-surface-variant text-[11px] truncate">
                  {comp.subText}
                </span>
              </div>
            ))}
          </div>

          <div className="mt-space-xs pt-space-xs flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm border-t border-surface-container text-[12px]">
            <span className="flex items-center gap-1">
              <span className="material-symbols-outlined text-[16px] text-secondary">check_circle</span>
              3 of 5 Core Competency thresholds unlocked
            </span>
            <span className="font-code-sm text-code-sm font-semibold">Target: 80% Min for Placement</span>
          </div>
        </div>
      </div>

      {/* Main Roadmap & Phases Section */}
      <div className="flex flex-col gap-space-lg">
        {phases.map((phase) => {
          if (phase.status === 'completed') {
            return (
              <section
                key={phase.phaseNumber}
                className="bg-surface-container-lowest rounded-2xl shadow-sm p-space-lg transition-all hover:shadow-md border border-outline-variant/30"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-xs pb-space-md border-b border-surface-container">
                  <div className="flex items-center gap-space-sm">
                    <div className="w-9 h-9 rounded-full bg-secondary-fixed/50 text-secondary flex items-center justify-center shrink-0">
                      <span className="material-symbols-outlined text-[20px]">check</span>
                    </div>
                    <div>
                      <div className="flex items-center gap-space-xs">
                        <span className="font-label-sm text-label-sm uppercase tracking-wide text-secondary font-bold">
                          Phase {phase.phaseNumber}
                        </span>
                        <span className="px-space-xs py-0.5 rounded-full bg-secondary-fixed/30 text-secondary font-label-sm text-label-sm font-semibold text-[11px]">
                          Completed
                        </span>
                      </div>
                      <h3 className="font-headline-md text-headline-md text-on-surface font-bold">{phase.title}</h3>
                    </div>
                  </div>
                  <div className="text-left sm:text-right">
                    <span className="font-code-sm text-code-sm text-secondary font-bold text-[14px]">100% Complete</span>
                    <p className="font-label-sm text-label-sm text-on-surface-variant text-[12px]">{phase.durationText}</p>
                  </div>
                </div>

                <div className="flex flex-col gap-space-sm pt-space-md">
                  {phase.courses.map((course) => (
                    <div
                      key={course.id}
                      className="p-space-md rounded-xl bg-surface-container-low flex flex-col md:flex-row md:items-center justify-between gap-space-sm border border-surface-container"
                    >
                      <div className="flex items-start gap-space-sm min-w-0">
                        <span className="material-symbols-outlined text-secondary text-[22px] mt-0.5 shrink-0">
                          check_circle
                        </span>
                        <div className="min-w-0">
                          <div className="flex items-center gap-space-xs flex-wrap">
                            <h4 className="font-title-sm text-title-sm text-on-surface font-semibold">{course.title}</h4>
                            {course.badgeText && (
                              <span className="inline-flex items-center gap-0.5 px-space-xs py-0.5 rounded-full bg-surface-container-highest text-on-surface-variant font-label-sm text-label-sm text-[11px]">
                                <span className="material-symbols-outlined text-[13px] text-secondary">workspace_premium</span>{' '}
                                {course.badgeText}
                              </span>
                            )}
                          </div>
                          <p className="font-body-sm text-body-sm text-on-surface-variant truncate text-[13px]">
                            {course.description}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-space-sm self-end md:self-center shrink-0">
                        <span className="font-code-sm text-code-sm text-on-surface-variant">Score: {course.score}%</span>
                        <button
                          type="button"
                          className="px-space-sm py-1 rounded-lg bg-surface-container hover:bg-surface-container-high text-on-surface font-label-sm text-label-sm flex items-center gap-1 transition-colors font-semibold"
                        >
                          <span className="material-symbols-outlined text-[15px]">visibility</span> Review
                        </button>
                      </div>
                    </div>
                  ))}

                  {phase.capstone && (
                    <div className="p-space-md rounded-xl bg-surface-container-lowest shadow-sm flex flex-col gap-space-xs border border-secondary/20">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-xs">
                        <div className="flex items-center gap-space-sm">
                          <div className="p-1.5 rounded-lg bg-secondary-fixed/50 text-secondary flex items-center justify-center">
                            <span className="material-symbols-outlined text-[20px]">military_tech</span>
                          </div>
                          <div>
                            <span className="font-label-sm text-label-sm uppercase tracking-wider text-secondary font-bold text-[11px]">
                              Phase Capstone Project
                            </span>
                            <h4 className="font-title-sm text-title-sm text-on-surface font-bold">{phase.capstone.title}</h4>
                          </div>
                        </div>
                        <div className="flex items-center gap-space-sm">
                          <span className="px-space-sm py-0.5 rounded-full bg-secondary-fixed/60 text-secondary font-code-sm text-code-sm font-bold">
                            Graded: {phase.capstone.score}
                          </span>
                          <span className="font-label-sm text-label-sm text-on-surface-variant text-[12px]">
                            {phase.capstone.reviewer}
                          </span>
                        </div>
                      </div>
                      <div className="p-space-sm rounded-lg bg-surface-container-low text-on-surface-variant font-body-sm text-body-sm italic flex items-start gap-space-xs mt-space-xs border border-surface-container text-[13px]">
                        <span className="material-symbols-outlined text-secondary text-[18px] shrink-0 not-italic">
                          chat_bubble
                        </span>
                        <span>{phase.capstone.feedbackQuote}</span>
                      </div>
                    </div>
                  )}
                </div>
              </section>
            );
          }

          if (phase.status === 'in_progress') {
            return (
              <section
                key={phase.phaseNumber}
                className="bg-surface-container-lowest rounded-2xl shadow-sm p-space-lg transition-all hover:shadow-md ring-2 ring-primary/20 border border-primary/20"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-xs pb-space-md border-b border-surface-container">
                  <div className="flex items-center gap-space-sm">
                    <div className="w-9 h-9 rounded-full bg-primary-fixed text-primary flex items-center justify-center shrink-0">
                      <span className="material-symbols-outlined text-[20px]">autorenew</span>
                    </div>
                    <div>
                      <div className="flex items-center gap-space-xs">
                        <span className="font-label-sm text-label-sm uppercase tracking-wide text-primary font-bold">
                          Phase {phase.phaseNumber}
                        </span>
                        <span className="px-space-xs py-0.5 rounded-full bg-primary-fixed text-primary font-label-sm text-label-sm font-semibold text-[11px]">
                          In Progress
                        </span>
                      </div>
                      <h3 className="font-headline-md text-headline-md text-on-surface font-bold">{phase.title}</h3>
                    </div>
                  </div>
                  <div className="text-left sm:text-right">
                    <span className="font-code-sm text-code-sm text-primary font-bold text-[14px]">
                      {phase.progressPercent}% Active
                    </span>
                    <p className="font-label-sm text-label-sm text-on-surface-variant text-[12px]">{phase.durationText}</p>
                  </div>
                </div>

                <div className="flex flex-col gap-space-sm pt-space-md">
                  {phase.courses.map((course) => (
                    <div
                      key={course.id}
                      className="p-space-md rounded-xl bg-surface-container-low flex flex-col md:flex-row md:items-center justify-between gap-space-sm border border-surface-container"
                    >
                      <div className="flex items-start gap-space-sm min-w-0">
                        <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center shrink-0 mt-0.5">
                          <span className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse"></span>
                        </div>
                        <div className="min-w-0">
                          <h4 className="font-title-sm text-title-sm text-on-surface font-semibold">{course.title}</h4>
                          <p className="font-body-sm text-body-sm text-on-surface-variant truncate text-[13px]">
                            {course.description}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-space-sm self-end md:self-center shrink-0">
                        {course.score && (
                          <span className="font-code-sm text-code-sm text-primary font-semibold">
                            {course.score}%
                          </span>
                        )}
                        <button
                          type="button"
                          className="px-space-md py-1.5 rounded-xl bg-primary hover:bg-primary-container text-on-primary font-label-sm text-label-sm flex items-center gap-1 transition-colors font-semibold"
                        >
                          <span className="material-symbols-outlined text-[15px]">play_arrow</span> Resume
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            );
          }

          return (
            <section
              key={phase.phaseNumber}
              className="bg-surface-container-low/60 rounded-2xl p-space-lg opacity-70 border border-surface-container"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-xs pb-space-md border-b border-surface-container">
                <div className="flex items-center gap-space-sm">
                  <div className="w-9 h-9 rounded-full bg-surface-container-highest text-outline flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-[20px]">lock</span>
                  </div>
                  <div>
                    <div className="flex items-center gap-space-xs">
                      <span className="font-label-sm text-label-sm uppercase tracking-wide text-outline font-bold">
                        Phase {phase.phaseNumber}
                      </span>
                      <span className="px-space-xs py-0.5 rounded-full bg-surface-container-highest text-outline font-label-sm text-label-sm font-semibold text-[11px]">
                        Locked
                      </span>
                    </div>
                    <h3 className="font-headline-md text-headline-md text-on-surface-variant font-bold">{phase.title}</h3>
                  </div>
                </div>
                <div className="text-left sm:text-right">
                  <span className="font-label-sm text-label-sm text-outline font-semibold">Requires Phase 2 Signoff</span>
                  <p className="font-label-sm text-label-sm text-outline text-[12px]">{phase.durationText}</p>
                </div>
              </div>

              <div className="flex flex-col gap-space-sm pt-space-md">
                {phase.courses.map((course) => (
                  <div
                    key={course.id}
                    className="p-space-md rounded-xl bg-surface-container-lowest/50 flex flex-col md:flex-row md:items-center justify-between gap-space-sm border border-surface-container/60"
                  >
                    <div className="flex items-start gap-space-sm min-w-0">
                      <span className="material-symbols-outlined text-outline text-[20px] mt-0.5 shrink-0">lock</span>
                      <div className="min-w-0">
                        <h4 className="font-title-sm text-title-sm text-on-surface-variant font-semibold">{course.title}</h4>
                        <p className="font-body-sm text-body-sm text-outline truncate text-[13px]">{course.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
};
