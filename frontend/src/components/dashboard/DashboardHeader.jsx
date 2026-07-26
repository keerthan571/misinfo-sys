import { FaUserCircle } from "react-icons/fa";

const DashboardHeader = ({ userName }) => {
  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const hour = new Date().getHours();

  let greeting = "Good Evening";

  if (hour < 12) {
    greeting = "Good Morning";
  } else if (hour < 17) {
    greeting = "Good Afternoon";
  }

  return (
    <div className="
      bg-slate-100
      rounded-3xl
      border border-slate-200
      shadow-md
      p-8
      flex
      justify-between
      items-center
      mb-8
    ">

      <div>

        <h1 className="text-4xl font-extrabold text-slate-800 leading-tight">
          AI Misinformation
          <br />
          Dashboard
        </h1>

        <p className="text-slate-600 mt-3 text-lg">
          Monitor and analyse misinformation efficiently.
        </p>

        <p className="text-sm text-slate-500 mt-4">
          {today}
        </p>

      </div>

      <div className="
        flex
        items-center
        gap-4
        bg-white
        rounded-2xl
        px-6
        py-4
        shadow-sm
      ">

        <FaUserCircle
          className="text-blue-600"
          size={54}
        />

        <div>

          <p className="font-bold text-slate-800 text-lg">
            {greeting}
          </p>

          <p className="text-slate-600">
            Welcome back,
            <br />
            <span className="font-semibold">
              {userName}
            </span>
          </p>

        </div>

      </div>

    </div>
  );
};

export default DashboardHeader;