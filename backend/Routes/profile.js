import express from 'express' 
import User from '../Models/user.model.js'  
import jwt from 'jsonwebtoken' 

const router=express.Router() 

router.get('/',async (req,res)=>{
    const token=req.cookies.logintoken 
    if (!token){
        return res.status(401).json({message:"Unauthorized"})
    }
    const decoded = jwt.verify(token, process.env.SECRET_KEY);
    const userid=decoded.id
    const user=await User.findOne({_id:userid})
    res.status(200).json({user})
})


export default router