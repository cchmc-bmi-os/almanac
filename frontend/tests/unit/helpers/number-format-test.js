import { numberFormat } from 'almanac/helpers/number-format';
import { module, test } from 'qunit';

module('Unit | Helper | number format', function() {
  // Replace this with your real tests.
  test('it works', function(assert) {
    assert.equal(numberFormat([100000]), '100,000', 'this is a test');
    assert.equal(numberFormat([100]), '100', 'this is a test');
    assert.equal(numberFormat([1000000]), '1,000,000', 'this is a test');
  });
});
