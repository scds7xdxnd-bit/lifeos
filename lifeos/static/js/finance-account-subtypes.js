/**
 * Finance Account Subtypes Loader
 * Manages fetching and caching of valid account subtypes per type
 * API: GET /finance/accounts/subtypes/<account_type>
 */

const lifeosAccountSubtypes = (() => {
  // Cache: { asset: [...], liability: [...], ... }
  const cache = {};
  const API_BASE = "/api/finance/accounts/subtypes";

  const VALID_TYPES = ['asset', 'liability', 'equity', 'income', 'expense'];

  /**
   * Fetch valid subtypes for an account type
   * @param {string} accountType - One of: asset, liability, equity, income, expense
   * @returns {Promise<Array<string>>} Array of valid subtype strings
   */
  async function getSubtypes(accountType) {
    // Validate input
    if (!accountType || !VALID_TYPES.includes(accountType)) {
      throw new Error(`Invalid account_type: ${accountType}. Must be one of: ${VALID_TYPES.join(', ')}`);
    }

    // Check cache
    if (cache[accountType]) {
      return cache[accountType];
    }

    try {
      const headers = Object.assign(
        { 'Content-Type': 'application/json' },
        window.lifeosAuth?.authHeaders?.() || {}
      );
      const response = await fetch(`${API_BASE}/${encodeURIComponent(accountType)}`, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      const subtypes = data.subtypes || [];

      // Cache result
      cache[accountType] = subtypes;
      return subtypes;
    } catch (err) {
      console.error(`[AccountSubtypes] Error fetching ${accountType}:`, err);
      throw err;
    }
  }

  /**
   * Get all valid account type + subtype combinations
   * @returns {Promise<Object>} { asset: [...], liability: [...], ... }
   */
  async function getAllSubtypes() {
    const result = {};
    for (const type of VALID_TYPES) {
      try {
        result[type] = await getSubtypes(type);
      } catch (err) {
        console.warn(`[AccountSubtypes] Failed to load ${type}:`, err);
        result[type] = [];
      }
    }
    return result;
  }

  /**
   * Clear the cache (useful for testing or forcing refresh)
   */
  function clearCache() {
    for (const key of Object.keys(cache)) {
      delete cache[key];
    }
  }

  /**
   * Get subtypes from cache (does not fetch if missing)
   * @param {string} accountType - Account type
   * @returns {Array<string> | null} Cached subtypes or null if not loaded
   */
  function getCachedSubtypes(accountType) {
    return cache[accountType] || null;
  }

  return {
    getSubtypes,
    getAllSubtypes,
    clearCache,
    getCachedSubtypes,
    VALID_TYPES,
  };
})();

// Expose to window for global access
window.lifeosAccountSubtypes = lifeosAccountSubtypes;

// Export for module systems if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = lifeosAccountSubtypes;
}
