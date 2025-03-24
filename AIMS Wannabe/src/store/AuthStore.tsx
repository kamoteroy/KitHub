import { create } from "zustand";
import { toast } from "react-toastify";

interface User {
	idnum: string;
	name: string;
	balance: number;
	isAdmin: boolean;
}

interface AuthState {
	user: User | null;
	token: string | null;
	expiration: number | null;
	login: (user: User, token: string, expiresIn: number) => void;
	logout: (timedOut?: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => {
	const logout = (timedOut = false) => {
		localStorage.removeItem("user");
		localStorage.removeItem("token");
		localStorage.removeItem("expiration");
		set({ user: null, token: null, expiration: null });

		// Show toast only if session expired
		if (timedOut) {
			toast.warn("Session timed out. Please log in again.", {
				position: "top-right",
				autoClose: 3000,
			});
		}
	};

	// Check token expiration on app load
	const expiration = localStorage.getItem("expiration");
	if (expiration && Date.now() >= Number(expiration)) {
		logout(true); // Pass `true` to indicate timeout
	}

	return {
		user: localStorage.getItem("user")
			? JSON.parse(localStorage.getItem("user") as string)
			: null,
		token: localStorage.getItem("token") || null,
		expiration: expiration ? Number(expiration) : null,

		login: (user, token, expiresIn) => {
			const expirationTime = Date.now() + expiresIn * 1000;
			localStorage.setItem("user", JSON.stringify(user));
			localStorage.setItem("token", token);
			localStorage.setItem("expiration", expirationTime.toString());

			set({ user, token, expiration: expirationTime });

			// Auto logout when token expires
			setTimeout(() => logout(true), expiresIn * 1000);
		},

		logout,
	};
});
