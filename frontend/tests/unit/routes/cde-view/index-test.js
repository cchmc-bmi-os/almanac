import { module, test } from 'qunit';
import { setupTest } from 'ember-qunit';

module('Unit | Route | cde view/index', function(hooks) {
  setupTest(hooks);

  test('it exists', function(assert) {
    let route = this.owner.lookup('route:cde-view/index');
    assert.ok(route);
  });
});
