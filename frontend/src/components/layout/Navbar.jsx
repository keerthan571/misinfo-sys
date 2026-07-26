import { Bell, Search, UserCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Navbar() {

  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("token_type");
    navigate("/login");
  };

  return (
    <div className="h-20 bg-slate-900 border-b border-slate-700 flex items-center justify-between px-8">

      <div className="flex items-center bg-slate-800 rounded-lg px-4 py-2 w-96">

        <Search className="text-gray-400" size={20} />

        <input
          type="text"
          placeholder="Search News..."
          className="bg-transparent outline-none text-white ml-3 w-full"
        />

      </div>


      <div className="flex items-center gap-6">

        <Bell className="text-white cursor-pointer" />


        <div className="flex items-center gap-3 text-white">

          <UserCircle size={36} />

          <span>Mahesha</span>

          <button
            onClick={handleLogout}
            className="bg-red-600 px-3 py-2 rounded-lg text-sm"
          >
            Logout
          </button>

        </div>

      </div>

    </div>
  );
}