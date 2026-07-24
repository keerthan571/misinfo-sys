import { useState } from "react";
import { Mail, Lock, Eye, EyeOff } from "lucide-react";
import { Link } from "react-router-dom";

export default function Login() {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [remember, setRemember] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();

        if (!email || !password) {
            alert("Please enter email and password.");
            return;
        }

        setLoading(true);

        // Simulate API call
        setTimeout(() => {
            console.log({
                email,
                password,
                remember,
            });

            setLoading(false);
        }, 1500);
    };

    return (

        <div className="min-h-screen bg-slate-950 flex justify-center items-center">

            <div className="bg-slate-900 w-[430px] rounded-3xl shadow-2xl p-10">

                <h1 className="text-4xl font-bold text-center text-blue-500">
                    AI MISINFO
                </h1>

                <p className="text-center text-gray-400 mt-3">
                    Intelligence Platform
                </p>

                <h2 className="text-white text-2xl font-bold mt-10">
                    Welcome Back 👋
                </h2>

                <form
                    onSubmit={handleLogin}
                    className="mt-8 space-y-6"
                >

                    <div>

                        <label className="text-gray-300">
                            Email
                        </label>

                        <div className="flex items-center bg-slate-800 rounded-xl mt-2 px-4">

                            <Mail className="text-gray-400" />

                            <input
                                type="email"
                                value={email}
                                onChange={(e)=>setEmail(e.target.value)}
                                className="bg-transparent outline-none w-full p-4 text-white"
                                placeholder="Enter Email"
                            />

                        </div>

                    </div>

                    <div>

                        <label className="text-gray-300">
                            Password
                        </label>

                        <div className="flex items-center bg-slate-800 rounded-xl mt-2 px-4">

                            <Lock className="text-gray-400" />

                            <input
                                type={showPassword ? "text" : "password"}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="bg-transparent outline-none w-full p-4 text-white"
                                placeholder="Enter Password"
                            />

                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="text-gray-400 hover:text-white"
                            >
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>

                        </div>

                    </div>
                        <div className="flex items-center justify-between">

                        <label className="flex items-center gap-2 text-gray-300 cursor-pointer">

                            <input
                                type="checkbox"
                                checked={remember}
                                onChange={() => setRemember(!remember)}
                            />

                            Remember Me

                        </label>

                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-700 rounded-xl py-4 font-bold text-lg transition disabled:opacity-60"
                    >
                        {loading ? "Logging In..." : "Login"}
                    </button>

                </form>

                <div className="mt-8 text-center">

                <Link
                    to="/forgot-password"
                    className="text-blue-400 hover:underline"
                >
                    Forgot Password?
                </Link>

                    <p className="text-gray-400 mt-5">

                        Don't have an account?

                    </p>

                    <Link
                        to="/signup"
                        className="text-blue-400 hover:underline mt-2 inline-block"
                    >
                        Create Account
                    </Link>

                </div>

            </div>

        </div>

    );

}