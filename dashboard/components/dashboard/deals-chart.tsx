"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { CHART_DATA } from "@/lib/fake-data";

export function DealsChart() {
  return (
    <Card className="flex-1">
      <CardHeader className="pb-0">
        <CardTitle className="text-sm font-semibold text-white/80">
          Activity — Last 7 Days
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-3">
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={CHART_DATA} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="dealsGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#9333ea" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#9333ea" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="alertsGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis
              dataKey="day"
              tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                background: "#0d0d14",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: "10px",
                color: "#fff",
                fontSize: "12px",
                boxShadow: "0 10px 40px rgba(0,0,0,0.5)",
              }}
              itemStyle={{ color: "rgba(255,255,255,0.8)" }}
              cursor={{ stroke: "rgba(147,51,234,0.2)", strokeWidth: 1 }}
            />
            <Legend
              wrapperStyle={{ fontSize: "11px", color: "rgba(255,255,255,0.4)" }}
            />
            <Area
              type="monotone"
              dataKey="deals"
              stroke="#9333ea"
              strokeWidth={2}
              fill="url(#dealsGrad)"
              name="Deals Found"
            />
            <Area
              type="monotone"
              dataKey="alerts"
              stroke="#38bdf8"
              strokeWidth={2}
              fill="url(#alertsGrad)"
              name="Alerts Sent"
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
