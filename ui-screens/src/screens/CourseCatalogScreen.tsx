import React, { useState } from 'react';
import { CourseCardData } from '../types';

interface CourseCatalogScreenProps {
  courses: CourseCardData[];
}

export const CourseCatalogScreen: React.FC<CourseCatalogScreenProps> = ({ courses }) => {
  const [selectedRole, setSelectedRole] = useState<string>('Product Management');
  const [searchFilter, setSearchFilter] = useState<string>('');
  const [selectedLevel, setSelectedLevel] = useState<string>('Intermediate');
  const [bookmarks, setBookmarks] = useState<{ [id: string]: boolean }>({
    c1: true,
    c5: true
  });

  const roles = [
    'All Roles',
    'Product Management',
    'Data & Analytics',
    'UX/UI Design',
    'Software Engineering',
    'Leadership'
  ];

  const quickTopics = [
    'SQL',
    'Product Discovery',
    'System Design',
    'UX Heuristics',
    'Financial Modeling'
  ];

  const toggleBookmark = (id: string) => {
    setBookmarks((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const filteredCourses = courses.filter((c) => {
    const matchesRole = selectedRole === 'All Roles' || c.role === selectedRole;
    const matchesSearch =
      searchFilter === '' ||
      c.title.toLowerCase().includes(searchFilter.toLowerCase()) ||
      c.instructor.toLowerCase().includes(searchFilter.toLowerCase());
    return matchesRole && matchesSearch;
  });

  return (
    <div className="flex flex-col w-full">
      {/* Top Command & Header Tier */}
      <section className="flex flex-col gap-space-lg mb-space-xl">
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-space-md">
          <div className="max-w-3xl flex flex-col gap-space-xs">
            <div className="flex items-center gap-space-xs text-primary font-label-sm text-label-sm uppercase tracking-wider font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
              Enterprise Catalog • Spring Term 2025
            </div>
            <h1 className="font-headline-xl text-headline-xl text-on-surface tracking-tight font-bold">
              Explore Courses & Learning Paths
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">
              Browse over 250+ role-based courses, interactive skill labs, and certified career tracks taught by leading practitioners.
            </p>
          </div>
          <div className="flex items-center gap-space-sm">
            <div className="px-space-md py-space-xs rounded-xl bg-surface-container-low flex items-center gap-space-xs text-on-surface-variant border border-surface-container">
              <span className="material-symbols-outlined text-[18px] text-secondary">workspace_premium</span>
              <span className="font-label-sm text-label-sm">
                Enterprise License: <span className="text-on-surface font-bold">Active</span>
              </span>
            </div>
          </div>
        </div>

        {/* Search Hero Bar */}
        <div className="bg-surface-container-lowest p-space-md rounded-2xl shadow-sm flex flex-col gap-space-md border border-outline-variant/30">
          <div className="relative flex items-center w-full">
            <span className="material-symbols-outlined absolute left-space-md text-on-surface-variant text-[24px]">
              search
            </span>
            <input
              type="text"
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              placeholder="Search by competency, tool, mentor, or syllabus topics..."
              className="w-full pl-12 pr-28 py-3 rounded-xl bg-surface-container-low text-on-surface placeholder:text-on-surface-variant/70 font-body-md text-body-md focus:bg-surface-container-lowest focus:outline-none transition-all border border-transparent focus:border-primary/30"
            />
            <div className="absolute right-space-sm flex items-center gap-space-xs">
              <span className="hidden md:inline-flex items-center px-space-xs py-0.5 rounded font-code-sm text-code-sm bg-surface-container-high text-on-surface-variant text-[11px]">
                ⌘K
              </span>
              <button
                type="button"
                className="px-space-md py-2 rounded-lg bg-primary hover:bg-primary-container text-on-primary font-label-md text-label-md transition-all active:scale-[0.98] font-semibold"
              >
                Search
              </button>
            </div>
          </div>

          {/* Quick Filter Tags */}
          <div className="flex flex-wrap items-center gap-space-xs pt-1">
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase mr-space-xs tracking-wider font-semibold">
              Quick Topics:
            </span>
            {quickTopics.map((topic) => (
              <button
                key={topic}
                type="button"
                onClick={() => setSearchFilter(topic === searchFilter ? '' : topic)}
                className={`quick-tag px-space-sm py-1 rounded-full font-label-sm text-label-sm transition-colors text-[12px] font-medium ${
                  searchFilter === topic
                    ? 'bg-primary-fixed text-primary shadow-sm font-semibold'
                    : 'bg-surface-container text-on-surface hover:bg-primary-fixed hover:text-primary'
                }`}
              >
                {topic}
              </button>
            ))}
          </div>
        </div>

        {/* Role Filter Navigation Tabs */}
        <div className="flex items-center gap-space-xs overflow-x-auto pb-1 -mx-2 px-2 scrollbar-none">
          {roles.map((role) => {
            const isActive = selectedRole === role;
            return (
              <button
                key={role}
                type="button"
                onClick={() => setSelectedRole(role)}
                className={`px-space-lg py-2.5 rounded-xl font-label-md text-label-md transition-all whitespace-nowrap font-medium ${
                  isActive
                    ? 'bg-primary text-on-primary font-semibold shadow-sm'
                    : 'text-on-surface-variant hover:bg-surface-container-low'
                }`}
              >
                {role}
              </button>
            );
          })}
        </div>
      </section>

      {/* Workspace Grid: Sidebar & Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-xl items-start">
        {/* Filter Sidebar (Cols 1-3) */}
        <aside className="lg:col-span-3 bg-surface-container-lowest p-space-lg rounded-2xl shadow-sm flex flex-col gap-space-lg border border-outline-variant/30">
          <div className="flex items-center justify-between pb-space-sm">
            <div className="flex items-center gap-space-xs">
              <span className="material-symbols-outlined text-[20px] text-primary">tune</span>
              <span className="font-headline-md text-headline-md text-on-surface font-bold">Filters</span>
            </div>
            <button
              type="button"
              onClick={() => {
                setSearchFilter('');
                setSelectedRole('All Roles');
              }}
              className="font-label-sm text-label-sm text-primary hover:underline transition-all font-semibold"
            >
              Reset Filters
            </button>
          </div>

          {/* Skill & Competency */}
          <div className="flex flex-col gap-space-xs">
            <span className="font-label-md text-label-md text-on-surface uppercase tracking-wider text-[11px] font-bold">
              Skill & Competency
            </span>
            <div className="flex flex-col gap-2 pt-1">
              {[
                { name: 'Product Discovery', count: 24, checked: true },
                { name: 'Wireframing', count: 11, checked: false },
                { name: 'Python & SQL', count: 19, checked: false },
                { name: 'A/B Testing', count: 8, checked: true },
                { name: 'Scrum & Agile', count: 15, checked: false },
                { name: 'Leadership', count: 14, checked: false },
              ].map((item, idx) => (
                <label key={idx} className="flex items-center justify-between cursor-pointer group">
                  <div className="flex items-center gap-space-xs">
                    <input
                      type="checkbox"
                      defaultChecked={item.checked}
                      className="w-4 h-4 rounded text-primary focus:ring-0 accent-primary"
                    />
                    <span className="font-body-sm text-body-sm text-on-surface group-hover:text-primary transition-colors text-[13px]">
                      {item.name}
                    </span>
                  </div>
                  <span className="font-code-sm text-code-sm text-on-surface-variant text-[11px]">{item.count}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="w-full h-[1px] bg-surface-container"></div>

          {/* Experience Level */}
          <div className="flex flex-col gap-space-xs">
            <span className="font-label-md text-label-md text-on-surface uppercase tracking-wider text-[11px] font-bold">
              Experience Level
            </span>
            <div className="flex flex-col gap-2 pt-1">
              {['Beginner', 'Intermediate', 'Advanced'].map((lvl) => (
                <label key={lvl} className="flex items-center justify-between cursor-pointer group">
                  <div className="flex items-center gap-space-xs">
                    <input
                      type="checkbox"
                      checked={selectedLevel === lvl}
                      onChange={() => setSelectedLevel(lvl)}
                      className="w-4 h-4 rounded text-primary focus:ring-0 accent-primary"
                    />
                    <span className="font-body-sm text-body-sm text-on-surface group-hover:text-primary transition-colors text-[13px]">
                      {lvl}
                    </span>
                  </div>
                  <span className="font-code-sm text-code-sm text-on-surface-variant text-[11px]">
                    {lvl === 'Intermediate' ? 22 : lvl === 'Beginner' ? 18 : 8}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="w-full h-[1px] bg-surface-container"></div>

          {/* Format */}
          <div className="flex flex-col gap-space-xs">
            <span className="font-label-md text-label-md text-on-surface uppercase tracking-wider text-[11px] font-bold">
              Format
            </span>
            <div className="flex flex-col gap-2 pt-1">
              {[
                { name: 'Self-paced', count: 32, checked: true },
                { name: 'Cohort-based', count: 6, checked: false },
                { name: 'Interactive Lab', count: 7, checked: false },
                { name: 'Video Course', count: 25, checked: false },
              ].map((fmt, idx) => (
                <label key={idx} className="flex items-center justify-between cursor-pointer group">
                  <div className="flex items-center gap-space-xs">
                    <input
                      type="checkbox"
                      defaultChecked={fmt.checked}
                      className="w-4 h-4 rounded text-primary focus:ring-0 accent-primary"
                    />
                    <span className="font-body-sm text-body-sm text-on-surface group-hover:text-primary transition-colors text-[13px]">
                      {fmt.name}
                    </span>
                  </div>
                  <span className="font-code-sm text-code-sm text-on-surface-variant text-[11px]">{fmt.count}</span>
                </label>
              ))}
            </div>
          </div>
        </aside>

        {/* Main Catalog Viewport (Cols 4-12) */}
        <div className="lg:col-span-9 flex flex-col gap-space-lg">
          {/* Sub-Bar: Meta count, Active Filter Chips, Sort Dropdown */}
          <div className="bg-surface-container-lowest p-space-md rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-space-md border border-outline-variant/30">
            <div className="flex flex-wrap items-center gap-space-xs">
              <span className="font-label-md text-label-md text-on-surface font-bold mr-space-xs">
                Showing {filteredCourses.length} courses
              </span>
              <div className="flex items-center gap-1.5 px-space-sm py-1 rounded-full bg-primary-fixed text-primary font-label-sm text-label-sm font-semibold text-[12px]">
                <span>Role: {selectedRole}</span>
              </div>
              <div className="flex items-center gap-1.5 px-space-sm py-1 rounded-full bg-primary-fixed text-primary font-label-sm text-label-sm font-semibold text-[12px]">
                <span>Level: {selectedLevel}</span>
              </div>
            </div>

            {/* Sort Select */}
            <div className="flex items-center gap-space-xs shrink-0">
              <span className="font-label-sm text-label-sm text-on-surface-variant">Sort by:</span>
              <div className="relative">
                <select className="appearance-none bg-surface-container-low text-on-surface font-label-md text-label-md pl-space-md pr-8 py-1.5 rounded-xl focus:outline-none cursor-pointer border border-surface-container">
                  <option defaultValue="popular">Most Popular</option>
                  <option>Highest Rated</option>
                  <option>Newest</option>
                  <option>Duration: Shortest First</option>
                </select>
                <span className="material-symbols-outlined pointer-events-none absolute right-2 top-2 text-[18px] text-on-surface-variant">
                  expand_more
                </span>
              </div>
            </div>
          </div>

          {/* Courses Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-space-lg">
            {filteredCourses.map((c) => {
              const isBookmarked = !!bookmarks[c.id];
              return (
                <div
                  key={c.id}
                  className="bg-surface-container-lowest rounded-2xl shadow-sm hover:shadow-md transition-all duration-300 flex flex-col overflow-hidden group border border-outline-variant/30"
                >
                  <div className="relative h-44 w-full overflow-hidden bg-surface-container">
                    <img
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      src={c.imageUrl}
                      alt={c.title}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>

                    {/* Tag badge */}
                    <div className="absolute top-space-sm left-space-sm flex items-center gap-1.5 px-space-sm py-1 rounded-full bg-secondary text-on-secondary font-label-sm text-label-sm shadow-sm font-semibold text-[11px]">
                      {c.tagType === 'in_progress' ? (
                        <>
                          <span className="w-1.5 h-1.5 rounded-full bg-secondary-fixed animate-ping"></span>
                          Enrolled • In Progress
                        </>
                      ) : (
                        <span>{c.tag}</span>
                      )}
                    </div>

                    <div className="absolute bottom-space-sm left-space-sm right-space-sm flex items-center justify-between text-white font-label-sm text-label-sm text-[12px]">
                      <span className="flex items-center gap-1 bg-black/40 backdrop-blur-md px-2 py-0.5 rounded-md">
                        <span className="material-symbols-outlined text-[14px]">schedule</span> {c.duration}
                      </span>
                      <span className="bg-black/40 backdrop-blur-md px-2 py-0.5 rounded-md font-medium">
                        {c.level}
                      </span>
                    </div>
                  </div>

                  <div className="p-space-lg flex flex-col flex-1 justify-between gap-space-md">
                    <div className="flex flex-col gap-space-xs">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1 text-[#d97706]">
                          <span className="material-symbols-outlined text-[16px]">star</span>
                          <span className="font-label-sm text-label-sm font-bold text-on-surface">{c.rating}</span>
                          <span className="font-body-sm text-body-sm text-on-surface-variant text-[12px]">
                            ({c.ratingCount})
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => toggleBookmark(c.id)}
                          className="text-on-surface-variant hover:text-primary transition-colors"
                        >
                          <span className="material-symbols-outlined text-[20px]">
                            {isBookmarked ? 'bookmark' : 'bookmark_border'}
                          </span>
                        </button>
                      </div>

                      <h2 className="font-title-sm text-title-sm text-on-surface group-hover:text-primary transition-colors line-clamp-2 font-bold">
                        {c.title}
                      </h2>

                      <div className="flex items-center gap-2 mt-1">
                        <div className="w-6 h-6 rounded-full bg-primary-fixed flex items-center justify-center font-label-sm text-label-sm text-primary font-bold text-[10px]">
                          {c.instructorInitials}
                        </div>
                        <div className="flex flex-col">
                          <span className="font-label-sm text-label-sm text-on-surface leading-tight font-semibold">
                            {c.instructor}
                          </span>
                          <span className="font-body-sm text-body-sm text-on-surface-variant text-[11px] leading-tight">
                            {c.instructorRole}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Footer Actions */}
                    {c.progress ? (
                      <div className="flex flex-col gap-2 pt-space-xs">
                        <div className="flex items-center justify-between font-label-sm text-label-sm text-[12px]">
                          <span className="text-on-surface-variant">Course Progress</span>
                          <span className="text-primary font-bold">{c.progress}%</span>
                        </div>
                        <div className="w-full h-2 rounded-full bg-surface-container overflow-hidden">
                          <div
                            className="bg-primary h-full rounded-full transition-all duration-500"
                            style={{ width: `${c.progress}%` }}
                          ></div>
                        </div>
                        <button
                          type="button"
                          className="mt-2 w-full py-2.5 rounded-xl bg-primary hover:bg-primary-container text-on-primary font-label-md text-label-md transition-all active:scale-[0.98] flex items-center justify-center gap-space-xs shadow-sm font-semibold"
                        >
                          <span className="material-symbols-outlined text-[18px]">play_arrow</span>
                          Resume Course
                        </button>
                      </div>
                    ) : (
                      <div className="pt-space-xs">
                        <button
                          type="button"
                          className="w-full py-2.5 rounded-xl bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-label-md text-label-md transition-all active:scale-[0.98] flex items-center justify-center gap-space-xs font-semibold"
                        >
                          <span className="material-symbols-outlined text-[18px] text-secondary">verified</span>
                          Enroll (Included in Path)
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
