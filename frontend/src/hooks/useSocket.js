import { useEffect, useCallback } from "react";
import { useAuth } from "../contexts/AuthContext";
import socketService from "../services/socketService";

const useSocket = () => {
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      socketService.connect(localStorage.getItem("token"));
    } else {
      socketService.disconnect();
    }

    return () => {
      socketService.disconnect();
    };
  }, [user]);

  const subscribe = useCallback((event, callback) => {
    socketService.on(event, callback);
    return () => socketService.off(event, callback);
  }, []);

  const emit = useCallback((event, data) => {
    socketService.emit(event, data);
  }, []);

  const subscribeToDevice = useCallback((deviceId) => {
    socketService.subscribeToDevice(deviceId);
  }, []);

  const unsubscribeFromDevice = useCallback((deviceId) => {
    socketService.unsubscribeFromDevice(deviceId);
  }, []);

  const sendDeviceCommand = useCallback((deviceId, command) => {
    socketService.sendDeviceCommand(deviceId, command);
  }, []);

  const requestDeviceState = useCallback((deviceId) => {
    socketService.requestDeviceState(deviceId);
  }, []);

  return {
    isConnected: socketService.isConnected(),
    subscribe,
    emit,
    subscribeToDevice,
    unsubscribeFromDevice,
    sendDeviceCommand,
    requestDeviceState,
  };
};

export default useSocket;
