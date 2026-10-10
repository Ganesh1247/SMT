import {
  UserProfile,
  ActiveSpotlightModule,
  DailyActivity,
  RoadmapMilestone,
  CohortEvent,
  PracticeLab,
  CourseCardData,
  VerifiedCompetency,
  CurriculumPhase
} from './types';

export const currentUser: UserProfile = {
  name: "Elena Vance",
  role: "Workforce Fellow",
  avatarUrl: "https://lh3.googleusercontent.com/aida-public/AB6AXuAKnFQ8TgHq-j0qZW0fVwXmBgCL8FA_OJRq3ZXa2Edw7UNt2u0QO94RqAvH-8U5Us5lwvuLwb1w-iwuGbSRAqFIkWaEY0ZspT9zJZn9RwLfpRMjZkWre_TfTCavmV9qNrE1lTqSOaYZggDrC7vl_Oo9mtV3LkDCQiAPgBWJVtT16o46DVLBkctJjxhcSr4qUco58bslOTvqqG_h6j07PwbuKs4Gcbb6EeX03zd0n83_16Gj8DVtGQfbHQ",
  track: "Associate to Senior PM Track",
  cohort: "Cohort #14 • Week 6",
  currentMilestone: "Product Strategy & Discovery",
  milestoneProgress: 68,
  streakDays: 5,
  streakBest: 12,
  xpBonus: 150,
  q1Target: 84
};

export const activeSpotlightModule: ActiveSpotlightModule = {
  courseTitle: "User Discovery & Qualitative Research",
  moduleTitle: "Synthesizing Customer Interview Insights & Affinity Mapping",
  subTitle: "Module 3 of 5",
  moduleIndex: 3,
  totalModules: 5,
  progressPercent: 72,
  completedLessons: 4,
  totalLessons: 6,
  estimatedMinutesLeft: 18,
  benchmarkBadge: "Preps for Senior PM Benchmark",
  imageUrl: "https://lh3.googleusercontent.com/aida-public/AB6AXuB7zOcsG2X6T6bwdDvFAq28Wtm6VLFebTrGG54g-n4nnXk04li9HQnT-eKlAAlk0EfRUPLYFFsV2QrhP9kW_ZTJ4fuvsX4FVqqI6JDK98Vi9jPeq-t5YOu7DKvqQvzetXsmUEmtzx5RAXwvmdoMzgoQvVy10g9jNFWiegrSkcZxuqGr46wECzx9TYVBGd5knDj0wAMl7AFYMky2h1ajIleJw9wwLxNZsqc5Qn3U61wGMeWuUOemkW8IqQ",
  lessons: [
    {
      id: "3.1",
      title: "3.1 Structuring Non-Biased Interview Guides",
      duration: "14m",
      status: "done"
    },
    {
      id: "3.2",
      title: "3.2 Conducting Problem Exploration Calls (Live Teardown)",
      duration: "22m",
      status: "done"
    },
    {
      id: "3.3",
      title: "3.3 Affinity Mapping & Pain-Point Hierarchy",
      duration: "Now",
      status: "active",
      notes: "Includes interactive Figma template exercise"
    },
    {
      id: "3.4",
      title: "3.4 Translating Insights into User Story Maps",
      duration: "25m",
      status: "locked"
    }
  ]
};

export const weeklyActivities: DailyActivity[] = [
  { day: 'M', hours: 0.8 },
  { day: 'T', hours: 1.2 },
  { day: 'W', hours: 1.5 },
  { day: 'T', hours: 1.0 },
  { day: 'F', hours: 0.5, isToday: true },
  { day: 'S', hours: 0.0 },
  { day: 'S', hours: 0.0 }
];

export const roadmapMilestones: RoadmapMilestone[] = [
  {
    id: "m1",
    number: "Milestone 01",
    title: "Product Fundamentals & Strategy",
    description: "Market analysis, problem sizing, PM operating rhythms, and competitive positioning matrices.",
    status: "complete",
    score: 96
  },
  {
    id: "m2",
    number: "Milestone 02",
    title: "Customer Discovery & Validation",
    description: "User interviews, JTBD frameworks, synthesis, assumption testing, and value proposition testing.",
    status: "in_progress",
    progressPercent: 68
  },
  {
    id: "m3",
    number: "Milestone 03",
    title: "Metrics, Analytics & Experiments",
    description: "A/B experiment design, North Star definition, cohort retention models, and funnel diagnostics.",
    status: "locked",
    requiresSignoff: "Requires Milestone 2 signoff"
  },
  {
    id: "m4",
    number: "Milestone 04",
    title: "Roadmapping & Stakeholder Influence",
    description: "Executive consensus building, trade-off frameworks, delivery handoffs, and Senior PM defense deck.",
    status: "locked",
    tag: "Capstone • Final Defense"
  }
];

