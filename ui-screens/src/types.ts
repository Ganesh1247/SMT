export type NavigationTab = 
  | 'dashboard'
  | 'my-learning-path'
  | 'course-catalog'
  | 'assignments-and-practice'
  | 'skills-and-progress'
  | 'calendar'
  | 'certificates-and-badges'
  | 'help-and-resources'
  | 'settings';

export interface UserProfile {
  name: string;
  role: string;
  avatarUrl: string;
  track: string;
  cohort: string;
  currentMilestone: string;
  milestoneProgress: number;
  streakDays: number;
  streakBest: number;
  xpBonus: number;
  q1Target: number;
}

export interface LessonChecklistItem {
  id: string;
  title: string;
  duration: string;
  status: 'done' | 'active' | 'locked';
  notes?: string;
}

export interface ActiveSpotlightModule {
  courseTitle: string;
  moduleTitle: string;
  subTitle: string;
  moduleIndex: number;
  totalModules: number;
  progressPercent: number;
  completedLessons: number;
  totalLessons: number;
  estimatedMinutesLeft: number;
  benchmarkBadge: string;
  imageUrl: string;
  lessons: LessonChecklistItem[];
}

export interface DailyActivity {
  day: 'M' | 'T' | 'W' | 'T' | 'F' | 'S' | 'S';
  hours: number;
  isToday?: boolean;
}

export interface RoadmapMilestone {
  id: string;
  number: string;
  title: string;
  description: string;
  status: 'complete' | 'in_progress' | 'locked';
  score?: number;
  progressPercent?: number;
  requiresSignoff?: string;
  tag?: string;
}

export interface CohortEvent {
  id: string;
  title: string;
  type: 'assignment' | 'live_qa' | 'workshop';
  dueOrTime: string;
  description: string;
  speakerOrMentor?: string;
  speakerAvatar?: string;
  urgent?: boolean;
  actionText: string;
}

export interface PracticeLab {
  id: string;
  title: string;
  category: string;
  duration: string;
  description: string;
  icon: string;
  isCompleted?: boolean;
}

export interface CourseCardData {
  id: string;
  title: string;
  instructor: string;
  instructorRole: string;
  instructorAvatar?: string;
  instructorInitials?: string;
  rating: number;
  ratingCount: number;
  duration: string;
  level: 'Beginner' | 'Intermediate' | 'Advanced';
  tag: string;
  tagType: 'in_progress' | 'path_core' | 'systems_lab' | 'partner' | 'standard';
  progress?: number;
  isBookmarked?: boolean;
  imageUrl: string;
  role: string;
}

export interface VerifiedCompetency {
  name: string;
  scorePercent: number;
  subText: string;
  status: 'unlocked' | 'in_progress' | 'locked';
}

export interface CurriculumPhase {
  phaseNumber: number;
  title: string;
  status: 'completed' | 'in_progress' | 'locked';
  progressPercent: number;
  durationText: string;
  courses: {
    id: string;
    title: string;
    description: string;
    score?: number;
    badgeText?: string;
    isVerified?: boolean;
  }[];
  capstone?: {
    title: string;
    score: string;
    reviewer: string;
    feedbackQuote: string;
  };
}
