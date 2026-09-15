/** Spec §8.3 — 로딩 중 정지 화면 금지. */
export function Loading({ label = '준비하고 있어요' }: { label?: string }) {
  return (
    <div className="loading">
      <div className="dots" aria-hidden="true"><i /><i /><i /></div>
      <p>{label}</p>
    </div>
  )
}
