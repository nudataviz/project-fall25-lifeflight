import { Box } from "@mui/material";
import Header from "../../components/Header";
import KPIBullets from "../../components/4.1KPIBullets";
export default function KPIDashboard() {
  return (
    <Box m="20px">
      <Header title="KPI & Executive Dashboard" subtitle="KPI & Executive Dashboard" />
      
      {/* Chart 4.1: Core KPI Bullet Charts */}
      <Box mt="20px">
        <KPIBullets />
      </Box>
    </Box>
  );
}