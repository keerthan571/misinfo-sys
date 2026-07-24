export default function DashboardHeader({ userName = "User" }) {
  const hour = new Date().getHours();

  let greeting = "Welcome";

  if (hour < 12) greeting = "Good Morning";
  else if (hour < 17) greeting = "Good Afternoon";
  else greeting = "Good Evening";

  return (
    <div>
      <h1 className="text-4xl font-bold text-white">
        {greeting}, {userName} 👋
      </h1>

      <p className="text-gray-400 mt-2">
        Here's an overview of your misinformation analysis activity.
      </p>
    </div>
  );
}