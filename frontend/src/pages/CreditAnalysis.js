import React, { useState } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Grid,
  Box,
  Alert,
  CircularProgress
} from '@mui/material';
import { creditRiskService } from '../services/api';

const CreditAnalysis = () => {
  const [formData, setFormData] = useState({
    income: '',
    creditScore: '',
    loanAmount: '',
    employmentLength: '',
    debtToIncomeRatio: ''
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const analysisResult = await creditRiskService.analyzeCreditRisk(formData);
      setResult(analysisResult);
    } catch (error) {
      setError('Error analyzing credit risk. Please try again.');
      console.error('Analysis error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Credit Risk Analysis
      </Typography>
      
      <Card>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Annual Income"
                  name="income"
                  type="number"
                  value={formData.income}
                  onChange={handleInputChange}
                  required
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Credit Score"
                  name="creditScore"
                  type="number"
                  value={formData.creditScore}
                  onChange={handleInputChange}
                  required
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Loan Amount"
                  name="loanAmount"
                  type="number"
                  value={formData.loanAmount}
                  onChange={handleInputChange}
                  required
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Employment Length (years)"
                  name="employmentLength"
                  type="number"
                  value={formData.employmentLength}
                  onChange={handleInputChange}
                  required
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Debt to Income Ratio"
                  name="debtToIncomeRatio"
                  type="number"
                  step="0.01"
                  value={formData.debtToIncomeRatio}
                  onChange={handleInputChange}
                  required
                />
              </Grid>
              
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={loading}
                    sx={{ minWidth: 200 }}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Analyze Risk'}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>
      
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
      
      {result && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Analysis Result
            </Typography>
            <Typography variant="body1">
              Risk Level: <strong>{result.riskLevel}</strong>
            </Typography>
            <Typography variant="body1">
              Risk Score: <strong>{result.riskScore}</strong>
            </Typography>
            <Typography variant="body2" sx={{ mt: 2 }}>
              {result.explanation}
            </Typography>
          </CardContent>
        </Card>
      )}
    </Container>
  );
};

export default CreditAnalysis;