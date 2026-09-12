// const express = require("express");
// const cors = require("cors");
// const fs = require("fs");
// const path = require("path");
// const haversine = require("haversine-distance");

// const app = express();
// app.use(cors());
// app.use(express.json());

// const SHIPS_FILE = "ships.txt";
// const DATA_FILE = "ais_data.json";


// app.use(express.static(path.join(__dirname, "public")));  // ✅ Serve static files

// app.get("/", (req, res) => {
//     res.sendFile(path.join(__dirname, "public", "index.html"));  // ✅ Serve index.html
// });

// // ✅ Route: Get Oil Tankers from ships.txt
// app.get("/ships", (req, res) => {
//     fs.readFile(SHIPS_FILE, "utf8", (err, data) => {
//         if (err) return res.status(500).json({ error: "Error reading file" });

//         const ships = data.trim().split("\n").map(line => {
//             const match = line.match(/ShipId: (\d+), Latitude: ([\d.-]+), Longitude: ([\d.-]+), SOG: ([\d.]+) knots, COG: ([\d.]+), Ship Type: (.+)/);
//             if (match) {
//                 return {
//                     shipId: match[1],
//                     latitude: parseFloat(match[2]),
//                     longitude: parseFloat(match[3]),
//                     sog: parseFloat(match[4]),
//                     cog: parseFloat(match[5]),
//                     type: match[6]
//                 };
//             }
//         }).filter(ship => ship);

//         res.json(ships);
//     });
// });

// // ✅ Load AIS Data from JSON
// const loadAISData = () => {
//     try {
//         const data = fs.readFileSync(DATA_FILE, "utf8");
//         return JSON.parse(data);
//     } catch (error) {
//         return [];
//     }
// };

// // ✅ Route: Get Stored AIS Data (Oil Spill)
// app.get("/api/data", (req, res) => {
//     res.json(loadAISData());
// });

// // ✅ Route: Find Nearest Vessels Using Haversine
// app.post("/api/nearest", (req, res) => {
//     const data = loadAISData();
//     const { latitude, longitude, k = 5 } = req.body;

//     if (!latitude || !longitude) return res.status(400).json({ error: "Latitude and Longitude are required" });
//     if (!data.length) return res.status(404).json({ error: "No AIS data available" });

//     const distances = data.map(vessel => ({
//         ShipId: vessel.ShipId,
//         Distance: haversine({ lat: latitude, lon: longitude }, { lat: vessel.Latitude, lon: vessel.Longitude }) / 1000
//     }));

//     distances.sort((a, b) => a.Distance - b.Distance);
//     res.json(distances.slice(0, k));
// });

// // ✅ Route: KNN Correlation
// app.post("/api/knn", (req, res) => {
//     const data = loadAISData();
//     const { k = 3 } = req.body;

//     if (data.length < k) return res.status(400).json({ error: "Not enough data for KNN" });

//     const coordinates = data.map(v => [v.Latitude, v.Longitude]);

//     const knn = require("ml-knn");
//     const knnModel = new knn(coordinates, coordinates);

//     const result = data.map((vessel, idx) => {
//         const distances = coordinates.map((coord, i) => ({
//             ShipId: data[i].ShipId,
//             Distance: haversine({ lat: vessel.Latitude, lon: vessel.Longitude }, { lat: coord[0], lon: coord[1] }) / 1000
//         }));
//         distances.sort((a, b) => a.Distance - b.Distance);
//         return {
//             ShipId: vessel.ShipId,
//             Nearest: distances.slice(1, k + 1)
//         };
//     });

//     res.json(result);
// });

// // ✅ Start Server
// const PORT = 3000;
// app.listen(PORT, () => {
//     console.log(`Server running at http://localhost:${PORT}`);
// });
//2nd modified code
const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");
const haversine = require("haversine-distance");

const app = express();
app.use(cors());
app.use(express.json());

const SHIPS_FILE = "ships.txt";
const DATA_FILE = "ais_data.json";

app.use(express.static(path.join(__dirname, "public")));

// ✅ Route: Serve index.html
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "public", "index.html"));
});

// ✅ Load AIS Data from JSON
const loadAISData = () => {
    try {
        const data = fs.readFileSync(DATA_FILE, "utf8");
        return JSON.parse(data);
    } catch (error) {
        return [];
    }
};

