/**
 * Finance Account Search Module
 * Provides typeahead search functionality for accounts with inline creation support
 * API: GET /finance/accounts/search?q=<query>&limit=<limit>&include_ml=<bool>
 */

const lifeosAccountSearch = (() => {
  const SEARCH_DEBOUNCE_MS = 300;
  const SEARCH_TIMEOUT_MS = 5000;
  const MAX_RESULTS = 20;

  /**
   * Search accounts by name (typeahead)
   * @param {string} query - Search query (1-100 chars)
   * @param {number} limit - Max results (default 20)
   * @param {boolean} includeMl - Include ML suggestions (default true)
   * @returns {Promise<Array>} Array of account results
   */
  async function searchAccounts(query = '', limit = MAX_RESULTS, includeMl = true) {
    if (!query || query.trim().length === 0) {
      return [];
    }

    const params = new URLSearchParams({
      q: query.substring(0, 100),
      limit: Math.min(limit, MAX_RESULTS),
      include_ml: includeMl ? 'true' : 'false',
    });

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), SEARCH_TIMEOUT_MS);
      const response = await fetch(
        `/api/finance/accounts/search?${params.toString()}`,
        {
          method: 'GET',
          headers: window.lifeosAuth?.authHeaders?.() || {},
          signal: controller.signal,
        }
      );
      clearTimeout(timeout);

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          console.warn('[AccountSearch] Auth required');
          return [];
        }
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.results || [];
    } catch (err) {
      if (err.name === 'AbortError') {
        console.warn('[AccountSearch] Request timeout');
      } else {
        console.error('[AccountSearch] Error:', err);
      }
      return [];
    }
  }

  /**
   * Create a new account inline (minimal input)
   * @param {string} name - Account name (required, max 255 chars)
   * @param {string} accountType - Account type (asset/liability/equity/income/expense)
   * @param {string} [accountSubtype] - Account subtype (optional, depends on type)
   * @param {number} [categoryId] - Existing category ID (optional)
   * @param {string} [categoryNameNew] - New category name to create (optional)
   * @returns {Promise<Object>} Created account object {id, name, account_type, account_subtype, category_id, created_at}
   */
  async function createAccountInline(name, accountType, accountSubtype = null, categoryId = null, categoryNameNew = null) {
    if (!name || name.trim().length === 0) {
      throw new Error('Account name is required');
    }

    const body = {
      name: name.substring(0, 255),
      account_type: accountType,
    };

    if (accountSubtype) {
      body.account_subtype = accountSubtype;
    }

    if (categoryId) {
      body.category_id = categoryId;
    }

    if (categoryNameNew) {
      body.category_name_new = categoryNameNew;
    }

    try {
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
      const headers = window.lifeosAuth?.authHeaders?.() || {};
      headers['Content-Type'] = 'application/json';
      if (csrfToken) {
        headers['X-CSRF-Token'] = csrfToken;
      }

      const response = await fetch('/api/finance/accounts/inline', {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMsg = errorData.error || errorData.message || `HTTP ${response.status}`;
        throw new Error(errorMsg);
      }

      const data = await response.json();
      
      // Clear categories cache if a new category was created
      if (categoryNameNew && window.lifeosAccountCategories?.clearCache) {
        window.lifeosAccountCategories.clearCache();
      }

      return data.account;
    } catch (err) {
      console.error('[AccountSearch] Create error:', err);
      throw err;
    }
  }

  /**
   * Format a result for display
   * @param {Object} result - Result from search API
   * @returns {string} Display text
   */
  function formatResultDisplay(result) {
    if (!result) return '';
    const parts = [result.name];
    if (result.account_type) {
      parts.push(`[${result.account_type}]`);
    }
    if (result.account_subtype) {
      parts.push(`(${result.account_subtype})`);
    }
    return parts.join(' ');
  }

  /**
   * Highlight matched part of text
   * @param {string} text - Full text
   * @param {string} query - Search query
   * @returns {string} HTML with <mark> tags
   */
  function highlightMatch(text, query) {
    if (!text || !query) return text;
    const queryLower = query.toLowerCase();
    const textLower = text.toLowerCase();
    const idx = textLower.indexOf(queryLower);
    if (idx === -1) return text;
    return (
      text.substring(0, idx) +
      '<mark>' +
      text.substring(idx, idx + query.length) +
      '</mark>' +
      text.substring(idx + query.length)
    );
  }

  /**
   * Create a debounced search function
   * @param {Function} callback - Called with results
   * @param {number} delayMs - Debounce delay
   * @returns {Function} Debounced search function
   */
  function createDebouncedSearch(callback, delayMs = SEARCH_DEBOUNCE_MS) {
    let timeoutId = null;
    let lastQuery = '';

    return async (query) => {
      lastQuery = query;
      if (timeoutId !== null) {
        clearTimeout(timeoutId);
      }

      if (!query || query.trim().length === 0) {
        callback([]);
        return;
      }

      timeoutId = setTimeout(async () => {
        const results = await searchAccounts(query);
        // Only update if query hasn't changed
        if (query === lastQuery) {
          callback(results);
        }
      }, delayMs);
    };
  }

  return {
    searchAccounts,
    createAccountInline,
    formatResultDisplay,
    highlightMatch,
    createDebouncedSearch,
  };
})();

// Expose to window for global access
window.lifeosAccountSearch = lifeosAccountSearch;

// Export for module systems if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = lifeosAccountSearch;
}
