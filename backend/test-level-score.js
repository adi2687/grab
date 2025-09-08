import mongoose from 'mongoose';
import dotenv from 'dotenv';
import User from './Models/user.model.js';
import fetch from 'node-fetch';

dotenv.config();

// ---------------- MongoDB Connection ----------------
const connectDB = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URI, {
            useNewUrlParser: true,
            useUnifiedTopology: true,
        });
        console.log('MongoDB connected');
    } catch (error) {
        console.error('MongoDB connection error:', error);
        process.exit(1);
    }
};

// ---------------- List Users ----------------
async function listUsers() {
    try {
        const users = await User.find({}, 'email username role');
        // console.log('Available users:');
        // console.log(users);
        return users;
    } catch (error) {
        console.error('Error listing users:', error);
        return [];
    }
}

// ---------------- Test Level Score ----------------
const testLevelScore = async () => {
    try {
        await connectDB();
        
        // List available users
        const users = await listUsers();
        if (users.length === 0) {
            throw new Error('No users in database');
        }
        
        const testUser = users[0]; // pick first user
        console.log('Testing level score for user:', testUser.username);

        const currentDate = new Date();

        // ---------------- Prepare test payload ----------------
        const testData = {
            user_id: testUser._id.toString(),
            role: testUser.role || 'merchant',  // fallback
            features: {
                // Merchant default features
                login_rate: 0.9,
                streak_days: 30,
                sales_30d: 120,
                order_fulfillment_rate: 0.95,
                return_rate: 0.05,
                rating: 4.7,
                avg_order_value: 250.75,
                peak_hour_sales: 45,
                complaints_received: 2,
                new_customers_acquired: 25,
                repeat_customer_rate: 0.65,
                total_hours_operated: 300,
                first_time_account: false,

                // Spam detection features
                review_count: 50,
                rating_variance: 0.1,
                avg_review_length: 120,
                logins_per_day: 1.2,
                std_login_time: 0.3,
                account_age_days: 400,

                // --- Added to avoid KeyError ---
                active: 1
            },
            activity_log: [
                { event: 'login', timestamp: currentDate.toISOString(),active:true }
            ],
            history_scores: [78, 82, 80]  // previous months
        };

        // console.log('Sending test data:', JSON.stringify(testData, null, 2));

        // ---------------- Call FastAPI ML service ----------------
        const response = await fetch('http://localhost:5000/calculate-score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(testData)
        });
        // console.log('Response is here homie ', response);
        if (!response.ok) {
            const errorText = await response.text();
            console.error('ML Service Error:', {
                status: response.status,
                statusText: response.statusText,
                error: errorText
            });
            throw new Error(`ML Service request failed: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();

        if (result.status === 'success') {
            console.log('✅ Level score calculated successfully:');
            console.log('User ID:', result.user_id);
            console.log('Final Score:', result.final_score);
            console.log('Credit Score:', result.credit_score);
            console.log('Spam Score:', result.spam_score);
            console.log('Tier:', result.tier);
            console.log('Reason Log:', result.reason_log);
            console.log('Penalty:', result.penalty);
            console.log('Consistency Bonus:', result.consistency_bonus);
            console.log('Boost Applied:', result.boost);
        } else {
            console.error('❌ Failed to calculate level score:', result.message);
        }

    } catch (error) {
        console.error('Error in test:', error);
    } finally {
        process.exit(0);
    }
};

testLevelScore();
