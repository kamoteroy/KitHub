import React, { JSX } from "react";
import {
	BrowserRouter as Router,
	Route,
	Routes,
	Navigate,
} from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Home from "./pages/Home";
import { useAuthStore } from "./store/AuthStore";
import ForgotPassword from "./pages/Forgot";
import ChangePIN from "./pages/ChangePIN";

const PrivateRoute: React.FC<{ element: JSX.Element }> = ({ element }) => {
	const { user } = useAuthStore();
	return user ? element : <Navigate to="/home" />;
};

const PublicRoute: React.FC<{ element: JSX.Element }> = ({ element }) => {
	const { user } = useAuthStore();
	return user ? <Navigate to="/login" /> : element;
};

const App: React.FC = () => {
	const isAuthenticated = useAuthStore((state) => state.user !== null);

	return (
		<Router>
			<Routes>
				<Route
					path="/"
					element={<Navigate to={isAuthenticated ? "/home" : "/login"} />}
				/>
				<Route
					path="*"
					element={<Navigate to={isAuthenticated ? "/home" : "/login"} />}
				/>

				{/* Public Routes */}
				<Route path="/login" element={<PublicRoute element={<Login />} />} />
				<Route path="/signup" element={<PublicRoute element={<Signup />} />} />
				<Route
					path="/forgot"
					element={<PublicRoute element={<ForgotPassword />} />}
				/>

				{/* Private Routes */}
				<Route path="/home" element={<PrivateRoute element={<Home />} />} />
				<Route
					path="/change"
					element={<PrivateRoute element={<ChangePIN />} />}
				/>
			</Routes>
		</Router>
	);
};

export default App;
