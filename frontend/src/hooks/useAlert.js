import { useState, useCallback } from "react";

const useAlert = () => {
  const [alert, setAlert] = useState({
    open: false,
    message: "",
    severity: "info",
  });

  const showAlert = useCallback((message, severity = "info") => {
    setAlert({
      open: true,
      message,
      severity,
    });
  }, []);

  const hideAlert = useCallback(() => {
    setAlert((prev) => ({
      ...prev,
      open: false,
    }));
  }, []);

  const showSuccess = useCallback(
    (message) => {
      showAlert(message, "success");
    },
    [showAlert]
  );

  const showError = useCallback(
    (message) => {
      showAlert(message, "error");
    },
    [showAlert]
  );

  const showWarning = useCallback(
    (message) => {
      showAlert(message, "warning");
    },
    [showAlert]
  );

  const showInfo = useCallback(
    (message) => {
      showAlert(message, "info");
    },
    [showAlert]
  );

  return {
    alert,
    showAlert,
    hideAlert,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };
};

export default useAlert;
