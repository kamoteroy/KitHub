import { create } from "zustand";

interface AuthState {
	user: string | null;
	login: (user: string) => void;
	logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
	user: localStorage.getItem("user"),
	login: (user) => {
		localStorage.setItem("user", user);
		set({ user });
	},
	logout: () => {
		localStorage.removeItem("user");
		set({ user: null });
	},
}));
