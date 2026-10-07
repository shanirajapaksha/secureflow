import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

interface AttackTypesChartProps {
  summary?: Record<string, number>;
}

const COLORS = [
  "hsl(0 72% 51%)",
  "hsl(183 74% 44%)",
  "hsl(262 83% 58%)",
  "hsl(38 92% 50%)",
  "hsl(142 76% 36%)",
  "hsl(210 40% 50%)",
];

export function AttackTypesChart({ summary = {} }: AttackTypesChartProps) {
  const entries = Object.entries(summary);
  const totalAttacks = entries.reduce((sum, [, value]) => sum + value, 0);

  const data =
    totalAttacks > 0
      ? entries.map(([name, value], index) => ({
          name,
          value,
          color: COLORS[index % COLORS.length],
          percent: ((value / totalAttacks) * 100).toFixed(1),
        }))
      : [{ name: "No Intrusions", value: 1, color: "hsl(215 20% 55%)", percent: "0" }];

  return (
    <div className="h-full w-full">
      <h3 className="text-lg font-semibold text-foreground mb-4">Intrusion Type Distribution</h3>

      <div className="flex items-center justify-between gap-6">
        <div className="relative w-40 h-40">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} cx="50%" cy="50%" innerRadius={45} outerRadius={65} paddingAngle={2} dataKey="value" strokeWidth={0}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(222 47% 8%)",
                  border: "1px solid hsl(222 47% 16%)",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
            </PieChart>
          </ResponsiveContainer>

          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold font-mono text-foreground">{totalAttacks}</span>
            <span className="text-xs text-muted-foreground">Intrusions</span>
          </div>
        </div>

        <div className="flex flex-col gap-3 flex-1">
          {data.map((item) => (
            <div key={item.name} className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
              <span className="text-sm text-muted-foreground">{item.name}</span>
              <span className="text-sm font-mono text-foreground ml-auto">{"percent" in item ? `${item.percent}%` : ""}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
