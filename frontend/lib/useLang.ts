'use client'

import { useState, useEffect, useCallback } from 'react'
import type { Lang } from '@/components/landing/translations'

const STORAGE_KEY = 'lifeos-lang'
const DEFAULT_LANG: Lang = 'en'

function readLang(): Lang {
  if (typeof window === 'undefined') return DEFAULT_LANG
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'en' || stored === 'zh' || stored === 'ko') return stored
  return DEFAULT_LANG
}

export function useLang() {
  const [lang, setLangState] = useState<Lang>(DEFAULT_LANG)

  // Hydrate from localStorage after mount
  useEffect(() => {
    setLangState(readLang())
  }, [])

  const setLang = useCallback((l: Lang) => {
    setLangState(l)
    localStorage.setItem(STORAGE_KEY, l)
  }, [])

  return [lang, setLang] as const
}
