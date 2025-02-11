import React from "react";
import { Alert, Snackbar } from "@mui/material";

const AlertMessage = ({
  open,
  onClose,
  message,
  severity = "info",
  autoHideDuration = 6000,
}) => {
  return (
    <Snackbar
      open={open}
      autoHideDuration={autoHideDuration}
      onClose={onClose}
      anchorOrigin={{ vertical: "top", horizontal: "right" }}
    >
      <Alert onClose={onClose} severity={severity} variant="filled">
        {message}
      </Alert>
    </Snackbar>
  );
};

export default AlertMessage;
