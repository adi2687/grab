import express from express 
const router=express.Router()
router.post("/login", async (req, res) => {
    const { email, password } = req.body;
    const user=await user.findOne({email}) 

});
module.exports=router
