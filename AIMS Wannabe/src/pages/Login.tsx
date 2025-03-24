import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuthStore } from "../store/AuthStore";
import CONFIG from "../components/Config";

const Login: React.FC = () => {
	const [idnum, setIDnum] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState<string | null>(null);
	const [focusedField, setFocusedField] = useState<"idnum" | "password" | null>(
		null
	);
	const navigate = useNavigate();

	const handleLogin = async (e: React.FormEvent) => {
		e.preventDefault();

		try {
			const id = idnum.replace(/-/g, "");
			const response = await axios.post(`${CONFIG.BASE_URL}/login`, {
				id,
				password,
			});

			if (response.data.token) {
				const expiresIn = 60;
				console.log(expiresIn);
				useAuthStore
					.getState()
					.login(response.data.user, response.data.token, 60);
				navigate("/");
			} else {
				setError("Login failed. Please try again.");
			}
		} catch (error: any) {
			setError(error.response?.data?.message || "Invalid email or password");
			console.error("Login failed", error);
		}
	};

	return (
		<div className="flex items-center justify-center h-screen bg-gradient-to-b from-yellow-200 to-yellow-600">
			<div className="bg-gray-700 border border-gray-600 rounded-lg shadow-xl p-8 w-96">
				<h2 className="text-white text-lg font-bold mb-4 border-b pb-2">
					User Authentication
				</h2>

				<form onSubmit={handleLogin}>
					<label
						className={`text-sm ${
							focusedField === "idnum" ? "text-green-400" : "text-white"
						}`}
					>
						ID Number:
					</label>
					<input
						type="text"
						placeholder="xx-xxxx-xxx"
						className="w-full p-2 mb-4 border rounded bg-white text-black"
						value={idnum}
						onChange={(e) => {
							let value = e.target.value.replace(/\D/g, ""); // Remove non-numeric characters

							// Auto format as XX-XXXX-XXX
							if (value.length > 2)
								value = value.slice(0, 2) + "-" + value.slice(2);
							if (value.length > 7)
								value = value.slice(0, 7) + "-" + value.slice(7, 10);

							setIDnum(value);
						}}
						onFocus={() => setFocusedField("idnum")}
						onBlur={() => setFocusedField(null)}
						maxLength={11} // Ensures the format does not exceed XX-XXXX-XXX
						required
					/>

					<label
						className={`text-sm ${
							focusedField === "password" ? "text-green-400" : "text-white"
						}`}
					>
						Pin:
					</label>
					<input
						type="password"
						placeholder="••••••"
						className="w-full p-2 mb-4 border rounded bg-white text-black"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						onFocus={() => setFocusedField("password")}
						onBlur={() => setFocusedField(null)}
						maxLength={6}
						required
					/>

					<div className="flex flex-col justify-center items-center">
						<button
							type="submit"
							className="bg-yellow-500 text-black px-4 py-2 rounded hover:bg-yellow-400"
						>
							Login
						</button>
						{error && <p className="mt-2 text-red-400">{error}</p>}
					</div>
				</form>

				<p className="text-white mt-4 text-sm">
					Forgot your password?{" "}
					<a href="/forgot" className="text-blue-400 underline">
						Click here
					</a>
				</p>
			</div>
		</div>
	);
};

export default Login;
