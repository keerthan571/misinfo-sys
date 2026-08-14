import { useState } from "react";
import { Mail, ShieldCheck, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import apiClient from "../api/apiClient";

export default function ForgotPassword() {
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        setMessage("");
        setError("");

        if (!email) {
            setError("Please enter your email address.");
            return;
        }

        setLoading(true);

        try {
            const response = await apiClient.post(
                "/api/auth/forgot-password",
                {
                    email: email.trim(),
                }
            );

            setMessage(
                response.data?.message ||
                "If an account exists with this email, a password reset link has been sent."
            );

            setEmail("");
        } catch (error) {
            console.error(
                "FORGOT PASSWORD ERROR:",
                error
            );

            setError(
                error.response?.data?.detail ||
                "Unable to process your request. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#020617] flex items-center justify-center px-4 relative overflow-hidden">

            {/* Background glow */}
            <div className="absolute inset-0 pointer-events-none">

                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[650px] bg-blue-600/10 rounded-full blur-[140px]" />

                <div className="absolute top-0 right-0 w-[350px] h-[350px] bg-blue-500/5 rounded-full blur-[120px]" />

            </div>

            {/* Main Card */}
            <div className="relative w-full max-w-[430px] bg-[#0f172a]/95 border border-slate-700/40 rounded-[24px] shadow-[0_25px_70px_rgba(0,0,0,0.5)] px-10 py-10 backdrop-blur-xl">

                {/* Branding */}
                <div className="text-center">

                    <div className="flex justify-center mb-4">

                        <div className="w-12 h-12 rounded-xl bg-blue-600/15 border border-blue-500/20 flex items-center justify-center">

                            <ShieldCheck
                                className="text-blue-400"
                                size={27}
                            />

                        </div>

                    </div>

                    <h1 className="text-4xl font-bold tracking-tight text-blue-500">
                        AI MISINFO
                    </h1>

                    <p className="text-slate-400 mt-2 text-sm">
                        AI-Powered Misinformation Intelligence
                    </p>

                </div>

                {/* Heading */}
                <div className="mt-9">

                    <h2 className="text-white text-2xl font-bold">
                        Reset your password
                    </h2>

                    <p className="text-slate-400 text-sm mt-2">
                        Enter your registered email address to receive
                        instructions to reset your password.
                    </p>

                    <div className="mt-5 border-t border-slate-700/50" />

                </div>

                {/* Form */}
                <form
                    onSubmit={handleSubmit}
                    className="mt-7 space-y-5"
                >

                    {/* Email */}
                    <div>

                        <label className="text-slate-300 text-sm font-medium">
                            Email
                        </label>

                        <div className="flex items-center bg-[#1e293b] border border-slate-700/60 rounded-xl mt-2 px-4 transition-all duration-200 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10">

                            <Mail
                                className="text-slate-400 shrink-0"
                                size={20}
                            />

                            <input
                                type="email"
                                value={email}
                                onChange={(e) =>
                                    setEmail(e.target.value)
                                }
                                className="bg-transparent outline-none w-full py-4 px-3 text-white placeholder:text-slate-500"
                                placeholder="Enter your email"
                                autoComplete="email"
                            />

                        </div>

                    </div>

                    {/* Success message */}
                    {message && (
                        <div className="rounded-xl border border-green-500/20 bg-green-500/10 px-4 py-3 text-sm text-green-400">
                            {message}
                        </div>
                    )}

                    {/* Error message */}
                    {error && (
                        <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                            {error}
                        </div>
                    )}

                    {/* Submit */}
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white rounded-xl py-4 font-semibold text-base transition-all duration-200 shadow-lg shadow-blue-600/15 hover:shadow-blue-500/25 hover:-translate-y-[1px] disabled:opacity-60 disabled:hover:translate-y-0 disabled:cursor-not-allowed"
                    >
                        {loading
                            ? "Sending..."
                            : "Send Reset Link"}
                    </button>

                </form>

                {/* Back to login */}
                <div className="mt-7 pt-6 border-t border-slate-700/40 text-center">

                    <Link
                        to="/login"
                        className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 font-medium text-sm transition-colors"
                    >

                        <ArrowLeft size={16} />

                        Back to Login

                    </Link>

                </div>

            </div>

        </div>
    );
}