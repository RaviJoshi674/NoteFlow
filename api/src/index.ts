import express from "express";
import cors from "cors";
import multer from "multer";
import dotenv from "dotenv";
import { createServer } from "http";
import { Server } from "socket.io";

import {
    pool,
    redis,
    createLectureAndJob
} from "./db";

dotenv.config();

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
    cors: { origin: "*" },
});

app.use(cors());
app.use(express.json());

/* ---------------- File Upload ---------------- */

const upload = multer({
    dest: "/uploads",
});

/* ---------------- Upload API ---------------- */

app.post(
    "/upload",
    upload.single("file"),
    async (req, res) => {
        try {
            if (!req.file || !req.body.title) {
                return res
                    .status(400)
                    .json({ error: "Missing title or file" });
            }

            const { lectureId, jobId } =
                await createLectureAndJob(
                    req.body.title,
                    req.file
                );

            await redis.lpush(
                "lecture_jobs",
                JSON.stringify({
                    jobId,
                    lectureId,
                })
            );

            res.status(201).json({
                lectureId,
                jobId,
            });
        } catch (err) {
            console.error(err);
            res.status(500).json({
                error: "Failed to upload lecture",
            });
        }
    }
);

/* ---------------- Job Status API ---------------- */

app.get("/jobs/:jobId", async (req, res) => {
    const { jobId } = req.params;

    const result = await pool.query(
        `
    SELECT status,
           current_stage,
           retry_count,
           max_retries,
           error_message
    FROM processing_jobs
    WHERE id = $1
    `,
        [jobId]
    );

    if (result.rowCount === 0) {
        return res
            .status(404)
            .json({ error: "Job not found" });
    }

    res.json(result.rows[0]);
});

/* ---------------- WebSocket (Optional) ---------------- */

io.on("connection", (socket) => {
    console.log("Client connected:", socket.id);
});

/* ---------------- Server Start ---------------- */

const PORT = process.env.PORT || 4000;

httpServer.listen(PORT, () => {
    console.log(`API server running on port ${PORT}`);
});
