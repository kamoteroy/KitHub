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
import Transactions from "./pages/Transactions";
import Load from "./pages/Load";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const PrivateRoute: React.FC<{ element: JSX.Element }> = ({ element }) => {
	const { user } = useAuthStore();
	return user ? element : <Navigate to="/login" />;
};

const PublicRoute: React.FC<{ element: JSX.Element }> = ({ element }) => {
	const { user } = useAuthStore();
	return user ? <Navigate to="/" /> : element;
};

const App: React.FC = () => {
	const isAuthenticated = useAuthStore((state) => state.user !== null);

	return (
		<>
			<ToastContainer position="bottom-right" />
			<Router>
				<Routes>
					<Route
						path="*"
						element={<Navigate to={isAuthenticated ? "/" : "/login"} />}
					/>

					{/* Public Routes */}
					<Route path="/login" element={<PublicRoute element={<Login />} />} />
					<Route
						path="/signup"
						element={<PublicRoute element={<Signup />} />}
					/>
					<Route
						path="/forgot"
						element={<PublicRoute element={<ForgotPassword />} />}
					/>

					{/* Private Routes */}
					<Route path="/" element={<PrivateRoute element={<Home />} />} />
					<Route
						path="/transactions"
						element={<PrivateRoute element={<Transactions />} />}
					/>
					<Route
						path="/change"
						element={<PrivateRoute element={<ChangePIN />} />}
					/>
					<Route path="/load" element={<PrivateRoute element={<Load />} />} />
				</Routes>
			</Router>
		</>
	);
};

export default App;
