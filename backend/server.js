const express = require("express"); 
const app = express();
import connect from './connections/connection.js'
import dotenv from 'dotenv'
dotenv.config()
connect(process.env.MONGO_URI)
const PORT = process.env.PORT || 3000;

app.get("/", (req, res) => {
    res.send("Hello World!");
});
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
