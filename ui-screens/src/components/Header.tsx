import React, { useState } from 'react';
import { UserProfile, NavigationTab } from '../types';

interface HeaderProps {
  currentTab: NavigationTab;
  user: UserProfile;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onSelectTab: (tab: NavigationTab) => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  user,
  searchQuery,
  onSearchChange,
  onSelectTab
}) => {
  const [showNotifications, setShowNotifications] = useState(false);

  const getBreadcrumbLabel = () => {
    switch (currentTab) {
      case 'dashboard':
        return 'Overview';
      case 'my-learning-path':
        return 'Career Path Roadmap';
      case 'course-catalog':
        return 'Course Catalog';
      case 'assignments-and-practice':
        return 'Assignments & Practice';
      case 'skills-and-progress':
        return 'Skills & Radar';
      default:
        return 'Overview';
    }
  };

  return (
    <header className="fixed top-0 left-72 right-0 h-16 bg-surface/90 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)] z-40 flex items-center justify-between px-space-lg border-b border-outline-variant/30">
      {/* Breadcrumbs */}
      <div className="flex items-center gap-space-md">
        <nav className="flex items-center gap-space-xs font-label-md text-label-md text-on-surface-variant">
          <button
            onClick={() => onSelectTab('dashboard')}
            className="hover:text-on-surface transition-colors font-medium"
          >
            LMS
          </button>
          <span className="material-symbols-outlined text-[16px] text-outline">chevron_right</span>
          <span className="text-on-surface font-semibold">{getBreadcrumbLabel()}</span>
        </nav>
      </div>

      {/* Header Actions */}
      <div className="flex items-center gap-space-md">
        {/* Quick Search */}
        <div className="relative flex items-center">
          <div className="flex items-center bg-surface-container-lowest px-space-md py-1.5 rounded-xl shadow-[0_1px_4px_rgba(0,0,0,0.04)] text-on-surface-variant hover:text-on-surface transition-all w-64 justify-between border border-outline-variant/40">
            <div className="flex items-center gap-space-xs w-full">
              <span className="material-symbols-outlined text-[18px] text-on-surface-variant">search</span>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                placeholder="Quick search..."
                className="bg-transparent border-none outline-none font-body-sm text-body-sm text-on-surface placeholder:text-on-surface-variant/70 w-full"
              />
            </div>
            <kbd className="font-code-sm text-code-sm bg-surface-container-high text-on-surface-variant px-1.5 py-0.5 rounded font-medium text-[11px] shrink-0">
              ⌘K
            </kbd>
          </div>
        </div>

        {/* Notifications */}
        <div className="relative">
          <button
            aria-label="Notifications"
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 rounded-xl bg-surface-container-lowest hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors relative flex items-center justify-center border border-outline-variant/40"
            type="button"
          >
            <span className="material-symbols-outlined text-[22px]">notifications</span>
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-error ring-2 ring-surface-container-lowest"></span>
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 rounded-xl bg-surface-container-lowest shadow-lg border border-outline-variant/40 p-space-md flex flex-col gap-2 z-50">
              <div className="flex items-center justify-between pb-1 border-b border-surface-container">
                <span className="font-label-md text-label-md font-bold text-on-surface">Notifications</span>
                <span className="font-code-sm text-code-sm text-primary font-semibold">2 New</span>
              </div>
              <div className="p-2 rounded-lg bg-surface-container-low hover:bg-surface-container transition-colors">
                <span className="font-label-sm text-label-sm font-semibold text-on-surface block">Assignment due tomorrow</span>
                <span className="font-body-sm text-body-sm text-on-surface-variant text-[12px] block">Discovery Deck review deadline at 11:59 PM.</span>
              </div>
              <div className="p-2 rounded-lg bg-surface-container-low hover:bg-surface-container transition-colors">
                <span className="font-label-sm text-label-sm font-semibold text-on-surface block">Live Q&A Session</span>
                <span className="font-body-sm text-body-sm text-on-surface-variant text-[12px] block">With Melissa Chen on Thursday.</span>
              </div>
            </div>
          )}
        </div>

        {/* User Profile Badge */}
        <div className="flex items-center gap-space-sm pl-1 pr-space-md py-1 bg-surface-container-lowest rounded-full shadow-[0_1px_4px_rgba(0,0,0,0.04)] border border-outline-variant/40 cursor-pointer">
          <img
            alt={user.name}
            className="w-8 h-8 rounded-full object-cover"
            src={user.avatarUrl}
          />
          <div className="flex flex-col text-left">
            <span className="font-label-sm text-label-sm text-on-surface font-semibold leading-tight">{user.name}</span>
            <span className="font-label-sm text-label-sm text-on-surface-variant text-[11px] leading-tight">{user.role}</span>
          </div>
          <span className="material-symbols-outlined text-[16px] text-on-surface-variant ml-1">expand_more</span>
        </div>
      </div>
    </header>
  );
};
