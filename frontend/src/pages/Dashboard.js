import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Box,
  Button,
  Alert,
} from "@mui/material";
import { creditRiskService } from "../services/api";

const Dashboard = () => {
  const [dashboardStats, setDashboardStats] = useState({
    total_applications_processed: 0,
    total_accepted: 0,
    under_review_manual: 0,
    total_rejected: 0,
    accepted_percentage: 0,
    under_review_percentage: 0,
    rejected_percentage: 0,
    low_risk_count: 0,
    moderate_risk_count: 0,
    high_risk_count: 0,
    low_risk_percentage: 0,
    moderate_risk_percentage: 0,
    high_risk_percentage: 0,
    status_check: "Loading...",
    last_updated: null,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await creditRiskService.getDashboardStats();
      if (data.success) {
        setDashboardStats(data.dashboard_stats);
      } else {
        throw new Error("Failed to fetch dashboard statistics");
      }
    } catch (error) {
      console.error("Error fetching dashboard statistics:", error);
      setError(error.message);
      // Keep existing data if fetch fails
    } finally {
      setLoading(false);
    }
  };

  const refreshStats = async () => {
    try {
      setError(null);
      const data = await creditRiskService.refreshDashboardStats();
      if (data.success) {
        setDashboardStats(data.refreshed_stats);
      }
    } catch (error) {
      console.error("Error refreshing statistics:", error);
      setError(error.message);
    }
  };

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 4,
        }}
      >
        <Typography variant="h4" gutterBottom>
          Credit Risk Analyzer: Executive Dashboard
        </Typography>
        <Button variant="outlined" onClick={refreshStats} disabled={loading}>
          Refresh Data
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Main Dashboard Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderLeft: "5px solid #6366f1",
              backgroundColor: loading ? "#f5f5f5" : "white",
            }}
          >
            <CardContent sx={{ textAlign: "center" }}>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Applications Processed
              </Typography>
              <Typography
                variant="h3"
                component="div"
                sx={{ fontWeight: "bold", my: 1 }}
              >
                {loading ? "..." : dashboardStats.total_applications_processed}
              </Typography>
              <Typography variant="body2" color="primary">
                Status Check: {dashboardStats.status_check}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderLeft: "5px solid #10b981",
              backgroundColor: loading ? "#f5f5f5" : "white",
            }}
          >
            <CardContent sx={{ textAlign: "center" }}>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Accepted
              </Typography>
              <Typography
                variant="h3"
                component="div"
                color="success.main"
                sx={{ fontWeight: "bold", my: 1 }}
              >
                {loading ? "..." : dashboardStats.total_accepted}
              </Typography>
              <Typography variant="body2" color="success.main">
                {dashboardStats.accepted_percentage}% of total portfolio
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderLeft: "5px solid #f59e0b",
              backgroundColor: loading ? "#f5f5f5" : "white",
            }}
          >
            <CardContent sx={{ textAlign: "center" }}>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Under Review (Manual)
              </Typography>
              <Typography
                variant="h3"
                component="div"
                color="warning.main"
                sx={{ fontWeight: "bold", my: 1 }}
              >
                {loading ? "..." : dashboardStats.under_review_manual}
              </Typography>
              <Typography variant="body2" color="warning.main">
                {dashboardStats.under_review_percentage}% of total portfolio
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderLeft: "5px solid #ef4444",
              backgroundColor: loading ? "#f5f5f5" : "white",
            }}
          >
            <CardContent sx={{ textAlign: "center" }}>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Rejected
              </Typography>
              <Typography
                variant="h3"
                component="div"
                color="error"
                sx={{ fontWeight: "bold", my: 1 }}
              >
                {loading ? "..." : dashboardStats.total_rejected}
              </Typography>
              <Typography variant="body2" color="error">
                {dashboardStats.rejected_percentage}% of total portfolio
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Portfolio Risk Distribution */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography
            variant="h5"
            gutterBottom
            sx={{ textAlign: "center", mb: 3 }}
          >
            Portfolio Risk Distribution
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  p: 2,
                  backgroundColor: "#f0fdf4",
                  borderRadius: 2,
                  mb: 1,
                }}
              >
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      backgroundColor: "#10b981",
                      borderRadius: "50%",
                      mr: 1,
                    }}
                  />
                  <Typography variant="body1">Low Risk (Green)</Typography>
                </Box>
                <Typography
                  variant="h6"
                  color="success.main"
                  sx={{ fontWeight: "bold" }}
                >
                  {loading ? "..." : `${dashboardStats.low_risk_percentage}%`}
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={12} md={4}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  p: 2,
                  backgroundColor: "#fefce8",
                  borderRadius: 2,
                  mb: 1,
                }}
              >
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      backgroundColor: "#f59e0b",
                      borderRadius: "50%",
                      mr: 1,
                    }}
                  />
                  <Typography variant="body1">Moderate Risk (Amber)</Typography>
                </Box>
                <Typography
                  variant="h6"
                  color="warning.main"
                  sx={{ fontWeight: "bold" }}
                >
                  {loading
                    ? "..."
                    : `${dashboardStats.moderate_risk_percentage}%`}
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={12} md={4}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  p: 2,
                  backgroundColor: "#fef2f2",
                  borderRadius: 2,
                  mb: 1,
                }}
              >
                <Box sx={{ display: "flex", alignItems: "center" }}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      backgroundColor: "#ef4444",
                      borderRadius: "50%",
                      mr: 1,
                    }}
                  />
                  <Typography variant="body1">High Risk (Red)</Typography>
                </Box>
                <Typography
                  variant="h6"
                  color="error"
                  sx={{ fontWeight: "bold" }}
                >
                  {loading ? "..." : `${dashboardStats.high_risk_percentage}%`}
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {/* Risk Counts */}
          <Box sx={{ mt: 3, display: "flex", justifyContent: "center" }}>
            <Typography variant="body2" color="textSecondary">
              Risk Distribution: {dashboardStats.low_risk_count} Low •{" "}
              {dashboardStats.moderate_risk_count} Moderate •{" "}
              {dashboardStats.high_risk_count} High
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Last Updated */}
      {dashboardStats.last_updated && (
        <Box sx={{ textAlign: "center", mt: 2 }}>
          <Typography variant="body2" color="textSecondary">
            Last Updated:{" "}
            {new Date(dashboardStats.last_updated).toLocaleString()}
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default Dashboard;
