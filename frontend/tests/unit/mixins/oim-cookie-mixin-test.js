import EmberObject from '@ember/object';
import OimCookieMixinMixin from 'almanac/mixins/oim-cookie-mixin';
import { module, test } from 'qunit';

module('Unit | Mixin | oim cookie mixin', function() {
  // Replace this with your real tests.
  test('it works', function(assert) {
    let OimCookieMixinObject = EmberObject.extend(OimCookieMixinMixin);
    let subject = OimCookieMixinObject.create();
    assert.ok(subject);
  });
});
