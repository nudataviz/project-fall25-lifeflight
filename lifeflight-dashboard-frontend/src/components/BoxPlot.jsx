import { useState, useEffect, useMemo } from "react";
import { Box, Paper, Typography, CircularProgress, Alert } from "@mui/material";
import { useTheme } from "@mui/material";
import { ResponsiveBoxPlot } from "@nivo/boxplot";
import { tokens } from "../theme";

const BoxPlot = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  const [boxplotData, setBoxplotData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBoxplotData = async () => {
      try {
        const response = await fetch("http://localhost:5001/api/boxplot");
        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.message || "Failed to fetch boxplot data");
        }
        const result = await response.json();
        if (result.status === "success") {
          setBoxplotData(result.data);
        } else {
          throw new Error(result.message || "Failed to fetch boxplot data");
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchBoxplotData();
  }, []);

  const VEH_ORDER = ["LF1", "LF2", "LF3", "LF4"];
  const VEH_LABELS = {
    LF1: "Helicopter based out of Bangor(LF1)",
    LF2: "Helicopter based out of Lewiston(LF2)",
    LF3: "Airplane based out of Bangor(LF3)",
    LF4: "Helicopter based out of Sanford(LF4)",
  };

  const nivoData = useMemo(() => {
    if (!boxplotData || !boxplotData.vehicles) return [];
    return boxplotData.vehicles.flatMap((veh) =>
      veh.values.map((value, idx) => ({
        id: `${veh.veh}-${idx}`,
        group: veh.veh,
        value,
      }))
    );
  }, [boxplotData]);

  return (
    <Box m="20px">
      <Typography variant="h3" sx={{ mb: "10px", color: colors.grey[100] }}>
        Vehicle Mileage Distribution
      </Typography>

      <Typography variant="h6" sx={{ mb: "10px", color: colors.grey[300] }}>
        Vehicle Mileage Distribution: Mileage distribution of each base location's historical missions.
      </Typography>
        <Typography variant="body2" sx={{ mb: "20px", color: colors.grey[400], fontStyle: "italic" }}>
        {/* 用来参考各基地的覆盖范围，以及各基地的平均里程，判断各基地的里程是否合理。 */}
        This chart is used to reference the coverage range of each base location and the average mileage of each base location to determine if the mileage of each base location is reasonable.
      </Typography>

      {loading && (
        <Box display="flex" justifyContent="center" alignItems="center" height="400px">
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {!loading && !error && boxplotData && (
        <>
          <Paper sx={{ p: 3, mb: 3, height: "500px", backgroundColor: colors.primary[400] }}>
            <Box height="440px">
              <ResponsiveBoxPlot
                data={nivoData}
                groups={VEH_ORDER}
                margin={{ top: 50, right: 60, bottom: 80, left: 80 }}
                minValue="auto"
                maxValue="auto"
                colors={{ scheme: "paired" }}
                borderRadius={2}
                axisBottom={{
                  tickRotation: 0,
                  legend: "Base Location",
                  legendOffset: 46,
                  legendPosition: "middle",
                  format: (value) => VEH_LABELS[value] || value,
                }}
                axisLeft={{
                  legend: "Mileage - Loaded (miles)",
                  legendOffset: -60,
                  legendPosition: "middle",
                }}
                enableGridX={false}
                enableGridY={true}
                fillSelectedBoxes
                medianColor={colors.redAccent[400]}
                whiskerThickness={2}
                isInteractive={true}
                theme={{
                  axis: {
                    domain: {
                      line: {
                        stroke: colors.grey[100],
                        strokeWidth: 1,
                      },
                    },
                    ticks: {
                      line: {
                        stroke: colors.grey[100],
                        strokeWidth: 1,
                      },
                      text: {
                        fill: colors.grey[100],
                      },
                    },
                    legend: {
                      text: {
                        fill: colors.grey[100],
                      },
                    },
                  },
                  grid: {
                    line: {
                      stroke: colors.grey[700],
                    },
                  },
                }}
              />
            </Box>
          </Paper>
        </>
      )}
    </Box>
  );
};

export default BoxPlot;
