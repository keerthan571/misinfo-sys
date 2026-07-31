import {
  Bell,
  UserCircle,
  LogOut,
} from "lucide-react";

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import apiClient from "../../api/apiClient";

export default function Navbar() {
  const [user, setUser] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await apiClient.get("/api/auth/me");
        setUser(response.data);
      } catch (error) {
        console.error(error);

        localStorage.removeItem("token");
        localStorage.removeItem("token_type");
        localStorage.removeItem("email");

        navigate("/login");
      }
    };

    fetchUser();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("token_type");
    localStorage.removeItem("email");

    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-40 h-24 bg-slate-900 border-b border-slate-800 px-10 flex items-center justify-between">

      {/* Left Side (Blank) */}
      <div className="flex-1"></div>

      {/* Right Side */}
      <div className="flex items-center gap-6">

        {/* Notification */}
        <button className="relative w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center hover:bg-slate-700 transition">
          <Bell size={20} className="text-slate-300" />
          <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-red-500"></span>
        </button>

        {/* User */}
        <div className="flex items-center gap-3 bg-slate-800 border border-slate-700 rounded-2xl px-4 py-2">
          <UserCircle
            size={42}
            className="text-blue-400"
          />

          <div>
            <p className="text-xs text-slate-400">
              Logged in as
            </p>

            <p className="text-white font-semibold">
              {user?.name || "User"}
            </p>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 h-12 px-5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-medium transition"
        >
          <LogOut size={18} />
          Logout
        </button>

      </div>

    </header>
  );
}