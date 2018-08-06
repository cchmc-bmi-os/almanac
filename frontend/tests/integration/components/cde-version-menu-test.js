import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find, findAll } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | cde version menu', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    await render(hbs`{{cde-version-menu}}`);

    assert.ok(find('.menu'));
    assert.equal(findAll('.nav .nav-item').length, 2);
    assert.ok(find('.menu .project').textContent.trim(), 'LPDR');
  });
});
