import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/AuthStore";

const Navbar: React.FC = () => {
	const { isAdmin } = useAuthStore((state) => state.user) || {};
	const navItems = [
		{ name: "Home", path: "/" },
		{ name: "Change PIN", path: "/change" },
		{ name: "History", path: "/transactions" },
	];

	if (isAdmin) {
		navItems.push({ name: "Load", path: "/load" });
	}

	const logout = useAuthStore((state) => state.logout);
	const navigate = useNavigate();

	const handleLogout = () => {
		logout(false);
		navigate("/login");
	};

	return (
		<nav className=" p-2 w-full flex flex-wrap justify-center  top-0 left-0">
			<div className="flex flex-wrap justify-center gap-2">
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
