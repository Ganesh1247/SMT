import React from 'react';
import { NavigationTab, UserProfile } from '../types';

interface SidebarProps {
  currentTab: NavigationTab;
  onSelectTab: (tab: NavigationTab) => void;
  user: UserProfile;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, user }) => {
  const mainNavItems: { id: NavigationTab; label: string; icon: string }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: 'dashboard' },
    { id: 'my-learning-path', label: 'My Learning Path', icon: 'route' },
    { id: 'course-catalog', label: 'Course Catalog', icon: 'menu_book' },
    { id: 'assignments-and-practice', label: 'Assignments & Practice', icon: 'assignment_turned_in' },
    { id: 'skills-and-progress', label: 'Skills & Progress', icon: 'trending_up' },
    { id: 'calendar', label: 'Calendar', icon: 'calendar_today' },
    { id: 'certificates-and-badges', label: 'Certificates & Badges', icon: 'verified' },
  ];

  const secondaryNavItems: { id: NavigationTab; label: string; icon: string }[] = [
    { id: 'help-and-resources', label: 'Help & Resources', icon: 'help' },
    { id: 'settings', label: 'Settings', icon: 'settings' },
  ];

  return (
    <aside className="fixed left-0 top-0 h-full w-72 bg-surface-container-lowest shadow-[0_1px_8px_rgba(0,0,0,0.04)] z-50 flex flex-col justify-between py-space-md transition-all duration-300 border-r border-outline-variant/30">
      <div className="flex flex-col">
        {/* Brand Logo and Title */}
        <div className="px-space-lg py-space-sm flex items-center justify-between">
          <div className="flex items-center gap-space-sm cursor-pointer" onClick={() => onSelectTab('dashboard')}>
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary font-bold">
              <span className="material-symbols-outlined text-[22px]">school</span>
            </div>
            <span className="font-title-sm text-title-sm font-bold text-primary tracking-tight">Pathway LMS</span>
          </div>
          <button
            aria-label="Toggle sidebar"
            className="text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low rounded-lg p-space-xs transition-colors"
            type="button"
          >
            <span className="material-symbols-outlined text-[20px]">menu_open</span>
          </button>
        </div>

        {/* View Switcher Pill */}
        <div className="px-space-lg my-space-md">
          <button
            className="w-full flex items-center justify-between px-space-md py-space-xs rounded-full bg-surface-container-low text-on-surface hover:bg-surface-container transition-colors"
            type="button"
          >
            <div className="flex items-center gap-space-sm">
              <span className="w-2 h-2 rounded-full bg-secondary"></span>
              <span className="font-label-sm text-label-sm uppercase font-semibold text-on-surface tracking-wider">Learner View</span>
            </div>
            <span className="material-symbols-outlined text-[16px] text-on-surface-variant">unfold_more</span>
          </button>
        </div>

        {/* Main Navigation List */}
        <nav className="flex flex-col px-space-md gap-1">
          {mainNavItems.map((item) => {
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center gap-space-sm px-space-md py-2.5 rounded-xl font-label-md text-label-md transition-all text-left ${
                  isActive
                    ? 'bg-primary text-on-primary font-semibold shadow-sm'
                    : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
                }`}
              >
                <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            );
          })}

          <div className="h-[1px] bg-surface-container-high my-space-sm mx-space-md"></div>

          {secondaryNavItems.map((item) => {
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center gap-space-sm px-space-md py-2 rounded-xl font-label-md text-label-md transition-all text-left ${
                  isActive
                    ? 'bg-primary text-on-primary font-semibold shadow-sm'
                    : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
                }`}
              >
                <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Target Progress Box */}
      <div className="px-space-lg pt-space-md">
        <div className="p-space-md rounded-xl bg-surface-container-low flex flex-col gap-space-xs border border-surface-container">
          <div className="flex items-center justify-between">
            <span className="font-label-sm text-label-sm text-on-surface font-semibold">Q1 Target</span>
            <span className="font-code-sm text-code-sm text-primary font-bold">{user.q1Target}%</span>
          </div>
          <div className="w-full h-1.5 rounded-full bg-surface-container-high overflow-hidden">
            <div
              className="bg-secondary h-full rounded-full transition-all duration-500"
              style={{ width: `${user.q1Target}%` }}
            ></div>
          </div>
          <p className="font-label-sm text-label-sm text-on-surface-variant text-[11px]">3 milestones remaining</p>
        </div>
      </div>
    </aside>
  );
};
