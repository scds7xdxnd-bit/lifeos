/**
 * LifeOS Calendar - API Module
 * Handles calendar events and interpretations CRUD operations.
 * 
 * Usage:
 *   const { listEvents, createEvent, confirmInterpretation } = window.lifeosCalendar;
 *   const events = await listEvents({ start_date: '2025-12-01', end_date: '2025-12-31' });
 *   const event = await createEvent({ title: 'Gym workout', start_time: '2025-12-07T18:00:00' });
 * 
 * @module calendar-api
 */
(function () {
  "use strict";

  const API_BASE = "/api/calendar";

  /**
   * Build auth headers from lifeosAuth with CSRF token from meta tag
   * The meta tag CSRF is session-bound and more reliable than localStorage
   * @param {Object} [extra={}] - Additional headers to merge
   * @returns {HeadersInit}
   */
  function authHeaders(extra = {}) {
    let base = {};
    if (window.lifeosAuth && typeof window.lifeosAuth.authHeaders === "function") {
      base = window.lifeosAuth.authHeaders(extra);
    } else {
      base = { "Content-Type": "application/json", ...extra };
    }
    // Prefer CSRF token from meta tag (matches current session) over localStorage
    const metaCsrf = document.querySelector('meta[name="csrf-token"]')?.content;
    if (metaCsrf) base["X-CSRF-Token"] = metaCsrf;
    return base;
  }

  // ==================== Calendar Events ====================

  /**
   * List calendar events with optional filters
   * @param {Object} [options] - Query options
   * @param {string} [options.start_date] - ISO datetime start filter
   * @param {string} [options.end_date] - ISO datetime end filter
   * @param {string} [options.source] - Source filter (manual, sync_google, sync_apple, api)
   * @param {number} [options.limit=50] - Max results
   * @param {number} [options.offset=0] - Pagination offset
   * @returns {Promise<Array>} List of calendar events
   */
  async function listEvents(options = {}) {
    const params = new URLSearchParams();
    if (options.start_date) params.set("start_date", options.start_date);
    if (options.end_date) params.set("end_date", options.end_date);
    if (options.source) params.set("source", options.source);
    if (options.limit) params.set("limit", String(options.limit));
    if (options.offset) params.set("offset", String(options.offset));

    const url = `${API_BASE}/events${params.toString() ? "?" + params : ""}`;
    const resp = await fetch(url, {
      method: "GET",
      headers: authHeaders(),
      credentials: "include",
    });

    const json = await resp.json();
    if (!json.ok) {
      throw new Error(json.error || "Failed to fetch events");
    }
    return json.events;
  }

  /**
   * Get a single calendar event by ID
   * @param {number} eventId - Event ID
   * @returns {Promise<Object>} Event with interpretations
   */
  async function getEvent(eventId) {
    const resp = await fetch(`${API_BASE}/events/${eventId}`, {
      method: "GET",
      headers: authHeaders(),
      credentials: "include",
    });

    const json = await resp.json();
    if (!json.ok) {
      throw new Error(json.error || "Failed to fetch event");
    }
    return json.event;
  }

  /**
   * Create a new calendar event
   * @param {Object} data - Event data
   * @param {string} data.title - Event title (required)
   * @param {string} data.start_time - ISO datetime (required)
   * @param {string} [data.end_time] - ISO datetime
   * @param {string} [data.description] - Event description
   * @param {string} [data.location] - Location
   * @param {boolean} [data.all_day=false] - All-day event
   * @param {string} [data.color] - Hex color
   * @param {boolean} [data.is_private=false] - Privacy flag
   * @param {Array<string>} [data.tags=[]] - Tags
   * @returns {Promise<Object>} Created event
   */
  async function createEvent(data) {
    const resp = await fetch(`${API_BASE}/events`, {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      credentials: "include",
      body: JSON.stringify(data),
    });

    const json = await resp.json();
    if (!json.ok) {
      throw new Error(json.error || "Failed to create event");
    }
    return json.event;
  }

  /**
   * Update an existing calendar event
   * @param {number} eventId - Event ID
   * @param {Object} data - Fields to update
   * @returns {Promise<Object>} Updated event
   */
  async function updateEvent(eventId, data) {
    const resp = await fetch(`${API_BASE}/events/${eventId}`, {
      method: "PATCH",
      headers: authHeaders({ "Content-Type": "application/json" }),
      credentials: "include",
      body: JSON.stringify(data),
    });

    const json = await resp.json();
    if (!json.ok) {
      throw new Error(json.error || "Failed to update event");
    }
    return json.event;
  }

  /**
   * Delete a calendar event
   * @param {number} eventId - Event ID
   * @returns {Promise<void>}
   */
  async function deleteEvent(eventId) {
    const resp = await fetch(`${API_BASE}/events/${eventId}`, {
      method: "DELETE",
      headers: authHeaders(),
      credentials: "include",
    });

    const json = await resp.json();
    if (!json.ok) {
      throw new Error(json.error || "Failed to delete event");
    }
  }

  // ==================== Interpretations ====================

  /**
   * Get pending interpretations for review
   * @param {Object} [options] - Query options
   * @param {string} [options.domain] - Filter by domain
   * @param {number} [options.limit=50] - Max results
   * @param {number} [options.offset=0] - Pagination offset
   * @returns {Promise<Array>} List of pending interpretations
   */
  async function getPendingInterpretations(options = {}) {
    const params = new URLSearchParams();
    if (options.domain) params.set("domain", options.domain);
    if (options.limit) params.set("limit", String(options.limit));
    if (options.offset) params.set("offset", String(options.offset));

    const url = `${API_BASE}/interpretations/pending${params.toString() ? "?" + params : ""}`;
    const resp = await fetch(url, {
      method: "GET",
      headers: authHeaders(),
      credentials: "include",
    });

    const json = await resp.json();
    if (!json.ok) {
      throw new Error(json.error || "Failed to fetch interpretations");
    }
    return json.interpretations;
  }

  /**
   * Update interpretation status
   * @param {number} interpretationId - Interpretation ID
   * @param {string} status - New status: 'confirmed', 'rejected', 'ignored'
   * @returns {Promise<Object>} Updated interpretation
   */
  async function updateInterpretation(interpretationId, status) {
    const resp = await fetch(`${API_BASE}/interpretations/${interpretationId}`, {
      method: "PATCH",
      headers: authHeaders({ "Content-Type": "application/json" }),
      credentials: "include",
      body: JSON.stringify({ status }),
    });

    const json = await resp.json();
    if (!json.ok) {
      throw new Error(json.error || "Failed to update interpretation");
    }
    return json.interpretation;
  }

  /**
   * Confirm an interpretation (creates domain record)
   * @param {number} interpretationId - Interpretation ID
   * @returns {Promise<Object>} Updated interpretation
   */
  async function confirmInterpretation(interpretationId) {
    return updateInterpretation(interpretationId, "confirmed");
  }

  /**
   * Reject an interpretation
   * @param {number} interpretationId - Interpretation ID
   * @returns {Promise<Object>} Updated interpretation
   */
  async function rejectInterpretation(interpretationId) {
    return updateInterpretation(interpretationId, "rejected");
  }

  /**
   * Ignore an interpretation
   * @param {number} interpretationId - Interpretation ID
   * @returns {Promise<Object>} Updated interpretation
   */
  async function ignoreInterpretation(interpretationId) {
    return updateInterpretation(interpretationId, "ignored");
  }

  // ==================== Utilities ====================

  /**
   * Get events for a specific date
   * @param {Date|string} date - Date to fetch events for
   * @returns {Promise<Array>} Events for that day
   */
  async function getEventsForDate(date) {
    const d = typeof date === "string" ? new Date(date) : date;
    const dateStr = d.toISOString().split("T")[0];
    return listEvents({
      start_date: dateStr + "T00:00:00",
      end_date: dateStr + "T23:59:59",
    });
  }

  /**
   * Get events for current week
   * @returns {Promise<Array>} Events for this week
   */
  async function getEventsThisWeek() {
    const today = new Date();
    const weekStart = new Date(today);
    weekStart.setDate(today.getDate() - today.getDay());
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6);

    return listEvents({
      start_date: weekStart.toISOString(),
      end_date: weekEnd.toISOString(),
    });
  }

  /**
   * Get pending interpretation count
   * @param {string} [domain] - Optional domain filter
   * @returns {Promise<number>} Count of pending interpretations
   */
  async function getPendingCount(domain = null) {
    const interpretations = await getPendingInterpretations({ domain, limit: 500 });
    return interpretations.length;
  }

  // ==================== Domain Constants ====================

  const DOMAINS = {
    finance: { name: "Finance", icon: "💰", color: "#0b4f9c" },
    health: { name: "Health", icon: "❤️", color: "#dc2626" },
    habits: { name: "Habits", icon: "🎯", color: "#7c3aed" },
    skills: { name: "Skills", icon: "📚", color: "#059669" },
    projects: { name: "Projects", icon: "📁", color: "#ea580c" },
    relationships: { name: "Relationships", icon: "👥", color: "#db2777" },
  };

  const SOURCES = {
    manual: "Manual",
    sync_google: "Google Calendar",
    sync_apple: "Apple Calendar",
    api: "API",
  };

  // Public API
  const lifeosCalendar = {
    // Events
    listEvents,
    getEvent,
    createEvent,
    updateEvent,
    deleteEvent,
    // Interpretations
    getPendingInterpretations,
    updateInterpretation,
    confirmInterpretation,
    rejectInterpretation,
    ignoreInterpretation,
    // Utilities
    getEventsForDate,
    getEventsThisWeek,
    getPendingCount,
    // Constants
    DOMAINS,
    SOURCES,
  };

  // Expose to window
  window.lifeosCalendar = lifeosCalendar;

  // ES module export (if supported)
  if (typeof module !== "undefined" && module.exports) {
    module.exports = lifeosCalendar;
  }
})();
