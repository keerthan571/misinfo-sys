import { useState } from "react";
import { Mail } from "lucide-react";
import { Link } from "react-router-dom";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!email) {
      alert("Please enter your email.");
      return;
    }

    setLoading(true);

    setTimeout(() => {
      alert("Password reset link sent successfully.");
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
          Reset Your Password
        </p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">

          <div>
            <label className="text-gray-300">Email</label>

            <div className="flex items-center bg-slate-800 rounded-xl mt-2 px-4">
              <Mail className="text-gray-400" />

              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-transparent outline-none w-full p-4 text-white"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 rounded-xl py-4 font-bold transition disabled:opacity-60"
          >
            {loading ? "Sending..." : "Send Reset Link"}
          </button>

        </form>

        <div className="text-center mt-6">
          <Link
            to="/login"
            className="text-blue-400 hover:underline"
          >
            Back to Login
          </Link>
        </div>

      </div>
    </div>
  );
}