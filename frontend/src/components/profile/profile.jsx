import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import './Profile.css'
const Profile = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const apiurl = import.meta.env.VITE_BACKEND_URL || "http://localhost:3000";

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch(`${apiurl}/profile`, {
          method: "GET",
          headers:{
            "Content-Type":"application/json"
          },
          credentials: "include", // ✅ send cookies
        });

        const data = await response.json();
        if (response.ok) {
          setUser(data.user);
          localStorage.setItem("user", JSON.stringify(data.user));
        } else {
          alert(data.message || "Failed to load profile");
          navigate("/login");
        }
      } catch (err) {
        console.error(err);
        alert("Error fetching profile");
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    // If cached user exists, use it first
    const cachedUser = localStorage.getItem("user");
    if (cachedUser) {
      setUser(JSON.parse(cachedUser));
      setLoading(false);
    }

    fetchProfile();
  }, [navigate, apiurl]);

  const handleLogout = async () => {
    try {
      await fetch(`${apiurl}/logout`, {
        method: "POST",
        credentials: "include",
      });

      localStorage.removeItem("logintoken");
      localStorage.removeItem("user") // clear cache
      navigate("/login");
    } catch {
      alert("Logout failed, try again.");
    }
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div className="profile-container">
      <div className="profile-card">
        <h2>Profile</h2>
        {user ? (
          <>
            <p><strong>Username:</strong> {user.username}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>Genre:</strong> {user.role}</p>
            <p><strong>Age:</strong> {user.age}</p>
            <p><strong>Gender:</strong> {user.gender}</p>
            <p><strong>Country:</strong> {user.country}</p>
            <p><strong>City:</strong> {user.city}</p>
            <button onClick={handleLogout}>Logout</button>

            <div onClick={()=>navigate("/cibil")}>
              Calculate cibil score 
            </div>
          </>
        ) : (
          <p>No user data</p>
        )}
        
      </div>
    </div>
  );
};

export default Profile;
