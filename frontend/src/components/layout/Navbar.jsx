import {
  Bell,
  Search,
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
        navigate("/login");
      }
    };

    fetchUser();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("email");
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-40 h-24 bg-slate-900 border-b border-slate-800 px-10 flex items-center justify-between">

      {/* Search */}
      <div className="relative w-[460px]">

        <Search
          size={20}
          className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400"
        />

        <input
          type="text"
          placeholder="Search analyses..."
          className="w-full h-14 rounded-2xl bg-slate-800 border border-slate-700 pl-14 pr-20 text-white placeholder:text-slate-500 outline-none focus:border-blue-500 transition"
        />

        <div className="absolute right-4 top-1/2 -translate-y-1/2 bg-slate-700 text-slate-300 text-xs px-2 py-1 rounded-md">
          Ctrl K
        </div>

      </div>

      {/* Right Side */}
      <div className="flex items-center gap-7">

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