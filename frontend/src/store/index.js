import { createStore } from "vuex";

console.log('Store module loading');

const stored = sessionStorage.getItem("authData");
const authData = stored ? JSON.parse(stored) : null;

const storedUser = sessionStorage.getItem("userData");
const userData = storedUser ? JSON.parse(storedUser) : null;

console.log('Stored auth data:', authData);
console.log('Stored user data:', userData);

export default createStore({
  state: {
    backendUrl: "http://127.0.0.1:5000",
    authData: authData,
    isAuthenticated: !!authData,
    userData: userData,
  },

  mutations: {
    SET_AUTH(state, authData) {
      state.authData = authData;
      state.isAuthenticated = true;
      sessionStorage.setItem("authData", JSON.stringify(authData));
    },

    LOGOUT(state) {
      sessionStorage.removeItem("authData");
      sessionStorage.removeItem("userData");
      state.authData = null;
      state.userData = null;
      state.isAuthenticated = false;
    },

    SET_USER_DATA(state, payload) {
      state.userData = payload;
      sessionStorage.setItem("userData", JSON.stringify(payload));
    },
  },

  actions: {
    login({ commit }, authData) {
      commit("SET_AUTH", authData);
    },
    logout({ commit }) {
      commit("LOGOUT");
    },
    async fetchUserData({ commit, state }) {
      const userId = state.authData?.id;
      if (!userId) return;

      const url = `${state.backendUrl}/api/user/${userId}`;
      try {
        const res = await fetch(url, {
          headers: {
            "Content-Type": "application/json",
            Authorization: state.authData?.token,
          },
        });

        if (!res.ok) throw new Error("Failed to fetch user data");

        const data = await res.json();
        commit("SET_USER_DATA", data);
      } catch (error) {
        console.error("Error fetching user data:", error);
      }
    },
  },

  getters: {
    isAuthenticated: (state) => state.isAuthenticated,
    userData: (state) => state.userData,
    userEmail: (state) => state.authData?.email,
    userRole: (state) => state.authData?.role,
    userId: (state) => state.authData?.id,
  },
});