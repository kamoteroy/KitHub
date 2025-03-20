import React, { useState } from "react";

interface FilterProps {
	search: string;
	setSearch: (value: string) => void;
	priceRange: [number, number];
	setPriceRange: (value: [number, number]) => void;
	startDate: string;
	setStartDate: (value: string) => void;
	endDate: string;
	setEndDate: (value: string) => void;
}

const TransactionsFilter: React.FC<FilterProps> = ({
	search,
	setSearch,
	priceRange,
	setPriceRange,
	startDate,
	setStartDate,
	endDate,
	setEndDate,
}) => {
	const [isOpen, setIsOpen] = useState(false);

	return (
		<div>
			{/* Filter Button */}
			<button
				className="bg-red-600 text-white px-4 py-2 rounded"
				onClick={() => setIsOpen(true)}
			>
				Filter Transactions
			</button>

			{/* Popup Modal */}
			{isOpen && (
				<div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
					<div className="bg-white p-6 rounded shadow-lg w-96">
						<h2 className="text-lg font-semibold mb-4">Filter Transactions</h2>

						{/* Search Bar */}
						<input
							type="text"
							placeholder="Search Item, Amount, Date"
							className="w-full p-2 border rounded mb-3"
							value={search}
							onChange={(e) => setSearch(e.target.value)}
						/>

						{/* Price Range Slider */}
						<label className="block mb-1">
							Price Range: {priceRange[0]} - {priceRange[1]}
						</label>
						<input
							type="range"
							min="0"
							max="1000"
							value={priceRange[0]}
							onChange={(e) =>
								setPriceRange([Number(e.target.value), priceRange[1]])
							}
							className="w-full"
						/>
						<input
							type="range"
							min="0"
							max="1000"
							value={priceRange[1]}
							onChange={(e) =>
								setPriceRange([priceRange[0], Number(e.target.value)])
							}
							className="w-full mb-3"
						/>

						{/* Date Pickers */}
						<input
							type="date"
							className="w-full p-2 border rounded mb-3"
							value={startDate}
							onChange={(e) => setStartDate(e.target.value)}
						/>
						<input
							type="date"
							className="w-full p-2 border rounded mb-3"
							value={endDate}
							onChange={(e) => setEndDate(e.target.value)}
						/>

						{/* Buttons */}
						<div className="flex justify-between">
							<button
								className="bg-gray-400 px-4 py-2 rounded"
								onClick={() => setIsOpen(false)}
							>
								Cancel
							</button>
							<button
								className="bg-blue-600 text-white px-4 py-2 rounded"
								onClick={() => setIsOpen(false)}
							>
								Apply
							</button>
						</div>
					</div>
				</div>
			)}
		</div>
	);
};

export default TransactionsFilter;
