/** * Utility function to handle try-catch with a function.
 * @param {Function} fn - The function to execute.
 * @returns {Array} An array containing the result or error.
 */
export const tryCatch = (fn) => {
  try {
    const result = fn();
    return [result, null];
  } catch (err) {
    return [null, err];
  }
};