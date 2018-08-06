import { helper } from '@ember/component/helper';
import { isEmpty } from '@ember/utils';
/**
 * This will limit the length of the string to 50 chars or
 * the specified limit with the numChars hash
 *
 * @module almanac/helpers/string-limit
 * @param {String|Array} string The string or array to use for limiting
 * @param {Object} hash Used to specify the limit of characters (numChars)
 * @returns {String}
 */
export function stringLimit(string, hash) {
  // set defaults
  if (Array.isArray(string)) {
    string = string[0];
  }

  let length = hash === undefined ? 50 : hash.numChars;

  // default to 50 characters if not specified
  if (isEmpty(length)) {
    length = 50;
  }

  // if the actual string is less than the specified length
  // just return the string.
  if (isEmpty(string) || string.length <= length) {
    return string;
  }

  // return the substring
  return `${string.substring(0, length).trim()}...`;
}

export default helper(stringLimit);