'use client';

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";



interface ScoreData {
  bin: string;
  count: number;
}

interface ChartProps {
  data: ScoreData[];
}

export default function LeadScoreChart({ data }: ChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
        <XAxis
          dataKey="bin"
          stroke="#888888"
          fontSize={12}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          stroke="#888888"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => `${value}`}
        />
        <Tooltip cursor={{ fill: 'rgba(243, 244, 246, 0.5)' }} />
        <Bar dataKey="count" fill="#16a34a" radius={[4, 4, 0, 0]} name="Número de Leads" />
      </BarChart>
    </ResponsiveContainer>
  );
}