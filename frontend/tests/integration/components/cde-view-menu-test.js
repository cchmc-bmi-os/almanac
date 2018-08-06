import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find, findAll } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | cde view menu', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    let cde = {
      name: 'Test CDE'
    };

    this.set('cde', cde);
    await render(hbs`{{cde-view-menu cde=cde}}`);

    assert.ok(find('.menu'));
    assert.equal(findAll('.menu .nav-item').length, 5, 'it has 5 menu items');
    assert.equal(find('.menu .project').textContent.trim(), 'LPDR', 'it has the correct project name');
  });
});
