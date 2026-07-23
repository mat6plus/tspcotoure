/**
 * TSP Couture - Centralized Security & Validation Module
 * Provides XSS protection, sanitization, and strict input validation utilities.
 */

(function () {
    const SecurityUtils = {
        /**
         * HTML entity encodes a string to prevent XSS injection.
         * @param {string} str - Raw user input string.
         * @returns {string} Safe, sanitized string with HTML characters encoded.
         */
        sanitizeInput: function (str) {
            if (typeof str !== 'string') return '';
            return str
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#x27;')
                .replace(/\//g, '&#x2F;');
        },

        /**
         * Safely renders text in a DOM element by setting its textContent.
         * This strictly prevents the execution of nested script tags or HTML tags.
         * @param {HTMLElement} element - Target DOM element.
         * @param {string} text - Text value to display.
         */
        safeRender: function (element, text) {
            if (element) {
                element.textContent = text || '';
            }
        },

        /**
         * Validates an email address against a secure RFC 5322 regex pattern.
         * @param {string} email - Email address input.
         * @returns {boolean} True if email conforms to strict format rules.
         */
        validateEmail: function (email) {
            if (typeof email !== 'string') return false;
            // Strict email pattern that filters out invalid formatting
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            return emailRegex.test(email.trim());
        },

        /**
         * Validates a phone number against international/local standard patterns.
         * @param {string} phone - Phone input string.
         * @returns {boolean} True if valid structure.
         */
        validatePhone: function (phone) {
            if (typeof phone !== 'string') return false;
            // Matches international format (+1234567890) and common national formats
            const phoneRegex = /^\+?[0-9\s\-()]{7,20}$/;
            return phoneRegex.test(phone.trim());
        },

        /**
         * Validates body measurements to ensure they are numeric and within plausible human limits.
         * @param {string|number} value - Measurement value.
         * @param {number} min - Minimum limit in cm (e.g. 10cm).
         * @param {number} max - Maximum limit in cm (e.g. 300cm).
         * @returns {boolean} True if measurement is valid.
         */
        validateMeasurement: function (value, min = 10, max = 300) {
            const numericValue = Number(value);
            if (isNaN(numericValue)) return false;
            return numericValue >= min && numericValue <= max;
        },

        /**
         * Validates a file drop or selection against strict security whitelists.
         * @param {File} file - Selected file.
         * @param {Object} options - Validation constraints.
         * @param {Array<string>} options.allowedExtensions - Whitelist of extensions (lowercase, e.g. ['jpg', 'png']).
         * @param {Array<string>} options.allowedMimeTypes - Whitelist of MIME types (e.g. ['image/jpeg', 'image/png']).
         * @param {number} options.maxSizeBytes - Maximum allowed size in bytes.
         * @returns {{isValid: boolean, error: string|null}} Object detailing validation success or failure message.
         */
        validateFile: function (file, options = {}) {
            const defaults = {
                allowedExtensions: ['jpg', 'jpeg', 'png', 'webp'],
                allowedMimeTypes: ['image/jpeg', 'image/png', 'image/webp'],
                maxSizeBytes: 10 * 1024 * 1024 // 10MB default
            };

            const config = Object.assign({}, defaults, options);

            if (!file) {
                return { isValid: false, error: 'No file selected.' };
            }

            // 1. Size Validation
            if (file.size > config.maxSizeBytes) {
                const maxSizeMb = (config.maxSizeBytes / (1024 * 1024)).toFixed(1);
                return { isValid: false, error: `File size exceeds the ${maxSizeMb}MB maximum limit.` };
            }

            // 2. Extension Validation
            const dotIndex = file.name.lastIndexOf('.');
            if (dotIndex === -1) {
                return { isValid: false, error: 'File has no valid extension.' };
            }
            const extension = file.name.substring(dotIndex + 1).toLowerCase();
            if (!config.allowedExtensions.includes(extension)) {
                return { isValid: false, error: `Invalid file extension. Only ${config.allowedExtensions.join(', ')} are allowed.` };
            }

            // 3. MIME Type Validation
            if (!config.allowedMimeTypes.includes(file.type)) {
                return { isValid: false, error: 'Invalid image format type. Web-safe images (JPEG, PNG, WEBP) only.' };
            }

            return { isValid: true, error: null };
        }
    };

    // Attach to global window object and freeze to prevent tampering
    window.SecurityUtils = Object.freeze(SecurityUtils);
})();
