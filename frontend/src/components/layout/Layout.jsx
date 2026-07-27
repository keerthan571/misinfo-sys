import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

export default function Layout({ children }) {
  return (
    <div className="flex">

      <Sidebar />

      <div className="flex-1 bg-slate-900 min-h-screen">

        <Navbar />

        <div className="p-8">
          {children}
        </div>

      </div>

    </div>
  );
}