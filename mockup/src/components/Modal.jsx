export default function Modal({ title, onClose, children, width = 'max-w-sm' }) {
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div className={`bg-white rounded-2xl p-5 w-full ${width}`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-slate-900">{title}</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-lg leading-none">
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}
