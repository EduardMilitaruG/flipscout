"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { BRAND_SHARE } from "@/lib/fake-data";

export function BrandPieChart() {
  return (
    <Card className="w-full lg:w-64 flex-shrink-0">
      <CardHeader className="pb-0">
        <CardTitle className="text-sm font-semibold text-white/80">
          Brand Share
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-2">
        <ResponsiveContainer width="100%" height={150}>
          <PieChart>
            <Pie
              data={BRAND_SHARE}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={65}
              paddingAngle={3}
              dataKey="value"
              strokeWidth={0}
            >
              {BRAND_SHARE.map((entry, i) => (
                <Cell key={i} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "#0d0d14",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: "8px",
                color: "#fff",
                fontSize: "11px",
              }}
              formatter={(value: number) => [`${value}%`, "Share"]}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="space-y-1 mt-1">
          {BRAND_SHARE.map((item) => (
            <div key={item.name} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5">
                <div
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-white/50">{item.name}</span>
              </div>
              <span className="text-white/70 font-medium">{item.value}%</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
