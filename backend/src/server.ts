// server.ts

import express from 'express';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware configurations
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});