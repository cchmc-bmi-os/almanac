import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | cde version footer', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    this.set('siteQuestion', { name: 'testing' });

    await render(hbs`{{cde-version-footer siteQuestion=siteQuestion}}`);

    assert.ok(find('a.btn.btn-primary'))
    assert.equal(find('a.btn.btn-primary').textContent.trim(), 'Question');
  });
});