export const upcomingEvents: CohortEvent[] = [
  {
    id: "ev1",
    title: "Sprint Assignment: Discovery Deck Review",
    type: "assignment",
    dueOrTime: "Due Tomorrow, 11:59 PM",
    description: "Submit raw audio transcripts and affinity clustering boards for review by Mentor Sarah Blake.",
    urgent: true,
    actionText: "Upload Deck"
  },
  {
    id: "ev2",
    title: "Live Q&A: Metrics That Matter",
    type: "live_qa",
    dueOrTime: "Thursday • 2:00 PM EST",
    description: "With Melissa Chen, VP of Product at FinScale. Live teardown of leading KPI trees.",
    speakerOrMentor: "Melissa Chen",
    speakerAvatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuCiOir7o6HC8MAeQ2TnoWO1eo8K6nj95HG57W5BE54PyAPUHHyEhvoW6CoKWMN54IoDROgbroiN-JBsxQQz4CJmoCq0oEjjaSoUf7V5dJ21-pJmBW9bq42aYgJMuNu6t-VD0908Inczez8kiUldt7bOT-w3_UxT0UfKaQxsmuCh5j7Ko9ZG7W0gBInNYywkNE8B7eK4ZO3pm6gGiE6ccYblFkLruagT0lEjXZn4C5-WkLtRPpE_1OX9iQ",
    actionText: "RSVP Seat"
  }
];

export const practiceLabs: PracticeLab[] = [
  {
    id: "lab1",
    title: "Product Analytics Rapid Quiz",
    category: "Analytics",
    duration: "10 min",
    description: "Test your North Star Metric knowledge & retention formula intuition.",
    icon: "quiz"
  },
  {
    id: "lab2",
    title: "PRD Teardown Peer Review",
    category: "Documentation",
    duration: "25 min",
    description: "Review a cohort peer's onboarding PRD draft and leave rubric-based feedback.",
    icon: "rate_review"
  }
];

