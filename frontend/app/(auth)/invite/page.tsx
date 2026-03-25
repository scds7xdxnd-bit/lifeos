import { redirect } from 'next/navigation'

interface InvitePageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>
}

function _asString(value: string | string[] | undefined): string {
  if (Array.isArray(value)) return (value[0] || '').trim()
  return (value || '').trim()
}

export default async function InviteRedirectPage({ searchParams }: InvitePageProps) {
  const params = await searchParams
  const token = _asString(params.token)
  const email = _asString(params.email).toLowerCase()

  if (!token) {
    redirect('/login')
  }

  const next = email
    ? `/login?token=${encodeURIComponent(token)}&email=${encodeURIComponent(email)}`
    : `/login?token=${encodeURIComponent(token)}`

  redirect(next)
}
