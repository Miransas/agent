"use client";

import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const chartData = [
  { day: "Mon", sent: 1820, delivered: 1798 },
  { day: "Tue", sent: 1950, delivered: 1920 },
  { day: "Wed", sent: 2100, delivered: 2071 },
  { day: "Thu", sent: 1740, delivered: 1715 },
  { day: "Fri", sent: 1880, delivered: 1854 },
  { day: "Sat", sent: 1620, delivered: 1601 },
  { day: "Sun", sent: 1737, delivered: 1675 },
];

interface TooltipPayloadEntry {
  name?: string;
  value?: number | string;
  color?: string;
  dataKey?: string;
}

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border border-white/[0.08] bg-[#0a0a0a] px-3 py-2 shadow-lg">
      <div className="mb-1 text-xs font-medium uppercase tracking-wider text-zinc-500">
        {label}
      </div>
      <div className="flex flex-col gap-1">
        {payload.map((entry) => (
          <div
            key={entry.dataKey ?? entry.name}
            className="flex items-center justify-between gap-4 text-xs"
          >
            <span className="capitalize text-zinc-400">{entry.name}</span>
            <span className="font-mono font-medium text-[#8CFF2E]">
              {Number(entry.value).toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function MetricsChart() {
  // recharts' ResponsiveContainer can't measure the parent during SSR and logs
  // a width/height warning; gating render until after mount avoids it.
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <div className="flex h-[280px] flex-col rounded-xl border border-white/[0.06] bg-[#0a0a0a] p-6">
      <div className="mb-1 flex items-baseline justify-between">
        <h2 className="text-sm font-medium text-foreground">
          Delivery rate over time
        </h2>
        <span className="text-xs text-zinc-500">Last 7 days</span>
      </div>
      <p className="mb-4 text-xs text-zinc-500">
        Sent vs. delivered, by day
      </p>
      <div className="-ml-2 min-h-0 flex-1">
        {mounted ? (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
          >
            <CartesianGrid
              stroke="rgba(255,255,255,0.04)"
              vertical={false}
            />
            <XAxis
              dataKey="day"
              stroke="transparent"
              tick={{ fill: "#71717a", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              dy={6}
            />
            <YAxis hide domain={["dataMin - 100", "dataMax + 100"]} />
            <Tooltip
              cursor={{
                stroke: "rgba(140,255,46,0.2)",
                strokeWidth: 1,
              }}
              content={<ChartTooltip />}
            />
            <Line
              type="monotone"
              dataKey="sent"
              name="Sent"
              stroke="#8CFF2E"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#8CFF2E", stroke: "#0a0a0a", strokeWidth: 2 }}
            />
            <Line
              type="monotone"
              dataKey="delivered"
              name="Delivered"
              stroke="#8CFF2E"
              strokeOpacity={0.4}
              strokeWidth={1.5}
              dot={false}
              activeDot={{ r: 4, fill: "#8CFF2E", fillOpacity: 0.6, stroke: "#0a0a0a", strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
        ) : null}
      </div>
    </div>
  );
}
