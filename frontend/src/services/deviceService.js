import api from "./api";

const deviceService = {
  getAllDevices: async () => {
    return api.get("/devices");
  },

  getDevice: async (deviceId) => {
    return api.get(`/devices/${deviceId}`);
  },

  addDevice: async (deviceData) => {
    return api.post("/devices", deviceData);
  },

  updateDevice: async (deviceId, deviceData) => {
    return api.put(`/devices/${deviceId}`, deviceData);
  },

  deleteDevice: async (deviceId) => {
    return api.delete(`/devices/${deviceId}`);
  },

  getDeviceState: async (deviceId) => {
    return api.get(`/devices/${deviceId}/state`);
  },

  sendCommand: async (deviceId, command) => {
    return api.post(`/devices/${deviceId}/command`, command);
  },

  uploadScript: async (deviceId, scriptFile) => {
    const formData = new FormData();
    formData.append("file", scriptFile);
    return api.post(`/scripts/${deviceId}`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  removeScript: async (deviceId, scriptName) => {
    return api.delete(`/scripts/${deviceId}/${scriptName}`);
  },

  enqueueScript: async (deviceId, scriptName) => {
    return api.post(`/enqueue-script/${deviceId}`, { name: scriptName });
  },

  dequeueScript: async (deviceId, scriptName) => {
    return api.post(`/dequeue-script/${deviceId}`, { name: scriptName });
  },

  getDevicesByType: async (deviceType) => {
    return api.get(`/devices/type/${deviceType}`);
  },

  getDevicesByRoom: async (roomId) => {
    return api.get(`/devices/room/${roomId}`);
  },

  getDeviceEvents: async (deviceId, limit = 100) => {
    return api.get(`/devices/${deviceId}/events`, { params: { limit } });
  },

  updateDeviceConfig: async (deviceId, config) => {
    return api.put(`/devices/${deviceId}/config`, config);
  },

  discoverDevices: async () => {
    return api.post("/devices/discover");
  },
};

export default deviceService;
