'use client';

import { FunnelChart, Funnel, LabelList, Tooltip, ResponsiveContainer } from 'recharts';

interface FunnelData {
  step_name: string;
  user_count: number;
}

interface ChartProps {
  data: FunnelData[];
}

export default function ActivationFunnelChart({ data }: ChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <FunnelChart>
        <Tooltip />
        <Funnel
          dataKey="user_count"
          data={data}
          isAnimationActive
        >
          <LabelList position="right" fill="#000" stroke="none" dataKey="step_name" />
        </Funnel>
      </FunnelChart>
    </ResponsiveContainer>
  );
}