export const catalogCourses: CourseCardData[] = [
  {
    id: "c1",
    title: "User Discovery & Qualitative Research",
    instructor: "Sarah Jenkins",
    instructorRole: "Staff PM at Figma",
    instructorInitials: "SJ",
    rating: 4.9,
    ratingCount: 1420,
    duration: "6.5 hrs",
    level: "Intermediate",
    tag: "Enrolled • In Progress",
    tagType: "in_progress",
    progress: 72,
    isBookmarked: true,
    imageUrl: "https://lh3.googleusercontent.com/aida-public/AB6AXuAZzlEcZ0dRbRIHd20lPKY1foUJejEU07fVClhavt8_BS8nctHKBzmsDl-dqb4_CilaVnEKhNEB6Yz3gmT7KYVuMl3fZAJmg9w4mU3zujqVDQwGdP_APOU49ErDtQMF0ZdGiX_VOTK737RP6PcSbKJFhlT_BxyRgwpjXbdPRbvIqwLKhc1Zk3hrwta8jZTqZ88ucvWbD4kmMwHoopB25_MtB682qBm4BunRaJmtdAWxnrKtC64RhxAz0g",
    role: "Product Management"
  },
  {
    id: "c2",
    title: "Quantitative Product Analytics & A/B Testing",
    instructor: "David Park",
    instructorRole: "Principal Data Scientist",
    instructorInitials: "DP",
    rating: 4.8,
    ratingCount: 980,
    duration: "8 hrs",
    level: "Intermediate",
    tag: "Path Core",
    tagType: "path_core",
    isBookmarked: false,
    imageUrl: "https://lh3.googleusercontent.com/aida-public/AB6AXuATmejhX_L9UutByXG3LO6CnSfvETNb9jfRB11YEl0cHFwj857gNLI5ipJSdloBy3VBqbs_ob4ycE3-1IrcoV5U8zNlGFiENTtrDSpm_qC3Oj8qZum5DtiAX3irilnjW6jRCBni27xCjL6sVqQUoAj58Pt2wu5UbGWvsoFU1Xa9zF9jDODC1FHy0wRj_ot0c3UL3WIyXrmgU1aRQYW3cmgKJ39LYHpMobwWNKoAbg2sQ08z2SVDJYwLMw",
    role: "Product Management"
  },
  {
    id: "c3",
    title: "Technical Architecture for Product Managers",
    instructor: "Alex Rivera",
    instructorRole: "Head of Engineering",
    instructorInitials: "AR",
    rating: 4.9,
    ratingCount: 2100,
    duration: "5 hrs",
    level: "Intermediate",
    tag: "Systems Lab",
    tagType: "systems_lab",
    isBookmarked: false,
    imageUrl: "https://lh3.googleusercontent.com/aida-public/AB6AXuDxK8xTECzzgWNZ4iVghOwLqwGnyX5atPU5G4mANEa0Yiv417WmquSYTl3O7qS-KrDESEpdjvEfI0DOvLWotXZcFveCLIEt1QhcaM0oyjwCYZddY9tPeYavwWJoGb4qQECezYJA--lUgqmGIMkDuo9xGRE5oylj3rHU9k8h2Rvi1cJ-qd0OLHyJ84G8bX1ucd-M0_-4XbsCfzT2pr35zS8zwrzyEH6Y-ij9jO0i0OmYrki8PIMymgcTvA",
    role: "Software Engineering"
  },
  {
    id: "c4",
    title: "Executive Storytelling & Roadmapping",
    instructor: "Rachel Moore",
    instructorRole: "VP of Product",
    instructorInitials: "RM",
    rating: 4.9,
    ratingCount: 840,
    duration: "4 hrs",
    level: "Advanced",
    tag: "Cohort Special",
    tagType: "standard",
    isBookmarked: false,
    imageUrl: "https://lh3.googleusercontent.com/aida-public/AB6AXuCiOir7o6HC8MAeQ2TnoWO1eo8K6nj95HG57W5BE54PyAPUHHyEhvoW6CoKWMN54IoDROgbroiN-JBsxQQz4CJmoCq0oEjjaSoUf7V5dJ21-pJmBW9bq42aYgJMuNu6t-VD0908Inczez8kiUldt7bOT-w3_UxT0UfKaQxsmuCh5j7Ko9ZG7W0gBInNYywkNE8B7eK4ZO3pm6gGiE6ccYblFkLruagT0lEjXZn4C5-WkLtRPpE_1OX9iQ",
    role: "Leadership"
  },
  {
    id: "c5",
    title: "SQL & Data Pipeline Fundamentals for PMs",
    instructor: "Priya Sharma",
    instructorRole: "Lead Analytics Architect",
    instructorInitials: "PS",
    rating: 4.7,
    ratingCount: 1650,
    duration: "9 hrs",
    level: "Beginner",
    tag: "Interactive Lab",
    tagType: "standard",
    isBookmarked: true,
    imageUrl: "https://lh3.googleusercontent.com/aida-public/AB6AXuB7zOcsG2X6T6bwdDvFAq28Wtm6VLFebTrGG54g-n4nnXk04li9HQnT-eKlAAlk0EfRUPLYFFsV2QrhP9kW_ZTJ4fuvsX4FVqqI6JDK98Vi9jPeq-t5YOu7DKvqQvzetXsmUEmtzx5RAXwvmdoMzgoQvVy10g9jNFWiegrSkcZxuqGr46wECzx9TYVBGd5knDj0wAMl7AFYMky2h1ajIleJw9wwLxNZsqc5Qn3U61wGMeWuUOemkW8IqQ",
    role: "Data & Analytics"
  },
  {
    id: "c6",
    title: "Design Systems & High-Fidelity UX Heuristics",
    instructor: "Lucas Bennett",
    instructorRole: "Principal Design Director",
    instructorInitials: "LB",
    rating: 4.9,
    ratingCount: 1120,
    duration: "5.5 hrs",
    level: "Intermediate",
    tag: "Studio Track",
    tagType: "standard",
    isBookmarked: false,
    imageUrl: "https://lh3.googleusercontent.com/aida-public/AB6AXuAZzlEcZ0dRbRIHd20lPKY1foUJejEU07fVClhavt8_BS8nctHKBzmsDl-dqb4_CilaVnEKhNEB6Yz3gmT7KYVuMl3fZAJmg9w4mU3zujqVDQwGdP_APOU49ErDtQMF0ZdGiX_VOTK737RP6PcSbKJFhlT_BxyRgwpjXbdPRbvIqwLKhc1Zk3hrwta8jZTqZ88ucvWbD4kmMwHoopB25_MtB682qBm4BunRaJmtdAWxnrKtC64RhxAz0g",
    role: "UX/UI Design"
  }
];

