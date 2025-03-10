import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/AuthStore"; // Adjust the import as needed

const Navbar: React.FC = () => {
	const navItems = [
		{ name: "Home", path: "/home" },
		{ name: "Change PIN", path: "/change" },
		{ name: "History", path: "/history" },
	];

	const logout = useAuthStore((state) => state.logout);
	const navigate = useNavigate();

	const handleLogout = () => {
		logout();
		navigate("/login");
	};

	return (
		<nav className="bg-red p-2 w-full flex justify-center fixed top-0 left-0">
			<div className="flex flex-wrap justify-center md:justify-center items-center space-x-2">
				{navItems.map((item) => (
					<NavLink
						key={item.name}
						to={item.path}
						className="px-4 py-2 rounded-md text-sm text-white bg-red-700 hover:bg-yellow-300 hover:text-black transition"
					>
						{item.name}
					</NavLink>
				))}

				<button
					onClick={handleLogout}
					className="px-4 py-2 rounded-md text-sm text-white bg-red-700 hover:bg-yellow-500 hover:text-black transition"
				>
					Logout
				</button>
			</div>
		</nav>
	);
};

export default Navbar;
