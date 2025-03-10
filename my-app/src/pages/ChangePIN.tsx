import React, { useState } from "react";
import Navbar from "../components/Navbar";

const ChangePIN: React.FC = () => {
	const [oldPassword, setOldPassword] = useState("");
	const [newPassword, setNewPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");

	const handleChangePassword = (e: React.FormEvent) => {
		e.preventDefault();
		if (newPassword !== confirmPassword) {
			alert("New passwords do not match");
			return;
		}
		alert("Password changed successfully!");
	};

	return (
		<>
			<div className="flex flex-col md:flex-row h-screen bg-gradient-to-b from-yellow-200 to-yellow-600">
				<Navbar />
				{/* Main Content */}
				<div className="flex-1 flex justify-center items-center p-6">
					<div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
						<h2 className="text-lg font-bold mb-4 text-center">
							Change Password
						</h2>
						<form onSubmit={handleChangePassword} className="space-y-4">
							<input
								type="password"
								placeholder="Old Password"
								className="w-full p-2 border rounded"
								value={oldPassword}
								onChange={(e) => setOldPassword(e.target.value)}
								required
							/>
							<input
								type="password"
								placeholder="New Password"
								className="w-full p-2 border rounded"
								value={newPassword}
								onChange={(e) => setNewPassword(e.target.value)}
								required
							/>
							<input
								type="password"
								placeholder="Confirm Password"
								className="w-full p-2 border rounded"
								value={confirmPassword}
								onChange={(e) => setConfirmPassword(e.target.value)}
								required
							/>
							<div className="flex justify-between">
								<button
									type="submit"
									className="bg-yellow-500 text-black px-4 py-2 rounded hover:bg-yellow-600"
								>
									Change Password
								</button>
								<button
									type="reset"
									className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
									onClick={() => {
										setOldPassword("");
										setNewPassword("");
										setConfirmPassword("");
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
