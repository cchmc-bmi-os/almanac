import { module, test } from 'qunit';
import { setupTest } from 'ember-qunit';

module('Unit | Route | cde view/visibility', function(hooks) {
  setupTest(hooks);

  test('it exists', function(assert) {
    let route = this.owner.lookup('route:cde-view/visibility');
    assert.ok(route);
  });
});
