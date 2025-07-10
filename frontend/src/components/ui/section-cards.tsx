import KpiCard from "../KpiCard"

async function getKpiData(kpiName: string) {
  const backendUrl = "http://backend:8000";
  const res = await fetch(`${backendUrl}/api/analytics/kpi/${kpiName}`, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}

export async function SectionCards() {
  const [
    qualifiedLeadsData,
    emailEngagementData,
    newActivationsData,
    funnelConversionData
  ] = await Promise.all([
    getKpiData('qualified-leads'),
    getKpiData('email-engagement'),
    getKpiData('new-activations'),
    getKpiData('funnel-conversion-rate')
  ]);

  return (
    <div className="*:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:shadow-xs lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
      {qualifiedLeadsData && (
        <KpiCard
          title={qualifiedLeadsData.metric_name}
          metricValue={qualifiedLeadsData.current_value}
          percentageChange={qualifiedLeadsData.percentage_change}
          description={qualifiedLeadsData.description}
        />
      )}
      {emailEngagementData && (
        <KpiCard
          title={emailEngagementData.metric_name}
          metricValue={emailEngagementData.current_value}
          percentageChange={emailEngagementData.percentage_change}
          description={emailEngagementData.description}
          metricSuffix="%"
        />
      )}
      {newActivationsData && (
        <KpiCard
          title={newActivationsData.metric_name}
          metricValue={newActivationsData.current_value}
          percentageChange={newActivationsData.percentage_change}
          description={newActivationsData.description}
        />
      )}
      {funnelConversionData && (
        <KpiCard
          title={funnelConversionData.metric_name}
          metricValue={funnelConversionData.current_value}
          percentageChange={funnelConversionData.percentage_change}
          description={funnelConversionData.description}
          metricSuffix="%"
        />
      )}
    </div>
  )
}
