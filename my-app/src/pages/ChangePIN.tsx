import React, { useState } from "react";
import Navbar from "../components/Navbar";
import { useAuthStore } from "../store/AuthStore";
import CONFIG from "../components/Config";

const ChangePIN: React.FC = () => {
	const { token } = useAuthStore();
	const [oldPassword, setOldPassword] = useState("");
	const [newPassword, setNewPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [success, setSuccess] = useState("");

	const handleChangePassword = async (e: React.FormEvent) => {
		e.preventDefault();
		setError("");
		setSuccess("");
		if (newPassword !== confirmPassword) {
			setError("New passwords do not match.");
			return;
		}
		try {
			setLoading(true);

			const response = await fetch(`${CONFIG.BASE_URL}/changepin`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				body: JSON.stringify({
					oldPIN: oldPassword,
					newPIN: newPassword,
				}),
			});

			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.message || "Failed to change PIN.");
			}

			setSuccess("PIN changed successfully!");
			setOldPassword("");
			setNewPassword("");
			setConfirmPassword("");
		} catch (err: any) {
			setError(err.message);
		} finally {
			setLoading(false);
		}
	};

	return (
		<>
			<div className="flex flex-col items-center justify-center h-screen bg-gradient-to-b from-yellow-200 to-yellow-600">
				<Navbar />
				<div className="flex-1 flex justify-center items-center p-6">
					<div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
						<h2 className="text-lg font-bold mb-4 text-center">Change PIN</h2>

						{error && <p className="text-red-500 text-center">{error}</p>}
						{success && <p className="text-green-500 text-center">{success}</p>}

						<form onSubmit={handleChangePassword} className="space-y-4">
							<input
								type="password"
								placeholder="Old PIN"
								className="w-full p-2 border rounded"
								value={oldPassword}
								onChange={(e) => setOldPassword(e.target.value)}
								maxLength={6}
								required
							/>
							<input
								type="password"
								placeholder="New PIN"
								className="w-full p-2 border rounded"
								value={newPassword}
								onChange={(e) => setNewPassword(e.target.value)}
								maxLength={6}
								required
							/>
							<input
								type="password"
								placeholder="Confirm PIN"
								className="w-full p-2 border rounded"
								value={confirmPassword}
								onChange={(e) => setConfirmPassword(e.target.value)}
								maxLength={6}
								required
							/>
							<div className="flex justify-between">
								<button
									type="submit"
									className="bg-yellow-500 text-black px-4 py-2 rounded hover:bg-yellow-600"
									disabled={loading}
								>
									{loading ? "Changing..." : "Change PIN"}
								</button>
								<button
									type="reset"
									className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
									onClick={() => {
										setOldPassword("");
										setNewPassword("");
										setConfirmPassword("");
										setError("");
										setSuccess("");
									}}
								>
									Clear Entries
								</button>
							</div>
						</form>
					</div>
				</div>
			</div>
		</>
	);
};

export default ChangePIN;
