import React, { useState } from 'react';
import { NavigationTab } from './types';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardScreen } from './screens/DashboardScreen';
import { CourseCatalogScreen } from './screens/CourseCatalogScreen';
import { LearningPathScreen } from './screens/LearningPathScreen';
import {
  currentUser,
  activeSpotlightModule,
  weeklyActivities,
  roadmapMilestones,
  upcomingEvents,
  practiceLabs,
  catalogCourses,
  verifiedCompetencies,
  curriculumPhases
} from './mockData';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavigationTab>('dashboard');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const renderActiveScreen = () => {
    switch (currentTab) {
      case 'dashboard':
        return (
          <DashboardScreen
            user={currentUser}
            module={activeSpotlightModule}
            weeklyActivities={weeklyActivities}
            roadmapMilestones={roadmapMilestones}
            upcomingEvents={upcomingEvents}
            practiceLabs={practiceLabs}
            onNavigate={setCurrentTab}
          />
        );
      case 'my-learning-path':
        return (
          <LearningPathScreen
            competencies={verifiedCompetencies}
            phases={curriculumPhases}
          />
        );
      case 'course-catalog':
        return (
          <CourseCatalogScreen
            courses={catalogCourses}
          />
        );
      default:
        return (
          <DashboardScreen
            user={currentUser}
            module={activeSpotlightModule}
            weeklyActivities={weeklyActivities}
            roadmapMilestones={roadmapMilestones}
            upcomingEvents={upcomingEvents}
            practiceLabs={practiceLabs}
            onNavigate={setCurrentTab}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-background font-body-md text-body-md text-on-surface antialiased flex flex-col">
      {/* Fixed Left Navigation Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        user={currentUser}
      />

      {/* Main Content Area */}
      <div className="pl-72 flex-1 flex flex-col">
        {/* Top Header Bar */}
        <Header
          currentTab={currentTab}
          user={currentUser}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onSelectTab={setCurrentTab}
        />

        {/* Dynamic Screen Viewport */}
        <main className="w-full pt-16 bg-background px-space-lg py-space-lg min-h-screen">
          {renderActiveScreen()}
        </main>
      </div>
    </div>
  );
};

export default App;
