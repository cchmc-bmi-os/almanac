import getCookie from 'almanac/utils/get-cookie';
import { module, test } from 'qunit';

module('Unit | Utility | get cookie', function() {
  // Replace this with your real tests.
  test('it works', function(assert) {
    assert.equal(getCookie('whatwhat'), '', 'it sets the cookie correctly');
    assert.equal(getCookie('heyyou'), '', 'it sets the cookie correctly');
    assert.equal(getCookie('novalue'), '', 'it sets the cookie correctly');
  });
});