// ✅ Route: Get Live Tanker Data from ships.txt
app.get("/ships", (req, res) => {
    fs.readFile(SHIPS_FILE, "utf8", (err, data) => {
        if (err) return res.status(500).json({ error: "Error reading file" });

        const ships = data.trim().split("\n").map(line => {
            const match = line.match(/ShipId: (\d+), Latitude: ([\d.-]+), Longitude: ([\d.-]+), SOG: ([\d.]+) knots, COG: ([\d.]+) degrees, Ship Type: (.+)/);
            if (match) {
                return {
                    ShipId: match[1],
                    Latitude: parseFloat(match[2]),
                    Longitude: parseFloat(match[3]),
                    SOG: parseFloat(match[4]),
                    COG: parseFloat(match[5]),
                    Type: match[6]
                };
            }
        }).filter(Boolean);

        res.json(ships);
    });
});

// ✅ Route: Get Stored AIS Data (Oil Spill Vessels)
app.get("/api/data", (req, res) => {
    res.json(loadAISData());
});
// ✅ Function: Calculate Bearing Between Two Coordinates
function calculateBearing(lat1, lon1, lat2, lon2) {
    const toRadians = deg => deg * (Math.PI / 180);
    const toDegrees = rad => rad * (180 / Math.PI);

    const dLon = toRadians(lon2 - lon1);
    const y = Math.sin(dLon) * Math.cos(toRadians(lat2));
    const x = Math.cos(toRadians(lat1)) * Math.sin(toRadians(lat2)) -
              Math.sin(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.cos(dLon);

    const bearing = toDegrees(Math.atan2(y, x));
    return (bearing + 360) % 360; // Normalize to 0-360
}

// ✅ Function: Check If Ship Is Heading Toward Oil Spill
function isHeadingToward(spillLat, spillLon, shipLat, shipLon, cog) {
    const bearing = calculateBearing(shipLat, shipLon, spillLat, spillLon);
    const angleDifference = Math.abs(bearing - cog);
    return angleDifference <= 20 || Math.abs(angleDifference - 360) <= 20; // Within 20°
}

// ✅ Route: Find Ships Heading Toward the Oil Spill
app.post("/api/trajectory", (req, res) => {
    const { latitude, longitude } = req.body; // Oil spill location
    if (!latitude || !longitude) {
        return res.status(400).json({ error: "Latitude and Longitude are required" });
    }

    const ships = loadAISData();
    
    // Filter ships that are heading toward the oil spill
    const headingShips = ships.filter(ship => {
        const bearing = calculateBearing(latitude, longitude, ship.Latitude, ship.Longitude);
        const angleDifference = Math.abs(bearing - ship.COG);
        console.log(`ShipID: ${ship.ShipId}, Bearing: ${bearing}, COG: ${ship.COG}, Difference: ${angleDifference}`);
        return isHeadingToward(latitude, longitude, ship.Latitude, ship.Longitude, ship.COG);
    });

    // Send the filtered ships as a response
    res.json(headingShips);
});

// ✅ Route: Find Nearest Vessels Using Haversine Formula
app.post("/api/nearest", (req, res) => {
    const data = loadAISData();
    const { latitude, longitude, k = 5 } = req.body;

    if (!latitude || !longitude) return res.status(400).json({ error: "Latitude and Longitude are required" });
    if (!data.length) return res.status(404).json({ error: "No AIS data available" });

    const distances = data.map(vessel => ({
        ShipId: vessel.ShipId,
        Distance: haversine({ lat: latitude, lon: longitude }, { lat: vessel.Latitude, lon: vessel.Longitude }) / 1000
    }));

    distances.sort((a, b) => a.Distance - b.Distance);
    res.json(distances.slice(0, k));
});

// // ✅ Route: KNN Correlation
// app.post("/api/knn", (req, res) => {
//     const data = loadAISData();
//     const { k = 3 } = req.body;

//     if (data.length < k) return res.status(400).json({ error: "Not enough data for KNN" });

//     const coordinates = data.map(v => [v.Latitude, v.Longitude]);

//     const knn = require("ml-knn");
//     const knnModel = new knn(coordinates, coordinates);

//     const result = data.map((vessel, idx) => {
//         const distances = coordinates.map((coord, i) => ({
//             ShipId: data[i].ShipId,
//             Distance: haversine({ lat: vessel.Latitude, lon: vessel.Longitude }, { lat: coord[0], lon: coord[1] }) / 1000
//         }));
//         distances.sort((a, b) => a.Distance - b.Distance);
//         return {
//             ShipId: vessel.ShipId,
//             Nearest: distances.slice(1, k + 1)
//         };
//     });

//     res.json(result);
// });


// ✅ Start Server
const PORT = 3001;
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
// Updated server.js to use only ships.txt as input and fix trajectory functionality
