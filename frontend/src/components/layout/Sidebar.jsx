import { NavLink } from "react-router-dom";

import {
  LayoutDashboard,
  Search,
  Network,
  TrendingUp,
  History,
  ShieldCheck,
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

];



export default function Sidebar() {


  return (

    <aside className="
      w-72
      min-h-screen
      bg-slate-950
      border-r
      border-slate-800
      flex
      flex-col
    ">


      {/* Logo */}

      <div className="
        px-7
        py-8
        border-b
        border-slate-800
      ">


        <div className="flex items-center gap-3">


          <div className="
            w-12
            h-12
            rounded-2xl
            bg-blue-600
            flex
            items-center
            justify-center
            shadow-lg
          ">

            <ShieldCheck
              size={28}
              className="text-white"
            />

          </div>



          <div>

            <h1 className="
              text-xl
              font-bold
              text-white
              tracking-wide
            ">

              AI MISINFO

            </h1>


            <p className="
              text-slate-400
              text-sm
            ">

              Analysis Platform

            </p>


          </div>


        </div>


      </div>





      {/* Navigation */}

      <nav className="
        flex-1
        p-5
        space-y-2
      ">


        {menuItems.map((item) => (

          <NavLink

            key={item.title}

            to={item.path}

            end={item.path === "/"}

            className={({ isActive }) =>

              `
              flex
              items-center
              gap-4
              px-4
              py-3.5
              rounded-2xl
              font-medium
              transition-all
              duration-300

              ${
                isActive
                  ? "bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }
              `

            }

          >

            {item.icon}

            <span>
              {item.title}
            </span>


          </NavLink>

        ))}


      </nav>





      {/* Footer */}

      <div className="
        p-5
        border-t
        border-slate-800
      ">


        <div className="
          bg-slate-900
          rounded-2xl
          p-4
        ">


          <p className="
            text-sm
            font-semibold
            text-white
          ">

            AI Misinformation

          </p>


          <p className="
            text-xs
            text-slate-400
            mt-1
          ">

            Version 2.0

          </p>


        </div>


      </div>



    </aside>

  );

}