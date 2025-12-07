/**
 * LifeOS Finance - Account Categories Module
 * Handles listing and creating account categories via API.
 * 
 * Usage:
 *   const { listCategories, createCategory } = window.lifeosAccountCategories;
 *   const cats = await listCategories(); // all categories
 *   const assetCats = await listCategories({ base_type: 'asset' });
 *   const custom = await createCategory('asset', 'Operating');
 * 
 * @module finance-account-categories
 */
(function () {
  "use strict";

  const API_BASE = "/api/finance";

  /**
   * Build auth headers from lifeosAuth
   * @returns {Promise<HeadersInit>}
   */
  async function authHeaders() {
    if (window.lifeosAuth && typeof window.lifeosAuth.authHeaders === "function") {
      return window.lifeosAuth.authHeaders();
    }
    return { "Content-Type": "application/json" };
  }

  /**
   * List account categories
   * @param {Object} [options] - Query options
   * @param {string} [options.base_type] - Filter by base_type (asset, liability, equity, revenue, expense)
   * @param {boolean} [options.include_system=true] - Include system categories
   * @returns {Promise<Array<{id: number, name: string, base_type: string, is_default: boolean, is_system: boolean}>>}
   */
  async function listCategories(options = {}) {
    const params = new URLSearchParams();
    if (options.base_type) {
      params.set("base_type", options.base_type);
    }
    if (options.include_system === false) {
      params.set("include_system", "false");
    }

    const url = `${API_BASE}/account-categories${params.toString() ? "?" + params : ""}`;
    const headers = await authHeaders();

    const resp = await fetch(url, {
      method: "GET",
      headers,
      credentials: "include",
    });

    const json = await resp.json();
    if (!json.ok) {
      throw new Error(json.error || "Failed to fetch categories");
    }
    return json.categories;
  }

  /**
   * Create a custom account category
   * @param {string} base_type - Base account type (asset, liability, equity, revenue, expense)
   * @param {string} name - Category name
   * @param {boolean} [is_default=false] - Whether this is the default category for the base_type
   * @returns {Promise<{id: number, name: string, base_type: string, is_default: boolean, is_system: boolean}>}
   */
  async function createCategory(base_type, name, is_default = false) {
    const headers = await authHeaders();
    const resp = await fetch(`${API_BASE}/account-categories`, {
      method: "POST",
      headers,
      credentials: "include",
      body: JSON.stringify({ base_type, name, is_default }),
    });

    const json = await resp.json();
    if (!json.ok) {
      const errorMap = {
        invalid_base_type: "Invalid account type",
        invalid_name: "Invalid category name",
        validation_error: "Validation failed",
      };
      throw new Error(errorMap[json.error] || json.error || "Failed to create category");
    }
    return json.category;
  }

  /**
   * Get categories grouped by base_type
   * @param {boolean} [includeSystem=true] - Include system categories
   * @returns {Promise<Object<string, Array>>} Map of base_type -> categories
   */
  async function listCategoriesGrouped(includeSystem = true) {
    const categories = await listCategories({ include_system: includeSystem });
    const grouped = {};
    for (const cat of categories) {
      if (!grouped[cat.base_type]) {
        grouped[cat.base_type] = [];
      }
      grouped[cat.base_type].push(cat);
    }
    return grouped;
  }

  /**
   * Cache for categories (refreshes on create)
   */
  let _cache = null;
  let _cacheTime = 0;
  const CACHE_TTL = 60000; // 1 minute

  /**
   * Get categories with caching
   * @param {Object} [options] - Query options
   * @returns {Promise<Array>}
   */
  async function listCategoriesCached(options = {}) {
    // Skip cache if filtering
    if (options.base_type || options.include_system === false) {
      return listCategories(options);
    }

    const now = Date.now();
    if (_cache && now - _cacheTime < CACHE_TTL) {
      return _cache;
    }

    const categories = await listCategories(options);
    _cache = categories;
    _cacheTime = now;
    return categories;
  }

  /**
   * Clear the categories cache
   */
  function clearCache() {
    _cache = null;
    _cacheTime = 0;
  }

  /**
   * Create category and clear cache
   * @param {string} base_type 
   * @param {string} name 
   * @param {boolean} [is_default=false]
   * @returns {Promise<Object>}
   */
  async function createCategoryAndClearCache(base_type, name, is_default = false) {
    const category = await createCategory(base_type, name, is_default);
    clearCache();
    return category;
  }

  // Public API
  const lifeosAccountCategories = {
    listCategories,
    createCategory,
    listCategoriesGrouped,
    listCategoriesCached,
    clearCache,
    createCategoryAndClearCache,
  };

  // Expose to window
  window.lifeosAccountCategories = lifeosAccountCategories;

  // ES module export (if supported)
  if (typeof module !== "undefined" && module.exports) {
    module.exports = lifeosAccountCategories;
  }
})();
