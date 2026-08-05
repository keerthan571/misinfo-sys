const PUBLISHERS = [

    {
        keywords: [
            "india today"
        ],
        name: "India Today",
        verified: true,
        followers: 18500000,
        type: "News Publisher",
        color: "#d71920"
    },

    {
        keywords: [
            "india tv"
        ],
        name: "India TV",
        verified: true,
        followers: 16200000,
        type: "News Publisher",
        color: "#0057b8"
    },

    {
        keywords: [
            "ndtv"
        ],
        name: "NDTV",
        verified: true,
        followers: 12400000,
        type: "News Publisher",
        color: "#c62828"
    },

    {
        keywords: [
            "bbc",
            "bbc news"
        ],
        name: "BBC News",
        verified: true,
        followers: 24000000,
        type: "News Publisher",
        color: "#bb1919"
    },

    {
        keywords: [
            "cnn"
        ],
        name: "CNN",
        verified: true,
        followers: 62000000,
        type: "News Publisher",
        color: "#cc0000"
    },

    {
        keywords: [
            "reuters"
        ],
        name: "Reuters",
        verified: true,
        followers: 26000000,
        type: "News Agency",
        color: "#ff8000"
    },

    {
        keywords: [
            "aaj tak"
        ],
        name: "Aaj Tak",
        verified: true,
        followers: 22000000,
        type: "News Publisher",
        color: "#d50000"
    },

    {
        keywords: [
            "zee news"
        ],
        name: "Zee News",
        verified: true,
        followers: 9800000,
        type: "News Publisher",
        color: "#b71c1c"
    },

    {
        keywords: [
            "news18"
        ],
        name: "News18",
        verified: true,
        followers: 11300000,
        type: "News Publisher",
        color: "#1e3a8a"
    },

    {
        keywords: [
            "times now"
        ],
        name: "Times Now",
        verified: true,
        followers: 9500000,
        type: "News Publisher",
        color: "#0f4c81"
    },

    {
        keywords: [
            "republic",
            "republic tv"
        ],
        name: "Republic TV",
        verified: true,
        followers: 9100000,
        type: "News Publisher",
        color: "#d32f2f"
    },

    {
        keywords: [
            "abp news"
        ],
        name: "ABP News",
        verified: true,
        followers: 8700000,
        type: "News Publisher",
        color: "#d32f2f"
    },

    {
        keywords: [
            "the hindu"
        ],
        name: "The Hindu",
        verified: true,
        followers: 8400000,
        type: "Newspaper",
        color: "#003366"
    },

    {
        keywords: [
            "hindustan times"
        ],
        name: "Hindustan Times",
        verified: true,
        followers: 7600000,
        type: "Newspaper",
        color: "#0d47a1"
    },

    {
        keywords: [
            "indian express"
        ],
        name: "Indian Express",
        verified: true,
        followers: 6900000,
        type: "Newspaper",
        color: "#d32f2f"
    }

];

export default class SourceDetector {

    static detect(text = "") {

        if (!text) {
            return this.defaultSource();
        }

        const content =
            text
                .replace(/\r/g, "")
                .toLowerCase();

        // STEP 1
        // Detect known publishers

        for (const publisher of PUBLISHERS) {

            if (
                publisher.keywords.some(
                    keyword =>
                        content.includes(keyword)
                )
            ) {
                return publisher;
            }

        }

        // STEP 2
        // Detect unknown publisher from first OCR lines

        const lines =
            text
                .split("\n")
                .map(line => line.trim())
                .filter(Boolean)
                .slice(0, 6);

        for (const line of lines) {

            const clean =
                line
                    .replace(/[^A-Za-z ]/g, "")
                    .trim();

            if (
                clean.length < 4 ||
                clean.length > 35
            ) {
                continue;
            }

            const lower =
                clean.toLowerCase();

            if (
                lower.includes("breaking") ||
                lower.includes("live") ||
                lower.includes("exclusive") ||
                lower.includes("watch live") ||
                lower.includes("subscribe")
            ) {
                continue;
            }

            if (
                /^[A-Z ]+$/.test(line) ||
                /^[A-Z][a-z]+(?: [A-Z][a-z]+)*$/.test(clean)
            ) {

                return {

                    name:
                        clean
                            .split(" ")
                            .map(
                                word =>
                                    word.charAt(0).toUpperCase() +
                                    word.slice(1).toLowerCase()
                            )
                            .join(" "),

                    verified: false,

                    followers: null,

                    type: "Publisher",

                    color: "#64748b"

                };

            }

        }

        return this.defaultSource();
    }

    static defaultSource() {

        return {

            name: "Original Source",

            verified: false,

            followers: null,

            type: "Unknown",

            color: "#7c3aed"

        };

    }

}