import React, { useEffect, useRef, useState } from "react";
import axios from "axios";
import { useAuthStore } from "../store/AuthStore";
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSave } from "@fortawesome/free-solid-svg-icons";
import Navbar from "../components/Navbar";
import CONFIG from "../components/Config";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

interface Transaction {
	type: string;
	amount: string;
	time: string;
}

const Transactions: React.FC = () => {
	const [transactions, setTransactions] = useState<Transaction[]>([]);
	const [loading, setLoading] = useState<boolean>(true);
	const [error, setError] = useState<string | null>(null);
	const { token, logout } = useAuthStore();
	const { idnum, name, balance } = useAuthStore((state) => state.user) || {};
	const navigate = useNavigate();
	const tableRef = useRef<HTMLDivElement>(null);

	const formattedIdnum = idnum
		? idnum.toString().replace(/(\d{2})(\d{4})(\d{3})/, "$1-$2-$3")
		: "";

	const [search, setSearch] = useState("");
	const [startDate, setStartDate] = useState("");
	const [endDate, setEndDate] = useState("");

	useEffect(() => {
		if (!idnum || !token) return;

		const fetchTransactions = async () => {
			setLoading(true);
			try {
				const response = await axios.get(`${CONFIG.BASE_URL}/transactions`, {
					headers: {
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`,
					},
				});
				setTransactions(response.data);
			} catch (err: any) {
				if (err.response?.status === 403) {
					logout();
					navigate("/login");
				} else {
					setError(
						err.response?.data?.message || "Failed to fetch transactions"
					);
				}
			} finally {
				setLoading(false);
			}
		};

		fetchTransactions();
	}, [idnum, token, logout, navigate]);

	const filteredTransactions = transactions.filter((transaction) => {
		const transactionDate = new Date(transaction.time)
			.toISOString()
			.split("T")[0];

		return (
			(!search ||
				transaction.type.toLowerCase().includes(search.toLowerCase()) ||
				transaction.amount.toString().includes(search)) &&
			(!startDate || transactionDate >= startDate) &&
			(!endDate || transactionDate <= endDate)
		);
	});

	const handleSavePDF = async () => {
		const tableElement = tableRef.current;
		if (!tableElement) return;

		tableElement.style.overflow = "visible";

		const scaleFactor = window.devicePixelRatio || 2;

		const canvas = await html2canvas(tableElement, {
			scale: scaleFactor,
			useCORS: true,
			backgroundColor: "#ffffff",
			windowWidth: tableElement.scrollWidth,
			windowHeight: tableElement.scrollHeight,
		} as any);

		const imgData = canvas.toDataURL("image/png");
		const pdf = new jsPDF("p", "mm", "a4");

		const imgWidth = 190;
		const imgHeight = (canvas.height * imgWidth) / canvas.width;
		const pageHeight = 297;

		let remainingHeight = imgHeight;
		let currentY = 10;

		while (remainingHeight > 0) {
			pdf.addImage(imgData, "PNG", 10, currentY, imgWidth, imgHeight);

			remainingHeight -= pageHeight;
			currentY -= pageHeight;

			if (remainingHeight > 0) pdf.addPage();
		}

		pdf.save(`${name} Transactions.pdf`);
	};

	return (
		<div className="bg-gradient-to-b from-yellow-200 to-yellow-600 min-h-screen">
			<Navbar />
			<div className="p-6">
				<div className="md:flex md:flex-row md:justify-between md:items-center flex flex-col gap-2">
					<h2 className="order-1 text-lg font-semibold">
						WELCOME, {name} ({formattedIdnum})
					</h2>
					<div className="order-5 flex flex-col md:my-4 md:flex md:flex-row md:gap-4 md:order-2 gap-2">
						<input
							type="text"
							placeholder="Search Item, Amount, Date"
							className="md:w-96 p-2 border border-black rounded bg-white"
							value={search}
							onChange={(e) => setSearch(e.target.value)}
						/>
						<div className="flex justify-around md:gap-4">
							<input
								type="date"
								className="text-sm p-2 border rounded border border-black"
								value={startDate}
								onChange={(e) => setStartDate(e.target.value)}
							/>
							<input
								type="date"
								className="text-sm p-2 border rounded border border-black"
								value={endDate}
								onChange={(e) => setEndDate(e.target.value)}
							/>
						</div>
					</div>
					<div className="order-2 flex items-center justify-between w-full sm:w-auto sm:flex-row sm:gap-4">
						<h2 className="text-lg font-semibold">BALANCE: {balance}</h2>
						<button
							onClick={handleSavePDF}
							className="bg-blue-600 text-white px-4 py-2 rounded"
						>
							<FontAwesomeIcon icon={faSave} className="w-5 h-5" />
						</button>
					</div>
				</div>

				<div
					ref={tableRef}
					className="bg-white shadow-md rounded-lg overflow-hidden mt-2"
				>
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
										filteredTransactions.map((transaction, index) => {
											const [date] = transaction.time.split("T");
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
													<td className="p-1 border md:text-right md:pr-4 text-center">
														{transaction.amount}
													</td>
												</tr>
											);
										})
									) : (
										<tr>
											<td colSpan={3} className="p-4 text-center">
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
	);
};

export default Transactions;
