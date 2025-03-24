import express from "express";
import cors from "cors";
import jwt from "jsonwebtoken";
import dotenv from "dotenv";
import { createClient } from "@supabase/supabase-js";
import type { Request, Response, NextFunction } from "express";

dotenv.config();

const app = express();
const PORT = 5000;
const SECRET_KEY = process.env.JWT_SECRET || "supersecretkey";

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
	res.json("bobo");
});

const supabase = createClient(
	process.env.SUPABASE_URL!,
	process.env.SUPABASE_ANON_KEY!
);

interface AuthenticatedRequest extends Request {
	idnum?: string;
	isAdmin?: boolean;
}

const authenticateToken = (
	req: AuthenticatedRequest,
	res: Response,
	next: NextFunction
) => {
	const token = req.headers.authorization?.split(" ")[1];
	if (!token) return res.status(401).json({ message: "Unauthorized" });

	try {
		const decoded = jwt.verify(token, SECRET_KEY) as {
			idnum: string;
			isAdmin: boolean;
		};
		req.idnum = decoded.idnum;
		req.isAdmin = decoded.isAdmin;
		next();
	} catch (error) {
		return res.status(403).json({ message: "Invalid token" });
	}
};

app.get(
	"/transactions",
	authenticateToken,
	async (req: AuthenticatedRequest, res: Response) => {
		const { idnum } = req;
		if (!idnum) return res.status(400).json({ message: "Missing ID number" });

		try {
			const { data, error } = await supabase
				.from("transactions")
				.select("type, amount, time")
				.eq("student", idnum)
				.order("time", { ascending: true });

			if (error) return res.status(400).json({ message: error.message });

			res.status(200).json(data);
		} catch (error) {
			res.status(500).json({ message: "Error fetching transactions" });
		}
	}
);

app.post("/login", async (req, res) => {
	const { id, password } = req.body;

	try {
		const { data, error } = await supabase
			.from("students")
			.select("*")
			.eq("idnum", id)
			.single();

		if (error || !data) {
			return res.status(401).json({ message: "Invalid ID number" });
		}

		if (data.pin != password) {
			return res.status(401).json({ message: "Invalid password" });
		}

		/*const passwordMatch = await bcrypt.compare(password, data.password); // Assuming 'password' field is hashed

		if (!passwordMatch) {
			return res.status(401).json({ message: "Invalid password" });
		}*/

		var expiresIn = 300; // 5 mins

		const token = jwt.sign(
			{ idnum: data.idnum, balance: data.balance, isAdmin: data.isAdmin },
			SECRET_KEY,
			{
				expiresIn: "60s",
			}
		);
		res.json({
			user: {
				name: data.fname + " " + data.lname,
				idnum: data.idnum,
				balance: data.balance,
				isAdmin: data.isAdmin,
			},
			token,
			expiresIn,
		});
	} catch (error) {
		console.error(error);
		res.status(500).json({ message: "Login failed" });
	}
});

app.post("/reset", async (req, res) => {
	const { idnum } = req.body;
	if (!idnum) {
		return res
			.status(400)
			.json({ success: false, message: "All fields are required." });
	}

	try {
		const { data: student, error: studentError } = await supabase
			.from("students")
			.select("idcode")
			.eq("idnum", idnum)
			.single();

		if (studentError || !student) {
			return res
				.status(404)
				.json({ success: false, error: "Student not found." });
		}

		res.json({ success: true, message: "Reset Password Request Sent!" });
	} catch (err) {
		res.status(500).json({ success: false, message: "Internal Server Error." });
	}
});

app.post(
	"/changepin",
	authenticateToken,
	async (req: AuthenticatedRequest, res: Response) => {
		const { idnum } = req;
		const { oldPIN, newPIN }: { oldPIN: string; newPIN: string } = req.body;

		if (!idnum || !oldPIN || !newPIN) {
			return res.status(400).json({ message: "Missing required fields" });
		}

		try {
			const { data, error } = await supabase
				.from("students")
				.select("pin")
				.eq("idnum", idnum)
				.single();

			if (error || !data || String(data.pin) !== String(oldPIN)) {
				return res.status(400).json({ message: "Incorrect old PIN" });
			}

			const { data: updatedData, error: updateError } = await supabase
				.from("students")
				.update({ pin: newPIN })
				.eq("idnum", idnum)
				.select();

			if (updateError || !updatedData) {
				throw updateError;
			}

			res.json({ message: "PIN changed successfully", updatedData });
		} catch (err) {
			console.error("Error changing PIN:", err);
			res.status(500).json({ message: "Server error" });
		}
	}
);

// Route to add credits
app.post(
	"/addcredits",
	authenticateToken,
	async (req: AuthenticatedRequest, res: Response) => {
		const { credits, idnum }: { credits: number; idnum: string } = req.body;
		const { isAdmin } = req;

		if (!isAdmin) {
			return res.status(403).json({ message: "Unauthorized" });
		}

		if (!idnum || isNaN(credits)) {
			return res.status(400).json({ message: "Invalid ID or credits" });
		}

		try {
			const { data, error } = await supabase
				.from("students")
				.select("deferred, forwardBalance, balance")
				.eq("idnum", idnum)
				.single();

			if (error || !data) {
				return res.status(404).json({ message: "User not found" });
			}

			let { balance, forwardBalance: fbalance, deferred } = data;

			if (deferred) {
				fbalance -= credits;
				if (fbalance < 0) {
					deferred = false;
					balance = -fbalance;
					fbalance = 0;
				}
			} else {
				balance = parseInt(balance) + credits;
			}

			const { error: updateError } = await supabase
				.from("students")
				.update({ forwardBalance: fbalance, balance, deferred })
				.eq("idnum", idnum);

			if (updateError) {
				return res.status(500).json({ message: "Failed to update balance" });
			}

			res.json({ message: "Credits added successfully", deferred });
		} catch (error) {
			console.error("Error adding credits:", error);
			res.status(500).json({ message: "Server error" });
		}
	}
);

app.listen(PORT, () => {
	console.log(`Server running on http://localhost:${PORT}`);
});
