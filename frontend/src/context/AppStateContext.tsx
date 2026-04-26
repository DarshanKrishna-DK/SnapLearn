import { createContext, useContext, useMemo, useState, useCallback, useEffect, type ReactNode } from 'react';
import { useLocalStorage } from '@/hooks/useLocalStorage';
import type { GradeLevel, LanguageCode } from '@/types';
import { defaultGrade, defaultLanguage, healthCheck } from '@/lib/api';

type Ctx = {
  studentId: string;
  setStudentId: (s: string) => void;
  gradeLevel: GradeLevel;
  setGradeLevel: (g: GradeLevel) => void;
  language: LanguageCode;
  setLanguage: (l: LanguageCode) => void;
  /** Increment after quiz (or any server-side profile change) so Profile and other views refetch. */
  profileRevision: number;
  bumpProfile: () => void;
  apiOnline: boolean | null;
  refreshApi: () => void;
  checking: boolean;
};

const AppStateContext = createContext<Ctx | null>(null);

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [saved, setSaved] = useLocalStorage('snaplearn-v2', {
    studentId: 'presentation-demo',
    gradeLevel: '10' as GradeLevel,
    language: 'en' as LanguageCode,
  });
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [checking, setChecking] = useState(true);
  const [profileRevision, setProfileRevision] = useState(0);
  const bumpProfile = useCallback(() => setProfileRevision((n) => n + 1), []);

  const syncLanding = useCallback(() => {
    const g = localStorage.getItem('selectedGrade');
    const l = localStorage.getItem('selectedLanguage');
    if (g && ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'].includes(g)) {
      setSaved((p) => ({ ...p, gradeLevel: g as GradeLevel }));
      localStorage.removeItem('selectedGrade');
    }
    if (l) {
      const ll = defaultLanguage(l);
      setSaved((p) => ({ ...p, language: ll }));
      localStorage.removeItem('selectedLanguage');
    }
  }, [setSaved]);

  useEffect(() => {
    syncLanding();
  }, [syncLanding]);

  const refreshApi = useCallback(() => {
    setChecking(true);
    void healthCheck()
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false))
      .finally(() => setChecking(false));
  }, []);

  useEffect(() => {
    refreshApi();
  }, [refreshApi]);

  const setStudentId = useCallback((studentId: string) => setSaved((p) => ({ ...p, studentId })), [setSaved]);
  const setGradeLevel = useCallback(
    (gradeLevel: GradeLevel) => setSaved((p) => ({ ...p, gradeLevel })),
    [setSaved]
  );
  const setLanguage = useCallback(
    (language: LanguageCode) => setSaved((p) => ({ ...p, language })),
    [setSaved]
  );

  const v = useMemo<Ctx>(
    () => ({
      studentId: saved.studentId,
      setStudentId,
      gradeLevel: defaultGrade(saved.gradeLevel),
      setGradeLevel,
      language: defaultLanguage(saved.language),
      setLanguage,
      profileRevision,
      bumpProfile,
      apiOnline,
      refreshApi,
      checking,
    }),
    [saved, setStudentId, setGradeLevel, setLanguage, profileRevision, bumpProfile, apiOnline, checking, refreshApi]
  );

  return <AppStateContext.Provider value={v}>{children}</AppStateContext.Provider>;
}

export function useAppState() {
  const c = useContext(AppStateContext);
  if (!c) throw new Error('useAppState outside provider');
  return c;
}
