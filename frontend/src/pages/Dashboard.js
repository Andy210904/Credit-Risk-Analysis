import React, { useState, useEffect } from 'react';
import { Container, Typography, Grid, Card, CardContent, Box } from '@mui/material';
import { creditRiskService } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalAnalyses: 0,
    highRiskCount: 0,
    mediumRiskCount: 0,
    lowRiskCount: 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // const data = await creditRiskService.getStatistics();
        // setStats(data);
        
        // Mock data for now
        setStats({
          totalAnalyses: 156,
          highRiskCount: 23,
          mediumRiskCount: 67,
          lowRiskCount: 66
        });
      } catch (error) {
        console.error('Error fetching statistics:', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Credit Risk Analysis Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Analyses
              </Typography>
              <Typography variant="h5" component="div">
                {stats.totalAnalyses}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ backgroundColor: '#ffebee' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                High Risk
              </Typography>
              <Typography variant="h5" component="div" color="error">
                {stats.highRiskCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ backgroundColor: '#fff8e1' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Medium Risk
              </Typography>
              <Typography variant="h5" component="div" color="warning.main">
                {stats.mediumRiskCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ backgroundColor: '#e8f5e8' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Low Risk
              </Typography>
              <Typography variant="h5" component="div" color="success.main">
                {stats.lowRiskCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;