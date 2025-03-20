import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Signup: React.FC = () => {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const navigate = useNavigate();

	const handleSignup = async (e: React.FormEvent) => {
		e.preventDefault();
		try {
			await axios.post("http://localhost:5000/signup", { email, password });
			navigate("/login");
		} catch (error) {
			console.error("Signup failed", error);
		}
	};

	return (
		<div>
			<h2>Signup</h2>
			<form onSubmit={handleSignup}>
				<input
					type="email"
					placeholder="Email"
					value={email}
					onChange={(e) => setEmail(e.target.value)}
					required
				/>
				<input
					type="password"
					placeholder="Password"
					value={password}
					onChange={(e) => setPassword(e.target.value)}
					required
				/>
				<button type="submit">Signup</button>
			</form>
		</div>
	);
};

export default Signup;
