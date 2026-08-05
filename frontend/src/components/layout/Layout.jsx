import { useState } from "react";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

export default function Layout({ children }) {

    const [collapsed, setCollapsed] = useState(false);

    return (

        <div className="flex overflow-x-hidden">

            <Sidebar
                collapsed={collapsed}
                setCollapsed={setCollapsed}
            />

            <div
                className="
                    flex-1
                    bg-slate-900
                    min-h-screen
                    transition-all
                    duration-300
                "
            >

                <Navbar />

                <div className="px-4 py-6 md:px-6 lg:px-8 xl:px-10">
                  <div className="mx-auto max-w-[1700px]">
                      {children}
                  </div>
              </div>

            </div>

        </div>

    );

}