"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { AnswerPayload, AssessmentResult, Question } from "@/lib/types";

const MAX_QUESTIONS = 10;
const STORAGE_KEY = "career_assessment_state_v1";

type PersistedState = {
  sessionId: string | null;
  currentQuestion: Question | null;
  answers: AnswerRecord[];
  result: AssessmentResult | null;
};

function readPersistedState(): PersistedState {
  if (typeof window === "undefined") {
    return { sessionId: null, currentQuestion: null, answers: [], result: null };
  }
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return { sessionId: null, currentQuestion: null, answers: [], result: null };
    const parsed = JSON.parse(raw) as PersistedState;
    return {
      sessionId: parsed.sessionId ?? null,
      currentQuestion: parsed.currentQuestion ?? null,
      answers: Array.isArray(parsed.answers) ? parsed.answers : [],
      result: parsed.result ?? null,
    };
  } catch {
    return { sessionId: null, currentQuestion: null, answers: [], result: null };
  }
}

function writePersistedState(data: PersistedState) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch {
    /* ignore storage failures */
  }
}

export type AnswerRecord = { questionId: string; value: AnswerPayload };

type AssessmentContextValue = {
  sessionId: string | null;
  currentQuestion: Question | null;
  answers: AnswerRecord[];
  result: AssessmentResult | null;
  maxQuestions: number;
  setSessionFromStart: (sessionId: string, question: Question) => void;
  setNextQuestion: (question: Question | null) => void;
  appendAnswer: (questionId: string, value: AnswerPayload) => void;
  setResult: (result: AssessmentResult) => void;
  resetAssessment: () => void;
};

const AssessmentContext = createContext<AssessmentContextValue | null>(null);

export function AssessmentProvider({ children }: { children: ReactNode }) {
  const persisted = readPersistedState();
  const [sessionId, setSessionId] = useState<string | null>(persisted.sessionId);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(persisted.currentQuestion);
  const [answers, setAnswers] = useState<AnswerRecord[]>(persisted.answers);
  const [result, setResultState] = useState<AssessmentResult | null>(persisted.result);

  const setSessionFromStart = useCallback((id: string, question: Question) => {
    setSessionId(id);
    setCurrentQuestion(question);
    setAnswers([]);
    setResultState(null);
    writePersistedState({
      sessionId: id,
      currentQuestion: question,
      answers: [],
      result: null,
    });
  }, []);

  const setNextQuestion = useCallback((question: Question | null) => {
    setCurrentQuestion(question);
    writePersistedState({
      sessionId,
      currentQuestion: question,
      answers,
      result,
    });
  }, [sessionId, answers, result]);

  const appendAnswer = useCallback((questionId: string, value: AnswerPayload) => {
    setAnswers((prev) => {
      const nextAnswers = [...prev, { questionId, value }];
      writePersistedState({
        sessionId,
        currentQuestion,
        answers: nextAnswers,
        result,
      });
      return nextAnswers;
    });
  }, [sessionId, currentQuestion, result]);

  const setResult = useCallback((r: AssessmentResult) => {
    setResultState(r);
    setCurrentQuestion(null);
    writePersistedState({
      sessionId,
      currentQuestion: null,
      answers,
      result: r,
    });
  }, [sessionId, answers]);

  const resetAssessment = useCallback(() => {
    setSessionId(null);
    setCurrentQuestion(null);
    setAnswers([]);
    setResultState(null);
    writePersistedState({
      sessionId: null,
      currentQuestion: null,
      answers: [],
      result: null,
    });
  }, []);

  const value = useMemo(
    () => ({
      sessionId,
      currentQuestion,
      answers,
      result,
      maxQuestions: MAX_QUESTIONS,
      setSessionFromStart,
      setNextQuestion,
      appendAnswer,
      setResult,
      resetAssessment,
    }),
    [
      sessionId,
      currentQuestion,
      answers,
      result,
      setSessionFromStart,
      setNextQuestion,
      appendAnswer,
      setResult,
      resetAssessment,
    ]
  );

  return (
    <AssessmentContext.Provider value={value}>
      {children}
    </AssessmentContext.Provider>
  );
}

export function useAssessment() {
  const ctx = useContext(AssessmentContext);
  if (!ctx) {
    throw new Error("useAssessment must be used within AssessmentProvider");
  }
  return ctx;
}
