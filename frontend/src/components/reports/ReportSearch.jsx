import { Search } from "lucide-react";

const ReportSearch = ({ search, setSearch }) => {
  return (
    <div className="bg-white rounded-xl shadow-lg p-5">

      <div className="relative">

        <Search
          size={20}
          className="absolute left-4 top-3 text-gray-400"
        />

        <input
          type="text"
          placeholder="Search reports..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="
            w-full
            border
            border-gray-300
            rounded-lg
            py-3
            pl-12
            pr-4
            focus:outline-none
            focus:ring-2
            focus:ring-blue-500
          "
        />

      </div>

    </div>
  );
};

export default ReportSearch;