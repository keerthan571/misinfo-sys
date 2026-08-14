import { useState } from "react";
import { Lock, Eye, EyeOff, ShieldCheck, CheckCircle, AlertCircle } from "lucide-react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import apiClient from "../api/apiClient";

export default function ResetPassword() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    const token = searchParams.get("token");

    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState("");

    const handleReset = async (e) => {
        e.preventDefault();

        setError("");

        if (!token) {
            setError("Invalid password reset link.");
            return;
        }

        if (!password || !confirmPassword) {
            setError("Please enter both password fields.");
            return;
        }

        if (password.length < 6) {
            setError("Password must be at least 6 characters long.");
            return;
        }

        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        setLoading(true);

        try {
            await apiClient.post(
                "/api/auth/reset-password",
                {
                    token,
                    new_password: password,
                }
            );

            setSuccess(true);

        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Unable to reset your password. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="min-h-screen bg-[#020617] flex items-center justify-center px-4 relative overflow-hidden">

                <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[650px] bg-blue-600/10 rounded-full blur-[140px]" />
                    <div className="absolute top-0 right-0 w-[350px] h-[350px] bg-blue-500/5 rounded-full blur-[120px]" />
                </div>

                <div className="relative w-full max-w-[540px] bg-[#0f172a]/95 border border-slate-700/40 rounded-[24px] shadow-[0_25px_70px_rgba(0,0,0,0.5)] px-10 py-12 backdrop-blur-xl">

                    <div className="text-center">

                        <div className="flex justify-center mb-6">
                            <div className="w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center">
                                <CheckCircle
                                    className="text-green-400"
                                    size={34}
                                />
                            </div>
                        </div>

                        <h1 className="text-3xl font-bold text-white">
                            Password Reset Successful
                        </h1>

                        <p className="text-slate-400 mt-3 leading-relaxed">
                            Your password has been updated successfully.
                            You can now sign in using your new password.
                        </p>

                        <button
                            onClick={() => navigate("/login")}
                            className="w-full mt-8 bg-blue-600 hover:bg-blue-500 text-white rounded-xl py-4 font-semibold transition-all duration-200 shadow-lg shadow-blue-600/15 hover:-translate-y-[1px]"
                        >
                            Back to Login
                        </button>

                    </div>

                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#020617] flex items-center justify-center px-4 relative overflow-hidden">

            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[650px] bg-blue-600/10 rounded-full blur-[140px]" />
                <div className="absolute top-0 right-0 w-[350px] h-[350px] bg-blue-500/5 rounded-full blur-[120px]" />
            </div>

            <div className="relative w-full max-w-[540px] bg-[#0f172a]/95 border border-slate-700/40 rounded-[24px] shadow-[0_25px_70px_rgba(0,0,0,0.5)] px-10 py-10 backdrop-blur-xl">

                {/* BRAND */}

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

                {/* HEADER */}

                <div className="mt-9">

                    <h2 className="text-white text-2xl font-bold">
                        Create a new password
                    </h2>

                    <p className="text-slate-400 text-sm mt-2 leading-relaxed">
                        Enter a new password for your AI MISINFO account.
                    </p>

                    <div className="mt-5 border-t border-slate-700/50" />

                </div>

                {/* ERROR */}

                {error && (
                    <div className="mt-6 flex items-start gap-3 bg-red-500/10 border border-red-500/25 rounded-xl px-4 py-3">

                        <AlertCircle
                            size={20}
                            className="text-red-400 shrink-0 mt-0.5"
                        />

                        <p className="text-red-400 text-sm">
                            {error}
                        </p>

                    </div>
                )}

                {/* FORM */}

                <form
                    onSubmit={handleReset}
                    className="mt-7 space-y-5"
                >

                    {/* PASSWORD */}

                    <div>

                        <label className="text-slate-300 text-sm font-medium">
                            New Password
                        </label>

                        <div className="flex items-center bg-[#1e293b] border border-slate-700/60 rounded-xl mt-2 px-4 transition-all duration-200 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10">

                            <Lock
                                className="text-slate-400 shrink-0"
                                size={20}
                            />

                            <input
                                type={showPassword ? "text" : "password"}
                                value={password}
                                onChange={(e) =>
                                    setPassword(e.target.value)
                                }
                                className="bg-transparent outline-none flex-1 min-w-0 py-4 px-3 text-white placeholder:text-slate-500"
                                placeholder="Enter your new password"
                                autoComplete="new-password"
                            />

                            <button
                                type="button"
                                onClick={() =>
                                    setShowPassword(!showPassword)
                                }
                                className="shrink-0 w-8 h-8 flex items-center justify-center text-slate-400 hover:text-white transition-colors rounded-lg"
                                aria-label={
                                    showPassword
                                        ? "Hide password"
                                        : "Show password"
                                }
                            >
                                {showPassword ? (
                                    <EyeOff size={20} />
                                ) : (
                                    <Eye size={20} />
                                )}
                            </button>

                        </div>

                    </div>

                    {/* CONFIRM PASSWORD */}

                    <div>

                        <label className="text-slate-300 text-sm font-medium">
                            Confirm Password
                        </label>

                        <div className="flex items-center bg-[#1e293b] border border-slate-700/60 rounded-xl mt-2 px-4 transition-all duration-200 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10">

                            <Lock
                                className="text-slate-400 shrink-0"
                                size={20}
                            />

                            <input
                                type={
                                    showConfirmPassword
                                        ? "text"
                                        : "password"
                                }
                                value={confirmPassword}
                                onChange={(e) =>
                                    setConfirmPassword(e.target.value)
                                }
                                className="bg-transparent outline-none flex-1 min-w-0 py-4 px-3 text-white placeholder:text-slate-500"
                                placeholder="Confirm your new password"
                                autoComplete="new-password"
                            />

                            <button
                                type="button"
                                onClick={() =>
                                    setShowConfirmPassword(
                                        !showConfirmPassword
                                    )
                                }
                                className="shrink-0 w-8 h-8 flex items-center justify-center text-slate-400 hover:text-white transition-colors rounded-lg"
                                aria-label={
                                    showConfirmPassword
                                        ? "Hide password"
                                        : "Show password"
                                }
                            >
                                {showConfirmPassword ? (
                                    <EyeOff size={20} />
                                ) : (
                                    <Eye size={20} />
                                )}
                            </button>

                        </div>

                    </div>

                    {/* PASSWORD REQUIREMENT */}

                    <div className="bg-slate-800/50 border border-slate-700/40 rounded-xl px-4 py-3">

                        <p className="text-slate-400 text-xs">
                            Password must contain at least 6 characters.
                        </p>

                    </div>

                    {/* SUBMIT */}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white rounded-xl py-4 font-semibold text-base transition-all duration-200 shadow-lg shadow-blue-600/15 hover:shadow-blue-500/25 hover:-translate-y-[1px] disabled:opacity-60 disabled:hover:translate-y-0 disabled:cursor-not-allowed"
                    >
                        {loading
                            ? "Updating password..."
                            : "Reset Password"}
                    </button>

                </form>

                {/* BACK */}

                <div className="mt-7 pt-6 border-t border-slate-700/40 text-center">

                    <Link
                        to="/login"
                        className="text-blue-400 hover:text-blue-300 font-medium text-sm transition-colors"
                    >
                        ← Back to Login
                    </Link>

                </div>

            </div>

        </div>
    );
}