import { Pool } from "pg";
import Redis from "ioredis";

/* ---------------- PostgreSQL ---------------- */

export const pool = new Pool({
    host: process.env.POSTGRES_HOST,
    port: Number(process.env.POSTGRES_PORT),
    user: process.env.POSTGRES_USER,
    password: process.env.POSTGRES_PASSWORD,
    database: process.env.POSTGRES_DB,
});

/* ---------------- Redis ---------------- */

export const redis = new Redis({
    host: process.env.REDIS_HOST,
    port: Number(process.env.REDIS_PORT),
});

/* ---------------- Lecture + Job ---------------- */

export const createLectureAndJob = async (
    title: string,
    file: Express.Multer.File
) => {
    const client = await pool.connect();

    try {
        await client.query("BEGIN");

        const lectureResult = await client.query(
            `
      INSERT INTO lectures
      (title, original_filename, file_path, mime_type, file_size_bytes)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING id
      `,
            [
                title,
                file.originalname,
                file.path,
                file.mimetype,
                file.size,
            ]
        );

        const lectureId = lectureResult.rows[0].id;

        const jobResult = await client.query(
            `
      INSERT INTO processing_jobs (lecture_id)
      VALUES ($1)
      RETURNING id
      `,
            [lectureId]
        );

        await client.query("COMMIT");

        return {
            lectureId,
            jobId: jobResult.rows[0].id,
        };
    } catch (err) {
        await client.query("ROLLBACK");
        throw err;
    } finally {
        client.release();
    }
};

/* ---------------- Job Updates ---------------- */

export const updateJobStatus = async (
    jobId: string,
    status: string,
    errorMessage: string | null = null
) => {
    await pool.query(
        `
    UPDATE processing_jobs
    SET status = $1,
        error_message = $2
    WHERE id = $3
    `,
        [status, errorMessage, jobId]
    );
};

export const updateJobStage = async (
    jobId: string,
    stage: string
) => {
    await pool.query(
        `
    UPDATE processing_jobs
    SET current_stage = $1
    WHERE id = $2
    `,
        [stage, jobId]
    );
};
