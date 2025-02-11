import { io } from "socket.io-client";

class SocketService {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.eventHandlers = new Map();
  }

  connect(token) {
    if (this.socket) {
      return;
    }

    const socketUrl =
      process.env.REACT_APP_SOCKET_URL || "http://localhost:5000";

    this.socket = io(socketUrl, {
      auth: {
        token,
      },
      transports: ["websocket"],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    this.socket.on("connect", () => {
      console.log("WebSocket connected");
      this.connected = true;
    });

    this.socket.on("disconnect", () => {
      console.log("WebSocket disconnected");
      this.connected = false;
    });

    this.socket.on("error", (error) => {
      console.error("WebSocket error:", error);
    });

    // Set up default event handlers
    this.setupDefaultHandlers();
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
    }
  }

  setupDefaultHandlers() {
    // Device state updates
    this.socket.on("device_state_update", (data) => {
      this.triggerEvent("device_state_update", data);
    });

    // Device status updates
    this.socket.on("device_status_update", (data) => {
      this.triggerEvent("device_status_update", data);
    });

    // Script execution updates
    this.socket.on("script_execution_update", (data) => {
      this.triggerEvent("script_execution_update", data);
    });

    // Device discovery updates
    this.socket.on("device_discovered", (data) => {
      this.triggerEvent("device_discovered", data);
    });

    // Automation triggers
    this.socket.on("automation_triggered", (data) => {
      this.triggerEvent("automation_triggered", data);
    });

    // Error notifications
    this.socket.on("error_notification", (data) => {
      this.triggerEvent("error_notification", data);
    });
  }

  on(event, callback) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    this.eventHandlers.get(event).add(callback);
  }

  off(event, callback) {
    if (this.eventHandlers.has(event)) {
      this.eventHandlers.get(event).delete(callback);
    }
  }

  triggerEvent(event, data) {
    if (this.eventHandlers.has(event)) {
      this.eventHandlers.get(event).forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in ${event} handler:`, error);
        }
      });
    }
  }

  emit(event, data) {
    if (this.socket && this.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn("Socket not connected. Unable to emit event:", event);
    }
  }

  isConnected() {
    return this.connected;
  }

  // Specific event emitters
  subscribeToDevice(deviceId) {
    this.emit("subscribe_device", { deviceId });
  }

  unsubscribeFromDevice(deviceId) {
    this.emit("unsubscribe_device", { deviceId });
  }

  sendDeviceCommand(deviceId, command) {
    this.emit("device_command", { deviceId, command });
  }

  requestDeviceState(deviceId) {
    this.emit("request_device_state", { deviceId });
  }
}

// Create a singleton instance
const socketService = new SocketService();

export default socketService;
