'use client'

import { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

export default function InviteRedirectPage() {
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    const token = (searchParams.get('token') || '').trim()
    const email = (searchParams.get('email') || '').trim().toLowerCase()

    if (!token) {
      router.replace('/login')
      return
    }

    const next = email
      ? `/login?token=${encodeURIComponent(token)}&email=${encodeURIComponent(email)}`
      : `/login?token=${encodeURIComponent(token)}`

    router.replace(next)
  }, [router, searchParams])

  return null
}
