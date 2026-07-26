import { NavLink } from "react-router-dom";

import {
  LayoutDashboard,
  Search,
  Network,
  TrendingUp,
  History,
  Settings,
} from "lucide-react";


const menuItems = [

  {
    title: "Dashboard",
    icon: <LayoutDashboard size={20} />,
    path: "/",
  },


  {
    title: "Analyze",
    icon: <Search size={20} />,
    path: "/analyze",
  },


  {
    title: "Graph Analytics",
    icon: <Network size={20} />,
    path: "/graph",
  },


  {
    title: "Prediction",
    icon: <TrendingUp size={20} />,
    path: "/prediction",
  },


  {
    title: "History",
    icon: <History size={20} />,
    path: "/history",
  },


  {
    title: "Settings",
    icon: <Settings size={20} />,
    path: "/settings",
  },

];



export default function Sidebar() {


  return (

    <div className="w-64 min-h-screen bg-slate-900 border-r border-slate-800">


      {/* Logo */}

      <div className="p-6 border-b border-slate-800">

        <h1 className="text-3xl font-bold text-blue-500">

          AI MISINFO

        </h1>


        <p className="text-gray-400 text-sm mt-2">

          Analysis Platform

        </p>


      </div>





      {/* Menu */}

      <div className="p-4 space-y-2">


        {
          menuItems.map((item) => (

            <NavLink

              key={item.title}

              to={item.path}

              end={item.path === "/"}

              className={({ isActive }) =>

                `flex items-center gap-4 p-4 rounded-xl transition-all ${
                  
                  isActive

                  ? "bg-blue-600 text-white"

                  : "text-gray-300 hover:bg-slate-800"

                }`

              }

            >

              {item.icon}

              <span>

                {item.title}

              </span>


            </NavLink>


          ))
        }


      </div>


    </div>

  );

}