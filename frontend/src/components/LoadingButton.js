import React from "react";
import { Button, CircularProgress } from "@mui/material";

const LoadingButton = ({ loading = false, children, startIcon, ...props }) => {
  return (
    <Button
      {...props}
      disabled={loading || props.disabled}
      startIcon={
        loading ? <CircularProgress size={20} color="inherit" /> : startIcon
      }
    >
      {children}
    </Button>
  );
};

export default LoadingButton;
