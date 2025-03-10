import express from "express";
import cors from "cors";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import dotenv from "dotenv";
import { createClient } from "@supabase/supabase-js";

dotenv.config();

const app = express();
const PORT = 5000;
const SECRET_KEY = process.env.JWT_SECRET || "supersecretkey";

app.use(cors());
app.use(express.json());

const supabase = createClient(
	process.env.SUPABASE_URL!,
	process.env.SUPABASE_ANON_KEY!
);

app.post("/signup", async (req, res) => {
	const { email, password } = req.body;

	try {
		console.log("ari");
		const { data, error } = await supabase.auth.signUp({ email, password });
		console.log(data);
		console.log(error);
		if (error) return res.status(400).json({ message: error.message });

		res
			.status(201)
			.json({ message: "User created successfully", user: data.user });
	} catch (error) {
		console.log("dre");
		res.status(500).json({ message: "Error creating user" });
	}
});

app.post("/login", async (req, res) => {
	const { id, password } = req.body;

	console.log(id);
	console.log(password);

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

		const token = jwt.sign({ idnum: data.idnum }, SECRET_KEY, {
			expiresIn: "1h",
		});

		res.json({ user: { idnum: data.idnum }, token });
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

app.listen(PORT, () => {
	console.log(`Server running on http://localhost:${PORT}`);
});
