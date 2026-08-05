import { NavLink } from "react-router-dom";
import {
    LayoutDashboard,
    Search,
    Network,
    TrendingUp,
    History,
    ShieldCheck,
    Menu,
    ChevronLeft,
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

export default function Sidebar({ collapsed, setCollapsed }) {
    return (
        <aside
            className={`
                ${collapsed ? "w-24" : "w-72md:w-64"}
                min-h-screen
                bg-slate-950
                border-r
                border-slate-800
                flex
                flex-col
                transition-all
                duration-300
            `}
        >
            <div className="flex justify-end p-4">
                <button
                    onClick={() => setCollapsed(!collapsed)}
                    className="text-slate-300 hover:text-white transition"
                >
                    {collapsed ? (
                        <Menu size={22} />
                    ) : (
                        <ChevronLeft size={22} />
                    )}
                </button>
            </div>

            <div className="px-6 pb-6 border-b border-slate-800">
                <div
                    className={`flex items-center ${
                        collapsed ? "justify-center" : "gap-3"
                    }`}
                >
                    <div className="w-12 h-12 rounded-2xl bg-blue-600 flex items-center justify-center shadow-lg">
                        <ShieldCheck size={28} className="text-white" />
                    </div>

                    {!collapsed && (
                        <div>
                            <h1 className="text-xl font-bold text-white tracking-wide">
                                AI MISINFO
                            </h1>

                            <p className="text-slate-400 text-sm">
                                Analysis Platform
                            </p>
                        </div>
                    )}
                </div>
            </div>

            <nav className="flex-1 p-5 space-y-2">
                {menuItems.map((item) => (
                    <NavLink
                        key={item.title}
                        to={item.path}
                        end={item.path === "/"}
                        title={collapsed ? item.title : ""}
                        className={({ isActive }) =>
                            `
                            flex
                            items-center
                            ${
                                collapsed
                                    ? "justify-center"
                                    : "gap-4 px-4"
                            }
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

                        {!collapsed && (
                            <span>{item.title}</span>
                        )}
                    </NavLink>
                ))}
            </nav>

            <div className="p-5 border-t border-slate-800">
                <div
                    className={`bg-slate-900 rounded-2xl p-4 ${
                        collapsed ? "flex justify-center" : ""
                    }`}
                >
                    {collapsed ? (
                        <ShieldCheck size={24} className="text-blue-400" />
                    ) : (
                        <div>
                            <p className="text-sm font-semibold text-white">
                                AI Misinformation
                            </p>

                            <p className="text-xs text-slate-400 mt-1">
                                Version 2.0
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </aside>
    );
}