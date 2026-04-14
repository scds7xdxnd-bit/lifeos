import type { Metadata } from 'next'
import TdeeToolPage from './_components/TdeeToolPage'

export const metadata: Metadata = {
  title: 'TDEE & BMR Calculator | LifeOS',
  description: 'Accurate daily energy expenditure and macro calculation using clinical formulas. Simple, private, and calm.',
  openGraph: {
    title: 'TDEE & BMR Calculator | LifeOS',
    description: 'Accurate daily energy expenditure and macro calculation using clinical formulas.',
    type: 'website',
    siteName: 'LifeOS',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'TDEE & BMR Calculator | LifeOS',
    description: 'Accurate daily energy expenditure and macro calculation using clinical formulas.',
  },
  robots: { index: true, follow: true },
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'TDEE & BMR Calculator',
  applicationCategory: 'HealthApplication',
  operatingSystem: 'Web',
  offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
  description:
    'Accurate daily energy expenditure and macro calculation using Mifflin-St Jeor and Katch-McArdle clinical formulas.',
  creator: { '@type': 'Organization', name: 'LifeOS' },
}

export default function Page() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <TdeeToolPage />
    </>
  )
}
