export default function getCookie(cname) {
  let value = '';
  let name = `${cname}=`;
  let ca = document.cookie.split(';');

  ca.some((cookie) => {
    while (cookie.charAt(0) === ' ') {
      cookie = cookie.substring(1);
    }

    if (cookie.indexOf(name) >= 0) {
      value = cookie.substring(name.length, cookie.length);
      return true;
    }
  });

  return value;
}
