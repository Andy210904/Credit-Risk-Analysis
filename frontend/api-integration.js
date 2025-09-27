// Backend API Configuration
const API_BASE_URL = "http://localhost:8000/api/frontend";

// Global variable to store uploaded data
let uploadedClientsData = null;

// Enhanced file handling function that connects to backend
async function handleFileSelectionAPI(file, uploadBtn, fileNameDisplay) {
  if (!file) return;

  const fileType = file.name.split(".").pop().toLowerCase();
  // Use passed parameters or fallback to DOM query
  if (!uploadBtn) uploadBtn = document.getElementById("analyze-batch-btn");
  if (!fileNameDisplay) fileNameDisplay = document.getElementById("file-name-display");

  if (fileType !== "csv" && fileType !== "json") {
    showTemporaryMessage(
      "Unsupported file type. Please use CSV or JSON.",
      "red"
    );
    return;
  }

  // Update UI to show uploading state
  if (uploadBtn) uploadBtn.disabled = true;
  if (fileNameDisplay) fileNameDisplay.textContent = "Uploading file...";

  try {
    if (fileType === "csv") {
      // Upload CSV to backend
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE_URL}/upload-csv`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Upload failed");
      }

      const result = await response.json();

      // Store the clients data globally
      uploadedClientsData = result.clients_data;
      batchFileData = result.clients_data; // For compatibility with existing code

      if (fileNameDisplay) {
        fileNameDisplay.textContent = `${file.name} (${result.total_clients} clients) - Uploaded to Backend`;
      }
      if (uploadBtn) {
        uploadBtn.disabled = false;
        uploadBtn.textContent = `Analyze Batch (${result.total_clients} Clients)`;
      }

      showTemporaryMessage(
        `Backend upload successful: ${result.total_clients} clients ready for analysis.`,
        "green"
      );
    } else if (fileType === "json") {
      // Handle JSON files locally (as before)
      const reader = new FileReader();
      reader.onload = function (e) {
        try {
          const contents = e.target.result;
          let clientsData = JSON.parse(contents);
          if (!Array.isArray(clientsData)) clientsData = [clientsData];

          uploadedClientsData = clientsData;
          batchFileData = clientsData;

          if (fileNameDisplay)
            fileNameDisplay.textContent = `${file.name} (${clientsData.length} clients)`;
          if (uploadBtn) {
            uploadBtn.disabled = false;
            uploadBtn.textContent = `Analyze Batch (${clientsData.length} Clients)`;
          }
          showTemporaryMessage(
            `JSON file loaded: ${clientsData.length} applications ready for analysis.`,
            "blue"
          );
        } catch (error) {
          uploadedClientsData = null;
          batchFileData = null;
          if (fileNameDisplay)
            fileNameDisplay.textContent = "Error during JSON parsing.";
          if (uploadBtn) {
            uploadBtn.disabled = true;
            uploadBtn.textContent = "Analyze Batch (0 Clients)";
          }
          showTemporaryMessage("Error parsing JSON file.", "red");
        }
      };
      reader.readAsText(file);
    }
  } catch (error) {
    console.error("File upload error:", error);
    uploadedClientsData = null;
    batchFileData = null;

    if (fileNameDisplay)
      fileNameDisplay.textContent = "Upload failed. Try again.";
    if (uploadBtn) {
      uploadBtn.disabled = true;
      uploadBtn.textContent = "Analyze Batch (0 Clients)";
    }
    showTemporaryMessage(`Upload failed: ${error.message}`, "red");
  }
}

// Enhanced batch processing that uses backend analysis
async function processBatchAPI(clientsData, uploadBtn) {
  if (!clientsData || clientsData.length === 0) {
    showTemporaryMessage("No client data available for analysis.", "red");
    if (uploadBtn) {
      uploadBtn.disabled = false;
      uploadBtn.textContent = "Analyze Batch (0 Clients)";
    }
    return;
  }

  // Update button to show processing state
  if (uploadBtn) {
    uploadBtn.disabled = true;
    uploadBtn.innerHTML =
      '<svg class="animate-spin w-5 h-5 mr-2 text-white" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" stroke-linecap="round" stroke-miterlimit="10" stroke-dasharray="80" stroke-dashoffset="60" style="stroke-opacity: 0.25;"></circle><path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg> Analyzing ' +
      clientsData.length +
      " Clients via Backend...";
  }

  try {
    // Send batch data to backend for analysis
    const response = await fetch(`${API_BASE_URL}/analyze-batch`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(clientsData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Batch analysis failed");
    }

    const batchResult = await response.json();

    // Update application history with backend results
    let firstResult = null;
    batchResult.results.forEach((result) => {
      if (!firstResult) firstResult = result;

      applicationHistory.push({
        id: result.applicant_id,
        date: result.date,
        risk: result.final_evaluation,
        score: result.approval_prediction_pct,
        status: result.status,
        color: result.color,
      });
    });

    // Set current result for single view
    if (firstResult) {
      currentRiskResult = firstResult;
    }

    // Reset button state
    if (uploadBtn) {
      uploadBtn.disabled = false;
      uploadBtn.textContent = `Analyze Batch (${clientsData.length} Clients)`;
    }

    showTemporaryMessage(
      `Backend analysis complete: ${batchResult.total_processed} applications processed. Navigating to Reports.`,
      "green"
    );

    // Navigate to Reports to view results
    setTimeout(() => {
      renderPage("Reports");
    }, 1000);
  } catch (error) {
    console.error("Backend batch analysis error:", error);

    // Reset button state
    if (uploadBtn) {
      uploadBtn.disabled = false;
      uploadBtn.textContent = `Analyze Batch (${clientsData.length} Clients)`;
    }

    showTemporaryMessage(
      `Backend analysis failed: ${error.message}. Try again or check backend connection.`,
      "red"
    );
  }
}

// Get entities from backend after CSV upload
async function getEntitiesFromBackend() {
  try {
    const response = await fetch(`${API_BASE_URL}/entities`);
    if (response.ok) {
      const data = await response.json();
      console.log("Entities retrieved from backend:", data);
      return data.clients_data;
    } else {
      throw new Error("Failed to get entities from backend");
    }
  } catch (error) {
    console.error("Error getting entities from backend:", error);
    return null;
  }
}

// Show client data from backend when "Show Data Preview" is clicked
async function showClientDataFromBackend() {
  const uploadBtn = document.getElementById("analyze-batch-btn");
  const fileNameDisplay = document.getElementById("file-name-display");

  // Update UI to show loading state
  if (uploadBtn) {
    uploadBtn.disabled = true;
    uploadBtn.textContent = "Loading Client Data...";
  }

  try {
    const clientsData = await getEntitiesFromBackend();
    
    if (clientsData && clientsData.length > 0) {
      // Store the data globally for compatibility
      batchFileData = clientsData;
      batchFileData.file = "backend_data.csv"; // Add filename for display
      uploadedClientsData = clientsData;

      // Update UI elements
      if (fileNameDisplay) {
        fileNameDisplay.textContent = `Backend Data (${clientsData.length} clients loaded)`;
      }
      if (uploadBtn) {
        uploadBtn.disabled = false;
        uploadBtn.textContent = `Show Data Preview (${clientsData.length} Clients)`;
      }

      showTemporaryMessage(`${clientsData.length} clients loaded from backend.`, 'green');
      
      // Re-render the page to show client data in preview table
      renderPage('ApplicationUpload');
      
    } else {
      // No data found
      if (fileNameDisplay) {
        fileNameDisplay.textContent = "No client data found in backend";
      }
      if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.textContent = "Show Data Preview (0 Clients)";
      }
      showTemporaryMessage('No client data found. Please upload a CSV file first.', 'yellow');
    }
    
  } catch (error) {
    console.error("Error loading client data from backend:", error);
    
    if (fileNameDisplay) {
      fileNameDisplay.textContent = "Error loading data from backend";
    }
    if (uploadBtn) {
      uploadBtn.disabled = true;
      uploadBtn.textContent = "Show Data Preview (Error)";
    }
    showTemporaryMessage(`Error loading client data: ${error.message}`, 'red');
  }
}

// Test backend connectivity
async function testBackendConnection() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (response.ok) {
      const health = await response.json();
      console.log("Backend connection successful:", health);
      showTemporaryMessage("Backend connected successfully!", "green");
      return true;
    } else {
      throw new Error("Backend health check failed");
    }
  } catch (error) {
    console.error("Backend connection failed:", error);
    showTemporaryMessage(
      "Backend connection failed. Using mock data.",
      "yellow"
    );
    return false;
  }
}

// Initialize backend connection check on page load
document.addEventListener("DOMContentLoaded", () => {
  // Test backend connection
  testBackendConnection();

  // Override the original file handling functions
  window.handleFileSelection = handleFileSelectionAPI;
  window.processBatch = processBatchAPI;
  window.showClientDataFromBackend = showClientDataFromBackend;
  window.getEntitiesFromBackend = getEntitiesFromBackend;
});

// Dashboard Statistics API Functions
async function getDashboardStatsFromBackend() {
  try {
    const response = await fetch(`http://localhost:8000/api/frontend/dashboard-stats`);
    if (response.ok) {
      const data = await response.json();
      return data.dashboard_stats;
    } else {
      throw new Error("Failed to get dashboard stats from backend");
    }
  } catch (error) {
    console.error("Error getting dashboard stats from backend:", error);
    return null;
  }
}

async function initializeDashboardStats() {
  try {
    const response = await fetch(`http://localhost:8000/api/frontend/dashboard-stats/initialize`, {
      method: 'POST'
    });
    if (response.ok) {
      const data = await response.json();
      return data.initialized_stats;
    } else {
      throw new Error("Failed to initialize dashboard stats");
    }
  } catch (error) {
    console.error("Error initializing dashboard stats:", error);
    return null;
  }
}

async function refreshDashboardStats() {
  try {
    const response = await fetch(`http://localhost:8000/api/frontend/dashboard-stats/refresh`, {
      method: 'POST'
    });
    if (response.ok) {
      const data = await response.json();
      return data.refreshed_stats;
    } else {
      throw new Error("Failed to refresh dashboard stats");
    }
  } catch (error) {
    console.error("Error refreshing dashboard stats:", error);
    return null;
  }
}

// Make dashboard functions globally available
window.getDashboardStatsFromBackend = getDashboardStatsFromBackend;
window.initializeDashboardStats = initializeDashboardStats;
window.refreshDashboardStats = refreshDashboardStats;

console.log("API Integration loaded. Backend URL:", API_BASE_URL);
