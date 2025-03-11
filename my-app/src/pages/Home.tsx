import React from "react";
import { useAuthStore } from "../store/AuthStore";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";

const Home: React.FC = () => {
	return (
		<div className="flex flex-col md:flex-row h-screen bg-gradient-to-b from-yellow-200 to-yellow-600">
			<Navbar />
		</div>
	);
};

export default Home;
