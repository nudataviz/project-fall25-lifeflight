import { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Chart } from 'react-chartjs-2';
import { useTheme } from "@mui/material";
import { tokens } from "../theme";
import { Box, ToggleButton, ToggleButtonGroup, Typography, Paper, Grid, CircularProgress } from "@mui/material";



ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const HistogramChart = ({ isDashboard = false }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [data, setData] = useState({ overall: [], by_season: {} });
  const [viewMode, setViewMode] = useState('overall'); // 'overall' or 'by_season'
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/hourly_departure');
        const result = await response.json();
        setData(result.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching hourly departure data:', error);
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <Box m={isDashboard ? 0 : "20px"} display="flex" justifyContent="center" alignItems="center" height={isDashboard ? "250px" : "400px"}>
        <CircularProgress />
      </Box>
    );
  }

  const getChartData = () => {
    if (viewMode === 'overall') {
      const hours = data.overall.map(item => item.hour);
      const counts = data.overall.map(item => item.count);
      const densities = data.overall.map(item => item.density);
      
      return {
        labels: hours,
        datasets: [
          {
            type: 'bar',
            label: 'Count',
            data: counts,
            backgroundColor: colors.blueAccent[500] + '80', // 80 = 50% opacity
            borderColor: colors.blueAccent[500],
            borderWidth: 1,
            yAxisID: 'y',
          },
          {
            type: 'line',
            label: 'Density',
            data: densities,
            borderColor: colors.greenAccent[500],
            backgroundColor: colors.greenAccent[500] + '40',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            yAxisID: 'y1',
            pointRadius: 0,
          },
        ],
      };
    } else {

      const hours = data.overall.map(item => item.hour);
      const seasons = ['Spring', 'Summer', 'Autumn', 'Winter'];
      const seasonColors = [
        colors.greenAccent[500],
        colors.blueAccent[500],
        colors.redAccent[500],
        colors.grey[500],
      ];
      
      const datasets = [];
      
    
      seasons.forEach((season, index) => {
        if (data.by_season[season]) {
          const densities = data.by_season[season].map(item => item.density);
          datasets.push({
            type: 'line',
            label: season,
            data: densities,
            borderColor: seasonColors[index],
            backgroundColor: seasonColors[index] + '40',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            pointRadius: 0,
            yAxisID: 'y1',
          });
        }
      });
      
      return {
        labels: hours,
        datasets: datasets,
      };
    }
  };

  const chartData = getChartData();

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: colors.grey[100],
        },
      },
      title: {
        display: true,
        text: viewMode === 'overall' 
          ? 'Hourly Departure Density (Overall)' 
          : 'Hourly Departure Density by Season',
        color: colors.grey[100],
        font: {
          size: 16,
        },
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      x: {
        ticks: {
          color: colors.grey[100],
          stepSize: 1,
        },
        grid: {
          color: colors.grey[800],
        },
        title: {
          display: true,
          text: 'Hour of Day',
          color: colors.grey[100],
        },
      },
      y: {
        type: 'linear',
        display: viewMode === 'overall',
        position: 'left',
        ticks: {
          color: colors.grey[100],
        },
        grid: {
          color: colors.grey[800],
        },
        title: {
          display: true,
          text: 'Count',
          color: colors.grey[100],
        },
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        ticks: {
          color: colors.grey[100],
        },
        grid: {
          drawOnChartArea: false,
        },
        title: {
          display: true,
          text: 'Density',
          color: colors.grey[100],
        },
      },
    },
  };

  return (
    <Box m={isDashboard ? 0 : "20px"}>
      {!isDashboard && (
        <Paper sx={{ p: 3, mb: 3, backgroundColor: colors.primary[400] }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <Typography variant="h3" sx={{ mb: 1, color: colors.grey[100] }}>
              Hourly Departure Density(Base on data in 2023)
              </Typography>
              {/* <Typography variant="h6" sx={{ mb: 1, color: colors.grey[300] }}>
                Hourly Departure Density(Base on data in 2023)
              </Typography> */}
              <Typography variant="body2" sx={{ color: colors.grey[400], fontStyle: 'italic' }}>
                This chart shows the hourly departure density of LifeFlight missions.
              </Typography>
            </Grid>
            <Grid item xs={12} md={4} sx={{ display: 'flex', justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
              <ToggleButtonGroup
                value={viewMode}
                exclusive
                onChange={(e, newMode) => {
                  if (newMode !== null) setViewMode(newMode);
                }}
                aria-label="view mode"
                sx={{
                  '& .MuiToggleButton-root': {
                    color: colors.grey[100],
                    borderColor: colors.grey[700],
                    '&.Mui-selected': {
                      backgroundColor: colors.blueAccent[700],
                      color: colors.grey[100],
                    },
                  },
                }}
              >
                <ToggleButton value="overall" aria-label="overall">
                  Overall
                </ToggleButton>
                <ToggleButton value="by_season" aria-label="by season">
                  By Season
                </ToggleButton>
              </ToggleButtonGroup>
            </Grid>
          </Grid>
        </Paper>
      )}
      <Paper sx={{ p: 2, backgroundColor: colors.primary[400] }}>
        <Box height={isDashboard ? "250px" : "400px"} width="100%">
          <Chart type="bar" data={chartData} options={options} />
        </Box>
      </Paper>
    </Box>
  );
};

export default HistogramChart;