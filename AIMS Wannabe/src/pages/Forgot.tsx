import { useState } from "react";
import axios from "axios";
import CONFIG from "../components/Config";

const ForgotPassword: React.FC = () => {
	const [idnum, setIDnum] = useState("");
	const [message, setMessage] = useState("");
	const [error, setError] = useState("");
	const [focusedField, setFocusedField] = useState<"idnum" | null>(null);
	const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		let value = e.target.value.replace(/\D/g, "");
		if (value.length > 10) value = value.slice(0, 10);

		let formatted = value.replace(
			/^(\d{2})(\d{0,4})(\d{0,3})$/,
			(_, p1, p2, p3) => [p1, p2, p3].filter(Boolean).join("-")
		);
		setIDnum(formatted);
	};

	const handlePasswordReset = async () => {
		setMessage("");
		setError("");

		if (!/^\d{2}-\d{4}-\d{3}$/.test(idnum)) {
			setError("Invalid ID number format. Use XX-XXXX-XXX.");
			return;
		}

		try {
			const filteredID = idnum.replace(/-/g, "");
			const response = await axios.post(`${CONFIG.BASE_URL}/reset`, {
				idnum: filteredID,
			});

			if (response.data.success) {
				setMessage("Password reset link sent! Check your email.");
			} else {
				setError(response.data.error || "ID number not found.");
			}
		} catch (err: any) {
			setError(err.response?.data?.error || "Something went wrong.");
		}
	};

	return (
		<div className="flex items-center justify-center min-h-screen bg-gradient-to-b from-yellow-200 to-yellow-600">
			<div className="bg-gray-700 border border-gray-600 rounded-lg shadow-lg text-white p-8 w-96">
				<h2 className="text-lg font-bold mb-2">Forgot Password</h2>
				<hr className="border-gray-400 mb-4" />

				<label
					className={`text-sm ${
						focusedField === "idnum" ? "text-green-400" : "text-white"
					}`}
				>
					ID Number:
				</label>
				<input
					type="text"
					className="w-full p-2 mb-4 mt-2 bg-gray-200 text-black rounded outline-none"
					placeholder="xx-xxxx-xxx"
					value={idnum}
					onChange={handleChange}
					onFocus={() => setFocusedField("idnum")}
					onBlur={() => setFocusedField(null)}
					maxLength={12}
				/>

				<button
					onClick={handlePasswordReset}
					className="w-full px-4 py-2 bg-red-800 hover:bg-red-700 text-white rounded"
				>
					Send Reset Link
				</button>

				{message && <p className="mt-4 text-green-400">{message}</p>}
				{error && <p className="mt-2 text-red-400">{error}</p>}

				<p className="text-white mt-4 text-sm flex justify-center">
					<a href="/login" className="text-blue-400 underline">
						Login
					</a>
				</p>
			</div>
		</div>
	);
};

export default ForgotPassword;
