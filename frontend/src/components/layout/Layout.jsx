import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

export default function Layout({ children }) {
  return (
    <div className="flex">

      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 bg-slate-950 min-h-screen">

        {/* Top Navbar */}
        <Navbar />

        {/* Page Content */}
        <div className="p-8">
          {children}
        </div>

      </div>

    </div>
  );
}