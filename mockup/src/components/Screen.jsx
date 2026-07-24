export default function Screen({ children, width = 'max-w-md' }) {
  return (
    <div className="min-h-svh w-full flex items-center justify-center p-4">
      <div className={`w-full ${width} bg-white rounded-2xl shadow-xl shadow-slate-200 border border-slate-200 p-8`}>
        {children}
      </div>
    </div>
  )
}
