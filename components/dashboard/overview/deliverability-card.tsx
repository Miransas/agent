const deliverability = 98.34;
const bounceRate = 1.66;
const complaintRate = 0.02;

export function DeliverabilityCard() {
  return (
    <div className="flex h-[280px] flex-col rounded-xl border border-white/[0.06] bg-[#0a0a0a] p-6">
      <div className="mb-1 flex items-baseline justify-between">
        <h2 className="text-sm font-medium text-foreground">Deliverability</h2>
        <span className="text-xs text-zinc-500">Last 7 days</span>
      </div>
      <p className="mb-6 text-xs text-zinc-500">
        Successful sends across all domains
      </p>

      <div className="flex flex-col items-center gap-3">
        <span className="font-mono text-4xl font-bold tracking-tight text-[#8CFF2E]">
          {deliverability.toFixed(2)}%
        </span>
        <div
          className="h-1 w-full overflow-hidden rounded-full bg-white/[0.05]"
          role="progressbar"
          aria-valuenow={deliverability}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          <div
            className="h-full rounded-full bg-[#8CFF2E] shadow-[0_0_8px_rgba(140,255,46,0.5)]"
            style={{ width: `${deliverability}%` }}
          />
        </div>
      </div>

      <div className="mt-auto flex flex-col gap-3 border-t border-white/[0.06] pt-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-zinc-400">Bounce rate</span>
          <span className="font-mono text-zinc-300">
            {bounceRate.toFixed(2)}%
          </span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-zinc-400">Complaint rate</span>
          <span className="font-mono text-zinc-300">
            {complaintRate.toFixed(2)}%
          </span>
        </div>
      </div>
    </div>
  );
}
