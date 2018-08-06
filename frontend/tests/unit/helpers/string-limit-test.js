import { stringLimit } from 'almanac/helpers/string-limit';
import { module, test } from 'qunit';

module('Unit | Helper | string limit', function() {
  // Replace this with your real tests.
  test('it works', function(assert) {
    assert.equal(stringLimit('this is a test', { numChars: 50 }), 'this is a test');
    assert.equal(stringLimit(''), '');
    assert.equal(stringLimit('this is a test', { numChars: 5 }), 'this...');
    assert.equal(stringLimit('this is a test'), 'this is a test');
  });
});
