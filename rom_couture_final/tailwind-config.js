tailwind.config = {
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "surface-container-lowest": "#ffffff",
                "primary-fixed-dim": "#ffb59b",
                "tertiary-fixed": "#ffdea7",
                "tertiary-container": "#966b00",
                "inverse-on-surface": "#f3f0f0",
                "secondary": "#4f5e81",
                "primary": "#914325",
                "on-tertiary-fixed-variant": "#5e4200",
                "tertiary": "#775400",
                "background": "#fbf9f8",
                "on-secondary": "#ffffff",
                "secondary-fixed": "#d9e2ff",
                "on-secondary-fixed-variant": "#384668",
                "error": "#ba1a1a",
                "surface-container": "#f0eded",
                "on-primary": "#ffffff",
                "on-error": "#ffffff",
                "on-background": "#1b1c1c",
                "on-surface": "#1b1c1c",
                "inverse-primary": "#ffb59a",
                "surface-container-high": "#e8e3e1",
                "on-surface-variant": "#55433d",
                "primary-container": "#ffdbcf",
                "secondary-container": "#dce2ff",
                "outline-variant": "#dbc1b9",
                "surface-container-low": "#f6f2f0",
                "outline": "#88726c",
                "on-primary-container": "#3b0a00",
                "surface": "#fbf9f8",
                "secondary-fixed-dim": "#bdc6eb",
                "primary-fixed": "#ffdbcf",
                "on-secondary-container": "#111c37",
                "on-primary-fixed": "#3b0a00",
                "on-primary-fixed-variant": "#712e12",
                "ink": "#171211",
                "muted": "#6d5a52",
                "ivory": "#fffaf6",
                "charcoal": "#221816",
                "gold": "#b9823b"
            },
            fontFamily: {
                "display-lg": ["Playfair Display", "Georgia", "serif"],
                "headline-sm": ["Playfair Display", "Georgia", "serif"],
                "headline-md": ["Playfair Display", "Georgia", "serif"],
                "body-lg": ["Inter", "system-ui", "sans-serif"],
                "body-md": ["Inter", "system-ui", "sans-serif"],
                "button-text": ["Space Grotesk", "system-ui", "sans-serif"],
                "label-caps": ["Space Grotesk", "system-ui", "sans-serif"]
            },
            fontSize: {
                "display-lg-mobile": ["2.5rem", { lineHeight: "1.05", letterSpacing: "-0.02em" }],
                "display-lg": ["4rem", { lineHeight: "1.05", letterSpacing: "-0.02em" }],
                "headline-xl": ["clamp(3rem, 8vw, 8.8rem)", { lineHeight: "0.92", letterSpacing: "-0.065em" }],
                "headline-md": ["1.75rem", { lineHeight: "1.2", letterSpacing: "-0.01em" }],
                "headline-sm": ["1.25rem", { lineHeight: "1.3", letterSpacing: "-0.01em" }],
                "body-lg": ["1rem", { lineHeight: "1.7" }],
                "body-md": ["0.875rem", { lineHeight: "1.6" }],
                "button-text": ["0.8125rem", { lineHeight: "1", letterSpacing: "0.08em" }],
                "label-caps": ["0.7rem", { lineHeight: "1", letterSpacing: "0.15em" }]
            },
            spacing: {
                "margin-mobile": "1.25rem",
                "margin-desktop": "2.5rem",
                "section": "clamp(4rem, 8vw, 8rem)"
            },
            maxWidth: {
                "container-max": "1280px"
            },
            boxShadow: {
                "soft": "0 24px 80px rgba(145, 67, 37, 0.12)",
                "cinema": "0 30px 100px rgba(23, 18, 17, 0.22)"
            },
            keyframes: {
                marquee: {
                    "0%": { transform: "translateX(0)" },
                    "100%": { transform: "translateX(-50%)" }
                },
                float: {
                    "0%, 100%": { transform: "translateY(0) rotate(0deg)" },
                    "50%": { transform: "translateY(-10px) rotate(1deg)" }
                },
                pulseRing: {
                    "0%": { transform: "scale(0.95)", opacity: "0.7" },
                    "100%": { transform: "scale(1.05)", opacity: "0.25" }
                }
            },
            animation: {
                marquee: "marquee 28s linear infinite",
                float: "float 7s ease-in-out infinite",
                pulseRing: "pulseRing 2.8s ease-out infinite"
            }
        }
    }
};
