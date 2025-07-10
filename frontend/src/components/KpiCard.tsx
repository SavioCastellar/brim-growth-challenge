'use client';

import { Card, CardAction, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "./ui/badge";
import { IconTrendingDown, IconTrendingUp } from "@tabler/icons-react";

interface KpiCardProps {
    title: string;
    metricValue: number;
    percentageChange: number;
    description: string;
    formatAsCurrency?: boolean;
    metricSuffix?: string;
}

export default function KpiCard({ title, metricValue, percentageChange, description, formatAsCurrency = false, metricSuffix = '' }: KpiCardProps) {
    const isPositive = percentageChange >= 0;

    const formattedMetric = formatAsCurrency
        ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(metricValue)
        : metricValue.toLocaleString('en-US');

    return (
        <Card className="@container/card bg-white">
            <CardHeader>
                <CardDescription>{title}</CardDescription>
                <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
                    {formattedMetric}{metricSuffix}
                </CardTitle>
                <CardAction>
                    <Badge variant="outline">
                        {isPositive ? <IconTrendingUp /> : <IconTrendingDown />}
                        {percentageChange.toFixed(1)}%
                    </Badge>
                </CardAction>
            </CardHeader>
            <CardFooter className="flex-col items-start gap-1.5 text-sm">
                <div className="line-clamp-1 flex gap-2 font-medium">
                    Trending up this month <IconTrendingUp className="size-4" />
                </div>
                <div className="text-muted-foreground">
                    {description}
                </div>
            </CardFooter>
        </Card>
    );
}