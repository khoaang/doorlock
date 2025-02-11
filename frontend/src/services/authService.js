import api from "./api";

const authService = {
  login: async (username, password) => {
    return api.post("/auth/login", { username, password });
  },

  register: async (userData) => {
    return api.post("/auth/register", userData);
  },

  getCurrentUser: async () => {
    return api.get("/users/me");
  },

  updateUser: async (userId, userData) => {
    return api.put(`/users/${userId}`, userData);
  },

  changePassword: async (oldPassword, newPassword) => {
    return api.post("/auth/change-password", { oldPassword, newPassword });
  },

  resetPassword: async (email) => {
    return api.post("/auth/reset-password", { email });
  },

  verifyResetToken: async (token) => {
    return api.post("/auth/verify-reset-token", { token });
  },

  setNewPassword: async (token, newPassword) => {
    return api.post("/auth/set-new-password", { token, newPassword });
  },
};

export default authService;
