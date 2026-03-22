'use client'

import { useCallback, useEffect, useState } from 'react'
import type { Lang } from '@/components/landing/translations'

const STORAGE_KEY = 'lifeos-lang'
const DEFAULT_LANG: Lang = 'en'
const LANG_CHANGE_EVENT = 'lifeos-lang-change'

type LangListener = (lang: Lang) => void
const listeners = new Set<LangListener>()

function readLang(): Lang {
  if (typeof window === 'undefined') return DEFAULT_LANG
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'en' || stored === 'zh' || stored === 'ko') return stored
  return DEFAULT_LANG
}

function writeLang(lang: Lang) {
  if (typeof window === 'undefined') return
  localStorage.setItem(STORAGE_KEY, lang)
  window.dispatchEvent(new CustomEvent<Lang>(LANG_CHANGE_EVENT, { detail: lang }))
}

function subscribe(listener: LangListener) {
  listeners.add(listener)
  return () => { listeners.delete(listener) }
}

function notify(nextLang: Lang) {
  listeners.forEach((listener) => listener(nextLang))
}

export function useLang() {
  // Keep first client render aligned with server-rendered markup.
  const [lang, setLangState] = useState<Lang>(DEFAULT_LANG)
  const [isHydrated, setIsHydrated] = useState(false)

  useEffect(() => {
    setLangState(readLang())
    setIsHydrated(true)
  }, [])

  useEffect(() => {
    return subscribe(setLangState)
  }, [])

  useEffect(() => {
    const onStorage = (event: StorageEvent) => {
      if (event.key !== STORAGE_KEY) return
      const nextLang = readLang()
      notify(nextLang)
    }
    const onLangChange = (event: Event) => {
      const customEvent = event as CustomEvent<Lang>
      const nextLang = customEvent.detail ?? readLang()
      notify(nextLang)
    }

    window.addEventListener('storage', onStorage)
    window.addEventListener(LANG_CHANGE_EVENT, onLangChange as EventListener)
    return () => {
      window.removeEventListener('storage', onStorage)
      window.removeEventListener(LANG_CHANGE_EVENT, onLangChange as EventListener)
    }
  }, [])

  const setLang = useCallback((l: Lang) => {
    writeLang(l)
    notify(l)
  }, [])

  return [lang, setLang, isHydrated] as const
}
