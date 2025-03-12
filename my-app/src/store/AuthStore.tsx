import { create } from "zustand";

interface User {
	idnum: string;
	name: string;
	balance: number;
	isAdmin: boolean;
}

interface AuthState {
	user: User | null;
	token: string | null;
	login: (user: User, token: string) => void;
	logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
	user: localStorage.getItem("user")
		? JSON.parse(localStorage.getItem("user") as string)
		: null,
	token: localStorage.getItem("token") || null,

	login: (user, token) => {
		localStorage.setItem("user", JSON.stringify(user));
		localStorage.setItem("token", token);
		set({ user, token });
	},

	logout: () => {
		localStorage.removeItem("user");
		localStorage.removeItem("token");
		set({ user: null, token: null });
	},
}));
