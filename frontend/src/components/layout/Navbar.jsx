import { Bell, Search, UserCircle } from "lucide-react";

export default function Navbar() {
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

        <div className="flex items-center gap-2">

          <UserCircle size={36} />

          <span>Mahesha</span>

        </div>

      </div>

    </div>
  );
}