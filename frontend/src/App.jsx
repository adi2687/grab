import React, { useEffect, useState } from 'react';
import Landing from './components/Landing/Landing';
import CardNav from './components/Navbar/CardNav';
const App=()=>{
  return(
    <div>
      <Landing/>
      <CardNav/>
    </div>
  )
}

export default App;