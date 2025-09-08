import express from 'express'
const router = express.Router()
import User from '../Models/user.model.js'
import grabids from '../Models/grabids.model.js'
import jwt from 'jsonwebtoken'

router.post('/', async (req, res) => {
    try {
        const { username, email, password, role, age, gender, country, city, grabid } = req.body;

        console.log(username, email, password, role, age, gender, country, city, grabid);

        if (grabid) {
            const response = await grabids.findOne({ GrabID: grabid });
            console.log(response);
            if (!response) {
                return res.json({ message: "Grabid not found" });
            }
        }

        let ans = 0;
        if (grabid) {
            // --- initial boost logic (same as your code) ---
            const grabiddetails = await grabids.findOne({ GrabID: grabid });
            const findthreemoregrabs = await grabids.find({ GrabID: { $gt: grabid } }).sort({ GrabID: 1 }).limit(3);
            const threemoredata = findthreemoregrabs.map((i) => i.GrabID);

            const firstdata = await grabids.findOne({ GrabID: threemoredata[0] });
            const seconddata = await grabids.findOne({ GrabID: threemoredata[1] });
            const thirddata = await grabids.findOne({ GrabID: threemoredata[2] });

            const company_preferences = {
                "SocialEngagement": 0.2,
                "FinancialEngagement": 1.0,
                "GigWorkerEngagement": 0.5,
                "JobEngagement": 0.7
            };
            const maxinitalboost = 20;

            let sum = 0;
            for (let i of Object.values(company_preferences)) sum += i;

            const normalizedweights = Object.values(company_preferences).map(i => Math.round((i / sum) * 10000) / 10000);

            function calculateWeightedBoost(data) {
                if (!data) return null;
                const engagementValues = [
                    data.SocialEngagement,
                    data.FinancialEngagement,
                    data.GigWorkerEngagement,
                    data.JobEngagement
                ];
                let weightedsum = 0;
                for (let i = 0; i < engagementValues.length; i++) {
                    weightedsum += engagementValues[i] * normalizedweights[i];
                }
                return (weightedsum / 100) * maxinitalboost;
            }

            const initialBoosts = [
                calculateWeightedBoost(grabiddetails),
                calculateWeightedBoost(firstdata),
                calculateWeightedBoost(seconddata),
                calculateWeightedBoost(thirddata)
            ].filter(boost => boost !== null);

            if (initialBoosts.length > 0) {
                const mean = initialBoosts.reduce((a, b) => a + b, 0) / initialBoosts.length;
                const errfactor = initialBoosts.map(boost => Math.abs(boost - mean));
                const maxerr = Math.max(...errfactor);

                let initialBoostNormalized = 0;
                if (maxerr > 0) {
                    initialBoostNormalized = ((initialBoosts[0] - Math.min(...initialBoosts)) / (Math.max(...initialBoosts) - Math.min(...initialBoosts))) * maxinitalboost;
                } else {
                    initialBoostNormalized = initialBoosts[0];
                }

                ans = initialBoostNormalized;
                console.log("Calculated Boost:", ans);
            } else {
                console.log("No data found to calculate the boost.");
            }
        }

        console.log('valid id');

        const user = new User({
            username,
            email,
            password,
            role,              // ✅ take role from body
            age,
            gender,
            country,
            city,
            grabId: grabid,    // ✅ matches schema
            mlScores: { initialBoost: ans } // ✅ save inside mlScores
        });

        const token = jwt.sign({ id: user._id }, process.env.SECRET_KEY);

        await user.save();

        res.cookie('logintoken', token, {
            httpOnly: true,
            secure: false,
            sameSite: 'lax',
            maxAge: 120 * 60 * 60 * 1000
        });

        res.status(200).json({ token, message: "User registered successfully" });
    } catch (err) {
        console.error("Error in /register:", err);
        res.status(500).json({ message: "Server error", error: err.message });
    }
});

export default router;
