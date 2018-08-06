import { module, test } from 'qunit';
import { setupTest } from 'ember-qunit';

module('Unit | Route | cde version', function(hooks) {
  setupTest(hooks);

  test('it exists', function(assert) {
    let route = this.owner.lookup('route:cde-version');
    assert.ok(route);
  });
});
