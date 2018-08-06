import { isEmpty } from '@ember/utils';
import getCookie from 'almanac/utils/get-cookie';
import config from 'almanac/config/environment';

/**
 * Checks to see if the transition or environment is whitelisted for OIM cookie check.
 *
 */
let shouldCheckOimCookie = function(transition) {
  if (config.environment === 'development' || config.environment === 'bmilpdralmt1' || config.environment === 'test') {
    return false;
  } else if (transition && transition.targetName === 'index') {
    return false;
  }

  return true;
};

/**
 * Checks if the ObSSOCookie is invalid.Some environments and routes are white
 * listed in the shouldCheckOimCookie(...) function and do not need to be checked.
 *
 */
export default function isOimCookieValid(transition = null) {
  let oimCookie = getCookie('ObSSOCookie');

  if (shouldCheckOimCookie(transition) && (isEmpty(oimCookie) || oimCookie === 'loggedoutcontinue')) {
    return false;
  }

  return true;
}
