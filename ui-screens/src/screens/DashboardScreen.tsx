import React, { useState } from 'react';
import {
  UserProfile,
  ActiveSpotlightModule,
  DailyActivity,
  RoadmapMilestone,
  CohortEvent,
  PracticeLab,
  NavigationTab
} from '../types';

interface DashboardScreenProps {
  user: UserProfile;
  module: ActiveSpotlightModule;
  weeklyActivities: DailyActivity[];
  roadmapMilestones: RoadmapMilestone[];
  upcomingEvents: CohortEvent[];
  practiceLabs: PracticeLab[];
  onNavigate: (tab: NavigationTab) => void;
}

export const DashboardScreen: React.FC<DashboardScreenProps> = ({
  user,
  module,
  weeklyActivities,
  roadmapMilestones,
  upcomingEvents,
  practiceLabs,
  onNavigate
}) => {
  const [rsvpState, setRsvpState] = useState<{ [id: string]: boolean }>({});

  const toggleRsvp = (id: string) => {
    setRsvpState((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="flex flex-col w-full gap-space-lg">
      {/* TOP WELCOME BANNER & STAT GLANCE */}
      <div className="relative overflow-hidden rounded-2xl bg-surface-container-lowest shadow-sm p-space-lg flex flex-col lg:flex-row lg:items-center justify-between gap-space-lg border border-outline-variant/30">
        <div className="absolute -right-16 -top-16 w-80 h-80 rounded-full bg-primary/5 pointer-events-none blur-3xl"></div>
        <div className="absolute right-64 -bottom-12 w-64 h-64 rounded-full bg-secondary/5 pointer-events-none blur-2xl"></div>

        <div className="flex flex-col gap-space-xs max-w-2xl relative z-10">
          <div className="flex items-center gap-space-xs">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-primary-fixed text-primary font-label-sm text-label-sm font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
              {user.track}
            </span>
            <span className="font-code-sm text-code-sm text-on-surface-variant font-medium">
              {user.cohort}
            </span>
          </div>
          <h1 className="font-headline-xl text-headline-xl text-on-surface tracking-tight font-bold">
            Good morning, {user.name.split(' ')[0]} 👋
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">
            You're <span className="font-semibold text-primary">{user.milestoneProgress}% through</span> your{' '}
            <strong className="text-on-surface font-semibold">{user.currentMilestone}</strong> milestone. Next up: User Interview Synthesis. Keep up the momentum!
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap sm:flex-nowrap items-center gap-space-sm relative z-10">
          <button
            type="button"
            className="group flex items-center justify-center gap-space-xs px-space-md py-3 rounded-xl bg-primary hover:bg-primary-container text-on-primary font-label-md text-label-md shadow-sm transition-all transform active:scale-95 whitespace-nowrap"
          >
            <span className="material-symbols-outlined text-[20px] transition-transform group-hover:scale-110">
              play_circle
            </span>
            <span>Resume Learning ({module.estimatedMinutesLeft}m left)</span>
          </button>
          <button
            type="button"
            onClick={() => onNavigate('my-learning-path')}
            className="flex items-center justify-center gap-space-xs px-space-md py-3 rounded-xl bg-surface-container-low hover:bg-surface-container text-on-surface font-label-md text-label-md transition-colors whitespace-nowrap border border-outline-variant/30"
          >
            <span>View Full Path</span>
            <span className="material-symbols-outlined text-[18px] text-on-surface-variant">arrow_forward</span>
          </button>
        </div>
      </div>

      {/* BENTO CORE SECTION: SPOTLIGHT LEARNING + WEEKLY STUDY RHYTHM */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
        {/* PRIMARY SPOTLIGHT: Continue Learning Card (8 cols) */}
        <div className="lg:col-span-8 flex flex-col rounded-2xl bg-surface-container-lowest shadow-sm overflow-hidden border border-outline-variant/30">
          <div className="relative h-48 sm:h-56 w-full overflow-hidden bg-surface-container-high">
            <img
              className="w-full h-full object-cover object-center transform hover:scale-105 transition-transform duration-700"
              src={module.imageUrl}
              alt={module.moduleTitle}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-inverse-surface/90 via-inverse-surface/40 to-transparent flex flex-col justify-between p-space-md sm:p-space-lg">
              <div className="flex items-center justify-between">
                <span className="px-3 py-1 rounded-full bg-surface-container-lowest/90 backdrop-blur-md font-label-sm text-label-sm text-primary flex items-center gap-1 shadow-sm font-semibold">
                  <span className="material-symbols-outlined text-[14px]">school</span>
                  Current Course • {module.subTitle}
                </span>
                <button
                  aria-label="Bookmark module"
                  className="w-8 h-8 rounded-full bg-surface-container-lowest/80 backdrop-blur-md text-on-surface flex items-center justify-center hover:bg-surface-container-lowest transition-colors"
                  type="button"
                >
                  <span className="material-symbols-outlined text-[18px]">bookmark</span>
                </button>
              </div>
              <div className="flex flex-col gap-1">
                <span className="font-label-sm text-label-sm uppercase tracking-wider text-primary-fixed-dim font-semibold">
                  {module.courseTitle}
                </span>
                <h2 className="font-headline-lg text-headline-lg text-on-primary line-clamp-1 font-bold">
                  {module.moduleTitle}
                </h2>
              </div>
            </div>
          </div>

          <div className="p-space-lg flex flex-col gap-space-md">
            {/* Progress Bar & Meta */}
            <div className="flex flex-col gap-space-xs">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-space-xs">
                  <span className="font-label-md text-label-md text-on-surface font-semibold">
                    Overall Course Progress
                  </span>
                  <span className="font-code-sm text-code-sm text-on-surface-variant">
                    • {module.completedLessons} of {module.totalLessons} Lessons Completed
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="font-headline-md text-headline-md text-primary font-bold">
                    {module.progressPercent}%
                  </span>
                </div>
              </div>
              <div className="w-full h-2 rounded-full bg-surface-container-high overflow-hidden">
                <div
                  className="bg-primary h-full rounded-full transition-all duration-500"
                  style={{ width: `${module.progressPercent}%` }}
                ></div>
              </div>
              <div className="flex items-center justify-between font-label-sm text-label-sm text-on-surface-variant pt-1">
                <span className="flex items-center gap-1">
                  <span className="material-symbols-outlined text-[15px] text-primary">schedule</span>
                  Estimated {module.estimatedMinutesLeft} mins to finish Module {module.moduleIndex}
                </span>
                <span className="text-secondary font-medium flex items-center gap-1">
                  <span className="material-symbols-outlined text-[15px]">verified_user</span>
                  {module.benchmarkBadge}
                </span>
              </div>
            </div>

            {/* Checklist */}
            <div className="flex flex-col gap-space-xs pt-space-xs">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
                Module Breakdown
              </span>
              <div className="flex flex-col rounded-xl bg-surface-container-low overflow-hidden border border-surface-container">
                {module.lessons.map((lesson) => {
                  if (lesson.status === 'done') {
                    return (
                      <div
                        key={lesson.id}
                        className="flex items-center justify-between px-space-md py-2.5 bg-surface-container-low hover:bg-surface-container transition-colors border-b border-surface-container/50 last:border-b-0"
                      >
                        <div className="flex items-center gap-space-sm min-w-0">
                          <span className="material-symbols-outlined text-secondary text-[20px]">
                            check_circle
                          </span>
                          <span className="font-body-sm text-body-sm text-on-surface line-clamp-1">
                            {lesson.title}
                          </span>
                        </div>
                        <span className="font-code-sm text-code-sm text-on-surface-variant px-2 py-0.5 rounded bg-surface-container-lowest">
                          {lesson.duration} • Done
                        </span>
                      </div>
                    );
                  }
                  if (lesson.status === 'active') {
                    return (
                      <div
                        key={lesson.id}
                        className="flex items-center justify-between px-space-md py-3 bg-surface-container-lowest shadow-[0_1px_4px_rgba(0,0,0,0.06)] rounded-lg mx-1 my-1 border border-primary/20"
                      >
                        <div className="flex items-center gap-space-sm min-w-0">
                          <div className="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                            <span className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse"></span>
                          </div>
                          <div className="flex flex-col min-w-0">
                            <span className="font-label-md text-label-md text-primary font-semibold truncate">
                              {lesson.title}
                            </span>
                            {lesson.notes && (
                              <span className="font-label-sm text-label-sm text-on-surface-variant text-[11px]">
                                {lesson.notes}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-space-xs shrink-0">
                          <span className="px-2 py-1 rounded bg-primary-fixed text-primary font-code-sm text-code-sm font-semibold">
                            Now
                          </span>
                          <button
                            className="px-3 py-1.5 rounded-lg bg-primary hover:bg-primary-container text-on-primary font-label-sm text-label-sm transition-all shadow-sm font-semibold"
                            type="button"
                          >
                            Continue
                          </button>
                        </div>
                      </div>
                    );
                  }
                  return (
                    <div
                      key={lesson.id}
                      className="flex items-center justify-between px-space-md py-2.5 bg-surface-container-low opacity-75 border-b border-surface-container/50 last:border-b-0"
                    >
                      <div className="flex items-center gap-space-sm min-w-0">
                        <span className="material-symbols-outlined text-outline text-[20px]">lock</span>
                        <span className="font-body-sm text-body-sm text-on-surface-variant line-clamp-1">
                          {lesson.title}
                        </span>
                      </div>
                      <span className="font-code-sm text-code-sm text-outline px-2 py-0.5">
                        {lesson.duration}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* SIDE PANEL: STUDY GOAL & STREAK (4 cols) */}
        <div className="lg:col-span-4 flex flex-col gap-space-lg">
          {/* Study Goal Card */}
          <div className="flex flex-col rounded-2xl bg-surface-container-lowest shadow-sm p-space-lg gap-space-md border border-outline-variant/30">
            <div className="flex items-center justify-between">
              <div className="flex flex-col">
                <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
                  Weekly Pace
                </span>
                <h3 className="font-headline-md text-headline-md text-on-surface font-bold">Study Goal</h3>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-secondary-fixed text-on-secondary-fixed-variant font-label-sm text-label-sm font-semibold">
                On Track
              </span>
            </div>

            {/* Radial SVG Gauge */}
            <div className="flex items-center gap-space-lg py-2">
              <div className="relative w-28 h-28 shrink-0 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" fill="transparent" r="40" stroke="#E2E8F0" strokeWidth="9"></circle>
                  <circle
                    cx="50"
                    cy="50"
                    fill="transparent"
                    r="40"
                    stroke="#4338ca"
                    strokeDasharray="188.5 251.32"
                    strokeLinecap="round"
                    strokeWidth="9"
                  ></circle>
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                  <span className="font-headline-lg text-headline-lg font-bold text-on-surface leading-none">
                    75<span className="text-xs text-primary font-bold">%</span>
                  </span>
                  <span className="font-label-sm text-label-sm text-on-surface-variant text-[11px] mt-0.5 font-semibold">
                    TARGET
                  </span>
                </div>
              </div>
              <div className="flex flex-col gap-1 min-w-0">
                <div className="flex items-baseline gap-1">
                  <span className="font-headline-xl text-headline-xl text-on-surface font-extrabold">4.5</span>
                  <span className="font-body-md text-body-md text-on-surface-variant font-medium">/ 6.0 hrs</span>
                </div>
                <p className="font-body-sm text-body-sm text-on-surface-variant text-[13px] leading-snug">
                  1.5 hours remaining to hit your weekly workforce milestone.
                </p>
              </div>
            </div>

            {/* 5-Day Study Streak Pill */}
            <div className="flex items-center justify-between p-space-sm px-space-md rounded-xl bg-surface-container-low border border-surface-container">
              <div className="flex items-center gap-space-xs">
                <span className="text-[20px] select-none">🔥</span>
                <div className="flex flex-col">
                  <span className="font-label-md text-label-md text-on-surface font-bold">
                    {user.streakDays}-Day Study Streak
                  </span>
                  <span className="font-label-sm text-label-sm text-on-surface-variant text-[11px]">
                    Personal best: {user.streakBest} days
                  </span>
                </div>
              </div>
              <span className="font-code-sm text-code-sm px-2 py-0.5 rounded bg-surface-container-highest text-primary font-semibold">
                +{user.xpBonus} XP
              </span>
            </div>

            {/* Weekly Activity Bar Chart */}
            <div className="flex flex-col gap-space-xs pt-1">
              <span className="font-label-sm text-label-sm text-on-surface-variant font-semibold">
                Daily Activity (Hours)
              </span>
              <div className="grid grid-cols-7 gap-2 items-end h-24 pt-2">
                {weeklyActivities.map((act, index) => {
                  const heightPercent = Math.max(act.hours * 50, 4);
                  return (
                    <div key={index} className="flex flex-col items-center gap-1 h-full justify-end">
                      <div
                        className={`w-full rounded-t transition-colors ${
                          act.isToday
                            ? 'bg-secondary animate-pulse'
                            : act.hours > 1.2
                            ? 'bg-primary'
                            : act.hours > 0.5
                            ? 'bg-primary/40 hover:bg-primary'
                            : 'bg-surface-container-high'
                        }`}
                        style={{ height: `${heightPercent}%` }}
                        title={`${act.day}: ${act.hours} hrs`}
                      ></div>
                      <span
                        className={`font-code-sm text-code-sm text-[10px] ${
                          act.isToday ? 'text-secondary font-bold' : 'text-on-surface-variant'
                        }`}
                      >
                        {act.day}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Credentials Earned Mini Banner */}
          <div className="flex flex-col rounded-2xl bg-surface-container-lowest shadow-sm p-space-md gap-space-sm border border-outline-variant/30">
            <div className="flex items-center justify-between">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
                Credentials Earned
              </span>
              <a className="font-label-sm text-label-sm text-primary hover:underline font-semibold" href="#credentials">
                View all (4)
              </a>
            </div>
            <div className="flex items-center gap-space-sm p-space-xs rounded-xl bg-surface-container-low border border-surface-container">
              <div className="w-10 h-10 rounded-lg bg-secondary-fixed text-on-secondary-fixed flex items-center justify-center shrink-0">
                <span className="material-symbols-outlined text-[22px]">military_tech</span>
              </div>
              <div className="flex flex-col min-w-0">
                <span className="font-label-md text-label-md text-on-surface font-semibold truncate">
                  User Research Maven
                </span>
                <span className="font-label-sm text-label-sm text-secondary font-medium text-[11px]">
                  Issued Feb 12 • Level 2 Badge
                </span>
              </div>
            </div>
            <div className="flex items-center gap-space-sm p-space-xs rounded-xl bg-surface-container-low border border-surface-container">
              <div className="w-10 h-10 rounded-lg bg-primary-fixed text-primary flex items-center justify-center shrink-0">
                <span className="material-symbols-outlined text-[22px]">workspace_premium</span>
              </div>
              <div className="flex flex-col min-w-0">
                <span className="font-label-md text-label-md text-on-surface font-semibold truncate">
                  Agile Roadmapping Pro
                </span>
                <span className="font-label-sm text-label-sm text-on-surface-variant text-[11px]">
                  Verified Certificate ID #8841
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ROADMAP PREVIEW (HORIZONTAL MILESTONES) */}
      <div className="flex flex-col rounded-2xl bg-surface-container-lowest shadow-sm p-space-lg gap-space-md border border-outline-variant/30">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-xs">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-headline-md text-headline-md text-on-surface font-bold">
                Product Manager Pathway Roadmap
              </h2>
              <span className="px-2.5 py-0.5 rounded-full bg-primary-fixed text-primary font-code-sm text-code-sm font-semibold">
                Track 2 of 4
              </span>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              Complete each foundational milestone and cohort evaluation to advance to Senior PM evaluation.
            </p>
          </div>
          <div className="flex items-center gap-space-xs text-on-surface-variant font-label-sm text-label-sm">
            <span className="flex items-center gap-1 font-medium">
              <span className="w-2.5 h-2.5 rounded-full bg-secondary"></span> Done
            </span>
            <span className="flex items-center gap-1 ml-2 font-medium">
              <span className="w-2.5 h-2.5 rounded-full bg-primary"></span> In-Progress
            </span>
            <span className="flex items-center gap-1 ml-2 font-medium">
              <span className="w-2.5 h-2.5 rounded-full bg-surface-container-highest"></span> Locked
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-space-md pt-2">
          {roadmapMilestones.map((m) => {
            if (m.status === 'complete') {
              return (
                <div key={m.id} className="relative flex flex-col p-space-md rounded-xl bg-surface-container-low transition-all border border-surface-container">
                  <div className="flex items-center justify-between mb-space-xs">
                    <span className="font-code-sm text-code-sm font-bold text-secondary uppercase">{m.number}</span>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-secondary-fixed text-on-secondary-fixed-variant font-label-sm text-label-sm font-semibold text-[11px]">
                      <span className="material-symbols-outlined text-[14px]">check</span> Complete
                    </span>
                  </div>
                  <h4 className="font-title-sm text-title-sm text-on-surface font-semibold mb-1">{m.title}</h4>
                  <p className="font-body-sm text-body-sm text-on-surface-variant line-clamp-2 mb-space-md text-[13px]">
                    {m.description}
                  </p>
                  <div className="mt-auto flex items-center justify-between pt-2 border-t border-surface-container">
                    <span className="font-label-sm text-label-sm text-secondary font-semibold flex items-center gap-1">
                      <span className="material-symbols-outlined text-[16px]">grade</span> Score {m.score}%
                    </span>
                    <button onClick={() => onNavigate('my-learning-path')} className="font-label-sm text-label-sm text-primary hover:underline font-semibold">
                      Review Archive
                    </button>
                  </div>
                </div>
              );
            }
            if (m.status === 'in_progress') {
              return (
                <div key={m.id} className="relative flex flex-col p-space-md rounded-xl bg-surface-container-lowest shadow-md ring-2 ring-primary/20 transform -translate-y-0.5 border border-primary/20">
                  <div className="flex items-center justify-between mb-space-xs">
                    <span className="font-code-sm text-code-sm font-bold text-primary uppercase">{m.number}</span>
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-primary-fixed text-primary font-label-sm text-label-sm font-semibold text-[11px]">
                      <span className="w-2 h-2 rounded-full bg-primary animate-ping"></span> In Progress
                    </span>
                  </div>
                  <h4 className="font-title-sm text-title-sm text-on-surface font-semibold mb-1">{m.title}</h4>
                  <p className="font-body-sm text-body-sm text-on-surface-variant line-clamp-2 mb-space-sm text-[13px]">
                    {m.description}
                  </p>
                  <div className="w-full h-1.5 rounded-full bg-surface-container-high overflow-hidden my-2">
                    <div className="bg-primary h-full rounded-full" style={{ width: `${m.progressPercent}%` }}></div>
                  </div>
                  <div className="mt-auto flex items-center justify-between pt-1">
                    <span className="font-code-sm text-code-sm text-on-surface-variant">{m.progressPercent}% Finished</span>
                    <button onClick={() => onNavigate('my-learning-path')} className="px-2.5 py-1 rounded bg-primary text-on-primary font-label-sm text-label-sm font-semibold hover:bg-primary-container transition-colors">
                      Jump in
                    </button>
                  </div>
                </div>
              );
            }
            return (
              <div key={m.id} className="relative flex flex-col p-space-md rounded-xl bg-surface-container-low/70 border border-surface-container">
                <div className="flex items-center justify-between mb-space-xs">
                  <span className="font-code-sm text-code-sm font-bold text-outline uppercase">{m.number}</span>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-surface-container-highest text-on-surface-variant font-label-sm text-label-sm text-[11px]">
                    <span className="material-symbols-outlined text-[13px]">lock</span> Locked
                  </span>
                </div>
                <h4 className="font-title-sm text-title-sm text-on-surface-variant font-semibold mb-1">{m.title}</h4>
                <p className="font-body-sm text-body-sm text-on-surface-variant line-clamp-2 mb-space-md text-[13px]">
                  {m.description}
                </p>
                <div className="mt-auto flex items-center gap-1 text-on-surface-variant font-label-sm text-label-sm pt-2 border-t border-surface-container text-[11px]">
                  <span className="material-symbols-outlined text-[15px]">info</span>
                  <span>{m.requiresSignoff || m.tag}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* LOWER SPLIT GRID: DEADLINES & PRACTICE */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start pb-space-lg">
        {/* UPCOMING DEADLINES & LIVE SESSIONS (7 cols) */}
        <div className="lg:col-span-7 flex flex-col rounded-2xl bg-surface-container-lowest shadow-sm p-space-lg gap-space-md border border-outline-variant/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-space-xs">
              <span className="material-symbols-outlined text-primary text-[24px]">event_upcoming</span>
              <h3 className="font-headline-md text-headline-md text-on-surface font-bold">Upcoming Deadlines & Live Cohorts</h3>
            </div>
            <span className="font-label-sm text-label-sm text-on-surface-variant font-semibold">2 events this week</span>
          </div>

          <div className="flex flex-col gap-space-sm">
            {upcomingEvents.map((evt) => {
              const isRsvped = rsvpState[evt.id];
              return (
                <div
                  key={evt.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-space-md rounded-xl bg-surface-container-low gap-space-md hover:bg-surface-container transition-colors border border-surface-container"
                >
                  <div className="flex items-start gap-space-sm">
                    {evt.speakerAvatar ? (
                      <div className="relative w-10 h-10 shrink-0">
                        <img className="w-10 h-10 rounded-xl object-cover" src={evt.speakerAvatar} alt={evt.speakerOrMentor} />
                        <span className="absolute -bottom-1 -right-1 w-3.5 h-3.5 rounded-full bg-secondary border-2 border-surface-container-lowest"></span>
                      </div>
                    ) : (
                      <div className="w-10 h-10 rounded-xl bg-tertiary-fixed text-on-tertiary-fixed flex items-center justify-center shrink-0">
                        <span className="material-symbols-outlined text-[22px]">assignment</span>
                      </div>
                    )}
                    <div className="flex flex-col">
                      <div className="flex items-center gap-space-xs flex-wrap">
                        <span className="font-label-md text-label-md text-on-surface font-bold">{evt.title}</span>
                        <span
                          className={`px-2 py-0.5 rounded-full font-label-sm text-label-sm font-semibold text-[11px] ${
                            evt.urgent
                              ? 'bg-error-container text-on-error-container'
                              : 'bg-surface-container-highest text-primary'
                          }`}
                        >
                          {evt.dueOrTime}
                        </span>
                      </div>
                      <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5 text-[13px]">
                        {evt.description}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center sm:self-center shrink-0">
                    {evt.type === 'live_qa' ? (
                      <button
                        type="button"
                        onClick={() => toggleRsvp(evt.id)}
                        className={`w-full sm:w-auto px-4 py-2 rounded-xl font-label-sm text-label-sm transition-all shadow-sm flex items-center justify-center gap-1.5 font-semibold ${
                          isRsvped
                            ? 'bg-secondary-fixed text-on-secondary-fixed cursor-default'
                            : 'bg-surface-container-lowest hover:bg-surface-container-high text-on-surface'
                        }`}
                      >
                        <span className="material-symbols-outlined text-[16px]">
                          {isRsvped ? 'check' : 'event_available'}
                        </span>
                        <span>{isRsvped ? 'RSVP Confirmed ✓' : 'RSVP Seat'}</span>
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="w-full sm:w-auto px-4 py-2 rounded-xl bg-primary hover:bg-primary-container text-on-primary font-label-sm text-label-sm transition-colors shadow-sm font-semibold"
                      >
                        {evt.actionText}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* PRACTICE & PEER LABS (5 cols) */}
        <div className="lg:col-span-5 flex flex-col rounded-2xl bg-surface-container-lowest shadow-sm p-space-lg gap-space-md border border-outline-variant/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-space-xs">
              <span className="material-symbols-outlined text-secondary text-[24px]">psychology</span>
              <h3 className="font-headline-md text-headline-md text-on-surface font-bold">Practice & Peer Labs</h3>
            </div>
            <span className="px-2 py-0.5 rounded bg-surface-container-low text-on-surface-variant font-code-sm text-code-sm font-semibold">
              Optional Boost
            </span>
          </div>

          <div className="flex flex-col gap-space-sm">
            {practiceLabs.map((lab) => (
              <div
                key={lab.id}
                className="group flex items-start justify-between p-space-md rounded-xl bg-surface-container-low hover:bg-surface-container transition-all border border-surface-container cursor-pointer"
              >
                <div className="flex items-start gap-space-sm">
                  <div className="w-9 h-9 rounded-lg bg-primary-fixed text-primary flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-[20px]">{lab.icon}</span>
                  </div>
                  <div className="flex flex-col">
                    <div className="flex items-center gap-1">
                      <span className="font-label-md text-label-md text-on-surface font-bold group-hover:text-primary transition-colors">
                        {lab.title}
                      </span>
                      <span className="text-xs px-1.5 py-0.2 rounded bg-surface-container-highest text-on-surface-variant font-code-sm text-[11px]">
                        {lab.duration}
                      </span>
                    </div>
                    <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5 text-[13px]">
                      {lab.description}
                    </p>
                  </div>
                </div>
                <button
                  aria-label="Start quiz"
                  className="w-8 h-8 rounded-full bg-surface-container-lowest text-on-surface hover:text-primary hover:bg-surface-container-high flex items-center justify-center transition-colors shrink-0 ml-2"
                  type="button"
                >
                  <span className="material-symbols-outlined text-[18px]">play_arrow</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