export const verifiedCompetencies: VerifiedCompetency[] = [
  {
    name: "Agile Execution",
    scorePercent: 90,
    subText: "Sprint rituals, backlog grooming, PRDs",
    status: "unlocked"
  },
  {
    name: "User Research",
    scorePercent: 85,
    subText: "Discovery interviews, persona validation",
    status: "unlocked"
  },
  {
    name: "Product Strategy",
    scorePercent: 70,
    subText: "TAM sizing, moat definitions, positioning",
    status: "in_progress"
  },
  {
    name: "Data Analysis & SQL",
    scorePercent: 60,
    subText: "Funnel metrics, A/B design, cohort retention",
    status: "in_progress"
  },
  {
    name: "Stakeholder Management & Exec Alignment",
    scorePercent: 40,
    subText: "C-suite consensus, trade-off communication (Unlocks in Phase 3)",
    status: "locked"
  }
];

export const curriculumPhases: CurriculumPhase[] = [
  {
    phaseNumber: 1,
    title: "Foundations of Product Management",
    status: "completed",
    progressPercent: 100,
    durationText: "Weeks 1 – 8 (40 Hours)",
    courses: [
      {
        id: "p1-c1",
        title: "Course 1: Product Sense & Core Frameworks",
        description: "First-principles product intuition, Kano models, CIRCLES method, and Jobs-to-be-Done mapping.",
        score: 98,
        badgeText: "Credential Issued",
        isVerified: true
      },
      {
        id: "p1-c2",
        title: "Course 2: Agile Product Ownership & User Stories",
        description: "Writing high-impact acceptance criteria, dual-track agile, sprint planning, and engineering sync.",
        score: 94,
        badgeText: "Verified",
        isVerified: true
      }
    ],
    capstone: {
      title: "Problem Brief & PRD v1",
      score: "96 / 100",
      reviewer: "Evaluated by Marcus Chen",
      feedbackQuote: "Exceptional edge-case analysis in section 3.2. User story dependencies demonstrate senior-level foresight."
    }
  },
  {
    phaseNumber: 2,
    title: "Discovery, Validation & Quantitative Analytics",
    status: "in_progress",
    progressPercent: 68,
    durationText: "Weeks 9 – 16 (44 Hours)",
    courses: [
      {
        id: "p2-c1",
        title: "Course 3: User Discovery & Qualitative Research",
        description: "Active sprint module: Synthesizing Customer Interview Insights & Affinity Mapping.",
        score: 72,
        badgeText: "In Progress"
      },
      {
        id: "p2-c2",
        title: "Course 4: Quantitative Product Analytics & A/B Testing",
        description: "Hypothesis prioritization, statistical significance calculations, and event taxonomy.",
        score: 45,
        badgeText: "Up Next"
      }
    ]
  },
  {
    phaseNumber: 3,
    title: "Strategic Roadmapping, Stakeholder Influence & Capstone Defense",
    status: "locked",
    progressPercent: 0,
    durationText: "Weeks 17 – 24 (36 Hours)",
    courses: [
      {
        id: "p3-c1",
        title: "Course 5: Technical Trade-offs & Platform Strategy",
        description: "Microservices vs monoliths, API contracts, latency budgets, and engineering empathy."
      },
      {
        id: "p3-c2",
        title: "Course 6: Senior PM Defense & Boardroom Alignment",
        description: "Final capstone portfolio defense reviewed by industry VP jury."
      }
    ]
  }
];
