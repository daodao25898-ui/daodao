import express from 'express';
import helmet from 'helmet';
import morgan from 'morgan';
import bodyParser from 'body-parser';

const app = express();

// Middleware configurations
app.use(helmet()); // Security headers
app.use(morgan('dev')); // Logging
app.use(bodyParser.json()); // JSON body parser
app.use(bodyParser.urlencoded({ extended: true })); // URL-encoded body parser

app.get('/', (req, res) => {
    res.send('Hello World!');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
