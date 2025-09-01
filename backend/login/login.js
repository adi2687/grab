import express from express 
const router=express.Router()
import User from '../models/user'
import jwt from 'jsonwebtoken'
router.post("/login", async (req, res) => {
    const { email, password } = req.body;
    const user=await user.findOne({email}) 
    if (!user){
        res.status(404).json({message:
            "User not found"
            
        })
        return
    }
    const passwordfromdb=user.db 
    if (passwordfromdb !== password){
        res.status(401).json({message:
            "Invalid password"
            
        })
        return
    }
    const secretkey=process.env.SECRET_KEY
    const token=jwt.sign({email},secretkey)
    res.cookie('logintoken',token,{
            httpOnly:true,
            secure:true,
            sameSite:'strict',
            maxAge:120*60*60*1000
        })
    res.status(200).json({message:"token found " , token:token})
    
});
module.exports=router
