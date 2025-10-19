// script.js - CogniSpike Dashboard Interaction

document.addEventListener("DOMContentLoaded", () => {
  const wheelOptions = document.querySelectorAll(".wheel-option");
  const contentOverlay = document.getElementById("content-overlay");
  const mainContentCard = document.getElementById("main-content-card");
  const contentPanels = document.querySelectorAll(".content-panel");
  const mainContainer = document.querySelector(".main-container");
  const closeCardButton = document.getElementById("close-card-button");

  // --- Panel Switching ---
  wheelOptions.forEach((option) => {
    option.addEventListener("click", () => {
      const targetPanelId = option.getAttribute("data-target");

      // Hide all panels first
      contentPanels.forEach((panel) => panel.classList.remove("active"));

      // Show the target panel
      const targetPanel = document.getElementById(targetPanelId);
      if (targetPanel) {
        targetPanel.classList.add("active");
        // Show the overlay and card
        contentOverlay.classList.add("visible");
        mainContainer.classList.add("blurred"); // Blur background
      }
    });
  });

  // --- Close Card Button ---
  closeCardButton.addEventListener("click", () => {
    contentOverlay.classList.remove("visible");
    mainContainer.classList.remove("blurred"); // Unblur background
  });

  // --- File Input Name Display ---
  function setupFileInputListener(inputId, spanId) {
    const fileInput = document.getElementById(inputId);
    const fileNameSpan = document.getElementById(spanId);
    if (fileInput && fileNameSpan) {
      fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
          fileNameSpan.textContent = fileInput.files[0].name;
        } else {
          fileNameSpan.textContent = "No file chosen";
        }
      });
    }
  }
  setupFileInputListener("image-upload-classifier", "file-name-classifier");
  setupFileInputListener("image-upload-visualizer", "file-name-visualizer");
  setupFileInputListener("image-upload-encoder", "file-name-encoder");

  // --- Placeholder Form Submission Handlers ---
  // We will replace these with actual fetch calls later

  function handleFormSubmit(formId, spinnerId, resultsId, endpoint) {
    const form = document.getElementById(formId);
    const spinner = document.getElementById(spinnerId);
    const resultsDiv = document.getElementById(resultsId);
    const submitButton = form.querySelector('button[type="submit"]');
    const fileInput = form.querySelector('input[type="file"]');

    if (!form) return;

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const file = fileInput.files[0];

      if (!file) {
        resultsDiv.textContent = "Please select an image file first.";
        resultsDiv.style.display = "block";
        return;
      }

      spinner.style.display = "block";
      resultsDiv.style.display = "none";
      submitButton.disabled = true;

      const formData = new FormData();
      formData.append("image", file);

      try {
        const response = await fetch(endpoint, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Server responded with an error.");
        }

        const data = await response.json();

        // Clear previous content and hide images
        resultsDiv.textContent = "";
        const existingImg = resultsDiv.querySelector("img");
        if (existingImg) existingImg.style.display = "none";

        if (endpoint === "/evaluate-image") {
          resultsDiv.textContent = data.message;
        } else if (endpoint === "/visualize") {
          const img = document.getElementById("raster-plot-image");
          if (img && data.raster_plot_url) {
            // Add a timestamp to prevent browser caching
            img.src = `${data.raster_plot_url}?t=${new Date().getTime()}`;
            img.style.display = "block";
            resultsDiv.textContent = "Raster plot generated successfully.";
          }
        } else if (endpoint === "/live-encoder") {
          const img = document.getElementById("spike-gif-image");
          if (img && data.spike_gif_url) {
            img.src = `${data.spike_gif_url}?t=${new Date().getTime()}`;
            img.style.display = "block";
            resultsDiv.textContent = "Spike GIF generated successfully.";
          }
        }
        resultsDiv.style.display = "block";
      } catch (error) {
        resultsDiv.textContent = `Error: ${error.message}`;
        resultsDiv.style.display = "block";
      } finally {
        spinner.style.display = "none";
        submitButton.disabled = false;
      }
    });
  }

  handleFormSubmit(
    "upload-form-classifier",
    "loading-spinner-classifier",
    "results-classifier",
    "/evaluate-image"
  );
  handleFormSubmit(
    "upload-form-visualizer",
    "loading-spinner-visualizer",
    "results-visualizer",
    "/visualize"
  );
  handleFormSubmit(
    "upload-form-encoder",
    "loading-spinner-encoder",
    "results-encoder",
    "/live-encoder"
  );
});
