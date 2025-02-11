import { useState, useCallback } from "react";

const useConfirm = () => {
  const [dialog, setDialog] = useState({
    open: false,
    title: "",
    message: "",
    confirmText: "Confirm",
    cancelText: "Cancel",
    severity: "warning",
    onConfirm: () => {},
  });

  const showConfirm = useCallback(
    ({
      title,
      message,
      confirmText = "Confirm",
      cancelText = "Cancel",
      severity = "warning",
      onConfirm,
    }) => {
      setDialog({
        open: true,
        title,
        message,
        confirmText,
        cancelText,
        severity,
        onConfirm,
      });
    },
    []
  );

  const hideConfirm = useCallback(() => {
    setDialog((prev) => ({
      ...prev,
      open: false,
    }));
  }, []);

  const handleConfirm = useCallback(() => {
    dialog.onConfirm();
    hideConfirm();
  }, [dialog, hideConfirm]);

  return {
    dialog,
    showConfirm,
    hideConfirm,
    handleConfirm,
  };
};

export default useConfirm;
