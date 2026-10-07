import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface NetworkTrafficChartProps {
  benignCount?: number;
  intrusionCount?: number;
}

export function NetworkTrafficChart({ benignCount = 0, intrusionCount = 0 }: NetworkTrafficChartProps) {
  const chartData = [
    { name: "Benign", value: benignCount },
    { name: "Intrusion", value: intrusionCount },
  ];

  return (
    <div className="h-full w-full">
      <h3 className="text-lg font-semibold text-foreground mb-4">Traffic Status Overview</h3>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
          <YAxis stroke="hsl(var(--muted-foreground))" />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
            }}
          />
          <Area type="monotone" dataKey="value" stroke="hsl(var(--primary))" fill="hsl(var(--primary))" fillOpacity={0.25} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
