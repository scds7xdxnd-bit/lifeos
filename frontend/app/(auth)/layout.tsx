export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <main
      className="min-h-screen flex items-center justify-center px-6"
      style={{
        background: 'linear-gradient(180deg, #F4F2EE 0%, #EAE7E0 60%, #DDD8CF 100%)',
      }}
    >
      {children}
    </main>
  )
}
