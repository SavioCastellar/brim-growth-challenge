'use client';

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface PerformanceData {
  variant_name: string;
  count: number;
}

interface ChartProps {
  data: PerformanceData[];
}

export default function EmailPerformanceChart({ data }: ChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
        <XAxis type="number" hide />
        <YAxis
          dataKey="variant_name"
          type="category"
          stroke="#888888"
          fontSize={12}
        />
        <Tooltip />
        <Legend />
        <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} name="E-mails Gerados" />
      </BarChart>
    </ResponsiveContainer>
  );
}