import React from "react";
import Navbar from "../components/Navbar";

const Home: React.FC = () => {
	return (
		<div className="flex flex-col h-screen bg-gradient-to-b from-yellow-200 to-yellow-600">
			<Navbar />
			<div className="flex-1 flex justify-center items-center p-6">
				Welcome to Aims wannabe.
			</div>
		</div>
	);
};

export default Home;
