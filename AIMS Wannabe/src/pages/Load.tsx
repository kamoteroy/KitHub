import React, { useState } from "react";
import axios from "axios";
import { useAuthStore } from "../store/AuthStore";
import Navbar from "../components/Navbar";
import CONFIG from "../components/Config";

const Load: React.FC = () => {
	const [idnum, setIDnum] = useState("");
	const [credits, setCredits] = useState("");
	const [error, setError] = useState<string | null>(null);
	const [success, setSuccess] = useState<string | null>(null);
	const [loading, setLoading] = useState(false);
	const { token } = useAuthStore();
	const [focusedField, setFocusedField] = useState<"idnum" | "credits" | null>(
		null
	);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setError(null);
		setSuccess(null);
		setLoading(true);

		const id = idnum.replace(/-/g, "");

		try {
			const response = await axios.post(
				`${CONFIG.BASE_URL}/addcredits`,
				{
					idnum: id,
					credits: credits,
				},
				{
					headers: {
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`,
					},
				}
			);

			const { message } = response.data;
			setSuccess(message);
			setIDnum("");
			setCredits("");
		} catch (err: any) {
			setError(err.response?.data?.message || "Failed to add credits");
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="flex flex-col items-center justify-center h-screen bg-gradient-to-b from-yellow-200 to-yellow-600">
			<Navbar />
			<div className="flex-1 flex justify-center items-center p-6">
				<div className="bg-red-900 border border-red-200 rounded-lg shadow-xl p-8 w-96">
					<h2 className="text-yellow-500 text-lg font-bold mb-4 border-b pb-2">
						Add Load
					</h2>

					<form onSubmit={handleSubmit}>
						<label
							className={`text-sm ${
								focusedField === "idnum" ? "text-yellow-300" : "text-white"
							}`}
						>
							ID Number:
						</label>
						<input
							type="text"
							placeholder="xx-xxxx-xxx"
							className="w-full p-2 mb-4 mt-2 border rounded bg-white text-black"
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
								focusedField === "credits" ? "text-yellow-300" : "text-white"
							}`}
						>
							Credits:
						</label>
						<input
							type="number"
							placeholder="Enter amount"
							className="w-full p-2 mb-4 mt-2 border rounded bg-white text-black appearance-none [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none [&::-moz-appearance:textfield]"
							value={credits}
							onChange={(e) => {
								const value = e.target.value;
								if (/^\d*$/.test(value)) {
									// Allow only digits (0-9)
									setCredits(value);
								}
							}}
							onFocus={() => setFocusedField("credits")}
							onBlur={() => setFocusedField(null)}
							required
						/>

						<div className="flex flex-col justify-center items-center">
							<button
								type="submit"
								disabled={loading}
								className="bg-yellow-500 text-black px-4 py-2 rounded hover:bg-yellow-400 disabled:bg-gray-400"
							>
								{loading ? "Processing..." : "Add"}
							</button>

							{error && <p className="mt-2 text-red-400">{error}</p>}
							{success && <p className="mt-2 text-green-400">{success}</p>}
						</div>
					</form>
				</div>
			</div>
		</div>
	);
};

export default Load;
