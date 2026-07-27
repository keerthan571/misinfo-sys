import React, { useState } from "react";
import "./SearchBar.css";

const SearchBar = ({ onSearch }) => {
  const [searchText, setSearchText] = useState("");

  const handleSearch = () => {
    if (onSearch) {
      onSearch(searchText.trim());
    }
  };

  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="Search USER_12, BOT_3..."
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") handleSearch();
        }}
      />

      <button onClick={handleSearch}>
        🔍 Search
      </button>
    </div>
  );
};

export default SearchBar;