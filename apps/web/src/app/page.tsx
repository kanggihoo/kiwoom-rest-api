import { DashboardPage } from "@/features/market-dashboard/components/dashboard-page";
import { mockMarketDashboardData } from "@/features/market-dashboard/mock/dashboard";

export default function Home() {
  return <DashboardPage data={mockMarketDashboardData} />;
}
