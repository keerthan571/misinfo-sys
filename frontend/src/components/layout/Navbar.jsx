import { UserCircle, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useUser } from "../../context/UserContext";

export default function Navbar({ collapsed }) {
  const navigate = useNavigate();
  const { user } = useUser();

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("token_type");
    localStorage.removeItem("email");

    navigate("/login");
  };

  return (
    <header className="flex items-center justify-end h-20 px-8 border-b border-slate-800 bg-slate-900">
      <div className="flex items-center gap-4">

        <div className="flex items-center gap-3 bg-slate-800 border border-slate-700 rounded-2xl px-3 py-2">
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