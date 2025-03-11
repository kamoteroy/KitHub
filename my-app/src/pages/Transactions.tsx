import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuthStore } from "../store/AuthStore";
import Navbar from "../components/Navbar";

interface Transaction {
	type: string;
	amount: string;
	time: string;
}

const Transactions: React.FC = () => {
	const [transactions, setTransactions] = useState<Transaction[]>([]);
	const [loading, setLoading] = useState<boolean>(true);
	const [error, setError] = useState<string | null>(null);
	const { token } = useAuthStore();

	const { idnum, name, balance } = useAuthStore((state) => state.user) || {};
	const formattedIdnum = idnum
		? idnum.toString().replace(/(\d{2})(\d{4})(\d{3})/, "$1-$2-$3")
		: "";

	useEffect(() => {
		const fetchTransactions = async () => {
			if (!idnum) return;

			setLoading(true);
			try {
				const response = await axios.get(`http://localhost:5000/transactions`, {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`,
					},
				});
				setTransactions(response.data);
			} catch (err: any) {
				setError(err.response?.data?.message || "Failed to fetch transactions");
			} finally {
				setLoading(false);
			}
		};

		fetchTransactions();
	}, [idnum]);

	return (
		<div className="bg-gradient-to-b from-yellow-200 to-yellow-600 min-h-screen">
			<Navbar />
			<div className="flex flex-col md:flex-row p-6 pt-16">
				<div className="flex-1 overflow-auto">
					<div className="flex justify-between items-center">
						<h2 className="text-lg font-semibold">
							WELCOME, {name} ({formattedIdnum})
						</h2>
						<h2 className="text-lg font-semibold">BALANCE: {balance}</h2>
					</div>
					<div className="mt-4 bg-white shadow-md rounded-lg overflow-hidden">
						<div className="overflow-x-auto">
							{loading ? (
								<p className="p-4 text-center">Loading transactions...</p>
							) : error ? (
								<p className="p-4 text-red-600 text-center">{error}</p>
							) : (
								<table className="w-full border-collapse">
									<thead>
										<tr className="bg-red-900 text-white">
											<th className="p-2 border">Date</th>
											<th className="p-2 border">Item</th>
											<th className="p-2 border">Amount</th>
										</tr>
									</thead>
									<tbody>
										{transactions.length > 0 ? (
											transactions.map((transaction, index) => {
												const [date, time] = transaction.time.split("T");

												const formattedTime = new Date(
													transaction.time
												).toLocaleTimeString("en-US", {
													hour: "numeric",
													minute: "2-digit",
													hour12: true,
												});

												return (
													<tr
														key={index}
														className={`${
															index % 2 === 0 ? "bg-gray-100" : "bg-white"
														} border`}
													>
														<td className="p-1 border pl-4">
															{date} {formattedTime}
														</td>
														<td className="p-1 border pl-4">
															{transaction.type}
														</td>
														<td className="p-1 border text-right pr-4">
															{transaction.amount}
														</td>
													</tr>
												);
											})
										) : (
											<tr>
												<td colSpan={4} className="p-4 text-center">
													No transactions found.
												</td>
											</tr>
										)}
									</tbody>
								</table>
							)}
						</div>
					</div>
				</div>
			</div>
		</div>
	);
};

export default Transactions;
